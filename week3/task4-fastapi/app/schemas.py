from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentSQLRequest(BaseModel):
    question: str = Field(min_length=1)


class AgentSQLResponse(BaseModel):
    sql: str | None
    result: Any
    summary: str
    status: Literal["success", "failed"]
    error: str | None = None


class Decomposition(BaseModel):
    intent: str
    tables: list[str]
    columns: list[str]
    filters: list[str] = Field(default_factory=list)


class SQLDraft(BaseModel):
    sql: str


class SummaryDraft(BaseModel):
    summary: str
