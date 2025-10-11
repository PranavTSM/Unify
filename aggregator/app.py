"""
Aggregator Service - Unified Inbox Orchestrator
Fetches data from multiple sources (Google, Microsoft) and aggregates them.
"""
 
import logging
import os
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
 
from aggregator_service import AggregatorService, fetch_and_normalize_all
from utils.scoring import score_and_rank_messages, filter_by_importance
 
load_dotenv()
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# Initialize aggregator service
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
aggregator_service = AggregatorService(mcp_base_url=MCP_SERVER_URL)
 
app = FastAPI(
    title="Unified Inbox Aggregator",
    description="Aggregates emails, messages, and calendar events from Google and Microsoft sources",
    version="1.0.0"
)
 
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "aggregator"}
 
@app.get("/unified/inbox")
async def get_unified_inbox(
    max_per_source: int = Query(default=20, ge=1, le=100),
    days_ahead: int = Query(default=3, ge=1, le=30),
    priority_threshold: float = Query(default=0.6, ge=0.0, le=1.0),
    include_raw: bool = Query(default=False)
):
    """
    Fetches and aggregates messages from all sources.
   
    Steps:
    1. Fetches Gmail messages via MCP client
    2. Fetches Outlook messages via MS Graph
    3. Fetches Teams messages via MS Graph
    4. Normalizes all messages to common format
    5. Scores and ranks by importance
    6. Returns unified inbox with prioritized messages
   
    Args:
        max_per_source: Maximum messages to fetch per source (1-100)
        days_ahead: Days ahead for calendar events (1-30)
        priority_threshold: Minimum importance score (0.0-1.0)
        include_raw: Whether to include raw API responses
   
    Returns:
        Unified inbox with prioritized messages and events
    """
    try:
        logger.info(f"Fetching unified inbox: max_per_source={max_per_source}, "
                   f"priority_threshold={priority_threshold}")
       
        result = aggregator_service.get_unified_inbox(
            max_messages_per_source=max_per_source,
            days_ahead=days_ahead,
            priority_threshold=priority_threshold
        )
       
        return result
   
    except Exception as e:
        logger.error(f"Error fetching unified inbox: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch unified inbox: {str(e)}")
 
@app.get("/unified/calendar")
async def get_unified_calendar(
    days_ahead: int = Query(default=7, ge=1, le=30),
    include_raw: bool = Query(default=False)
):
    """
    Fetches and aggregates calendar events from all sources.
   
    Steps:
    1. Fetches Google Calendar events via MCP client
    2. Fetches Microsoft Calendar events via MS Graph (when implemented)
    3. Normalizes events to common format
    4. Sorts by start time
    5. Returns unified calendar view
   
    Args:
        days_ahead: Number of days ahead to fetch events (1-30)
        include_raw: Whether to include raw API responses
   
    Returns:
        Unified calendar with events from all sources
    """
    try:
        logger.info(f"Fetching unified calendar: days_ahead={days_ahead}")
       
        result = aggregator_service.aggregate_events(
            days_ahead=days_ahead,
            include_raw=include_raw
        )
       
        return result
   
    except Exception as e:
        logger.error(f"Error fetching unified calendar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch unified calendar: {str(e)}")
 
@app.get("/unified/messages")
async def get_all_messages(
    max_per_source: int = Query(default=50, ge=1, le=100),
    include_raw: bool = Query(default=False),
    min_score: Optional[float] = Query(default=None, ge=0.0, le=1.0)
):
    """
    Fetch all messages from all sources with normalization and scoring.
   
    Args:
        max_per_source: Maximum messages per source
        include_raw: Include raw API responses
        min_score: Filter by minimum importance score
   
    Returns:
        All normalized messages, optionally filtered by score
    """
    try:
        logger.info(f"Fetching all messages: max_per_source={max_per_source}")
       
        result = aggregator_service.aggregate_messages(
            max_per_source=max_per_source,
            include_raw=include_raw
        )
       
        # Apply score filter if specified
        if min_score is not None:
            result["normalized"] = filter_by_importance(result["normalized"], min_score)
            result["summary"]["filtered_count"] = len(result["normalized"])
            result["summary"]["min_score_filter"] = min_score
       
        return result
   
    except Exception as e:
        logger.error(f"Error fetching messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")
 
@app.get("/unified/all")
async def get_all_data(
    max_messages_per_source: int = Query(default=50, ge=1, le=100),
    days_ahead: int = Query(default=7, ge=1, le=30),
    include_raw: bool = Query(default=False)
):
    """
    Fetch everything - all messages and calendar events from all sources.
   
    Args:
        max_messages_per_source: Maximum messages per source
        days_ahead: Days ahead for calendar events
        include_raw: Include raw API responses
   
    Returns:
        Complete aggregated data (messages + events)
    """
    try:
        logger.info("Fetching all data (messages + events)")
       
        result = aggregator_service.aggregate_all(
            max_messages_per_source=max_messages_per_source,
            days_ahead=days_ahead,
            include_raw=include_raw
        )
       
        return result
   
    except Exception as e:
        logger.error(f"Error fetching all data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch all data: {str(e)}")
 
@app.post("/unified/inbox/summarize")
async def summarize_inbox(message_ids: List[str]):
    """
    Get AI summaries for specified messages.
   
    TODO: Implement LLM integration
    """
    logger.info(f"Summarizing messages: {message_ids}")
   
    return {
        "status": "not_implemented",
        "message": "LLM summarization is under development",
        "integration": "TODO: Connect to llm_service summarizer endpoint"
    }
 
@app.post("/unified/inbox/extract-actions")
async def extract_actions_from_messages(message_ids: List[str]):
    """
    Extract actionable items from messages.
   
    TODO: Implement LLM integration
    """
    logger.info(f"Extracting actions from messages: {message_ids}")
   
    return {
        "status": "not_implemented",
        "message": "LLM action extraction is under development",
        "integration": "TODO: Connect to llm_service action_extractor endpoint"
    }
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
 