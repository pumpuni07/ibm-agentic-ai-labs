# Natural Language SQL Agent — LangChain + IBM Granite + MySQL

Ask a MySQL database questions in plain English. A LangChain **SQL agent** (`ZERO_SHOT_REACT_DESCRIPTION`) inspects the schema, plans, writes and executes the SQL, recovers from parsing errors, and answers in natural language — powered by IBM **Granite** on watsonx.ai over the classic **Chinook** music-store database.

```
"Which country's customers spent the most by invoice?"
        │
        ▼
LangChain SQL Agent (ReAct loop)
  → list tables → inspect schema → write SQL → execute → observe → answer
        │                                  │
   Granite (watsonx.ai)              MySQL (Chinook)
```

## Project Structure

```
01-nl-sql-agent/
├── db_config.py     # Env-var credential handling (stdlib, tested)
├── sql_agent.py     # Agent assembly + CLI (--prompt "...")
├── requirements.txt # Pinned per the guided project
└── tests/           # 6 tests (verified passing)
```

## Setup & Usage

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export MYSQL_PASSWORD="your-password"
# optional overrides: MYSQL_USERNAME, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE (default: Chinook)

python sql_agent.py --prompt "How many Albums are there in the database?"
python sql_agent.py --prompt "Which country's customers spent the most by invoice?"
```

Requires a reachable MySQL server with the [Chinook sample database](https://github.com/lerocha/chinook-database) loaded, plus watsonx access (no-key auth works only inside IBM Skills Network — use your own credentials/project_id elsewhere).

## What the Tests Verify

URI construction, environment-variable defaults and the required-password error path, env→URI round-trip, and a **credential guard**: the original lab hardcoded its lab-database password and internal host IP in the script; this project moved them to environment variables, and a test permanently asserts those strings never re-enter the source.

## Attribution

Based on the IBM Skills Network guided project *"Build a Natural Language SQL Agent"* (author: Ricky Shi; contributors: Karan Goswami, Kunal Makwana, Wojciech "Victor" Fulmyk), completed as part of my IBM RAG and Agentic AI Professional Certificate. Restructured (env-var credentials, `__main__` guard, tests) for portfolio use.
