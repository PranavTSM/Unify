"""
Client for LLM Service Action Extraction
"""

import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

LLM_SERVICE_URL = "http://localhost:8002"

def extract_actions_from_text(text: str, context: str = "") -> List[Dict[str, Any]]:
    """
    Extract action items from text using LLM service.
    
    Args:
        text: Text to analyze
        context: Additional context
        
    Returns:
        List of extracted action items
    """
    try:
        response = requests.post(
            f"{LLM_SERVICE_URL}/extract-actions",
            json={"text": text, "context": context}
        )
        response.raise_for_status()
        return response.json().get("actions", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to extract actions from LLM service: {e}")
        return []

