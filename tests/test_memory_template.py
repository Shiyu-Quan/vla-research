import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "research-memory-template"


class MemoryTemplateTests(unittest.TestCase):
    def test_runtime_json_templates_are_empty_arrays(self):
        for relative in (
            "papers/index.json",
            "gaps/gap-table.json",
            "state/reading-queue.json",
        ):
            path = TEMPLATE / relative
            self.assertTrue(path.exists(), relative)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [])

    def test_template_contains_no_pdfs(self):
        self.assertEqual(list(TEMPLATE.rglob("*.pdf")), [])

    def test_template_contains_required_guidance(self):
        expected = (
            "state/research-state.md",
            "matrices/metrics-schema.md",
            "taxonomy/hardware-mapping.md",
            "taxonomy/vla-acceleration-taxonomy.md",
            "pdfs/README.md",
        )
        for relative in expected:
            path = TEMPLATE / relative
            self.assertTrue(path.exists(), relative)
            self.assertTrue(path.read_text(encoding="utf-8").strip(), relative)

    def test_template_has_no_runtime_records(self):
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in TEMPLATE.rglob("*.md")
        )
        self.assertNotIn('"id":', markdown)
        self.assertNotIn("verification_status", markdown)


if __name__ == "__main__":
    unittest.main()
