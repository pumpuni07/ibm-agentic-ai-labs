# IBM Agentic AI Labs

Hands-on **AI agent and Model Context Protocol (MCP)** projects completed as part of my **IBM RAG and Agentic AI Professional Certificate**. Each project is self-contained with pinned requirements and a verified test suite — including **real end-to-end MCP protocol integration tests** (actual server subprocesses, genuine JSON-RPC, zero mocks).

Third repository in a portfolio trilogy: [`ibm-watsonx-genai-portfolio`](https://github.com/pumpuni07/ibm-watsonx-genai-portfolio) (GenAI applications) → [`ibm-rag-retrieval-labs`](https://github.com/pumpuni07/ibm-rag-retrieval-labs) (retrieval & multimodal RAG) → **this repo** (agents, orchestration & MCP).

## Projects

| # | Project | Stack | Status |
|---|---------|-------|--------|
| 01 | [Natural Language SQL Agent](./01-nl-sql-agent/) | LangChain SQL agent · IBM Granite · MySQL/Chinook | ✅ Complete — 6 tests passing |
| 02 | [LangGraph Workflow Router](./02-langgraph-workflow-router/) | LangGraph · conditional edges · intent routing | ✅ Complete — 7 tests passing |
| 03 | CrewAI NourishBot | CrewAI · Llama 4 vision · Gradio | 🚧 Planned (round 3) |
| 04 | AG2 Healthcare Chatbot | AG2 (AutoGen) · GroupChat | 🚧 Planned (round 3) |
| 05 | BeeAI Agent Systems | BeeAI · RequirementAgent · multi-agent | 🚧 Planned (round 3) |
| 06 | [MCP Client + Server](./06-mcp-client-server/) | MCP SDK · FastMCP · STDIO transport | ✅ Complete — 10 real protocol tests |
| 07 | [MCP Security System](./07-mcp-security-system/) | MCP · permissions · audit logging · GPT | ✅ Complete — 11 tests passing |

## Themes

- **Agentic patterns**: ReAct loops, tool calling, multi-agent orchestration, human-in-the-loop approval
- **Model Context Protocol**: STDIO transport, JSON-RPC handshake, tools/resources/prompts, URI templates, permission policies
- **Frameworks across the ecosystem**: LangChain, LangGraph, CrewAI, AG2, BeeAI, MCP SDK/FastMCP
- **Security engineering**: credentials via environment variables (with a test guarding against regression), permission tiers, audit trails
- **Verification discipline**: integration tests against real protocol subprocesses wherever possible; mocks only where live model calls are unavoidable

## Author

**Jack Pumpuni Frimpong-Manso** — GitHub: [pumpuni07](https://github.com/pumpuni07) · Portfolio: [jackpumpunifrimpongmanso.base44.app](https://jackpumpunifrimpongmanso.base44.app)

## Attribution & License

Based on IBM Skills Network guided labs (authors credited per project), completed, restructured, tested, and documented by me. My additions are under the [MIT License](./LICENSE); original lab materials remain property of IBM Skills Network and their authors.
