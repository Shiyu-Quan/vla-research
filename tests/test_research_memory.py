import json
import tempfile
import unittest
from pathlib import Path

from vla_research.memory import ResearchMemory, slugify


class ResearchMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory = ResearchMemory(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_slugify_keeps_readable_ascii_prefix(self):
        self.assertEqual(
            slugify("A 102.5-Hz Real-Time FPGA Action Accelerator"),
            "a-102-5-hz-real-time-fpga-action-accelerator",
        )

    def test_ensure_creates_empty_memory(self):
        self.memory.ensure()

        self.assertEqual(self.memory.load_index(), [])
        self.assertEqual(
            json.loads(self.memory.gaps_path.read_text(encoding="utf-8")),
            [],
        )
        self.assertEqual(
            json.loads(self.memory.reading_queue_path.read_text(encoding="utf-8")),
            [],
        )

    def test_add_update_search_and_card_rendering(self):
        created = self.memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional VLA Accelerator",
                "domain": "manipulation",
                "main_technique": "fictional action engine",
                "hardware_relevance": "Test-only record",
                "metrics": {"control_hz": "not_reported"},
                "tags": ["action-generation"],
                "key_claims": ["A fictional claim used only by tests."],
            }
        )

        self.assertEqual(created["verification_status"], "unverified")
        self.assertEqual(
            self.memory.search_papers("action engine")[0]["id"],
            "T01",
        )
        card_path = Path(created["card_path"])
        self.assertTrue(card_path.exists())
        self.assertIn(
            "A fictional claim used only by tests.",
            card_path.read_text(encoding="utf-8"),
        )

    def test_update_preserves_existing_fields(self):
        self.memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional VLA Accelerator",
                "domain": "manipulation",
                "notes": "keep this",
            }
        )

        updated = self.memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional VLA Accelerator Revised",
                "metrics": {"latency": "not_reported"},
            }
        )

        self.assertEqual(updated["notes"], "keep this")
        self.assertEqual(updated["title"], "Fictional VLA Accelerator Revised")

    def test_list_gaps_filters_by_priority_and_tag(self):
        self.memory.ensure()
        self.memory.gaps_path.write_text(
            json.dumps(
                [
                    {
                        "id": "G01",
                        "priority": "high",
                        "status": "open",
                        "tags": ["action-generation"],
                    },
                    {
                        "id": "G02",
                        "priority": "low",
                        "status": "open",
                        "tags": ["vision"],
                    },
                ]
            ),
            encoding="utf-8",
        )

        gaps = self.memory.list_gaps(priority="high", tag="action-generation")

        self.assertEqual([gap["id"] for gap in gaps], ["G01"])

    def test_recommend_next_reading_uses_queue_and_focus(self):
        self.memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional FPGA Action Accelerator",
                "domain": "manipulation",
                "main_technique": "FPGA action engine",
                "hardware_relevance": "Test-only hardware precedent",
                "metrics": {},
                "tags": ["fpga", "action-generation"],
            }
        )
        self.memory.reading_queue_path.write_text(
            json.dumps(
                [
                    {
                        "paper_id": "T01",
                        "priority": 100,
                        "reason": "Test queue priority",
                    }
                ]
            ),
            encoding="utf-8",
        )

        recommendations = self.memory.recommend_next_reading(
            focus="FPGA action",
            limit=1,
        )

        self.assertEqual(recommendations[0]["id"], "T01")
        self.assertEqual(recommendations[0]["reason"], "Test queue priority")

    def test_invalid_json_names_the_file_without_rewriting_it(self):
        self.memory.ensure()
        self.memory.index_path.write_text("{broken", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "index.json"):
            self.memory.load_index()

        self.assertEqual(
            self.memory.index_path.read_text(encoding="utf-8"),
            "{broken",
        )


if __name__ == "__main__":
    unittest.main()
