"""Experimental MCP server exposing the output compressor as a tool.

Model Context Protocol (MCP) stdio transport is newline-delimited JSON-RPC 2.0:
one JSON object per line on stdin, one response object per line on stdout. This
module implements the minimum to be useful — ``initialize``, ``tools/list``,
and ``tools/call`` for a single ``shrink`` tool — so an MCP-capable agent can
compress tool output at runtime.

It is marked **experimental**: the request handling is pure and unit-tested
(:func:`handle_request`), but the live stdio loop has not been validated against
every MCP client. Run it with ``monolith mcp``.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from monolith import __version__
from monolith.shrink import DEFAULT_LEVEL, LEVELS, shrink

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "monolith-shrink"

# JSON-RPC error code for an unknown method.
_METHOD_NOT_FOUND = -32601

_SHRINK_TOOL = {
    "name": "shrink",
    "description": "Compress verbose text/output deterministically to save tokens.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The text to compress."},
            "level": {
                "type": "string",
                "enum": list(LEVELS),
                "description": f"Compression level (default: {DEFAULT_LEVEL}).",
            },
        },
        "required": ["text"],
    },
}


def _result(request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_request(request: Dict[str, Any]) -> Dict[str, Any] | None:
    """Handle one JSON-RPC request and return the response.

    Returns ``None`` for notifications (requests without an ``id``), which by
    spec receive no response.
    """
    request_id = request.get("id")
    method = request.get("method")

    # Notifications carry no id and expect no reply.
    if request_id is None and method is not None:
        return None

    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": __version__},
            },
        )

    if method == "tools/list":
        return _result(request_id, {"tools": [_SHRINK_TOOL]})

    if method == "tools/call":
        params = request.get("params", {})
        if params.get("name") != "shrink":
            return _error(request_id, _METHOD_NOT_FOUND, f"unknown tool: {params.get('name')}")
        args = params.get("arguments", {})
        text = args.get("text", "")
        level = args.get("level", DEFAULT_LEVEL)
        if level not in LEVELS:
            level = DEFAULT_LEVEL
        result = shrink(text, level)
        return _result(
            request_id,
            {
                "content": [{"type": "text", "text": result.text}],
                # Non-standard but harmless extra for observability.
                "_meta": {
                    "before_tokens": result.before_tokens,
                    "after_tokens": result.after_tokens,
                    "reduction": round(result.reduction, 4),
                },
            },
        )

    return _error(request_id, _METHOD_NOT_FOUND, f"unknown method: {method}")


def serve(stdin=None, stdout=None) -> int:
    """Run the newline-delimited JSON-RPC loop until stdin closes."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            # Malformed line: emit a parse error with null id per JSON-RPC.
            stdout.write(json.dumps(_error(None, -32700, "parse error")) + "\n")
            stdout.flush()
            continue
        response = handle_request(request)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()
    return 0
