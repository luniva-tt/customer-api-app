"""
SQL Query Generator using Groq LLM
Converts structured decomposition to SQL queries
"""

import json
import os
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generates SQL queries from structured decompositions using Groq."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize SQL generator.
        
        Args:
            api_key: Groq API key (if None, uses GROQ_API_KEY env var)
            model: Model to use
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
    
    def generate_sql(self, decomposition: Dict[str, Any], schema_context: str = "") -> Dict[str, Any]:
        """
        Generate SQL query from decomposition.
        
        Args:
            decomposition: Structured query decomposition
            schema_context: Optional database schema info
            
        Returns:
            Dictionary with keys: sql, success, error
        """
        
        system_prompt = """You are an expert PostgreSQL SQL query generator.
Your task is to convert a structured query decomposition into a safe, correct SQL SELECT query.

IMPORTANT RULES:
1. Only generate SELECT queries - NEVER generate INSERT, UPDATE, DELETE, or DROP
2. Use table aliases for readability (e.g., 'c' for customers, 'o' for orders)
3. Use proper JOIN syntax: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN as needed
4. Include WHERE clauses for all filters
5. Include GROUP BY when aggregating
6. Use semicolon at the end
7. Return ONLY valid SQL, no markdown or extra text
8. Validate that column names and table names match the schema
9. Handle NULL values appropriately
10. Use DISTINCT when listing unique values

Generated SQL must be ready to execute directly against PostgreSQL."""
        
        # Build decomposition summary
        decomp_str = f"""
Decomposition:
- Intent: {decomposition.get('intent', 'Unknown')}
- Tables: {json.dumps(decomposition.get('tables', []))}
- Columns: {json.dumps(decomposition.get('columns', []))}
- Filters: {json.dumps(decomposition.get('filters', []))}
- Joins: {json.dumps(decomposition.get('joins', []))}
- Aggregate: {decomposition.get('aggregate', 'None')}
- Order By: {json.dumps(decomposition.get('order_by', []))}
- Notes: {decomposition.get('notes', '')}
"""
        
        user_prompt = f"""Generate a PostgreSQL SELECT query for this decomposition:
{decomp_str}

Schema Context:
{schema_context}

Return ONLY the SQL query with no explanation or markdown formatting."""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            
            sql_query = message.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            logger.info(f"Generated SQL: {sql_query[:100]}...")
            
            return {
                "sql": sql_query,
                "success": True,
                "error": None
            }
        
        except Exception as e:
            error_msg = f"Failed to generate SQL: {str(e)}"
            logger.error(error_msg)
            return {
                "sql": "",
                "success": False,
                "error": error_msg
            }
    
    def fix_sql_error(self, decomposition: Dict[str, Any], failed_sql: str, 
                      error_message: str, schema_context: str = "") -> Dict[str, Any]:
        """
        Attempt to fix SQL query based on error message.
        
        Args:
            decomposition: Original decomposition
            failed_sql: The SQL query that failed
            error_message: Error message from database
            schema_context: Database schema info
            
        Returns:
            Dictionary with keys: sql, success, error
        """
        
        system_prompt = """You are an expert PostgreSQL SQL fixer.
Your task is to fix a SQL query that has failed with an error.

IMPORTANT:
1. Analyze the error message carefully
2. Fix the SQL query to resolve the error
3. Return ONLY the corrected SQL query
4. Only generate SELECT queries
5. Do not add markdown formatting"""
        
        user_prompt = f"""Fix this SQL query that failed with an error:

Failed SQL:
{failed_sql}

Error Message:
{error_message}

Decomposition:
- Tables: {json.dumps(decomposition.get('tables', []))}
- Columns: {json.dumps(decomposition.get('columns', []))}
- Filters: {json.dumps(decomposition.get('filters', []))}
- Joins: {json.dumps(decomposition.get('joins', []))}

Schema:
{schema_context}

Return the corrected SQL query only."""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1024
            )
            
            sql_query = message.choices[0].message.content.strip()
            
            # Remove markdown
            if sql_query.startswith("```"):
                sql_query = sql_query[sql_query.find("\n")+1:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:sql_query.rfind("```")]
            
            sql_query = sql_query.strip()
            
            logger.info(f"Fixed SQL: {sql_query[:100]}...")
            
            return {
                "sql": sql_query,
                "success": True,
                "error": None
            }
        
        except Exception as e:
            error_msg = f"Failed to fix SQL: {str(e)}"
            logger.error(error_msg)
            return {
                "sql": "",
                "success": False,
                "error": error_msg
            }
