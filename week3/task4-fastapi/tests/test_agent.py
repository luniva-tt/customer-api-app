import pytest

from app.agent import SQLAgent
from app.llm import DeterministicLLMProvider
from week2.app.schemas import Decomposition, SQLDraft, SummaryDraft


class RepairingProvider(DeterministicLLMProvider):
    def __init__(self):
        self.repairs = 0

    def generate_sql(self, question, schema, decomposition):
        return SQLDraft(sql="SELECT COUNT(*) FROM missing_table")

    def repair_sql(self, question, schema, sql, error, attempt):
        self.repairs += 1
        return SQLDraft(
            sql=(
                'SELECT COUNT(*) FROM orders o JOIN customers c '
                'ON o."customerNumber" = c."customerNumber" '
                "WHERE o.status = 'Shipped' AND c.country = 'USA'"
            )
        )


class AlwaysBadProvider(DeterministicLLMProvider):
    def generate_sql(self, question, schema, decomposition):
        return SQLDraft(sql="SELECT COUNT(*) FROM missing_table")

    def repair_sql(self, question, schema, sql, error, attempt):
        return SQLDraft(sql="SELECT COUNT(*) FROM still_missing")

    def summarize(self, question, sql, result):
        return SummaryDraft(summary="This should not be used.")


class FakeExecutor:
    schema = {
        "orders": ["orderNumber", "status", "customerNumber"],
        "customers": ["customerNumber", "country"],
    }

    def __init__(self, fail_forever=False):
        self.calls = 0
        self.fail_forever = fail_forever

    def get_schema_snapshot(self):
        return self.schema

    def execute_select(self, sql):
        self.calls += 1
        if "missing" in sql:
            raise RuntimeError('relation "missing_table" does not exist')
        if self.fail_forever:
            raise RuntimeError("database unavailable")
        return 42, 0.012


@pytest.mark.asyncio
async def test_agent_repairs_failed_sql_and_returns_success():
    provider = RepairingProvider()
    executor = FakeExecutor()
    agent = SQLAgent(llm_provider=provider, query_executor=executor)

    response = await agent.answer("How many shipped orders are from USA customers?")

    assert response.status == "success"
    assert response.result == 42
    assert "COUNT" in response.sql
    assert provider.repairs == 1
    assert executor.calls == 2


@pytest.mark.asyncio
async def test_agent_returns_fallback_after_three_failed_attempts():
    agent = SQLAgent(llm_provider=AlwaysBadProvider(), query_executor=FakeExecutor())

    response = await agent.answer("How many shipped orders are from USA customers?")

    assert response.status == "failed"
    assert response.result is None
    assert "after 3 attempts" in response.summary
