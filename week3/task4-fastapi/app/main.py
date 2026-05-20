from collections.abc import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.agent import SQLAgent
from week2.app.database import QueryExecutor
from app.dependencies import AgentDep
from app.llm import LLMProvider, build_llm_provider
from week2.app.schemas import AgentSQLRequest, AgentSQLResponse
from app.settings import Settings, get_settings


def create_app(
    settings_provider: Callable[[], Settings] = get_settings,
    llm_provider_factory: Callable[[Settings], LLMProvider] = build_llm_provider,
    query_executor_factory: Callable[[Settings], QueryExecutor] | None = None,
    agent_factory: Callable[..., SQLAgent] = SQLAgent,
) -> FastAPI:
    def build_query_executor(settings: Settings) -> QueryExecutor:
        if query_executor_factory is not None:
            return query_executor_factory(settings)
        return QueryExecutor.from_settings(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = settings_provider()
        query_executor = build_query_executor(settings)
        llm_provider = llm_provider_factory(settings)
        agent = agent_factory(
            llm_provider=llm_provider,
            query_executor=query_executor,
            max_attempts=settings.max_attempts,
        )

        app.state.settings = settings
        app.state.query_executor = query_executor
        app.state.llm_provider = llm_provider
        app.state.agent = agent
        try:
            yield
        finally:
            close = getattr(query_executor, "close", None)
            if callable(close):
                close()

    app = FastAPI(title="FastAPI SQL Agent", lifespan=lifespan)

    @app.post("/agent/sql", response_model=AgentSQLResponse)
    async def agent_sql(request: AgentSQLRequest, agent: AgentDep) -> AgentSQLResponse:
        return await agent.answer(request.question)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
