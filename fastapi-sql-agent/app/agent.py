import asyncio
import logging
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.database import QueryExecutor
from app.llm import LLMProvider, build_llm_provider
from app.safety import SQLValidationError, validate_select_sql
from app.schemas import AgentSQLResponse, Decomposition

logger = logging.getLogger("sql_agent")
logging.basicConfig(level=logging.INFO)


class AgentState(TypedDict, total=False):
    question: str
    schema: dict[str, object]
    decomposition: Decomposition
    sql: str
    result: Any
    summary: str
    error: str
    attempt: int
    status: Literal["success", "failed"]


class SQLAgent:
    def __init__(self, llm_provider: LLMProvider, query_executor: QueryExecutor, max_attempts: int = 3):
        self.llm = llm_provider
        self.executor = query_executor
        self.max_attempts = max_attempts
        self.graph = self._build_graph()

    async def answer(self, question: str) -> AgentSQLResponse:
        initial_state: AgentState = {
            "question": question,
            "schema": self.executor.get_schema_snapshot(),
            "attempt": 1,
        }
        final_state = await asyncio.to_thread(self.graph.invoke, initial_state)
        return AgentSQLResponse(
            sql=final_state.get("sql"),
            result=final_state.get("result"),
            summary=final_state.get("summary", "Unable to answer the question."),
            status=final_state.get("status", "failed"),
            error=final_state.get("error"),
        )

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("understand_query", self._understand_query)
        graph.add_node("generate_sql", self._generate_sql)
        graph.add_node("validate_sql", self._validate_sql)
        graph.add_node("execute_sql", self._execute_sql)
        graph.add_node("repair_sql", self._repair_sql)
        graph.add_node("summarize", self._summarize)
        graph.add_node("fallback", self._fallback)

        graph.add_edge(START, "understand_query")
        graph.add_edge("understand_query", "generate_sql")
        graph.add_edge("generate_sql", "validate_sql")
        graph.add_conditional_edges(
            "validate_sql",
            self._route_after_validation,
            {"execute": "execute_sql", "repair": "repair_sql", "fallback": "fallback"},
        )
        graph.add_conditional_edges(
            "execute_sql",
            self._route_after_execution,
            {"summarize": "summarize", "repair": "repair_sql", "fallback": "fallback"},
        )
        graph.add_edge("repair_sql", "validate_sql")
        graph.add_edge("summarize", END)
        graph.add_edge("fallback", END)
        return graph.compile()

    def _understand_query(self, state: AgentState) -> AgentState:
        decomposition = self.llm.understand(state["question"], state["schema"])
        logger.info("decomposition step: %s", decomposition.model_dump())
        return {"decomposition": decomposition}

    def _generate_sql(self, state: AgentState) -> AgentState:
        draft = self.llm.generate_sql(state["question"], state["schema"], state["decomposition"])
        logger.info("SQL generation attempt %s: %s", state["attempt"], draft.sql)
        return {"sql": draft.sql, "error": ""}

    def _validate_sql(self, state: AgentState) -> AgentState:
        try:
            return {"sql": validate_select_sql(state["sql"]), "error": ""}
        except SQLValidationError as exc:
            return {"error": str(exc)}

    def _execute_sql(self, state: AgentState) -> AgentState:
        try:
            result, elapsed_ms = self.executor.execute_select(state["sql"])
            logger.info("execution time: %.2fms", elapsed_ms)
            return {"result": result, "status": "success", "error": ""}
        except Exception as exc:
            logger.info("SQL execution failed on attempt %s: %s", state["attempt"], exc)
            return {"error": str(exc)}

    def _repair_sql(self, state: AgentState) -> AgentState:
        next_attempt = state["attempt"] + 1
        draft = self.llm.repair_sql(
            state["question"],
            state["schema"],
            state["sql"],
            state["error"],
            next_attempt,
        )
        logger.info("SQL generation repair attempt %s: %s", next_attempt, draft.sql)
        return {"sql": draft.sql, "attempt": next_attempt, "error": ""}

    def _summarize(self, state: AgentState) -> AgentState:
        draft = self.llm.summarize(state["question"], state["sql"], state["result"])
        return {"summary": draft.summary, "status": "success"}

    def _fallback(self, state: AgentState) -> AgentState:
        return {
            "status": "failed",
            "result": None,
            "summary": f"Unable to generate a working SQL query after {self.max_attempts} attempts.",
        }

    def _route_after_validation(self, state: AgentState) -> str:
        if not state.get("error"):
            return "execute"
        if state["attempt"] >= self.max_attempts:
            return "fallback"
        return "repair"

    def _route_after_execution(self, state: AgentState) -> str:
        if state.get("status") == "success":
            return "summarize"
        if state["attempt"] >= self.max_attempts:
            return "fallback"
        return "repair"
