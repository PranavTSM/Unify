"""
Aggregator Service - Main service that fetches, normalizes, and aggregates data
"""
 
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
 
from fetchers import UnifiedAggregator
from utils.normalizer import (
    normalize_gmail_message,
    normalize_outlook_message,
    normalize_teams_message,
    normalize_calendar_event
)
from utils.scoring import calculate_importance_score
from utils.merger import merge_unified_inbox, merge_calendar_events
 
logger = logging.getLogger(__name__)
 
 
class AggregatorService:
    """
    Main aggregator service that coordinates fetching and normalization.
    """
   
    def __init__(self, mcp_base_url: str = "http://localhost:8000"):
        self.aggregator = UnifiedAggregator(mcp_base_url)
        logger.info(f"Aggregator service initialized with MCP URL: {mcp_base_url}")
   
    def aggregate_messages(self, max_per_source: int = 50,
                          include_raw: bool = False) -> Dict[str, Any]:
        """
        Aggregate messages from all sources (Gmail, Outlook, Teams).
       
        Args:
            max_per_source: Maximum messages to fetch per source
            include_raw: Whether to include raw message data in response
           
        Returns:
            Dictionary containing:
            - normalized: List of normalized messages
            - by_source: Messages grouped by source
            - summary: Aggregation summary
        """
        logger.info(f"Starting message aggregation (max_per_source={max_per_source})")
       
        # Fetch raw messages
        raw_messages = self.aggregator.fetch_all_messages(max_per_source)
       
        # Normalize messages
        normalized_by_source = {}
       
        for source, messages in raw_messages.items():
            logger.info(f"Normalizing {len(messages)} messages from {source}")
            normalized = []
           
            for msg in messages:
                try:
                    if source == "gmail":
                        norm_msg = normalize_gmail_message(msg)
                    elif source == "outlook":
                        norm_msg = normalize_outlook_message(msg)
                    elif source == "teams":
                        norm_msg = normalize_teams_message(msg)
                    else:
                        continue
                   
                    # Calculate importance score
                    if "error" not in norm_msg:
                        norm_msg["importance_score"] = calculate_importance_score(norm_msg)
                   
                    # Optionally include raw data
                    if include_raw:
                        norm_msg["_raw"] = msg
                   
                    normalized.append(norm_msg)
                   
                except Exception as e:
                    logger.error(f"Error normalizing {source} message: {e}")
           
            normalized_by_source[source] = normalized
       
        # Merge and deduplicate messages using merger
        normalized_messages = merge_unified_inbox(
            gmail_messages=normalized_by_source.get("gmail", []),
            outlook_messages=normalized_by_source.get("outlook", []),
            teams_messages=normalized_by_source.get("teams", [])
        )
       
        # Generate summary
        summary = {
            "total_messages": len(normalized_messages),
            "by_source": {
                source: len(msgs)
                for source, msgs in normalized_by_source.items()
            },
            "aggregated_at": datetime.utcnow().isoformat(),
            "errors": sum(1 for msg in normalized_messages if "error" in msg)
        }
       
        logger.info(f"Aggregation complete: {summary['total_messages']} total messages")
       
        return {
            "normalized": normalized_messages,
            "by_source": normalized_by_source,
            "summary": summary
        }
   
    def aggregate_events(self, days_ahead: int = 7,
                        include_raw: bool = False) -> Dict[str, Any]:
        """
        Aggregate calendar events from all sources.
       
        Args:
            days_ahead: Number of days ahead to fetch events
            include_raw: Whether to include raw event data
           
        Returns:
            Dictionary containing:
            - normalized: List of normalized events
            - by_source: Events grouped by source
            - summary: Aggregation summary
        """
        logger.info(f"Starting event aggregation (days_ahead={days_ahead})")
       
        # Fetch raw events
        raw_events = self.aggregator.fetch_all_events(days_ahead)
       
        # Normalize events
        normalized_by_source = {}
       
        for source, events in raw_events.items():
            logger.info(f"Normalizing {len(events)} events from {source}")
            normalized = []
           
            for event in events:
                try:
                    norm_event = normalize_calendar_event(event, source)
                   
                    # Optionally include raw data
                    if include_raw:
                        norm_event["_raw"] = event
                   
                    normalized.append(norm_event)
                   
                except Exception as e:
                    logger.error(f"Error normalizing {source} event: {e}")
           
            normalized_by_source[source] = normalized
       
        # Merge and deduplicate events using merger
        normalized_events = merge_calendar_events(
            google_events=normalized_by_source.get("google_calendar", []),
            msft_events=normalized_by_source.get("microsoft_calendar", [])
        )
       
        # Generate summary
        summary = {
            "total_events": len(normalized_events),
            "by_source": {
                source: len(events)
                for source, events in normalized_by_source.items()
            },
            "aggregated_at": datetime.utcnow().isoformat(),
            "errors": sum(1 for event in normalized_events if "error" in event)
        }
       
        logger.info(f"Event aggregation complete: {summary['total_events']} total events")
       
        return {
            "normalized": normalized_events,
            "by_source": normalized_by_source,
            "summary": summary
        }
   
    def aggregate_all(self, max_messages_per_source: int = 50,
                     days_ahead: int = 7,
                     include_raw: bool = False) -> Dict[str, Any]:
        """
        Aggregate both messages and events from all sources.
       
        Returns:
            Dictionary containing both messages and events aggregations
        """
        logger.info("Starting full aggregation (messages + events)")
       
        messages_result = self.aggregate_messages(
            max_per_source=max_messages_per_source,
            include_raw=include_raw
        )
       
        events_result = self.aggregate_events(
            days_ahead=days_ahead,
            include_raw=include_raw
        )
       
        return {
            "messages": messages_result,
            "events": events_result,
            "aggregated_at": datetime.utcnow().isoformat()
        }
   
    def get_unified_inbox(self, max_messages_per_source: int = 20,
                         days_ahead: int = 3,
                         priority_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Get a unified inbox view with prioritized messages and upcoming events.
       
        Args:
            max_messages_per_source: Max messages per source
            days_ahead: Days ahead for events
            priority_threshold: Minimum importance score to include
           
        Returns:
            Unified inbox with prioritized content
        """
        logger.info("Generating unified inbox view")
       
        # Get messages
        messages_result = self.aggregate_messages(max_per_source=max_messages_per_source)
       
        # Filter by importance
        priority_messages = [
            msg for msg in messages_result["normalized"]
            if msg.get("importance_score", 0) >= priority_threshold
        ]
       
        # Get upcoming events
        events_result = self.aggregate_events(days_ahead=days_ahead)
        upcoming_events = events_result["normalized"][:10]  # Top 10 upcoming
       
        # Combine unread messages
        unread_messages = [
            msg for msg in messages_result["normalized"]
            if not msg.get("is_read", True)
        ]
       
        return {
            "priority_messages": priority_messages[:20],  # Top 20
            "unread_messages": unread_messages[:50],  # Top 50 unread
            "upcoming_events": upcoming_events,
            "summary": {
                "total_messages": messages_result["summary"]["total_messages"],
                "priority_count": len(priority_messages),
                "unread_count": len(unread_messages),
                "upcoming_events_count": len(upcoming_events),
                "by_source": messages_result["summary"]["by_source"]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
 
 
# Convenience function for quick access
def fetch_and_normalize_all(mcp_url: str = "http://localhost:8000",
                            max_per_source: int = 50) -> Dict[str, Any]:
    """
    Convenience function to fetch and normalize all data.
   
    Args:
        mcp_url: MCP server base URL
        max_per_source: Maximum items per source
       
    Returns:
        Aggregated and normalized data
    """
    service = AggregatorService(mcp_url)
    return service.aggregate_all(max_messages_per_source=max_per_source)