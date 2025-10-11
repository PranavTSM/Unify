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
from llm_client import LLMServiceClient
from pydantic import BaseModel
 
load_dotenv()
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# Initialize services
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8002")

aggregator_service = AggregatorService(mcp_base_url=MCP_SERVER_URL)
llm_client = LLMServiceClient(base_url=LLM_SERVICE_URL)
 
app = FastAPI(
    title="Unified Inbox Aggregator",
    description="Aggregates emails, messages, and calendar events from Google and Microsoft sources",
    version="1.0.0"
)
 
@app.get("/health")
def health_check():
    """Health check endpoint with dependency status."""
    llm_healthy = llm_client.health_check()
    
    return {
        "status": "ok",
        "service": "aggregator",
        "dependencies": {
            "mcp_server": MCP_SERVER_URL,
            "llm_service": {
                "url": LLM_SERVICE_URL,
                "healthy": llm_healthy
            }
        }
    }
 
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
 
class SummarizeRequest(BaseModel):
    """Request model for message summarization."""
    message_ids: Optional[List[str]] = None
    mode: str = "executive"  # 'executive', 'bullets', 'paragraph'
    max_words: int = 200
    include_messages: bool = False
    store_in_memory: bool = False
    session_id: Optional[str] = None


@app.post("/unified/inbox/summarize")
async def summarize_inbox(request: SummarizeRequest):
    """
    Get AI summaries for messages.
    
    Options:
    - Summarize specific messages by ID
    - Summarize all recent priority messages (if no IDs provided)
    
    Args:
        request: SummarizeRequest with options
        
    Returns:
        Summary with message context and AI-generated summary
    """
    try:
        logger.info(f"Summarizing messages: mode={request.mode}, IDs={request.message_ids}")
        
        # Check LLM service health
        if not llm_client.health_check():
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available"
            )
        
        messages_to_summarize = []
        
        # If specific message IDs provided, fetch those messages
        if request.message_ids:
            # Fetch all messages first
            all_messages_result = aggregator_service.aggregate_messages(
                max_per_source=100,
                include_raw=False
            )
            all_messages = all_messages_result["normalized"]
            
            # Filter to requested IDs
            message_id_set = set(request.message_ids)
            messages_to_summarize = [
                msg for msg in all_messages
                if msg.get("id") in message_id_set
            ]
            
            if not messages_to_summarize:
                raise HTTPException(
                    status_code=404,
                    detail=f"No messages found with provided IDs"
                )
                
            logger.info(f"Found {len(messages_to_summarize)} messages matching IDs")
        else:
            # No IDs provided - summarize recent priority messages
            logger.info("No message IDs provided, fetching priority messages")
            unified_inbox = aggregator_service.get_unified_inbox(
                max_messages_per_source=20,
                days_ahead=3,
                priority_threshold=0.5
            )
            messages_to_summarize = unified_inbox.get("priority_messages", [])[:10]
            
            if not messages_to_summarize:
                return {
                    "status": "success",
                    "summary": "No priority messages to summarize",
                    "message_count": 0,
                    "bullets": []
                }
        
        # Call LLM service for summarization
        logger.info(f"Sending {len(messages_to_summarize)} messages to LLM service")
        
        summary_result = llm_client.summarize_batch(
            messages=messages_to_summarize,
            mode=request.mode,
            max_words=request.max_words,
            store=request.store_in_memory,
            session_id=request.session_id
        )
        
        # Build response
        response = {
            "status": "success",
            "summary": summary_result.get("summary", ""),
            "bullets": summary_result.get("bullets", []),
            "message_count": len(messages_to_summarize),
            "mode": request.mode,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Optionally include message details
        if request.include_messages:
            response["messages"] = [
                {
                    "id": msg.get("id"),
                    "source": msg.get("source"),
                    "subject": msg.get("subject"),
                    "sender": msg.get("sender"),
                    "timestamp": msg.get("timestamp")
                }
                for msg in messages_to_summarize
            ]
        
        logger.info("Successfully generated summary")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize messages: {str(e)}"
        )
 
