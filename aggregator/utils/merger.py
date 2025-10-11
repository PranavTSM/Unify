"""
Message and Event Merger - Combines and deduplicates data from multiple sources
"""

import logging
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
from dateutil import parser

logger = logging.getLogger(__name__)

def _compute_message_signature(msg: Dict[str, Any]) -> str:
    """
    Compute a signature for message deduplication.
    
    Uses subject + timestamp + sender email to identify duplicates.
    """
    try:
        subject = (msg.get("subject") or "").strip().lower()
        timestamp = msg.get("timestamp", "")
        sender = msg.get("sender", {})
        sender_email = ""
        
        if isinstance(sender, dict):
            sender_email = (sender.get("email") or "").strip().lower()
        elif isinstance(sender, str):
            sender_email = sender.strip().lower()
            
        # Create signature from key fields
        return f"{subject}|{timestamp}|{sender_email}"
    except Exception as e:
        logger.warning(f"Error computing message signature: {e}")
        return ""

def _parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string to datetime object."""
    try:
        if ts:
            return parser.parse(ts)
    except Exception as e:
        logger.debug(f"Could not parse timestamp '{ts}': {e}")
    return datetime.min

def merge_unified_inbox(
    gmail_messages: List[Dict[str, Any]],
    outlook_messages: List[Dict[str, Any]],
    teams_messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge messages from all sources into a unified inbox.
    
    Features:
    1. Combines all messages
    2. Deduplicates based on message signatures (subject + timestamp + sender)
    3. Sorts by timestamp (most recent first)
    4. Preserves source information
    
    Args:
        gmail_messages: Normalized Gmail messages
        outlook_messages: Normalized Outlook messages
        teams_messages: Normalized Teams messages
        
    Returns:
        Merged and deduplicated list of messages
    """
    logger.info(
        f"Merging messages: Gmail={len(gmail_messages)}, "
        f"Outlook={len(outlook_messages)}, Teams={len(teams_messages)}"
    )
    
    # Combine all messages
    all_messages = gmail_messages + outlook_messages + teams_messages
    
    # Deduplicate based on message signatures
    seen_signatures: Set[str] = set()
    unique_messages: List[Dict[str, Any]] = []
    duplicates = 0
    
    for msg in all_messages:
        signature = _compute_message_signature(msg)
        
        # Skip if we've seen this message before (or if signature is empty)
        if signature and signature in seen_signatures:
            duplicates += 1
            logger.debug(f"Skipping duplicate message: {signature}")
            continue
            
        if signature:
            seen_signatures.add(signature)
        unique_messages.append(msg)
    
    # Sort by timestamp (most recent first)
    try:
        unique_messages.sort(
            key=lambda x: _parse_timestamp(x.get('timestamp', '')),
            reverse=True
        )
    except Exception as e:
        logger.error(f"Error sorting messages: {e}")
    
    logger.info(
        f"Merged {len(unique_messages)} unique messages "
        f"(removed {duplicates} duplicates)"
    )
    return unique_messages

def _compute_event_signature(event: Dict[str, Any]) -> str:
    """
    Compute a signature for event deduplication.
    
    Uses title + start time to identify duplicates across calendars.
    """
    try:
        title = (event.get("title") or "").strip().lower()
        start = event.get("start", "")
        
        # Create signature from key fields
        return f"{title}|{start}"
    except Exception as e:
        logger.warning(f"Error computing event signature: {e}")
        return ""

def merge_calendar_events(
    google_events: List[Dict[str, Any]],
    msft_events: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge calendar events from Google and Microsoft.
    
    Features:
    1. Combines all events
    2. Deduplicates identical events (same title + start time)
    3. Sorts by start time (earliest first)
    4. Marks conflicts
    
    Returns:
        Merged and deduplicated list of events
    """
    logger.info(
        f"Merging calendar events: Google={len(google_events)}, "
        f"Microsoft={len(msft_events)}"
    )
    
    # Combine all events
    all_events = google_events + msft_events
    
    # Deduplicate based on event signatures
    seen_signatures: Set[str] = set()
    unique_events: List[Dict[str, Any]] = []
    duplicates = 0
    
    for event in all_events:
        signature = _compute_event_signature(event)
        
        # Skip if we've seen this event before
        if signature and signature in seen_signatures:
            duplicates += 1
            logger.debug(f"Skipping duplicate event: {signature}")
            continue
            
        if signature:
            seen_signatures.add(signature)
        unique_events.append(event)
    
    # Sort by start time (earliest first)
    try:
        unique_events.sort(
            key=lambda x: _parse_timestamp(x.get('start', '')),
            reverse=False
        )
    except Exception as e:
        logger.error(f"Error sorting events: {e}")
    
    # Detect and mark conflicts
    conflicts = detect_event_conflicts(unique_events)
    if conflicts:
        logger.info(f"Detected {len(conflicts)} event conflicts")
        # Mark conflicting events
        conflict_ids = set()
        for conflict_group in conflicts:
            for event in conflict_group:
                conflict_ids.add(event.get('id'))
        
        for event in unique_events:
            if event.get('id') in conflict_ids:
                event['has_conflict'] = True
    
    logger.info(
        f"Merged {len(unique_events)} unique events "
        f"(removed {duplicates} duplicates)"
    )
    return unique_events

def detect_event_conflicts(events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Detect conflicting calendar events.
    
    Finds events with overlapping time slots.
    
    Args:
        events: List of calendar events (should be sorted by start time)
        
    Returns:
        List of conflict groups, where each group is a list of overlapping events
    """
    logger.info(f"Detecting conflicts in {len(events)} events")
    
    conflicts: List[List[Dict[str, Any]]] = []
    
    # Sort events by start time if not already sorted
    try:
        sorted_events = sorted(
            events,
            key=lambda x: _parse_timestamp(x.get('start', ''))
        )
    except Exception:
        sorted_events = events
    
    # Check each pair of events for overlap
    i = 0
    while i < len(sorted_events):
        current = sorted_events[i]
        current_start = _parse_timestamp(current.get('start', ''))
        current_end = _parse_timestamp(current.get('end', ''))
        
        if current_start == datetime.min or current_end == datetime.min:
            i += 1
            continue
        
        # Find all events that overlap with current
        conflict_group = [current]
        
        for j in range(i + 1, len(sorted_events)):
            other = sorted_events[j]
            other_start = _parse_timestamp(other.get('start', ''))
            other_end = _parse_timestamp(other.get('end', ''))
            
            if other_start == datetime.min or other_end == datetime.min:
                continue
            
            # Check if events overlap
            # Events overlap if: other_start < current_end AND current_start < other_end
            if other_start < current_end and current_start < other_end:
                conflict_group.append(other)
        
        # Only add as conflict if there are multiple overlapping events
        if len(conflict_group) > 1:
            conflicts.append(conflict_group)
        
        i += 1
    
    logger.info(f"Found {len(conflicts)} conflict groups")
    return conflicts

