from time import perf_counter
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from app.safety import validate_select_sql
from app.settings import Settings, get_settings


class QueryExecutor:
    def __init__(self, engine: Engine | None = None):
        self.engine = engine or create_engine(get_settings().database_url, pool_pre_ping=True)

    @classmethod
    def from_settings(cls, settings: Settings) -> "QueryExecutor":
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        return cls(engine=engine)

    def get_schema_snapshot(self) -> dict[str, Any]:
        inspector = inspect(self.engine)
        schema: dict[str, Any] = {}
        for table_name in inspector.get_table_names():
            schema[table_name] = [column["name"] for column in inspector.get_columns(table_name)]
        schema["_value_hints"] = self._get_value_hints()
        return schema

    def _get_value_hints(self) -> dict[str, list[str]]:
        hints: dict[str, list[str]] = {}
        queries = {
            "orders.status": 'SELECT DISTINCT status FROM orders ORDER BY status',
            "customers.country": 'SELECT DISTINCT country FROM customers ORDER BY country',
        }
        with self.engine.connect() as connection:
            for key, query in queries.items():
                try:
                    hints[key] = [row[0] for row in connection.execute(text(query)).fetchall()]
                except Exception:
                    hints[key] = []
        return hints

    def execute_select(self, sql: str) -> tuple[Any, float]:
        safe_sql = validate_select_sql(sql)
        started = perf_counter()
        with self.engine.connect() as connection:
            rows = connection.execute(text(safe_sql)).mappings().all()
        elapsed_ms = (perf_counter() - started) * 1000

        if len(rows) == 1 and len(rows[0]) == 1:
            return next(iter(rows[0].values())), elapsed_ms
        return [dict(row) for row in rows], elapsed_ms

    def close(self) -> None:
        self.engine.dispose()
