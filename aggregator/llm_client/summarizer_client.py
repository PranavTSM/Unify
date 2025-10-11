"""
Client for LLM Service Summarization
"""

import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

LLM_SERVICE_URL = "http://localhost:8002"

def summarize_message(text: str, max_length: int = 150) -> Dict[str, Any]:
    """
    Get AI summary for a message.
    
    Args:
        text: Message text to summarize
        max_length: Maximum summary length
        
    Returns:
        Summary response from LLM service
    """
    try:
        response = requests.post(
            f"{LLM_SERVICE_URL}/summarize",
            json={"text": text, "max_length": max_length}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get summary from LLM service: {e}")
        return {"summary": "", "confidence": 0.0, "error": str(e)}

