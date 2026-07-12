# AG2 Healthcare Chatbot — Multi-Agent GroupChat Triage

Three **AG2 (AutoGen)** specialist agents collaborate in a **round-robin
GroupChat** on a patient inquiry: a **Triage Nurse** clarifies symptoms, a
**General Practitioner** gives non-diagnostic guidance, and a **Wellness
Advisor** adds lifestyle advice. A `UserProxyAgent` represents the patient.
Educational demo only — every agent carries a not-medical-advice disclaimer.

## Project Structure

```
04-ag2-healthcare-chatbot/
├── healthcare_chat.py  # Agents, GroupChat, manager, consultation runner
├── requirements.txt    # Pinned
└── tests/              # 4 tests (verified passing)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="..."   # or OPENAI_BASE_URL for a compatible endpoint
python healthcare_chat.py
python -m pytest tests -q     # 4 passed
```

## Tests

Real AG2 machinery — agent roles and disclaimers, GroupChat configuration
(4 agents, round-robin, max rounds), **genuine `next_agent` speaker-order
cycling** through all three specialists, and env-var-only credential handling
with a source-level guard against hard-coded keys.

## Attribution

Based on the IBM Skills Network guided lab building a healthcare GroupChat
with AG2, completed as part of my IBM RAG and Agentic AI Professional
Certificate. Restructured, tested, and documented by me.
