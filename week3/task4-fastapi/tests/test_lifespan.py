from fastapi.testclient import TestClient

from week2.app.main import create_app


class FakeExecutor:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeAgent:
    def __init__(self, llm_provider, query_executor, max_attempts):
        self.llm_provider = llm_provider
        self.query_executor = query_executor
        self.max_attempts = max_attempts


class FakeSettings:
    openai_api_key = None
    openai_model = "test-model"
    database_url = "postgresql+psycopg://test:test@localhost/test"
    max_attempts = 7


def test_lifespan_creates_shared_dependencies_and_closes_executor():
    executor = FakeExecutor()
    app = create_app(
        settings_provider=lambda: FakeSettings(),
        llm_provider_factory=lambda settings: "llm",
        query_executor_factory=lambda settings: executor,
        agent_factory=FakeAgent,
    )

    with TestClient(app):
        assert app.state.settings.max_attempts == 7
        assert app.state.llm_provider == "llm"
        assert app.state.query_executor is executor
        assert app.state.agent.query_executor is executor
        assert app.state.agent.max_attempts == 7

    assert executor.closed is True
