# LangGraph Intent-Based Workflow Router

A **StateGraph** that reads a user request, classifies its intent with an LLM, and routes it through **conditional edges** to one of four specialized handler nodes — the Intent-Based Routing pattern that underlies production multi-agent systems.

```
user_input ──► router node (LLM classifies)
                    │ conditional edges
   ┌────────────┬───┴────────┬──────────────────┐
ride_hailing  restaurant  groceries      default_handler
 dispatch      order       delivery      (reroute / support)
 summary       summary     order summary
```

## Project Structure

```
02-langgraph-workflow-router/
├── router.py         # State, nodes, conditional edges, compiled graph
├── requirements.txt
└── tests/            # 7 tests (verified passing — real graph execution)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Live run with watsonx Granite:
pip install langchain-ibm
export USE_WATSONX=true WATSONX_APIKEY="..." WATSONX_PROJECT_ID="..."
python router.py   # runs the lab's four test cases

# Or programmatically with any LangChain chat model:
#   import router; router.configure_llm(my_model); app = router.build_app()
```

## What the Tests Actually Verify

The **compiled StateGraph executes for real** — entry point, router node, conditional-edge dispatch, handler execution, and state merging are genuine LangGraph machinery; only the chat model is a deterministic `FakeListChatModel` scripting outputs so every path is exactly checkable. Verified: each of the four routes reaches its correct handler with correct final state; garbage classifications fall back to `default_handler`; classification output is whitespace/case-normalized; the original input survives into final state.

## Provenance (honest scope)

Based on the IBM Skills Network lab *"Implement Workflow Patterns with LangGraph"* (Intent-Based Routing pattern), completed as part of my IBM RAG and Agentic AI Professional Certificate. The graph assembly, groceries and default-handler node bodies, and the four test cases are **faithful to the lab**; `RouterState`'s fields, the router node/decision function, the LLM injection, and the ride-hailing/restaurant handler bodies were not captured in my source material and are **reconstructed** to the lab's documented pattern (labeled in the module docstring).
