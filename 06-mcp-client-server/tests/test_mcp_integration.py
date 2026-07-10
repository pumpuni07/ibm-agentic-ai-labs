"""End-to-end MCP integration tests — REAL protocol, no mocks.

Each test launches mcp_server.py as an actual subprocess via STDIO
transport, performs the MCP handshake, and exercises the protocol:
tool discovery/invocation, resource-template reading with URI parameter
extraction, and prompt rendering.

Note: connect/cleanup happen inside each test via the client_session()
context manager because the MCP transport's anyio cancel scopes must be
entered and exited in the same asyncio task (pytest-asyncio fixtures
tear down in a different task, which raises ExceptionGroup errors).
"""

import os
import sys
from contextlib import asynccontextmanager

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_client import MCPClient  # noqa: E402

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER = os.path.join(PROJECT_DIR, "mcp_server.py")

pytestmark = pytest.mark.asyncio


@asynccontextmanager
async def client_session():
    """Connect to the real server; guarantee same-task cleanup."""
    os.chdir(PROJECT_DIR)  # so resources/ resolves for the server
    c = MCPClient()
    try:
        await c.connect(SERVER)
        yield c
    finally:
        await c.cleanup()


class TestToolProtocol:
    async def test_discovers_both_tools(self):
        async with client_session() as client:
            tools = await client.list_tools()
            assert {t.name for t in tools} == {"echo", "write_file"}

    async def test_echo_round_trip(self):
        async with client_session() as client:
            result = await client.call_tool("echo", {"text": "Hello MCP!"})
            assert result.content[0].text == "Echo: Hello MCP!"

    async def test_write_file_creates_real_file(self):
        async with client_session() as client:
            result = await client.call_tool(
                "write_file",
                {"path": "test_output.txt",
                 "content": "Hello from MCP client!"},
            )
            assert "Successfully wrote" in result.content[0].text
            with open("test_output.txt") as f:
                assert f.read() == "Hello from MCP client!"
            os.unlink("test_output.txt")

    async def test_history_records_tool_calls(self):
        async with client_session() as client:
            await client.call_tool("echo", {"text": "one"})
            await client.call_tool("echo", {"text": "two"})
            assert len(client.history) == 2
            assert all(h["name"] == "echo" for h in client.history)


class TestResourceProtocol:
    async def test_template_discovered(self):
        async with client_session() as client:
            templates = await client.list_resources()
            uris = [t.uriTemplate for t in templates]
            assert "file://resources/{filename}" in uris

    async def test_uri_parameter_extraction(self):
        async with client_session() as client:
            result = await client.read_resource(
                "file://resources/project_info.txt"
            )
            text = result.contents[0].text
            assert "Project Name: MCP Client Lab" in text
            assert "Version: 1.0.0" in text

    async def test_template_serves_any_file_dynamically(self):
        async with client_session() as client:
            result = await client.read_resource("file://resources/notes.txt")
            assert "MCP uses JSON-RPC 2.0" in result.contents[0].text

    async def test_missing_file_handled(self):
        async with client_session() as client:
            result = await client.read_resource("file://resources/nope.txt")
            assert "File not found" in result.contents[0].text


class TestPromptProtocol:
    async def test_prompt_discovered_with_argument(self):
        async with client_session() as client:
            prompts = await client.list_prompts()
            review = next(p for p in prompts if p.name == "review_file")
            assert [a.name for a in review.arguments] == ["filename"]

    async def test_prompt_renders_with_substitution(self):
        async with client_session() as client:
            result = await client.get_prompt(
                "review_file", {"filename": "test.txt"}
            )
            text = result.messages[0].content.text
            assert "review the file 'test.txt'" in text
            assert "Overall quality assessment" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
