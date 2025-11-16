"""
Conversation History Manager for context-aware SQL generation.
"""
from typing import List, Dict, Optional
from datetime import datetime


class ConversationManager:
    """Manages conversation history for context-aware query generation."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation manager.
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.max_history = max_history
        self.history: List[Dict] = []
        self.last_query: Optional[str] = None
        self.last_sql: Optional[str] = None
    
    def add_turn(self, user_input: str, sql_query: str, context: Optional[Dict] = None):
        """
        Add a conversation turn to history.
        
        Args:
            user_input: User's natural language input
            sql_query: Generated SQL query
            context: Optional additional context
        """
        turn = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'sql_query': sql_query,
            'context': context or {}
        }
        
        self.history.append(turn)
        self.last_query = sql_query
        self.last_sql = sql_query
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def is_follow_up(self, user_input: str) -> bool:
        """
        Check if user input is a follow-up query.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            True if input appears to be a follow-up
        """
        if not self.last_query:
            return False
        
        follow_up_indicators = [
            'now show me',
            'now show',
            'show me',
            'also show',
            'and show',
            'then show',
            'next show',
            'also',
            'and',
            'then',
            'next',
            'filter',
            'refine',
            'narrow',
            'expand'
        ]
        
        input_lower = user_input.lower().strip()
        return any(indicator in input_lower for indicator in follow_up_indicators)
    
    def get_context_prompt(self) -> str:
        """
        Get context from conversation history for the model prompt.
        
        Returns:
            Formatted context string
        """
        if not self.history:
            return ""
        
        context_parts = ["Previous conversation:"]
        
        # Include last 2-3 turns for context
        recent_turns = self.history[-3:]
        for i, turn in enumerate(recent_turns, 1):
            context_parts.append(f"\nTurn {i}:")
            context_parts.append(f"  User: {turn['user_input']}")
            context_parts.append(f"  SQL: {turn['sql_query']}")
        
        return "\n".join(context_parts)
    
    def get_last_sql(self) -> Optional[str]:
        """Get the last generated SQL query."""
        return self.last_sql
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        self.last_query = None
        self.last_sql = None

