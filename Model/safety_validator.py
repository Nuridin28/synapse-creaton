"""
Safety Validator for SQL queries - ensures only safe SELECT queries are generated.
"""
import re
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from typing import List, Tuple


class SafetyValidator:
    """Validates SQL queries to ensure they are safe SELECT-only queries."""
    
    # Dangerous SQL keywords that should never appear
    DANGEROUS_KEYWORDS = {
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
        'TRUNCATE', 'CREATE', 'EXEC', 'EXECUTE', 'GRANT',
        'REVOKE', 'MERGE', 'REPLACE'
    }
    
    # Allowed SQL keywords (only SELECT-related)
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 
        'HAVING', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
        'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 
        'LIKE', 'BETWEEN', 'IS', 'NULL', 'DISTINCT', 'COUNT',
        'SUM', 'AVG', 'MAX', 'MIN', 'LIMIT', 'OFFSET', 'UNION',
        'ALL', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'ASC', 'DESC'
    }
    
    def validate(self, query: str) -> Tuple[bool, str]:
        """
        Validate that a SQL query is safe.
        
        Args:
            query: SQL query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Empty query provided"
        
        # Normalize query - remove leading comments and whitespace
        # Remove SQL comments (-- and /* */) but preserve the query structure
        # First, remove full-line comments that might appear before SELECT
        query_clean = re.sub(r'^\s*--.*?$', '', query, flags=re.MULTILINE)  # Remove -- comments at start of lines
        query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)  # Remove /* */ comments
        query_clean = query_clean.strip()
        query_upper = query_clean.upper()
        
        # Check if query starts with SELECT (after removing comments and whitespace)
        if not query_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Parse SQL to check for dangerous keywords (use cleaned query)
        try:
            parsed = sqlparse.parse(query_clean)
            if not parsed:
                return False, "Invalid SQL syntax"
            
            # Check each statement
            for statement in parsed:
                if not self._is_safe_statement(statement):
                    return False, "Query contains unsafe operations"
                    
        except Exception as e:
            return False, f"SQL parsing error: {str(e)}"
        
        # Check for dangerous keywords in the query
        query_words = set(query_upper.split())
        dangerous_found = query_words.intersection(self.DANGEROUS_KEYWORDS)
        
        if dangerous_found:
            return False, f"Query contains dangerous keywords: {', '.join(dangerous_found)}"
        
        return True, ""
    
    def _is_safe_statement(self, statement: Statement) -> bool:
        """Check if a parsed SQL statement is safe."""
        # Check token types
        for token in statement.flatten():
            if token.ttype is DML:
                # Only SELECT is allowed
                if token.value.upper() != 'SELECT':
                    return False
            elif token.ttype is Keyword:
                keyword = token.value.upper()
                if keyword in self.DANGEROUS_KEYWORDS:
                    return False
        
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent SQL injection attempts.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Sanitized input string
        """
        # Remove or escape potentially dangerous characters
        # For natural language, we mainly check for obvious SQL injection patterns
        dangerous_patterns = [
            '; DROP',
            '; DELETE',
            '; UPDATE',
            '; INSERT',
            'UNION SELECT',
            '1=1',
            'OR 1=1',
            '--',
            '/*',
            '*/'
        ]
        
        input_upper = user_input.upper()
        for pattern in dangerous_patterns:
            if pattern in input_upper:
                raise ValueError(f"Input contains potentially dangerous pattern: {pattern}")
        
        return user_input.strip()

