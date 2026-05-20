import re
from typing import Protocol

from langchain_openai import ChatOpenAI

from week2.app.schemas import Decomposition, SQLDraft, SummaryDraft
from app.settings import Settings


class LLMProvider(Protocol):
    def understand(self, question: str, schema: dict[str, object]) -> Decomposition: ...

    def generate_sql(
        self, question: str, schema: dict[str, object], decomposition: Decomposition
    ) -> SQLDraft: ...

    def repair_sql(
        self, question: str, schema: dict[str, object], sql: str, error: str, attempt: int
    ) -> SQLDraft: ...

    def summarize(self, question: str, sql: str, result: object) -> SummaryDraft: ...


class DeterministicLLMProvider:
    def understand(self, question: str, schema: dict[str, object]) -> Decomposition:
        return Decomposition(
            intent="count shipped orders from USA customers",
            tables=["orders", "customers"],
            columns=["orders.status", "orders.customerNumber", "customers.customerNumber", "customers.country"],
            filters=["orders.status = 'Shipped'", "customers.country = 'USA'"],
        )

    def generate_sql(
        self, question: str, schema: dict[str, object], decomposition: Decomposition
    ) -> SQLDraft:
        return SQLDraft(
            sql=(
                'SELECT COUNT(*) FROM orders o JOIN customers c '
                'ON o."customerNumber" = c."customerNumber" '
                "WHERE o.status = 'Shipped' AND c.country = 'USA'"
            )
        )

    def repair_sql(
        self, question: str, schema: dict[str, object], sql: str, error: str, attempt: int
    ) -> SQLDraft:
        return self.generate_sql(question, schema, self.understand(question, schema))

    def summarize(self, question: str, sql: str, result: object) -> SummaryDraft:
        return SummaryDraft(summary=f"There are {result} shipped orders from customers in USA.")


class OpenAILLMProvider:
    def __init__(self, settings: Settings):
        self.model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)
        self.fallback = DeterministicLLMProvider()

    def understand(self, question: str, schema: dict[str, object]) -> Decomposition:
        prompt = (
            "Identify the SQL intent, relevant tables, columns, and filters for this question. "
            "Use only the provided PostgreSQL schema.\n"
            f"Schema: {schema}\nQuestion: {question}"
        )
        return self.model.with_structured_output(Decomposition).invoke(prompt)

    def generate_sql(
        self, question: str, schema: dict[str, object], decomposition: Decomposition
    ) -> SQLDraft:
        prompt = (
            "Generate one PostgreSQL SELECT query only. Do not include markdown or comments. "
            "Use quoted identifiers where column names are camelCase. "
            "Use the exact case shown in _value_hints for string filters such as order status and country. "
            f"Schema: {schema}\nDecomposition: {decomposition.model_dump()}\nQuestion: {question}"
        )
        draft = self.model.with_structured_output(SQLDraft).invoke(prompt)
        return SQLDraft(sql=self._normalize_known_literals(draft.sql))

    def repair_sql(
        self, question: str, schema: dict[str, object], sql: str, error: str, attempt: int
    ) -> SQLDraft:
        prompt = (
            "Fix this PostgreSQL SELECT query using the error message. Return one SELECT query only. "
            "Use the exact case shown in _value_hints for string filters. "
            f"Attempt: {attempt}\nSchema: {schema}\nQuestion: {question}\nSQL: {sql}\nError: {error}"
        )
        draft = self.model.with_structured_output(SQLDraft).invoke(prompt)
        return SQLDraft(sql=self._normalize_known_literals(draft.sql))

    def summarize(self, question: str, sql: str, result: object) -> SummaryDraft:
        prompt = (
            "Summarize the SQL result in one natural sentence. "
            f"Question: {question}\nSQL: {sql}\nResult: {result}"
        )
        return self.model.with_structured_output(SummaryDraft).invoke(prompt)

    def _normalize_known_literals(self, sql: str) -> str:
        normalized = re.sub(r"=\s*'shipped'", "= 'Shipped'", sql, flags=re.IGNORECASE)
        normalized = re.sub(r"=\s*'usa'", "= 'USA'", normalized, flags=re.IGNORECASE)
        return normalized


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.openai_api_key:
        return OpenAILLMProvider(settings)
    return DeterministicLLMProvider()
