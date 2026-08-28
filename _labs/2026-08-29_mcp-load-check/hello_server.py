#!/usr/bin/env python3
"""依存なしの最小 MCP サーバー(stdio)。ツールを1つだけ持つ。"""
import json, sys

TOOLS = [{
    "name": "hello",
    "description": "名前を受け取って挨拶を返すだけのツール",
    "inputSchema": {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
}]

def reply(rid, result):
    sys.stdout.write(json.dumps(
        {"jsonrpc": "2.0", "id": rid, "result": result}) + "\n")
    sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    msg = json.loads(line)
    method, rid = msg.get("method"), msg.get("id")
    if method == "initialize":
        reply(rid, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hello", "version": "0.1.0"},
        })
    elif method == "tools/list":
        reply(rid, {"tools": TOOLS})
    elif method == "tools/call":
        who = msg["params"].get("arguments", {}).get("name", "誰か")
        reply(rid, {"content": [{"type": "text", "text": f"こんにちは、{who}"}]})
    elif rid is not None:
        reply(rid, {})
