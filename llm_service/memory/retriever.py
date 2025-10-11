"""
Unified Retriever - Combines Qdrant (semantic) + Redis (conversation) memory
Provides hybrid context for LLM queries.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from .embeddings_manager import get_embeddings_manager
from .redis_memory import get_redis_memory

logger = logging.getLogger(__name__)

class UnifiedRetriever:
    """Retrieves context from Qdrant (semantic) + Redis (conversation) memory."""
    
    def __init__(self):
        """Initialize memory managers."""
        try:
            self.embeddings = get_embeddings_manager()
            self.redis = get_redis_memory()
            logger.info("Initialized UnifiedRetriever with Qdrant + Redis")
        except Exception as e:
            logger.error(f"Failed to initialize UnifiedRetriever: {e}", exc_info=True)
            raise
    
    def get_context_for_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        include_conversation: bool = True
    ) -> Dict[str, Any]:
        """
        Get combined context from semantic search + conversation history.
        
        Args:
            query: Query text
            session_id: Optional session ID for conversation history
            top_k: Number of semantic search results
            include_conversation: Whether to include chat history
            
        Returns:
            Dict with combined context and sources
        """
        try:
            context_parts = []
            sources = []
            
            # 1. Get semantically similar content from Qdrant
            similar_docs = self.embeddings.query_similar(query, top_k=top_k)
            
            if similar_docs:
                context_parts.append("=== Relevant Information ===")
                for doc in similar_docs:
                    if doc.get("text"):
                        context_parts.append(doc["text"])
                        sources.append({
                            "type": "semantic",
                            "id": doc.get("id"),
                            "score": doc.get("score"),
                            "metadata": doc.get("metadata", {})
                        })
            
            # 2. Get recent conversation history from Redis
            if include_conversation and session_id:
                chat_history = self.redis.get_recent_context(session_id, n=10)
                if chat_history:
                    context_parts.append("\n=== Recent Conversation ===")
                    for msg in chat_history:
                        role = msg.get("role", "user").upper()
                        content = msg.get("content", "")
                        context_parts.append(f"{role}: {content}")
                    sources.append({
                        "type": "conversation",
                        "session_id": session_id,
                        "message_count": len(chat_history)
                    })
            
            # Combine all context
            combined_context = "\n".join(context_parts)
            
            # Truncate if too long
            max_context_length = 4000
            if len(combined_context) > max_context_length:
                combined_context = combined_context[:max_context_length] + "...[truncated]"
            
            return {
                "context": combined_context,
                "sources": sources,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error getting context for query: {e}", exc_info=True)
            return {
                "context": "",
                "sources": [],
                "query": query,
                "error": str(e)
            }
    
    def store_message_with_context(
        self,
        message_id: str,
        text: str,
        sender: str,
        session_id: Optional[str] = None,
        role: str = "user",
        entities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a message in both Qdrant (for semantic search) and Redis (for conversation).
        
        Args:
            message_id: Unique message identifier
            text: Message content
            sender: Message sender
            session_id: Optional session ID
            role: Message role (user/assistant/system)
            entities: Optional extracted entities
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            success = True
            
            if not metadata:
                metadata = {}
            
            metadata.update({
                "sender": sender,
                "role": role
            })
            
            if entities:
                metadata["entities"] = entities
            
            # 1. Store embedding in Qdrant
            try:
                self.embeddings.store_embedding(
                    text=text,
                    metadata=metadata,
                    doc_id=message_id
                )
                logger.info(f"Stored message {message_id} in Qdrant")
            except Exception as e:
                logger.error(f"Failed to store in Qdrant: {e}")
                success = False
            
            # 2. Store in Redis conversation history
            if session_id:
                try:
                    self.redis.append_message(
                        session_id=session_id,
                        role=role,
                        content=text,
                        metadata=metadata
                    )
                    logger.info(f"Stored message {message_id} in Redis session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to store in Redis: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing message with context: {e}", exc_info=True)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all memory systems."""
        try:
            status = {
                "qdrant": {},
                "redis": {}
            }
            
            # Qdrant status
            try:
                qdrant_info = self.embeddings.get_collection_info()
                status["qdrant"] = qdrant_info
                status["qdrant"]["status"] = "connected"
            except Exception as e:
                status["qdrant"]["status"] = f"error: {str(e)}"
            
            # Redis status
            try:
                self.redis.client.ping()
                status["redis"]["status"] = "connected"
            except Exception as e:
                status["redis"]["status"] = f"error: {str(e)}"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}", exc_info=True)
            return {
                "qdrant": {"status": "error"},
                "redis": {"status": "error"},
                "error": str(e)
            }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session from Redis."""
        try:
            return self.redis.clear_session(session_id)
        except Exception as e:
            logger.error(f"Error clearing session: {e}", exc_info=True)
            return False


# Singleton instance
_unified_retriever = None

def get_unified_retriever() -> UnifiedRetriever:
    """Get or create singleton UnifiedRetriever instance."""
    global _unified_retriever
    if _unified_retriever is None:
        _unified_retriever = UnifiedRetriever()
    return _unified_retriever
