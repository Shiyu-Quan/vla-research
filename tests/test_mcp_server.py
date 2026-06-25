import json
import tempfile
import unittest
from pathlib import Path

from vla_research.memory import ResearchMemory
from vla_research.server import TOOLS, handle_message


class McpServerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory = ResearchMemory(self.root)
        self.memory.add_or_update_paper(
            {
                "id": "T01",
                "title": "Fictional FPGA Action Accelerator",
                "domain": "manipulation",
                "main_technique": "fictional FPGA action engine",
                "hardware_relevance": "Test-only record",
                "metrics": {"control_hz": "not_reported"},
                "tags": ["fpga", "action-generation"],
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_returns_tools_capability(self):
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            },
            self.memory,
        )

        self.assertEqual(response["id"], 1)
        self.assertIn("tools", response["result"]["capabilities"])
        self.assertEqual(
            response["result"]["serverInfo"]["name"],
            "vla-research-memory",
        )

    def test_tools_list_exposes_five_tools(self):
        response = handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            self.memory,
        )

        self.assertEqual(
            {tool["name"] for tool in response["result"]["tools"]},
            {
                "search_papers",
                "get_paper",
                "add_or_update_paper",
                "list_gaps",
                "recommend_next_reading",
            },
        )
        self.assertEqual(len(TOOLS), 5)

    def test_search_tool_returns_structured_content(self):
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_papers",
                    "arguments": {"query": "FPGA", "limit": 5},
                },
            },
            self.memory,
        )

        self.assertFalse(response["result"]["isError"])
        result = response["result"]["structuredContent"]["results"][0]
        self.assertEqual(result["id"], "T01")
        self.assertEqual(
            json.loads(response["result"]["content"][0]["text"])["results"][0][
                "id"
            ],
            "T01",
        )

    def test_add_or_update_tool_writes_record(self):
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "add_or_update_paper",
                    "arguments": {
                        "paper": {
                            "id": "T02",
                            "title": "Fictional Runtime Study",
                        }
                    },
                },
            },
            self.memory,
        )

        self.assertEqual(
            response["result"]["structuredContent"]["paper"]["id"],
            "T02",
        )
        self.assertEqual(self.memory.get_paper("T02")["title"], "Fictional Runtime Study")

    def test_unknown_tool_is_protocol_error(self):
        response = handle_message(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "missing_tool", "arguments": {}},
            },
            self.memory,
        )

        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Unknown tool", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
