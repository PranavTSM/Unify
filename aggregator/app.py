"""
Aggregator Service - Unified Inbox Orchestrator
Fetches data from multiple sources (Google, Microsoft) and aggregates them.
"""
 
import logging
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
 
from aggregator_service import AggregatorService, fetch_and_normalize_all
from utils.scoring import score_and_rank_messages, filter_by_importance
from llm_client import LLMServiceClient
from pydantic import BaseModel
from actions import MessageActionService, snooze_message, get_snoozed_messages, get_due_snoozed_messages, unsnooze_message
from datetime import datetime, timedelta
from db.mongo_client import init_mongo, mongo_health_check
from db.repository import MessageRepository, EventRepository

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB
logger.info("Initializing MongoDB connection...")
init_mongo()

# Initialize services
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8002")

aggregator_service = AggregatorService(mcp_base_url=MCP_SERVER_URL)
llm_client = LLMServiceClient(base_url=LLM_SERVICE_URL)
action_service = MessageActionService(mcp_base_url=MCP_SERVER_URL)

# Initialize repositories
message_repo = MessageRepository()
event_repo = EventRepository()
 
app = FastAPI(
    title="Unified Inbox Aggregator",
    description="Aggregates emails, messages, and calendar events from Google and Microsoft sources",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default)
        "http://localhost:5174",  # Vite dev server (alternate port)
        "http://localhost:5175",  # Vite dev server (alternate port)
        "http://localhost:3000",  # Production frontend
        "http://frontend:3000",   # Docker frontend
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.get("/health")
def health_check():
    """Health check endpoint with dependency status."""
    llm_healthy = llm_client.health_check()
    mongo_healthy = mongo_health_check()
    
    return {
        "status": "ok",
        "service": "aggregator",
        "dependencies": {
            "mcp_server": MCP_SERVER_URL,
            "llm_service": {
                "url": LLM_SERVICE_URL,
                "healthy": llm_healthy
            },
            "mongodb": {
                "healthy": mongo_healthy,
                "enabled": mongo_healthy
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
    max_per_source: int = Query(default=20, ge=1, le=100),
    include_raw: bool = Query(default=False),
    min_score: Optional[float] = Query(default=None, ge=0.0, le=1.0)
):
    """
    Fetch all messages from all sources with normalization and scoring.
   
    Args:
        max_per_source: Maximum messages per source (default: 20)
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
    max_messages_per_source: int = Query(default=20, ge=1, le=100),
    days_ahead: int = Query(default=7, ge=1, le=30),
    include_raw: bool = Query(default=False)
):
    """
    Fetch everything - all messages and calendar events from all sources.
   
    Args:
        max_messages_per_source: Maximum messages per source (default: 20)
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


# ==================== MESSAGE ACTIONS ====================

class MessageActionRequest(BaseModel):
    message_id: str
    source: str  # 'gmail', 'outlook', 'teams'
    action: str  # 'mark_read', 'mark_unread', 'star', 'unstar', 'archive', 'delete'


class BulkActionRequest(BaseModel):
    message_ids: List[str]
    source: str
    action: str


class SnoozeRequest(BaseModel):
    message_id: str
    snooze_until: Optional[str] = None  # ISO datetime
    snooze_minutes: Optional[int] = None  # Alternative: snooze for N minutes


@app.post("/messages/action")
async def perform_message_action(request: MessageActionRequest):
    """Perform action on a single message (mark read, star, archive, delete)."""
    try:
        success = False
        
        if request.action == "mark_read":
            success = action_service.mark_as_read(request.message_id, request.source)
        elif request.action == "mark_unread":
            success = action_service.mark_as_unread(request.message_id, request.source)
        elif request.action == "star":
            success = action_service.star_message(request.message_id, request.source, True)
        elif request.action == "unstar":
            success = action_service.star_message(request.message_id, request.source, False)
        elif request.action == "archive":
            success = action_service.archive_message(request.message_id, request.source)
        elif request.action == "delete":
            success = action_service.delete_message(request.message_id, request.source)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        if not success:
            raise HTTPException(status_code=500, detail="Action failed")
        
        return {"success": True, "message_id": request.message_id, "action": request.action}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/bulk-action")
async def perform_bulk_action(request: BulkActionRequest):
    """Perform action on multiple messages at once."""
    try:
        results = action_service.bulk_action(request.message_ids, request.action, request.source)
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error performing bulk action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/snooze")
async def snooze_message_endpoint(request: SnoozeRequest):
    """Snooze a message until a specific time."""
    try:
        if request.snooze_until:
            until = datetime.fromisoformat(request.snooze_until.replace('Z', '+00:00'))
        elif request.snooze_minutes:
            until = datetime.utcnow() + timedelta(minutes=request.snooze_minutes)
        else:
            # Default: 1 hour
            until = datetime.utcnow() + timedelta(hours=1)
        
        snooze_message(request.message_id, until)
        
        return {
            "success": True,
            "message_id": request.message_id,
            "snoozed_until": until.isoformat()
        }
    except Exception as e:
        logger.error(f"Error snoozing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/snoozed")
async def get_snoozed():
    """Get all snoozed messages."""
    try:
        snoozed = get_snoozed_messages()
        due = get_due_snoozed_messages()
        
        return {
            "snoozed": snoozed,
            "due_now": due,
            "total_snoozed": len(snoozed),
            "total_due": len(due)
        }
    except Exception as e:
        logger.error(f"Error getting snoozed messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/messages/snooze/{message_id}")
async def unsnooze(message_id: str):
    """Remove snooze from a message."""
    try:
        success = unsnooze_message(message_id)
        if not success:
            raise HTTPException(status_code=404, detail="Message not snoozed")
        
        return {"success": True, "message_id": message_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsnoozing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SEARCH & ANALYTICS ====================

@app.get("/search")
async def search_messages(
    query: str = Query(..., min_length=1),
    sources: Optional[List[str]] = Query(None),
    max_results: int = Query(20, ge=1, le=200)
):
    """
    Advanced search across all messages.
    Searches in subject, body, sender, and uses smart filtering.
    """
    try:
        # Fetch all messages
        result = aggregator_service.aggregate_messages(max_per_source=100, include_raw=False)
        messages = result.get("normalized", [])
        
        query_lower = query.lower()
        matched = []
        
        for msg in messages:
            # Filter by source if specified
            if sources and msg.get("category") not in sources:
                continue
            
            # Search in multiple fields (ensure all are strings)
            searchable_text = " ".join([
                str(msg.get("subject", "")),
                str(msg.get("body_preview", "")),
                str(msg.get("sender", "")),
                str(msg.get("category", ""))
            ]).lower()
            
            if query_lower in searchable_text:
                matched.append(msg)
        
        # Limit results
        matched = matched[:max_results]
        
        return {
            "query": query,
            "total_results": len(matched),
            "messages": matched
        }
    
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/stats")
async def get_analytics():
    """Get inbox analytics and statistics."""
    try:
        result = aggregator_service.aggregate_messages(max_per_source=100, include_raw=False)
        messages = result.get("normalized", [])
        
        # Calculate stats
        total = len(messages)
        by_source = {}
        by_priority = {"high": 0, "medium": 0, "low": 0}
        unread_count = 0
        
        for msg in messages:
            source = msg.get("category", "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            
            score = msg.get("importance_score", 0.5)
            if score >= 0.75:
                by_priority["high"] += 1
            elif score >= 0.5:
                by_priority["medium"] += 1
            else:
                by_priority["low"] += 1
            
            if not msg.get("is_read", True):
                unread_count += 1
        
        return {
            "total_messages": total,
            "unread_count": unread_count,
            "by_source": by_source,
            "by_priority": by_priority,
            "read_percentage": ((total - unread_count) / total * 100) if total > 0 else 0
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MONGODB PAGINATION ENDPOINTS ====================

@app.get("/messages/paginated")
async def get_messages_paginated(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(default=None, description="Filter by source (gmail, outlook, teams)"),
    is_read: Optional[bool] = Query(default=None, description="Filter by read status"),
    min_score: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Minimum importance score"),
    search: Optional[str] = Query(default=None, description="Search in subject/body/sender")
):
    """
    Get messages with pagination from MongoDB.
    Fast and efficient for large datasets.
    
    Features:
    - Pagination support
    - Filtering by source, read status, importance
    - Full-text search
    - Returns total count and page info
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page
        source: Filter by source (gmail/outlook/teams)
        is_read: Filter by read status
        min_score: Minimum importance score filter
        search: Search query for subject/body/sender
        
    Returns:
        Paginated messages with metadata
    """
    try:
        logger.info(f"📖 Paginated query: page={page}, size={page_size}, source={source}")
        
        result = message_repo.get_messages(
            page=page,
            page_size=page_size,
            source=source,
            is_read=is_read,
            min_score=min_score,
            search_query=search
        )
        
        return {
            "status": "success",
            "data": result["messages"],
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total_count": result["total_count"],
                "total_pages": result["total_pages"],
                "has_next": result.get("has_next", False),
                "has_prev": result.get("has_prev", False)
            },
            "filters": {
                "source": source,
                "is_read": is_read,
                "min_score": min_score,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"Error in paginated messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{message_id}")
async def get_message_by_id(message_id: str):
    """
    Get a single message by ID from MongoDB.
    
    Args:
        message_id: Unique message identifier
        
    Returns:
        Message details
    """
    try:
        message = message_repo.get_message_by_id(message_id)
        
        if not message:
            raise HTTPException(status_code=404, detail=f"Message {message_id} not found")
        
        return {
            "status": "success",
            "data": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/paginated")
async def get_events_paginated(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    start_after: Optional[str] = Query(default=None, description="Only events starting after this date (ISO)")
):
    """
    Get calendar events with pagination from MongoDB.
    
    Args:
        page: Page number
        page_size: Items per page
        source: Filter by source (google_calendar, microsoft_calendar)
        start_after: Only events after this date
        
    Returns:
        Paginated events
    """
    try:
        result = event_repo.get_events(
            page=page,
            page_size=page_size,
            source=source,
            start_after=start_after
        )
        
        return {
            "status": "success",
            "data": result["events"],
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total_count": result["total_count"],
                "total_pages": result["total_pages"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in paginated events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics/mongodb")
async def get_mongodb_statistics():
    """
    Get statistics from MongoDB storage.
    Shows total messages, breakdown by source, read status, etc.
    """
    try:
        stats = message_repo.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "mongodb_enabled": mongo_health_check()
        }
        
    except Exception as e:
        logger.error(f"Error getting MongoDB statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
 