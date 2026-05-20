"""
SQL Query Validator
Validates SQL queries before execution
"""

import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validates SQL queries for safety and correctness."""
    
    # Blocked keywords
    BLOCKED_KEYWORDS = {
        'DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
        'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE', 'PRAGMA'
    }
    
    @staticmethod
    def is_safe_query(query: str) -> Tuple[bool, str]:
        """
        Check if query is safe to execute.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple (is_safe, reason)
        """
        
        # Remove comments
        query_clean = re.sub(r'--.*', '', query)
        query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
        
        # Check for blocked keywords
        tokens = query_clean.upper().split()
        
        for keyword in SQLValidator.BLOCKED_KEYWORDS:
            if keyword in tokens:
                return False, f"Blocked keyword: {keyword}"
        
        # Check that query starts with SELECT
        first_keyword = None
        for token in tokens:
            if token.isalpha():
                first_keyword = token.upper()
                break
        
        if first_keyword != 'SELECT':
            return False, f"Only SELECT queries allowed. Found: {first_keyword}"
        
        # Check for common injection patterns
        dangerous_patterns = [
            r';\s*(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)',
            r'(?:UNION|OR|AND)\s+1\s*=\s*1',
            r'--\s*',
            r'/\*.*\*/',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_clean, re.IGNORECASE):
                return False, f"Potentially dangerous pattern detected"
        
        return True, "Query is safe"
    
    @staticmethod
    def validate_query(query: str) -> Dict[str, Any]:
        """
        Comprehensive query validation.
        
        Args:
            query: SQL query string
            
        Returns:
            Dictionary with validation results
        """
        
        results = {
            "is_valid": True,
            "issues": []
        }
        
        # Check if query is not empty
        if not query or not query.strip():
            results["is_valid"] = False
            results["issues"].append("Query is empty")
            return results
        
        # Check safety
        is_safe, reason = SQLValidator.is_safe_query(query)
        if not is_safe:
            results["is_valid"] = False
            results["issues"].append(reason)
            logger.warning(f"Safety check failed: {reason}")
            return results
        
        # Check syntax basics
        if not query.rstrip().endswith(';'):
            query += ';'
            logger.debug("Added missing semicolon")
        
        # Check for SELECT
        if not query.strip().upper().startswith('SELECT'):
            results["is_valid"] = False
            results["issues"].append("Query must start with SELECT")
        
        # Check for balanced parentheses
        if query.count('(') != query.count(')'):
            results["is_valid"] = False
            results["issues"].append("Unbalanced parentheses")
        
        # Check for balanced quotes
        single_quotes = query.count("'") - query.count("\\'")
        if single_quotes % 2 != 0:
            results["is_valid"] = False
            results["issues"].append("Unbalanced single quotes")
        
        return results
    
    @staticmethod
    def check_query_completeness(query: str) -> Dict[str, Any]:
        """
        Check if query appears complete.
        
        Args:
            query: SQL query string
            
        Returns:
            Dictionary with completeness check results
        """
        
        query_upper = query.upper()
        
        checks = {
            "has_select": "SELECT" in query_upper,
            "has_from": "FROM" in query_upper,
            "has_where_if_needed": True,  # WHERE is optional
            "has_join_if_needed": True,   # JOIN is optional
            "appears_complete": query.strip().endswith(';')
        }
        
        return checks
