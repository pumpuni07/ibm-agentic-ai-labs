# BeeAI Agent Systems — The Full Progression

Twelve scripts walking the complete **BeeAI Framework** progression, from
prompt templating to a multi-agent capstone: custom tools on the real BeeAI
`Tool` pipeline, structured output, **ReActAgent**, **RequirementAgent** with
**ConditionalRequirement** rules, **HandoffTool** multi-agent delegation, and
typed **Workflow** execution — pinned to `beeai-framework==0.1.35`.

```
01 prompt template ─ 02 BeeAI PromptTemplate ─ 03 calculator Tool
04 structured output ─ 05 ChatModel ─ 06 ReAct agent ─ 07 built-in tools
08 RequirementAgent ─ 09 conditional requirements ─ 10 handoff multi-agent
11 Workflow ─ 12 full-system capstone
```

## Project Structure

```
05-beeai-agent-systems/
├── core.py               # SimplePromptTemplate, SimpleCalculatorTool, BusinessPlan
├── 01…12_*.py            # The twelve progression scripts
├── requirements.txt      # beeai-framework==0.1.35
└── tests/                # 27 tests (verified passing)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -q     # 27 passed
python 11_workflow.py         # runs offline; agent scripts need a model backend
```

## Tests

Everything verifiable offline is verified against **real framework machinery,
zero mocks**: `SimplePromptTemplate.render` genuinely substitutes single /
multiple / repeated variables; `SimpleCalculatorTool._safe_calculate`
genuinely enforces its safety contract (character allow-list rejects code
injection, zero-division → `ValueError`) — including an honestly documented
quirk: `2**8` passes the lab's character filter because `**` is two allowed
`*` chars; the tool's **full async pipeline executes through real BeeAI
`Tool.run()`** (schema validation, `StringToolOutput`, graceful error
output); the `BusinessPlan` schema accepts valid plans and rejects
missing/mistyped fields; tool metadata the LLM sees (name / description /
JSON schema) is exact; a real two-step `Workflow` executes with typed state;
and **all twelve scripts import cleanly against the pinned
`beeai-framework==0.1.35`** — a genuine API-compatibility check.

## Attribution

Based on the IBM Skills Network lab *"Building Agentic AI Systems with the
BeeAI Framework"* (author: Wojciech "Victor" Fulmyk), completed as part of my
IBM RAG and Agentic AI Professional Certificate. Rebuilt to the lab's
specification, tested, and documented by me.
