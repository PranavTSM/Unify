"""
LLM Service Client - Interface for communicating with LLM service
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMServiceClient:
    """Client for interacting with the LLM service."""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        Initialize LLM service client.
        
        Args:
            base_url: Base URL of the LLM service
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        logger.info(f"Initialized LLM service client with base URL: {self.base_url}")
    
    def health_check(self) -> bool:
        """
        Check if LLM service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "healthy"
        except Exception as e:
            logger.error(f"LLM service health check failed: {e}")
            return False
    
    def summarize_batch(
        self,
        messages: List[Dict[str, Any]],
        mode: str = "executive",
        max_words: int = 200,
        store: bool = False,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize a batch of messages.
        
        Args:
            messages: List of message dictionaries
            mode: Summarization mode ('executive', 'bullets', 'paragraph')
            max_words: Maximum words in summary
            store: Whether to store in memory system
            session_id: Optional session ID for memory storage
            
        Returns:
            Dict with 'summary', 'bullets', and 'token_usage'
        """
        try:
            # Prepare messages in the format expected by LLM service
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    "id": msg.get("id"),
                    "source": msg.get("source"),
                    "subject": msg.get("subject"),
                    "body": msg.get("body"),
                    "timestamp": msg.get("timestamp"),
                    "sender": msg.get("sender")
                }
                formatted_messages.append(formatted_msg)
            
            payload = {
                "messages": formatted_messages,
                "mode": mode,
                "max_words": max_words,
                "store": store,
                "session_id": session_id
            }
            
            logger.info(f"Sending {len(messages)} messages to LLM service for summarization")
            
            response = self.session.post(
                f"{self.base_url}/summarize-batch",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info("Successfully received summary from LLM service")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("LLM service request timed out")
            raise Exception("LLM service timeout - request took too long")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM service error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error calling LLM service: {e}", exc_info=True)
            raise
    
    def extract_actions(
        self,
        messages: List[Dict[str, Any]],
        context: str = "",
        priority_mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Extract action items from messages.
        
        Args:
            messages: List of message dictionaries
            context: Additional context for action extraction
            priority_mode: Priority calculation mode ('heuristic', 'llm', 'hybrid')
            
        Returns:
            Dict with 'actions' list
        """
        try:
            # Prepare messages in the format expected by LLM service
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    "id": msg.get("id"),
                    "source": msg.get("source"),
                    "subject": msg.get("subject"),
                    "body": msg.get("body"),
                    "timestamp": msg.get("timestamp"),
                    "sender": msg.get("sender")
                }
                formatted_messages.append(formatted_msg)
            
            payload = {
                "messages": formatted_messages,
                "context": context,
                "priority_mode": priority_mode
            }
            
            logger.info(f"Sending {len(messages)} messages to LLM service for action extraction")
            
            response = self.session.post(
                f"{self.base_url}/extract-actions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully extracted {len(result.get('actions', []))} actions")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("LLM service request timed out")
            raise Exception("LLM service timeout - request took too long")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM service error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error calling LLM service: {e}", exc_info=True)
            raise
    
    def ingest_unified_inbox(
        self,
        payload: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Ingest unified inbox data into LLM service memory (streaming).
        
        Args:
            payload: Unified inbox payload (priority_messages, unread_messages, upcoming_events)
            session_id: Optional session ID
            
        Returns:
            List of events from the streaming response
        """
        try:
            params = {}
            if session_id:
                params['session_id'] = session_id
            
            logger.info("Ingesting unified inbox data to LLM service")
            
            response = self.session.post(
                f"{self.base_url}/ingest",
                json=payload,
                params=params,
                timeout=120,
                stream=True
            )
            response.raise_for_status()
            
            # Parse NDJSON streaming response
            events = []
            for line in response.iter_lines():
                if line:
                    try:
                        event = requests.compat.json.loads(line)
                        events.append(event)
                        logger.debug(f"Ingestion event: {event.get('event')}")
                    except Exception as e:
                        logger.warning(f"Failed to parse event line: {e}")
            
            logger.info(f"Ingestion complete, received {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error ingesting to LLM service: {e}", exc_info=True)
            raise
    
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Summarize a single text string.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary string
        """
        try:
            payload = {
                "text": text,
                "max_length": max_length
            }
            
            response = self.session.post(
                f"{self.base_url}/summarize",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("summary", "")
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}", exc_info=True)
            raise
    
    def get_memory_status(self) -> Dict[str, Any]:
        """
        Get status of LLM service memory systems.
        
        Returns:
            Status dict with Qdrant and Redis information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/memory/status",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting memory status: {e}")
            return {"error": str(e)}

