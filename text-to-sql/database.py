"""
PostgreSQL Database Connection Manager
"""

import psycopg2
from psycopg2 import sql
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections and queries."""
    
    def __init__(self, host: str = "localhost", port: int = 5432,
                 database: str = "ecommerce_db", user: str = "postgres",
                 password: str = "luniva"):
        """
        Initialize database connection.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Connected to PostgreSQL: {self.database}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute a SELECT query safely.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Dictionary with keys: success, data, error, column_names
        """
        if not self.connection:
            return {
                "success": False,
                "data": [],
                "error": "Not connected to database",
                "column_names": []
            }
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            cursor.close()
            
            return {
                "success": True,
                "data": rows,
                "error": None,
                "column_names": column_names
            }
        
        except psycopg2.Error as e:
            error_msg = str(e)
            logger.error(f"Query execution error: {error_msg}")
            return {
                "success": False,
                "data": [],
                "error": error_msg,
                "column_names": []
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error: {error_msg}")
            return {
                "success": False,
                "data": [],
                "error": error_msg,
                "column_names": []
            }
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """
        Get table schema (column names and types).
        
        Args:
            table_name: Table name
            
        Returns:
            Dictionary mapping column names to data types
        """
        query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        
        result = self.execute_query(query, (table_name,))
        
        if result["success"]:
            schema = {row[0]: row[1] for row in result["data"]}
            return schema
        return {}
    
    def list_tables(self) -> List[str]:
        """
        Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        query = """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
        
        result = self.execute_query(query)
        
        if result["success"]:
            return [row[0] for row in result["data"]]
        return []
    
    def get_all_schemas(self) -> Dict[str, Dict[str, str]]:
        """
        Get schemas for all tables.
        
        Returns:
            Dictionary mapping table names to their schemas
        """
        tables = self.list_tables()
        schemas = {}
        
        for table in tables:
            schemas[table] = self.get_table_schema(table)
        
        return schemas
