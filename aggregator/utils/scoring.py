"""
Message Importance Scoring and Ranking
"""
 
import logging
from typing import List, Dict, Any
 
logger = logging.getLogger(__name__)
 
def calculate_importance_score(message: Dict[str, Any]) -> float:
    """
    Calculate importance score for a message using multiple heuristics.
   
    Scoring factors:
    - Sender importance (VIP, domain, direct vs CC)
    - Keywords and urgency indicators
    - Attachments
    - Message length
    - Source importance
   
    Returns:
        Score between 0.0 and 1.0 (higher = more important)
    """
    score = 0.3  # Base score
   
    subject = message.get("subject", "").upper()
    body = message.get("body", "").upper()
    sender_email = message.get("sender", {}).get("email", "").lower()
   
    # Urgency keywords
    urgency_keywords = ["URGENT", "ASAP", "IMMEDIATE", "PRIORITY", "IMPORTANT", "CRITICAL", "ACTION REQUIRED"]
    for keyword in urgency_keywords:
        if keyword in subject:
            score += 0.25
            break
        elif keyword in body:
            score += 0.15
            break
   
    # Has attachments
    if message.get("attachments") and len(message.get("attachments", [])) > 0:
        score += 0.1
   
    # Sender domain importance (adjust based on your needs)
    important_domains = ["ceo", "president", "director", "manager", "hr"]
    for domain in important_domains:
        if domain in sender_email:
            score += 0.15
            break
   
    # Direct message (in TO field vs CC)
    recipients = message.get("recipients", [])
    if len(recipients) == 1:  # Direct message
        score += 0.1
    elif len(recipients) > 10:  # Mass email
        score -= 0.1
   
    # Unread messages get slight boost
    if not message.get("is_read", True):
        score += 0.05
   
    # Source-based adjustments
    source = message.get("source", "")
    if source == "teams":  # Teams messages often more immediate
        score += 0.1
   
    # Message length (very short or very long might be less important)
    body_len = len(message.get("body", ""))
    if 100 < body_len < 2000:  # Sweet spot
        score += 0.05
   
    # Normalize score to 0-1 range
    return min(1.0, max(0.0, score))
 
def score_message_importance(message: Dict[str, Any]) -> float:
    """
    Calculate importance score for a message.
    Alias for calculate_importance_score for backward compatibility.
    """
    return calculate_importance_score(message)
 
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
 