# Text-to-SQL Pipeline

This module converts natural language questions into SQL queries and executes them against PostgreSQL.

## Architecture

```
text-to-sql/
├── database.py          # PostgreSQL connection & queries
├── sql_generator.py     # Generate SQL using Groq LLM
├── validator.py         # Validate queries for safety
├── executor.py          # Execute queries with retry logic
├── main.py             # Pipeline orchestration
├── config.py           # Configuration settings
├── logs/               # Execution logs
└── README.md           # This file
```

## Pipeline Flow

1. **Input**: Read decompositions from CSV
2. **Generation**: Convert decomposition to SQL using Groq
3. **Validation**: Check query safety and syntax
4. **Execution**: Run query against PostgreSQL
5. **Error Handling**: If failure, attempt fix with LLM (1 retry)
6. **Output**: Save results to CSV with status

## Usage

### Basic Usage

```bash
cd text-to-sql
python main.py
```

### Input Format

The pipeline expects `../week3/query_decompositions.csv` with columns:
- question
- intent
- tables (JSON array)
- columns (JSON array)
- filters (JSON array)
- joins (JSON array)
- aggregate
- order_by (JSON array)
- notes
- error

### Output Format

Results saved to `sql_results.csv`:
- question
- status (success, success_on_retry, failed, etc.)
- sql (generated SQL query)
- row_count (number of rows returned)
- error (error message if any)
- column_names (JSON array)

## Safety Features

- **Only SELECT queries** allowed (DELETE/DROP/UPDATE/INSERT blocked)
- **SQL injection prevention** (pattern detection)
- **Query validation** before execution
- **Error handling** with retry mechanism
- **Execution logging** for audit trail

## Error Handling

When a query fails:

1. Database error message is analyzed
2. Groq LLM attempts to fix the SQL
3. Fixed query is validated and executed (1 retry max)
4. If still fails, error is logged and pipeline continues

## Logging

- `logs/pipeline.log` - Overall pipeline execution
- `logs/execution_log.jsonl` - Per-query execution details (JSON Lines format)

Each execution log entry contains:
- timestamp
- question
- status
- sql
- row_count
- error (if any)

## Configuration

Edit `config.py` to customize:
- Database credentials
- Groq model and temperature
- Input/output file paths
- Query limits and timeouts

## Example

### Input Decomposition

```json
{
    "question": "Show all orders placed by customers in Germany",
    "intent": "retrieve orders",
    "tables": ["orders", "customers"],
    "columns": ["orderNumber", "customerName"],
    "filters": [{"column": "country", "condition": "=", "value": "Germany"}],
    "joins": [{"table1": "orders", "table2": "customers", "on": "customers.customerNumber = orders.customerNumber"}],
    "aggregate": null,
    "order_by": [],
    "notes": "Multi-table query with filter"
}
```

### Generated SQL

```sql
SELECT o.orderNumber, c.customerName
FROM orders o
JOIN customers c
ON o.customerNumber = c.customerNumber
WHERE c.country = 'Germany';
```

### Output Result

```json
{
    "question": "Show all orders placed by customers in Germany",
    "status": "success",
    "sql": "SELECT o.orderNumber, c.customerName FROM orders o JOIN customers c ON o.customerNumber = c.customerNumber WHERE c.country = 'Germany';",
    "row_count": 5,
    "error": "",
    "column_names": ["orderNumber", "customerName"]
}
```

## Requirements

- PostgreSQL database running and accessible
- Groq API key in `.env` file
- Python 3.8+

## Testing

To test individual components:

```python
# Test database connection
from database import DatabaseConnection
db = DatabaseConnection()
db.connect()
tables = db.list_tables()

# Test SQL generation
from sql_generator import SQLGenerator
gen = SQLGenerator()
decomp = {"tables": ["customers"], "columns": ["*"], ...}
result = gen.generate_sql(decomp)

# Test validation
from validator import SQLValidator
is_safe, reason = SQLValidator.is_safe_query("SELECT * FROM users;")
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify credentials in `config.py`
- Check hostname and port

### Groq API Error
- Verify GROQ_API_KEY in `.env`
- Check API key is valid
- Check rate limits

### Query Execution Error
- Check database schema matches decomposition
- Verify table and column names
- Check for NULL values or data type mismatches

## Statistics

After pipeline completion, view statistics:
- Total queries processed
- Success rate
- Retry success rate
- Total rows retrieved

See output in console or check `logs/execution_log.jsonl`
