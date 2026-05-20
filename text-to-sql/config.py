"""
Configuration for Text-to-SQL Pipeline
"""

# Database Configuration
DATABASE = {
    "host": "localhost",
    "port": 5432,
    "database": "ecommerce_db",
    "user": "postgres",
    "password": "luniva"
}

# Groq Configuration
GROQ = {
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.2,
    "max_tokens": 1024
}

# Executor Configuration
EXECUTOR = {
    "max_retries": 1,
    "log_dir": "logs"
}

# Input/Output Paths
PATHS = {
    "decompositions_input": "../week3/query_decompositions.csv",
    "sql_results_output": "sql_results.csv",
    "execution_log": "logs/execution_log.jsonl",
    "pipeline_log": "logs/pipeline.log"
}

# Query Execution Limits
LIMITS = {
    "max_rows_return": 10000,
    "query_timeout_seconds": 30
}
