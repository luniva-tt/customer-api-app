from fastapi.testclient import TestClient

from app.dependencies import get_agent
from app.main import app
from app.schemas import AgentSQLResponse


class StubAgent:
    async def answer(self, question):
        return AgentSQLResponse(
            sql='SELECT COUNT(*) FROM orders WHERE status = \'Shipped\'',
            result=42,
            summary="There are 42 shipped orders from customers in USA.",
            status="success",
        )


def test_post_agent_sql_returns_agent_response():
    app.dependency_overrides[get_agent] = lambda: StubAgent()
    client = TestClient(app)

    response = client.post(
        "/agent/sql",
        json={"question": "How many shipped orders are from USA customers?"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "sql": "SELECT COUNT(*) FROM orders WHERE status = 'Shipped'",
        "result": 42,
        "summary": "There are 42 shipped orders from customers in USA.",
        "status": "success",
        "error": None,
    }
