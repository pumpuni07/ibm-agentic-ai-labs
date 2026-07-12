# CrewAI NourishBot — Vision Meal Analysis + Coaching

Upload a meal photo, get nutrition coaching. A sequential two-agent **CrewAI**
pipeline: a multimodal **Nutrition Analyst** (Llama 4 vision on watsonx.ai)
identifies foods and estimates macros; a **Dietary Coach** (Granite) turns the
analysis into two or three practical suggestions. Wrapped in a **Gradio** UI.

```
meal photo + goal
      │
      ▼
Nutrition Analyst (Llama 4 vision) ──context──▶ Dietary Coach (Granite)
      │                                              │
  foods + macros                            actionable suggestions
```

## Project Structure

```
03-crewai-nourishbot/
├── nourishbot.py     # Agents, tasks, crew, image encoding, Gradio UI
├── requirements.txt  # Pinned
└── tests/            # 8 tests (verified passing)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export WATSONX_APIKEY="..." WATSONX_PROJECT_ID="..."
python nourishbot.py          # launches the Gradio UI
python -m pytest tests -q     # 8 passed
```

## Tests

Real CrewAI `Agent`/`Task`/`Crew` objects throughout — agent roles and
multimodality, task context wiring (analysis feeds coaching), sequential
process assembly, base64 image-encoding correctness (incl. jpg→jpeg
normalization), env-var-only credentials, and an end-to-end `analyze_meal`
flow where only the live `kickoff` LLM call is mocked (repo policy).

## Attribution

Based on the IBM Skills Network guided lab building a CrewAI nutrition
assistant, completed as part of my IBM RAG and Agentic AI Professional
Certificate. Restructured, tested, and documented by me.
