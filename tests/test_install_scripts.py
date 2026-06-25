import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "research-memory-template"
SCRIPTS = ROOT / "scripts"


def powershell_command() -> str:
    command = shutil.which("pwsh") or shutil.which("powershell")
    if not command:
        raise unittest.SkipTest("PowerShell is not available")
    return command


def run_script(
    script_name: str,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            powershell_command(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPTS / script_name),
            *args,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


class InstallScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory = self.root / "memory"
        self.codex_home = self.root / "codex"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_memory_preserves_existing_files(self):
        existing = self.memory / "state" / "research-state.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("keep me", encoding="utf-8")

        completed = run_script(
            "initialize-memory.ps1",
            "-MemoryPath",
            str(self.memory),
            "-TemplatePath",
            str(TEMPLATE),
        )

        self.assertEqual(existing.read_text(encoding="utf-8"), "keep me")
        self.assertTrue((self.memory / "papers" / "index.json").exists())
        self.assertIn("SKIPPED", completed.stdout)
        self.assertIn("CREATED", completed.stdout)

    def test_repeated_initialization_does_not_overwrite_json(self):
        run_script(
            "initialize-memory.ps1",
            "-MemoryPath",
            str(self.memory),
            "-TemplatePath",
            str(TEMPLATE),
        )
        index = self.memory / "papers" / "index.json"
        index.write_text('[{"id":"T01"}]', encoding="utf-8")

        run_script(
            "initialize-memory.ps1",
            "-MemoryPath",
            str(self.memory),
            "-TemplatePath",
            str(TEMPLATE),
        )

        self.assertEqual(index.read_text(encoding="utf-8"), '[{"id":"T01"}]')

    def test_install_resolves_custom_paths_without_global_changes(self):
        completed = run_script(
            "install.ps1",
            "-MemoryPath",
            str(self.memory),
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonInstall",
            "-SkipSmokeTest",
        )

        installed_skill = (
            self.codex_home / "skills" / "vla-research" / "SKILL.md"
        )
        self.assertTrue(installed_skill.exists())
        self.assertTrue((self.memory / "papers" / "index.json").exists())
        self.assertIn(str(self.memory.resolve()), completed.stdout)
        self.assertIn("[mcp_servers.vla_research]", completed.stdout)
        self.assertIn("VLA_RESEARCH_MEMORY", completed.stdout)

    def test_install_preserves_existing_skill_without_force(self):
        installed_skill = self.codex_home / "skills" / "vla-research"
        installed_skill.mkdir(parents=True)
        marker = installed_skill / "marker.txt"
        marker.write_text("keep", encoding="utf-8")

        completed = run_script(
            "install.ps1",
            "-MemoryPath",
            str(self.memory),
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonInstall",
            "-SkipSmokeTest",
        )

        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
        self.assertIn("Skill already exists", completed.stdout)

    def test_force_skill_update_replaces_existing_skill(self):
        installed_skill = self.codex_home / "skills" / "vla-research"
        installed_skill.mkdir(parents=True)
        (installed_skill / "marker.txt").write_text("remove", encoding="utf-8")

        run_script(
            "install.ps1",
            "-MemoryPath",
            str(self.memory),
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonInstall",
            "-SkipSmokeTest",
            "-ForceSkillUpdate",
        )

        self.assertFalse((installed_skill / "marker.txt").exists())
        self.assertTrue((installed_skill / "SKILL.md").exists())

    def test_uninstall_removes_skill_but_preserves_memory(self):
        run_script(
            "install.ps1",
            "-MemoryPath",
            str(self.memory),
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonInstall",
            "-SkipSmokeTest",
        )

        run_script(
            "uninstall.ps1",
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonUninstall",
        )

        self.assertFalse(
            (self.codex_home / "skills" / "vla-research").exists()
        )
        self.assertTrue(self.memory.exists())

    def test_uninstall_requires_explicit_memory_path_for_removal(self):
        completed = run_script(
            "uninstall.ps1",
            "-CodexHome",
            str(self.codex_home),
            "-SkipPythonUninstall",
            "-RemoveMemory",
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("MemoryPath", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