class ExtractActionsRequest(BaseModel):
    """Request model for action extraction."""
    message_ids: Optional[List[str]] = None
    context: str = ""
    priority_mode: str = "hybrid"  # 'heuristic', 'llm', 'hybrid'
    include_messages: bool = False
    min_priority: Optional[str] = None  # 'low', 'medium', 'high'


@app.post("/unified/inbox/extract-actions")
async def extract_actions_from_messages(request: ExtractActionsRequest):
    """
    Extract actionable items from messages using AI.
    
    Options:
    - Extract actions from specific messages by ID
    - Extract actions from all recent unread messages (if no IDs provided)
    
    Args:
        request: ExtractActionsRequest with options
        
    Returns:
        List of extracted action items with priority, due dates, assignees, etc.
    """
    try:
        logger.info(f"Extracting actions: mode={request.priority_mode}, IDs={request.message_ids}")
        
        # Check LLM service health
        if not llm_client.health_check():
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available"
            )
        
        messages_to_analyze = []
        
        # If specific message IDs provided, fetch those messages
        if request.message_ids:
            # Fetch all messages first
            all_messages_result = aggregator_service.aggregate_messages(
                max_per_source=100,
                include_raw=False
            )
            all_messages = all_messages_result["normalized"]
            
            # Filter to requested IDs
            message_id_set = set(request.message_ids)
            messages_to_analyze = [
                msg for msg in all_messages
                if msg.get("id") in message_id_set
            ]
            
            if not messages_to_analyze:
                raise HTTPException(
                    status_code=404,
                    detail=f"No messages found with provided IDs"
                )
                
            logger.info(f"Found {len(messages_to_analyze)} messages matching IDs")
        else:
            # No IDs provided - analyze recent unread messages
            logger.info("No message IDs provided, fetching unread messages")
            unified_inbox = aggregator_service.get_unified_inbox(
                max_messages_per_source=30,
                days_ahead=3,
                priority_threshold=0.4
            )
            messages_to_analyze = unified_inbox.get("unread_messages", [])[:20]
            
            if not messages_to_analyze:
                return {
                    "status": "success",
                    "actions": [],
                    "message_count": 0,
                    "summary": {
                        "total_actions": 0,
                        "by_priority": {"high": 0, "medium": 0, "low": 0},
                        "by_category": {}
                    }
                }
        
        # Call LLM service for action extraction
        logger.info(f"Sending {len(messages_to_analyze)} messages to LLM service for action extraction")
        
        actions_result = llm_client.extract_actions(
            messages=messages_to_analyze,
            context=request.context,
            priority_mode=request.priority_mode
        )
        
        actions = actions_result.get("actions", [])
        
        # Filter by minimum priority if specified
        if request.min_priority:
            priority_order = {"low": 0, "medium": 1, "high": 2}
            min_level = priority_order.get(request.min_priority.lower(), 0)
            
            actions = [
                action for action in actions
                if priority_order.get(action.get("priority", "low").lower(), 0) >= min_level
            ]
            logger.info(f"Filtered to {len(actions)} actions with priority >= {request.min_priority}")
        
        # Generate summary statistics
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        category_counts = {}
        
        for action in actions:
            priority = action.get("priority", "medium").lower()
            if priority in priority_counts:
                priority_counts[priority] += 1
            
            category = action.get("category", "task")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Build response
        response = {
            "status": "success",
            "actions": actions,
            "message_count": len(messages_to_analyze),
            "summary": {
                "total_actions": len(actions),
                "by_priority": priority_counts,
                "by_category": category_counts,
                "priority_mode": request.priority_mode
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Optionally include message details
        if request.include_messages:
            response["messages"] = [
                {
                    "id": msg.get("id"),
                    "source": msg.get("source"),
                    "subject": msg.get("subject"),
                    "sender": msg.get("sender"),
                    "timestamp": msg.get("timestamp")
                }
                for msg in messages_to_analyze
            ]
        
        logger.info(f"Successfully extracted {len(actions)} actions")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting actions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract actions: {str(e)}"
        )
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
 