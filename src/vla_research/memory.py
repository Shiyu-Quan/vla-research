from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(value: str, max_length: int = 80) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower())
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:max_length].rstrip("-") or "paper"


class ResearchMemory:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    @property
    def papers_dir(self) -> Path:
        return self.root / "papers"

    @property
    def index_path(self) -> Path:
        return self.papers_dir / "index.json"

    @property
    def gaps_path(self) -> Path:
        return self.root / "gaps" / "gap-table.json"

    @property
    def reading_queue_path(self) -> Path:
        return self.root / "state" / "reading-queue.json"

    def ensure(self) -> None:
        for directory in (
            "papers",
            "pdfs",
            "gaps",
            "state",
            "taxonomy",
            "matrices",
        ):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self._ensure_json_file(self.index_path, [])
        self._ensure_json_file(self.gaps_path, [])
        self._ensure_json_file(self.reading_queue_path, [])

    def search_papers(
        self,
        query: str = "",
        tags: list[str] | None = None,
        domain: str = "",
        verification_status: str = "",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        requested_tags = {tag.lower() for tag in (tags or [])}
        terms = [
            term.lower()
            for term in re.findall(r"[a-zA-Z0-9_.+-]+", query)
        ]
        results: list[tuple[int, dict[str, Any]]] = []

        for paper in self.load_index():
            paper_tags = {
                str(tag).lower() for tag in paper.get("tags", [])
            }
            if requested_tags and not requested_tags.issubset(paper_tags):
                continue
            if domain and domain.lower() not in str(
                paper.get("domain", "")
            ).lower():
                continue
            if verification_status and verification_status.lower() != str(
                paper.get("verification_status", "")
            ).lower():
                continue

            haystack = self._paper_search_text(paper)
            title = str(paper.get("title", "")).lower()
            score = 1 if not terms else 0
            for term in terms:
                if term in haystack:
                    score += 3 if term in title else 1
            if score:
                results.append((score, self._summary(paper)))

        results.sort(
            key=lambda item: (-item[0], str(item[1].get("id", "")))
        )
        return [item for _, item in results[: max(1, limit)]]

    def get_paper(self, paper_id: str) -> dict[str, Any]:
        target = paper_id.lower()
        for paper in self.load_index():
            if str(paper.get("id", "")).lower() == target:
                enriched = dict(paper)
                card = self._find_card_path(str(paper["id"]))
                if card:
                    enriched["card_path"] = str(card)
                    enriched["card_text"] = card.read_text(encoding="utf-8")
                return enriched
        raise KeyError(f"Paper not found: {paper_id}")

    def add_or_update_paper(
        self,
        paper: dict[str, Any],
    ) -> dict[str, Any]:
        self.ensure()
        paper_id = str(paper.get("id", "")).strip()
        existing = {
            str(item.get("id")): item for item in self.load_index()
        }
        merged = dict(existing.get(paper_id, {}))
        merged.update(paper)
        normalized = self._normalize_paper(merged)
        existing[normalized["id"]] = normalized
        self.save_index(list(existing.values()))

        card_path = self._card_path(normalized)
        for old_card in self.papers_dir.glob(f"{normalized['id']}-*.md"):
            if old_card != card_path:
                old_card.unlink()
        card_path.write_text(
            self._render_card(normalized),
            encoding="utf-8",
        )
        result = dict(normalized)
        result["card_path"] = str(card_path)
        return result

    def list_gaps(
        self,
        status: str = "",
        priority: str = "",
        tag: str = "",
    ) -> list[dict[str, Any]]:
        gaps = self._load_json(self.gaps_path, [])
        filtered = []
        for gap in gaps:
            if status and status.lower() != str(
                gap.get("status", "")
            ).lower():
                continue
            if priority and priority.lower() != str(
                gap.get("priority", "")
            ).lower():
                continue
            gap_tags = {
                str(item).lower() for item in gap.get("tags", [])
            }
            if tag and tag.lower() not in gap_tags:
                continue
            filtered.append(gap)
        return filtered

    def recommend_next_reading(
        self,
        focus: str = "",
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        papers = {
            str(paper.get("id")): paper for paper in self.load_index()
        }
        queue = self._load_json(self.reading_queue_path, [])
        terms = [
            term.lower()
            for term in re.findall(r"[a-zA-Z0-9_.+-]+", focus)
        ]
        recommendations: list[tuple[int, dict[str, Any]]] = []
        queued_ids: set[str] = set()

        for entry in queue:
            paper_id = str(entry.get("paper_id", ""))
            paper = papers.get(paper_id)
            if not paper:
                continue
            score = int(entry.get("priority", 0))
            score += self._focus_score(paper, terms)
            reason = str(entry.get("reason", "Queued reading"))
            recommendations.append(
                (score, self._recommendation(paper, reason))
            )
            queued_ids.add(paper_id)

        for paper_id, paper in papers.items():
            if paper_id in queued_ids:
                continue
            if str(paper.get("read_status", "")).lower() == "read":
                continue
            score = self._focus_score(paper, terms)
            tags = {str(tag).lower() for tag in paper.get("tags", [])}
            if tags.intersection(
                {"hardware-profiling", "dedicated-accelerator", "fpga", "xpu"}
            ):
                score += 20
            if score:
                recommendations.append(
                    (
                        score,
                        self._recommendation(
                            paper,
                            "Matches focus and remains unread",
                        ),
                    )
                )

        recommendations.sort(
            key=lambda item: (-item[0], str(item[1].get("id", "")))
        )
        return [item for _, item in recommendations[: max(1, limit)]]

    def load_index(self) -> list[dict[str, Any]]:
        self.ensure()
        data = self._load_json(self.index_path, [])
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON array in {self.index_path}")
        return data

    def save_index(self, papers: list[dict[str, Any]]) -> None:
        self.ensure()
        ordered = sorted(papers, key=lambda item: str(item.get("id", "")))
        self.index_path.write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _focus_score(
        self,
        paper: dict[str, Any],
        terms: list[str],
    ) -> int:
        haystack = self._paper_search_text(paper)
        return sum(10 for term in terms if term in haystack)

    def _recommendation(
        self,
        paper: dict[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        result = self._summary(paper)
        result["reason"] = reason
        return result

    def _summary(self, paper: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": paper.get("id"),
            "title": paper.get("title"),
            "year": paper.get("year"),
            "domain": paper.get("domain"),
            "main_technique": paper.get("main_technique"),
            "hardware_relevance": paper.get("hardware_relevance"),
            "metrics": paper.get("metrics", {}),
            "tags": paper.get("tags", []),
            "read_status": paper.get("read_status", ""),
            "verification_status": paper.get(
                "verification_status",
                "",
            ),
        }

    def _paper_search_text(self, paper: dict[str, Any]) -> str:
        values = [
            paper.get("id", ""),
            paper.get("title", ""),
            paper.get("domain", ""),
            paper.get("main_technique", ""),
            paper.get("hardware_relevance", ""),
            " ".join(str(tag) for tag in paper.get("tags", [])),
            json.dumps(paper.get("metrics", {}), ensure_ascii=False),
            " ".join(str(claim) for claim in paper.get("key_claims", [])),
        ]
        return " ".join(str(value).lower() for value in values)

    def _normalize_paper(
        self,
        paper: dict[str, Any],
    ) -> dict[str, Any]:
        if not str(paper.get("id", "")).strip():
            raise ValueError("Paper requires an id")
        if not str(paper.get("title", "")).strip():
            raise ValueError("Paper requires a title")

        normalized = dict(paper)
        normalized["id"] = str(normalized["id"]).strip()
        normalized["title"] = str(normalized["title"]).strip()
        defaults: dict[str, Any] = {
            "year": "",
            "status": "",
            "url": "",
            "domain": "",
            "model_type": "",
            "action_head": "",
            "main_technique": "",
            "hardware_relevance": "",
            "metrics": {},
            "tags": [],
            "evidence_level": "seed",
            "read_status": "queued",
            "verification_status": "unverified",
            "key_claims": [],
            "limitations": [],
            "notes": "",
        }
        for key, value in defaults.items():
            normalized.setdefault(key, value)
        normalized["updated_at"] = datetime.now(timezone.utc).isoformat()
        return normalized

    def _render_card(self, paper: dict[str, Any]) -> str:
        front_matter = json.dumps(paper, ensure_ascii=False, indent=2)
        claims = "\n".join(
            f"- {claim}" for claim in paper.get("key_claims", [])
        ) or "- No extracted claims yet."
        limitations = "\n".join(
            f"- {item}" for item in paper.get("limitations", [])
        ) or "- No limitations recorded yet."
        relevance = (
            paper.get("hardware_relevance", "")
            or "Not yet summarized."
        )
        notes = paper.get("notes", "") or "Add reading notes here."
        return (
            f"---\n{front_matter}\n---\n\n"
            f"# {paper['title']}\n\n"
            f"## Why It Matters\n\n{relevance}\n\n"
            f"## Key Claims\n\n{claims}\n\n"
            f"## Limitations\n\n{limitations}\n\n"
            f"## Notes\n\n{notes}\n"
        )

    def _card_path(self, paper: dict[str, Any]) -> Path:
        return self.papers_dir / (
            f"{paper['id']}-{slugify(str(paper['title']))}.md"
        )

    def _find_card_path(self, paper_id: str) -> Path | None:
        matches = sorted(self.papers_dir.glob(f"{paper_id}-*.md"))
        return matches[0] if matches else None

    def _ensure_json_file(self, path: Path, default: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(
                json.dumps(default, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return default
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
