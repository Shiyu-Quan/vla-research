from __future__ import annotations

import argparse
import json
from typing import Any

from .memory import ResearchMemory
from .server import default_memory_root


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query a local VLA research memory.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    search = commands.add_parser("search", help="Search papers.")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--tag", action="append", default=[])
    search.add_argument("--domain", default="")
    search.add_argument("--verification-status", default="")
    search.add_argument("--limit", type=int, default=10)

    get = commands.add_parser("get", help="Get one paper by ID.")
    get.add_argument("id")

    gaps = commands.add_parser("gaps", help="List research gaps.")
    gaps.add_argument("--status", default="")
    gaps.add_argument("--priority", default="")
    gaps.add_argument("--tag", default="")

    recommend = commands.add_parser(
        "recommend",
        help="Recommend next readings.",
    )
    recommend.add_argument("--focus", default="")
    recommend.add_argument("--limit", type=int, default=5)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    memory = ResearchMemory(default_memory_root())
    memory.ensure()

    if args.command == "search":
        _print_json(
            {
                "results": memory.search_papers(
                    query=args.query,
                    tags=args.tag,
                    domain=args.domain,
                    verification_status=args.verification_status,
                    limit=args.limit,
                )
            }
        )
    elif args.command == "get":
        _print_json({"paper": memory.get_paper(args.id)})
    elif args.command == "gaps":
        _print_json(
            {
                "gaps": memory.list_gaps(
                    status=args.status,
                    priority=args.priority,
                    tag=args.tag,
                )
            }
        )
    elif args.command == "recommend":
        _print_json(
            {
                "recommendations": memory.recommend_next_reading(
                    focus=args.focus,
                    limit=args.limit,
                )
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
