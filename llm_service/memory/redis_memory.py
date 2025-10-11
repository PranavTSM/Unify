"""
Redis Memory - Short-term Conversational Memory
Stores recent chat history per session for context using LangChain.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEFAULT_TTL = 3600 * 24  # 24 hours

class RedisMemory:
    """Manages short-term conversational memory with Redis using LangChain."""
    
    def __init__(self, redis_url: str = REDIS_URL):
        """Initialize Redis connection."""
        try:
            self.redis_url = redis_url
            self.ttl = DEFAULT_TTL
            # Test connection
            import redis
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            client.close()
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise
    
    def _get_history(self, session_id: str) -> RedisChatMessageHistory:
        """Get LangChain chat message history for a session."""
        return RedisChatMessageHistory(
            session_id=session_id,
            url=self.redis_url,
            ttl=self.ttl
        )
    
    def _role_to_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> BaseMessage:
        """Convert role/content to LangChain message."""
        additional_kwargs = {"metadata": metadata} if metadata else {}
        
        if role.lower() == "user" or role.lower() == "human":
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
        elif role.lower() == "assistant" or role.lower() == "ai":
            return AIMessage(content=content, additional_kwargs=additional_kwargs)
        elif role.lower() == "system":
            return SystemMessage(content=content, additional_kwargs=additional_kwargs)
        else:
            # Default to human message
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
    
    def _message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        """Convert LangChain message to dict format."""
        role_map = {
            "human": "user",
            "ai": "assistant",
            "system": "system"
        }
        
        role = role_map.get(message.type, "user")
        metadata = message.additional_kwargs.get("metadata", {})
        
        return {
            "role": role,
            "content": message.content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
    
    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append a message to session history using LangChain.
        
        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata dict
            
        Returns:
            True if successful
        """
        try:
            history = self._get_history(session_id)
            message = self._role_to_message(role, content, metadata)
            history.add_message(message)
            
            logger.debug(f"Appended {role} message to session {session_id} via LangChain")
            return True
            
        except Exception as e:
            logger.error(f"Error appending message: {e}", exc_info=True)
            return False
    
    def get_recent_context(
        self,
        session_id: str,
        n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages from session using LangChain.
        
        Args:
            session_id: Session identifier
            n: Number of recent messages to retrieve
            
        Returns:
            List of message dicts
        """
        try:
            history = self._get_history(session_id)
            all_messages = history.messages
            
            # Get last n messages
            recent_messages = all_messages[-n:] if len(all_messages) > n else all_messages
            
            # Convert to dict format
            messages = [self._message_to_dict(msg) for msg in recent_messages]
            
            logger.info(f"Retrieved {len(messages)} messages from session {session_id} via LangChain")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent context: {e}", exc_info=True)
            return []
    
    def get_all_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages from a session using LangChain.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of all message dicts
        """
        try:
            history = self._get_history(session_id)
            all_messages = history.messages
            
            # Convert to dict format
            messages = [self._message_to_dict(msg) for msg in all_messages]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting all messages: {e}", exc_info=True)
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session using LangChain.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            history = self._get_history(session_id)
            history.clear()
            logger.info(f"Cleared session {session_id} via LangChain")
            return True
        except Exception as e:
            logger.error(f"Error clearing session: {e}", exc_info=True)
            return False
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session using LangChain.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session info
        """
        try:
            history = self._get_history(session_id)
            messages = history.messages
            message_count = len(messages)
            
            return {
                "session_id": session_id,
                "message_count": message_count,
                "ttl_seconds": self.ttl,
                "exists": message_count > 0
            }
        except Exception as e:
            logger.error(f"Error getting session info: {e}", exc_info=True)
            return {"session_id": session_id, "exists": False}
    
    def format_context_string(
        self,
        session_id: str,
        n: int = 10
    ) -> str:
        """
        Get recent messages formatted as a context string.
        
        Args:
            session_id: Session identifier
            n: Number of recent messages
            
        Returns:
            Formatted context string
        """
        messages = self.get_recent_context(session_id, n)
        
        if not messages:
            return ""
        
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role.upper()}: {content}")
        
        return "\n".join(lines)
    
    def extend_session_ttl(self, session_id: str, ttl_seconds: int = DEFAULT_TTL) -> bool:
        """
        Extend the TTL of a session.
        
        Args:
            session_id: Session identifier
            ttl_seconds: New TTL in seconds
            
        Returns:
            True if successful
        """
        try:
            # Update the instance TTL (will apply to next get_history call)
            self.ttl = ttl_seconds
            logger.debug(f"Set TTL for session {session_id} to {ttl_seconds}s")
            return True
        except Exception as e:
            logger.error(f"Error extending session TTL: {e}", exc_info=True)
            return False
    
    def get_langchain_history(self, session_id: str) -> RedisChatMessageHistory:
        """
        Get the raw LangChain RedisChatMessageHistory object for advanced use.
        
        Args:
            session_id: Session identifier
            
        Returns:
            RedisChatMessageHistory instance
        """
        return self._get_history(session_id)
    
    @property
    def client(self):
        """
        Legacy property for backward compatibility.
        Returns a basic Redis client for status checks.
        """
        import redis
        return redis.from_url(self.redis_url, decode_responses=True)

# Singleton instance
_redis_memory = None

def get_redis_memory() -> RedisMemory:
    """Get or create singleton RedisMemory instance."""
    global _redis_memory
    if _redis_memory is None:
        _redis_memory = RedisMemory()
    return _redis_memory

