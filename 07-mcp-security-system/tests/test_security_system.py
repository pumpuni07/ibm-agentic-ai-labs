"""Tests for the MCP Security System.

Two layers, both against real code:

UNIT (no server): permission policy resolution — defaults, file
persistence round-trip, argument-specific overrides beating general
policies, secure 'ask' default for unknown tools — plus audit-log
formatting.

INTEGRATION (real server subprocess over STDIO, zero mocks): the base
client's call_tool_with_permission genuinely enforces policy against
mcp_permission_server.py — 'allow' executes and returns real tool
output; 'deny' blocks with no execution; 'ask' withholds execution and
returns the approval request; 'ask' + approved=True executes; every
decision lands in the audit log; and the audit-log resource is readable
via its URI.

Note: sessions are opened/closed inside each test (same-task
requirement for anyio cancel scopes — see project 06's README).
"""

import json
import os
import sys
from contextlib import asynccontextmanager

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_permission_client_base import MCPPermissionClient  # noqa: E402

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER = os.path.join(PROJECT_DIR, "mcp_permission_server.py")


def make_client(tmp_path) -> MCPPermissionClient:
    """Client with isolated permissions/audit files per test."""
    return MCPPermissionClient(
        SERVER, permissions_file=str(tmp_path / "permissions.json")
    )


# ---------------------------------------------------------------------------
# Unit layer: permission policy + audit logging (no server needed)
# ---------------------------------------------------------------------------

class TestPermissionPolicy:
    def test_secure_defaults(self, tmp_path):
        client = make_client(tmp_path)
        assert client.permissions == {
            "read_file": "allow",
            "write_file": "ask",
            "delete_file": "deny",
            "execute_command": "deny",
        }

    def test_unknown_tool_defaults_to_ask(self, tmp_path):
        client = make_client(tmp_path)
        assert client.check_permission("mystery_tool", {}) == "ask"

    def test_save_and_reload_round_trip(self, tmp_path):
        client = make_client(tmp_path)
        client.permissions["delete_file"] = "ask"
        client.save_permissions()
        reloaded = make_client(tmp_path)
        assert reloaded.permissions["delete_file"] == "ask"

    def test_argument_specific_override_beats_general_policy(self, tmp_path):
        client = make_client(tmp_path)
        args = {"filepath": "safe.txt"}
        arg_key = f"write_file:{json.dumps(args, sort_keys=True)}"
        client.permissions["write_file"] = "deny"
        client.permissions[arg_key] = "allow"
        assert client.check_permission("write_file", args) == "allow"
        assert client.check_permission(
            "write_file", {"filepath": "other.txt"}
        ) == "deny"


class TestAuditLog:
    def test_entries_contain_operation_decision_reason(self, tmp_path):
        client = make_client(tmp_path)
        client.log_audit("TOOL: write_file", "ASK", "Awaiting approval")
        content = client.audit_log_file.read_text()
        assert "TOOL: write_file" in content
        assert "Decision: ASK" in content
        assert "Reason: Awaiting approval" in content


# ---------------------------------------------------------------------------
# Integration layer: real permission enforcement over live STDIO
# ---------------------------------------------------------------------------

pytestmark_async = pytest.mark.asyncio


@asynccontextmanager
async def live_client(tmp_path):
    os.chdir(PROJECT_DIR)  # server's data/ dir resolves relative to it
    client = make_client(tmp_path)
    try:
        yield client
    finally:
        await client.cleanup()


@pytest.mark.asyncio
class TestLivePermissionEnforcement:
    async def test_allow_executes_real_tool(self, tmp_path):
        async with live_client(tmp_path) as client:
            # Seed a real file through the server itself (write is 'ask',
            # so pass approved=True)
            await client.call_tool_with_permission(
                "write_file",
                {"filepath": "seed.txt", "content": "hello audit"},
                approved=True,
            )
            result = await client.call_tool_with_permission(
                "read_file", {"filepath": "seed.txt"}
            )
            assert result[0].text == "hello audit"

    async def test_deny_blocks_without_execution(self, tmp_path):
        async with live_client(tmp_path) as client:
            result = await client.call_tool_with_permission(
                "delete_file", {"filepath": "seed.txt"}
            )
            assert "Permission denied" in result[0].text
            # File must still exist — read it back through the server
            check = await client.call_tool_with_permission(
                "read_file", {"filepath": "seed.txt"}
            )
            assert check[0].text == "hello audit"

    async def test_ask_withholds_and_returns_approval_request(self, tmp_path):
        async with live_client(tmp_path) as client:
            result = await client.call_tool_with_permission(
                "write_file",
                {"filepath": "pending.txt", "content": "should wait"},
            )
            assert "Permission required for tool: write_file" in result[0].text
            # Not executed: server reports file not found
            check = await client.call_tool_with_permission(
                "read_file", {"filepath": "pending.txt"}
            )
            assert "not found" in check[0].text

    async def test_ask_with_approval_executes(self, tmp_path):
        async with live_client(tmp_path) as client:
            result = await client.call_tool_with_permission(
                "write_file",
                {"filepath": "approved.txt", "content": "user said yes"},
                approved=True,
            )
            assert "Successfully wrote to approved.txt" in result[0].text

    async def test_every_decision_is_audited(self, tmp_path):
        async with live_client(tmp_path) as client:
            await client.call_tool_with_permission(
                "read_file", {"filepath": "seed.txt"}
            )
            await client.call_tool_with_permission(
                "delete_file", {"filepath": "seed.txt"}
            )
            await client.call_tool_with_permission(
                "write_file", {"filepath": "x.txt", "content": "y"}
            )
            log = client.audit_log_file.read_text()
            assert "TOOL: read_file - Decision: ALLOWED" in log
            assert "TOOL: delete_file - Decision: DENIED" in log
            assert "TOOL: write_file - Decision: ASK" in log

    async def test_audit_log_resource_readable_via_uri(self, tmp_path):
        async with live_client(tmp_path) as client:
            contents = await client.read_resource("file://audit/log")
            assert len(contents) >= 1  # server-side audit resource responds


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
