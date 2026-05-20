# FastAPI SQL Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated FastAPI + LangGraph SQL agent with safe SELECT validation, PostgreSQL execution, retry/repair, logging, Docker Compose, and tests.

**Architecture:** FastAPI handles HTTP schemas, LangGraph orchestrates agent steps, SQLAlchemy runs PostgreSQL reads, and LangChain/OpenAI supplies structured decomposition, SQL generation, repair, and summarization with deterministic fallbacks for local testing.

**Tech Stack:** Python 3.12, FastAPI, uvicorn, uv, SQLAlchemy, psycopg, LangGraph, LangChain OpenAI, sqlglot, pytest.

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `docker-compose.yml`
- Create: `README.md`

- [x] Add project metadata, runtime dependencies, pytest config, Docker Postgres service, and usage docs.

### Task 2: Tests First

**Files:**
- Create: `tests/test_safety.py`
- Create: `tests/test_agent.py`
- Create: `tests/test_api.py`

- [x] Write failing tests for SELECT-only validation, retry repair behavior, failed fallback behavior, and endpoint response contract.
- [x] Run targeted tests and confirm they fail because implementation modules do not exist yet.

### Task 3: Core Implementation

**Files:**
- Create: `app/__init__.py`
- Create: `app/settings.py`
- Create: `app/schemas.py`
- Create: `app/safety.py`
- Create: `app/database.py`
- Create: `app/llm.py`
- Create: `app/agent.py`
- Create: `app/main.py`

- [x] Implement typed settings, request/response schemas, SQL validation, schema introspection, SQL execution, LLM adapters, LangGraph workflow, and FastAPI routing.

### Task 4: Verification

**Files:**
- Verify all project files.

- [x] Run `uv run pytest`.
- [x] Run import/startup checks for the FastAPI app.
- [x] Report any Docker/OpenAI checks not run locally.
