"""
Message Importance Scoring and Ranking
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def score_message_importance(message: Dict[str, Any]) -> float:
    """
    Calculate importance score for a message.
    
    TODO: Implement scoring algorithm based on:
    - Sender importance (VIP, frequent contacts, domain)
    - Keywords and subject analysis
    - Urgency indicators (URGENT, ASAP, etc.)
    - Time sensitivity
    - Attachments
    - Thread activity
    - User's past interaction patterns
    
    Returns:
        Score between 0.0 and 1.0 (higher = more important)
    """
    logger.debug(f"Scoring message: {message.get('id')}")
    
    # TODO: Implement actual scoring logic
    score = 0.5  # Default score
    
    # Example factors:
    # if "URGENT" in message.get("subject", "").upper():
    #     score += 0.3
    # if message.get("sender", {}).get("email") in VIP_LIST:
    #     score += 0.2
    
    return min(1.0, max(0.0, score))

def score_and_rank_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score all messages and rank them by importance.
    
    Args:
        messages: List of normalized messages
        
    Returns:
        Messages sorted by importance score (descending)
    """
    logger.info(f"Scoring and ranking {len(messages)} messages")
    
    # Add importance scores to messages
    for message in messages:
        message["importance_score"] = score_message_importance(message)
    
    # Sort by score (highest first), then by timestamp (most recent first)
    ranked_messages = sorted(
        messages,
        key=lambda m: (m.get("importance_score", 0), m.get("timestamp", "")),
        reverse=True
    )
    
    logger.info(f"Ranked {len(ranked_messages)} messages")
    return ranked_messages

def filter_by_importance(
    messages: List[Dict[str, Any]],
    min_score: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Filter messages by minimum importance score.
    
    Args:
        messages: List of scored messages
        min_score: Minimum importance score threshold
        
    Returns:
        Filtered list of messages
    """
    filtered = [m for m in messages if m.get("importance_score", 0) >= min_score]
    logger.info(f"Filtered {len(messages)} messages to {len(filtered)} (min_score={min_score})")
    return filtered

