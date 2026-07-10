# MCP Security System — Permissions, Risk Tiers & Audit Logging

A production-pattern **four-component MCP security stack**: a server exposing tools at four risk tiers, a base client enforcing **allow / deny / ask** permission policies with a persistent audit trail, a Gradio **GUI app** for permission management, and a **GPT-4o-mini host app** that assesses risk and routes sensitive operations through human approval.

```
mcp_permission_server.py      4 risk-tiered tools (read LOW → execute CRITICAL)
        ▲  STDIO / JSON-RPC      + audit-log & permissions-config resources
        │                        + security_review prompt
mcp_permission_client_base.py  policy engine: allow/deny/ask, argument-specific
        │                      overrides, JSON persistence, audit logging
   ┌────┴─────┐
GUI app (7863)  AI host app (7864)
4-tab Gradio    GPT-4o-mini · risk assessment · yes/no approval flow
```

## Project Structure

```
07-mcp-security-system/
├── mcp_permission_server.py       # Risk-tiered tools + audit + resources + prompt
├── mcp_permission_client_base.py  # Permission engine (inherited by both apps)
├── mcp_permission_client_app.py   # GUI: Tools/Resources/Prompts/Permissions tabs
├── mcp_permission_host_app.py     # LLM host: synthetic tools, pending-approval flow
├── requirements.txt / pytest.ini
└── tests/                         # 11 tests (verified passing)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
mkdir -p data && echo "Sample content for testing" > data/test.txt

python mcp_permission_client_app.py mcp_permission_server.py   # GUI on :7863
export OPENAI_API_KEY="..."   # required for the AI host only
python mcp_permission_host_app.py mcp_permission_server.py     # host on :7864
```

## What the Tests Actually Verify — real enforcement, zero mocks

**Unit layer** (policy engine): secure defaults, unknown tools falling back to `ask`, JSON persistence round-trip, and **argument-specific overrides beating general policies** (`write_file` denied generally but allowed for one exact argument set). **Integration layer** (real server subprocess over STDIO): `allow` executes and returns genuine tool output; `deny` blocks **and the target file provably still exists**; `ask` withholds execution **and the file provably was not created**; `ask + approved=True` executes; all three decisions land in the audit log; the audit-log resource answers at its URI. The GUI/AI-host apps are exercised through the running applications (they require Gradio/OpenAI at runtime).

## Attribution

Based on the IBM Skills Network lab *"MCP Security with Permissions and Elicitation"* (author: Wojciech "Victor" Fulmyk), completed as part of my IBM RAG and Agentic AI Professional Certificate. The lab's elicitation implementation is conceptual (auto-approving demo), as documented in the base client. Test suite added for portfolio use.
