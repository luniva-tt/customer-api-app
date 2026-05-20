# FastAPI SQL Agent Design

## Goal

Build an isolated FastAPI project exposing `POST /agent/sql`, where an agent decomposes a natural language question, generates a safe PostgreSQL `SELECT` query, executes it, repairs failed SQL up to three attempts, and returns the result with a natural-language summary.

## Architecture

The app is a small LangGraph workflow around SQLAlchemy database access. FastAPI owns HTTP request and response validation. LangGraph owns the agent state machine: understand query, generate SQL, validate SQL, execute SQL, repair on error, summarize, or return fallback after retries.

OpenAI is used through LangChain structured output models so decomposition, SQL generation, repair, and summarization return typed Pydantic objects. A deterministic fallback handles the sample question and keeps tests reliable without making live LLM calls.

## Components

- `app/main.py`: FastAPI app and route.
- `app/settings.py`: environment-driven configuration.
- `app/database.py`: SQLAlchemy engine, schema introspection, and read-only query execution.
- `app/safety.py`: parser-based SQL validation that allows only one safe `SELECT` statement.
- `app/llm.py`: OpenAI/LangChain adapters with deterministic fallback behavior.
- `app/agent.py`: LangGraph workflow and retry routing.
- `tests/`: TDD coverage for validation, retry behavior, and the HTTP endpoint.

## Data Flow

The endpoint receives `{ "question": "..." }`, loads schema metadata, and starts the graph. The graph logs decomposition, SQL generation, and execution time. Query execution returns rows as dictionaries and scalar aggregates as a plain value. Final responses include `sql`, `result`, `summary`, and `status`.

## Error Handling

Only validation-safe SQL reaches PostgreSQL. If PostgreSQL raises an execution error, the graph records the error, asks the SQL repair node for a corrected query, and retries until attempt 3. If all attempts fail, the response status is `failed` with a fallback summary and diagnostic error.

## Testing

Tests cover SELECT-only validation, retry and repair after a bad query, fallback after repeated failures, and the FastAPI endpoint contract using dependency injection/mocking so unit tests do not require Docker or OpenAI.
