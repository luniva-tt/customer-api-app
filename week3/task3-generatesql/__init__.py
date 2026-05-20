"""
Text-to-SQL Pipeline Package
Converts natural language questions to SQL and executes them
"""

__version__ = "1.0.0"
__author__ = "Copilot"

from .database import DatabaseConnection
from .sql_generator import SQLGenerator
from .validator import SQLValidator
from .executor import QueryExecutor
from .main import TextToSQLPipeline

__all__ = [
    'DatabaseConnection',
    'SQLGenerator',
    'SQLValidator',
    'QueryExecutor',
    'TextToSQLPipeline'
]
