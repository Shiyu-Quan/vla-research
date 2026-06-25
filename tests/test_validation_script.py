import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ValidationScriptTests(unittest.TestCase):
    def test_validation_script_runs_tests_skill_check_and_cli(self):
        if os.environ.get("VLA_VALIDATION_CHILD") == "1":
            self.skipTest("Avoid recursive validation invocation")

        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            self.skipTest("PowerShell is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dependency_dir = temp_path / "validator_dependency"
            dependency_dir.mkdir()
            (dependency_dir / "validation_dependency.py").write_text(
                "VALUE = 'available'\n",
                encoding="utf-8",
            )
            fake_validator = temp_path / "quick_validate.py"
            fake_validator.write_text(
                "import pathlib, sys\n"
                "from validation_dependency import VALUE\n"
                "target = pathlib.Path(sys.argv[1])\n"
                "valid = VALUE == 'available' and (target / 'SKILL.md').exists()\n"
                "raise SystemExit(0 if valid else 1)\n",
                encoding="utf-8",
            )
            env = dict(
                os.environ,
                VLA_VALIDATION_CHILD="1",
                PYTHONPATH=str(dependency_dir),
            )
            completed = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "validate.ps1"),
                    "-PythonCommand",
                    sys.executable,
                    "-QuickValidatePath",
                    str(fake_validator),
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("VALIDATION PASSED", completed.stdout)


if __name__ == "__main__":
    unittest.main()
