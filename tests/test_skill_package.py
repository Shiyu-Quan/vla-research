import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skill" / "vla-research"


class SkillPackageTests(unittest.TestCase):
    def test_skill_contains_no_private_absolute_paths(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        )
        self.assertNotRegex(text, r"[A-Za-z]:\\Users\\")
        self.assertNotRegex(text, r"[A-Za-z]:\\papers\\")

    def test_skill_routes_complex_research_to_optional_ars(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("academic-research-suite", text)
        self.assertIn("If Academic Research Suite Is Unavailable", text)
        self.assertIn("Use VLA Research Alone", text)

    def test_skill_uses_portable_memory_configuration(self):
        text = (
            SKILL_ROOT / "references" / "memory-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("VLA_RESEARCH_MEMORY", text)
        self.assertIn("%USERPROFILE%\\Documents\\vla-research-memory", text)

    def test_cli_wrapper_imports_package_without_sys_path_mutation(self):
        text = (
            SKILL_ROOT / "scripts" / "vla_memory_cli.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("sys.path.insert", text)
        self.assertIn("from vla_research.cli import main", text)

    def test_openai_yaml_keeps_mcp_dependency_and_implicit_invocation(self):
        text = (
            SKILL_ROOT / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('value: "vla_research"', text)
        self.assertIn("allow_implicit_invocation: true", text)
        self.assertIn("$vla-research", text)


if __name__ == "__main__":
    unittest.main()
