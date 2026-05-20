# FastAPI SQL Agent

Small agentic FastAPI system that understands a question, generates PostgreSQL SQL, executes safe `SELECT` queries, repairs failed SQL, retries up to three attempts, and returns a natural-language summary.

## Setup

```bash
uv sync
docker compose up -d
uv run uvicorn app.main:app --reload
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/agent/sql \
  -H "Content-Type: application/json" \
  -d '{"question":"How many shipped orders are from USA customers?"}'
```

## Environment

Create `.env` from `.env.example`. `OPENAI_API_KEY` enables LLM-backed decomposition, SQL generation, repair, and summary. The app also includes a deterministic fallback for the sample question.

## Test

```bash
uv run pytest
```
