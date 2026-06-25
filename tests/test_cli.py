import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vla_research.memory import ResearchMemory


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        memory = ResearchMemory(self.root)
        memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional VLA Runtime",
                "domain": "edge deployment",
                "main_technique": "fictional runtime",
                "hardware_relevance": "Test-only record",
                "metrics": {},
                "tags": ["runtime"],
            }
        )
        memory.gaps_path.write_text(
            json.dumps(
                [
                    {
                        "id": "G01",
                        "priority": "high",
                        "status": "open",
                        "tags": ["runtime"],
                    }
                ]
            ),
            encoding="utf-8",
        )
        memory.reading_queue_path.write_text(
            json.dumps(
                [
                    {
                        "paper_id": "T01",
                        "priority": 100,
                        "reason": "Test queue",
                    }
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, *args: str) -> dict:
        env = dict(os.environ)
        env["VLA_RESEARCH_MEMORY"] = str(self.root)
        env["PYTHONPATH"] = str(SRC_ROOT)
        env["PYTHONUTF8"] = "1"
        completed = subprocess.run(
            [sys.executable, "-m", "vla_research.cli", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    def test_search_uses_environment_memory(self):
        payload = self.run_cli("search", "fictional")
        self.assertEqual(payload["results"][0]["id"], "T01")

    def test_get_returns_complete_record(self):
        payload = self.run_cli("get", "T01")
        self.assertEqual(payload["paper"]["title"], "Fictional VLA Runtime")

    def test_gaps_filters_records(self):
        payload = self.run_cli("gaps", "--priority", "high")
        self.assertEqual(payload["gaps"][0]["id"], "G01")

    def test_recommend_returns_queue(self):
        payload = self.run_cli("recommend", "--focus", "runtime")
        self.assertEqual(payload["recommendations"][0]["id"], "T01")


if __name__ == "__main__":
    unittest.main()
