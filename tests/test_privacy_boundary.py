import unittest
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".ps1",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".txt",
    ".gitignore",
}
PRIVATE_PATH_PATTERN = re.compile(
    r"[A-Za-z]:\\+(?:Users|papers)\\+",
    re.IGNORECASE,
)
PRIVATE_AUTHOR_TOKEN = "zha" + "ng"


def source_files():
    excluded_parts = {".git", "__pycache__", ".venv", "dist", "build"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if excluded_parts.intersection(relative.parts):
            continue
        yield path


class PrivacyBoundaryTests(unittest.TestCase):
    def test_repository_has_no_private_signatures_or_pdf_files(self):
        scanned = 0
        for path in source_files():
            scanned += 1
            if path.suffix.lower() == ".pdf":
                self.fail(f"PDF must not be published: {path}")
            if path.suffix.lower() in TEXT_SUFFIXES or path.name == ".gitignore":
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(
                    PRIVATE_PATH_PATTERN.search(text),
                    str(path),
                )
                self.assertNotIn(PRIVATE_AUTHOR_TOKEN, text.lower(), str(path))
        self.assertGreater(scanned, 10)

    def test_readme_documents_release_workflows(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in (
            "Installation",
            "MCP Configuration",
            "Upgrade",
            "Uninstall",
            "Academic Research Suite",
            "Privacy",
            "Testing",
        ):
            self.assertIn(heading, text)
        self.assertIn(".[validation]", text)

    def test_apache_license_and_notice_are_present(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        notice_text = (ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        self.assertIn("academic-research-suite", notice_text)
        self.assertIn("not bundled", notice_text)

    def test_gitignore_blocks_private_runtime_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in (
            "__pycache__/",
            "*.pdf",
            "research-memory/",
            ".venv/",
            "*.egg-info/",
        ):
            self.assertIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
