from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .memory import ResearchMemory


PROTOCOL_VERSION = "2025-06-18"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_papers",
        "title": "Search VLA Papers",
        "description": (
            "Search the VLA hardware/software co-design paper index by "
            "keyword, tag, domain, or verification status."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "domain": {"type": "string"},
                "verification_status": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
        },
    },
    {
        "name": "get_paper",
        "title": "Get VLA Paper",
        "description": (
            "Return one complete VLA paper record by ID, including its "
            "Markdown card when present."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "add_or_update_paper",
        "title": "Add Or Update VLA Paper",
        "description": (
            "Validate and write a paper record, update the index, and render "
            "a Markdown card."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"paper": {"type": "object"}},
            "required": ["paper"],
        },
    },
    {
        "name": "list_gaps",
        "title": "List VLA Research Gaps",
        "description": "Filter the VLA hardware research gap table.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "priority": {"type": "string"},
                "tag": {"type": "string"},
            },
        },
    },
    {
        "name": "recommend_next_reading",
        "title": "Recommend Next VLA Reading",
        "description": (
            "Recommend readings from the current queue and focus keywords."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "focus": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
            },
        },
    },
]


def default_memory_root() -> Path:
    if value := os.environ.get("VLA_RESEARCH_MEMORY"):
        return Path(value)
    return Path.home() / "Documents" / "vla-research-memory"


def handle_message(
    message: dict[str, Any],
    memory: ResearchMemory,
) -> dict[str, Any] | None:
    if "id" not in message:
        return None

    request_id = message["id"]
    method = message.get("method")
    try:
        if method == "initialize":
            requested = str(
                message.get("params", {}).get(
                    "protocolVersion",
                    PROTOCOL_VERSION,
                )
            )
            return _result(
                request_id,
                {
                    "protocolVersion": requested or PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": "vla-research-memory",
                        "title": "VLA Research Memory",
                        "version": __version__,
                    },
                    "instructions": (
                        "Use these tools to maintain a local VLA "
                        "hardware/software co-design research memory."
                    ),
                },
            )
        if method == "tools/list":
            return _result(request_id, {"tools": TOOLS})
        if method == "prompts/list":
            return _result(request_id, {"prompts": []})
        if method == "resources/list":
            return _result(request_id, {"resources": []})
        if method == "tools/call":
            return _call_tool(
                request_id,
                message.get("params", {}),
                memory,
            )
        return _error(request_id, -32601, f"Method not found: {method}")
    except Exception as exc:
        return _tool_error(request_id, str(exc))


def _call_tool(
    request_id: str | int,
    params: dict[str, Any],
    memory: ResearchMemory,
) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}

    if name == "search_papers":
        payload = {
            "results": memory.search_papers(
                query=str(arguments.get("query", "")),
                tags=list(arguments.get("tags", []) or []),
                domain=str(arguments.get("domain", "")),
                verification_status=str(
                    arguments.get("verification_status", "")
                ),
                limit=int(arguments.get("limit", 10)),
            )
        }
    elif name == "get_paper":
        payload = {"paper": memory.get_paper(str(arguments["id"]))}
    elif name == "add_or_update_paper":
        payload = {
            "paper": memory.add_or_update_paper(dict(arguments["paper"]))
        }
    elif name == "list_gaps":
        payload = {
            "gaps": memory.list_gaps(
                status=str(arguments.get("status", "")),
                priority=str(arguments.get("priority", "")),
                tag=str(arguments.get("tag", "")),
            )
        }
    elif name == "recommend_next_reading":
        payload = {
            "recommendations": memory.recommend_next_reading(
                focus=str(arguments.get("focus", "")),
                limit=int(arguments.get("limit", 5)),
            )
        }
    else:
        return _error(request_id, -32602, f"Unknown tool: {name}")

    return _result(
        request_id,
        {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                    ),
                }
            ],
            "structuredContent": payload,
            "isError": False,
        },
    )


def _result(
    request_id: str | int,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(
    request_id: str | int,
    code: int,
    message: str,
) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _tool_error(
    request_id: str | int,
    message: str,
) -> dict[str, Any]:
    return _result(
        request_id,
        {
            "content": [{"type": "text", "text": message}],
            "isError": True,
        },
    )


def main() -> int:
    memory = ResearchMemory(default_memory_root())
    memory.ensure()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            response = handle_message(message, memory)
        except json.JSONDecodeError as exc:
            response = _error(0, -32700, str(exc))
        if response is not None:
            sys.stdout.write(
                json.dumps(
                    response,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
