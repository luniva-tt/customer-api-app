import sqlglot
from sqlglot import exp


class SQLValidationError(ValueError):
    """Raised when generated SQL is not safe to execute."""


def validate_select_sql(sql: str) -> str:
    candidate = sql.strip()
    if not candidate:
        raise SQLValidationError("SQL query is empty.")

    try:
        statements = sqlglot.parse(candidate, read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise SQLValidationError(f"SQL parse failed: {exc}") from exc

    if len(statements) != 1:
        raise SQLValidationError("Only one SQL statement is allowed.")

    statement = statements[0]
    if not isinstance(statement, exp.Select):
        raise SQLValidationError("Only SELECT queries are allowed.")

    forbidden = (exp.Delete, exp.Update, exp.Insert, exp.Drop, exp.Create, exp.Alter)
    if statement.find(forbidden):
        raise SQLValidationError("Mutating SQL statements are not allowed.")

    return candidate.rstrip(";")
