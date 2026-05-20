"""
SQL Query Executor
Executes validated queries and handles retries
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from database import DatabaseConnection
from validator import SQLValidator
from sql_generator import SQLGenerator

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes SQL queries with error handling and retry logic."""
    
    MAX_RETRIES = 1
    LOG_DIR = "logs"
    
    def __init__(self, db: DatabaseConnection, generator: SQLGenerator):
        """
        Initialize executor.
        
        Args:
            db: DatabaseConnection instance
            generator: SQLGenerator instance
        """
        self.db = db
        self.generator = generator
        
        # Create logs directory
        os.makedirs(self.LOG_DIR, exist_ok=True)
    
    def execute(self, question: str, decomposition: Dict[str, Any], 
                schema_context: str = "") -> Dict[str, Any]:
        """
        Execute full pipeline from decomposition to SQL execution.
        
        Args:
            question: Original question
            decomposition: Structured decomposition
            schema_context: Database schema info
            
        Returns:
            Result dictionary with question, sql, result, status
        """
        
        result = {
            "question": question,
            "sql": "",
            "result": [],
            "status": "unknown",
            "error": None,
            "column_names": [],
            "row_count": 0
        }
        
        try:
            # Step 1: Generate SQL
            logger.info(f"Generating SQL for: {question[:50]}...")
            gen_result = self.generator.generate_sql(decomposition, schema_context)
            
            if not gen_result["success"]:
                result["status"] = "generation_failed"
                result["error"] = gen_result["error"]
                self._log_execution(result)
                return result
            
            sql_query = gen_result["sql"]
            result["sql"] = sql_query
            
            # Step 2: Validate SQL
            logger.info("Validating SQL query...")
            validation = SQLValidator.validate_query(sql_query)
            
            if not validation["is_valid"]:
                result["status"] = "validation_failed"
                result["error"] = "; ".join(validation["issues"])
                self._log_execution(result)
                return result
            
            # Step 3: Execute SQL
            logger.info("Executing SQL query...")
            exec_result = self.db.execute_query(sql_query)
            
            if exec_result["success"]:
                result["status"] = "success"
                result["result"] = exec_result["data"]
                result["column_names"] = exec_result["column_names"]
                result["row_count"] = len(exec_result["data"])
                logger.info(f"Success! Retrieved {result['row_count']} rows")
            
            else:
                # Step 4: Retry with fix
                error_msg = exec_result["error"]
                logger.warning(f"Query failed: {error_msg}")
                logger.info("Attempting to fix and retry...")
                
                fix_result = self.generator.fix_sql_error(
                    decomposition, 
                    sql_query,
                    error_msg,
                    schema_context
                )
                
                if not fix_result["success"]:
                    result["status"] = "execution_failed"
                    result["error"] = error_msg
                    self._log_execution(result)
                    return result
                
                fixed_sql = fix_result["sql"]
                result["sql"] = fixed_sql
                
                # Validate fixed query
                validation = SQLValidator.validate_query(fixed_sql)
                if not validation["is_valid"]:
                    result["status"] = "fixed_validation_failed"
                    result["error"] = "; ".join(validation["issues"])
                    self._log_execution(result)
                    return result
                
                # Execute fixed query
                exec_result = self.db.execute_query(fixed_sql)
                
                if exec_result["success"]:
                    result["status"] = "success_on_retry"
                    result["result"] = exec_result["data"]
                    result["column_names"] = exec_result["column_names"]
                    result["row_count"] = len(exec_result["data"])
                    logger.info(f"Retry success! Retrieved {result['row_count']} rows")
                else:
                    result["status"] = "execution_failed_after_retry"
                    result["error"] = exec_result["error"]
                    logger.error(f"Retry failed: {exec_result['error']}")
        
        except Exception as e:
            result["status"] = "unexpected_error"
            result["error"] = str(e)
            logger.exception("Unexpected error during execution")
        
        # Log execution
        self._log_execution(result)
        
        return result
    
    def _log_execution(self, result: Dict[str, Any]):
        """
        Log query execution to file.
        
        Args:
            result: Execution result
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "question": result.get("question", ""),
                "status": result.get("status", ""),
                "sql": result.get("sql", ""),
                "row_count": result.get("row_count", 0),
                "error": result.get("error", "")
            }
            
            log_file = os.path.join(self.LOG_DIR, "execution_log.jsonl")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.debug(f"Execution logged to {log_file}")
        
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics from logs.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "total": 0,
            "success": 0,
            "success_on_retry": 0,
            "failed": 0,
            "total_rows": 0
        }
        
        log_file = os.path.join(self.LOG_DIR, "execution_log.jsonl")
        
        if not os.path.exists(log_file):
            return stats
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    stats["total"] += 1
                    
                    status = entry.get("status", "")
                    if status == "success":
                        stats["success"] += 1
                    elif status == "success_on_retry":
                        stats["success_on_retry"] += 1
                    elif "failed" in status or "error" in status:
                        stats["failed"] += 1
                    
                    stats["total_rows"] += entry.get("row_count", 0)
        
        except Exception as e:
            logger.error(f"Failed to read execution stats: {e}")
        
        return stats
