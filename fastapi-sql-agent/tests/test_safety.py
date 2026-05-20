import pytest

from app.safety import SQLValidationError, validate_select_sql


def test_validate_select_sql_allows_joined_count_query():
    sql = (
        'SELECT COUNT(*) FROM orders o '
        'JOIN customers c ON o."customerNumber" = c."customerNumber" '
        "WHERE o.status = 'Shipped' AND c.country = 'USA'"
    )

    assert validate_select_sql(sql) == sql


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM orders",
        "UPDATE orders SET status = 'Shipped'",
        "SELECT * FROM orders; DROP TABLE orders;",
        "INSERT INTO orders VALUES (1)",
    ],
)
def test_validate_select_sql_rejects_unsafe_queries(sql):
    with pytest.raises(SQLValidationError):
        validate_select_sql(sql)
