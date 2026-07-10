# MCP Client + Server — Model Context Protocol from Scratch

A complete **Model Context Protocol** implementation pair: a FastMCP server exposing all three MCP primitives, and a Python client that launches it over **STDIO transport**, performs the JSON-RPC handshake, and drives it through an interactive CLI.

```
mcp_client.py ──launch subprocess──► mcp_server.py (FastMCP)
      │        JSON-RPC over stdio          │
      │  ◄── initialize handshake ──►       │
      ├─ tools:     echo, write_file        │
      ├─ resource:  file://resources/{filename}   (dynamic URI template)
      └─ prompt:    review_file(filename)
```

## Project Structure

```
06-mcp-client-server/
├── mcp_server.py    # FastMCP server: @tool, @resource template, @prompt
├── mcp_client.py    # STDIO client + CLI (tools/call/read/prompt/history/help)
├── resources/       # Files exposed via the URI template
├── requirements.txt
├── pytest.ini
└── tests/           # 10 REAL protocol integration tests
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python mcp_client.py mcp_server.py
```

Then at the `>` prompt: `tools`, `call` (e.g. `echo` with `{"text": "Hello MCP!"}`), `resources`, `read` (`file://resources/notes.txt`), `prompts`, `prompt` (`review_file` with `{"filename": "test.txt"}`), `history`, `help`, `quit`.

## What the Tests Actually Verify — real protocol, zero mocks

Every test **spawns the actual server as a subprocess** and speaks genuine MCP JSON-RPC over STDIO: tool discovery returns exactly `{echo, write_file}`; `echo` round-trips content; `write_file` creates a file on disk whose contents are read back and checked; the resource template is discovered and **URI parameter extraction genuinely works** (`file://resources/project_info.txt` → correct file contents, any file served dynamically, missing files handled); prompts are discovered with their argument schema and render with substitution.

One engineering note documented for reuse: MCP's transport uses anyio cancel scopes that must open/close **in the same asyncio task** — pytest-asyncio fixtures tear down in a different task, so each test manages its session via an async context manager instead.

## Attribution

Based on the IBM Skills Network lab *"Build a Custom MCP Client with Python"* (author: Wojciech "Victor" Fulmyk), completed as part of my IBM RAG and Agentic AI Professional Certificate, including the lab's history/help extensions. Integration test suite added for portfolio use.
