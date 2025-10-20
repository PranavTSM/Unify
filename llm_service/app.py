"""
LLM Service - OpenAI + Qdrant + LangChain Redis Memory
Clean implementation following reference architecture.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import json
from datetime import datetime
from uuid import uuid4

from fastapi.middleware.cors import CORSMiddleware

# Load environment variables BEFORE importing memory modules
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    from llm_service.summarizer import generate_summary
    from llm_service.action_extractor import extract_action_items
    from llm_service.memory.retriever import get_unified_retriever
except ModuleNotFoundError:
    # Running from llm_service directory
    from summarizer import generate_summary
    from action_extractor import extract_action_items
    from memory.retriever import get_unified_retriever
try:
    from llm_service.utils.scoring import heuristic_priority_score, label_from_score
except Exception:
    heuristic_priority_score = None
    label_from_score = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Service - OpenAI + Qdrant + Redis (LangChain)",
    description="AI-powered text analysis with semantic memory and conversation tracking",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] if you want to allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize unified memory system on startup
retriever = None

@app.on_event("startup")
async def startup_event():
    """Initialize memory systems on startup."""
    global retriever
    try:
        retriever = get_unified_retriever()
        logger.info("✅ Unified memory system initialized (Qdrant + Redis via LangChain)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize memory system: {e}", exc_info=True)
        logger.warning("Service will run without memory features")


# ==================== Request/Response Models ====================

class StoreRequest(BaseModel):
    """Request model for storing messages in memory."""
    id: str
    text: str
    metadata: Dict[str, Any] = {}
    session_id: Optional[str] = None
    sender: str = "unknown"
    role: str = "user"
    entities: Optional[List[str]] = None

class QueryRequest(BaseModel):
    """Request model for querying similar content."""
    query: str
    top_k: int = 5
    session_id: Optional[str] = None


class AggregatedPayload(BaseModel):
    """Payload from Aggregator service with unified data.

    This model intentionally keeps flexible typing to accept the exact
    aggregator JSON without strict nested schemas.
    """
    priority_messages: List[Dict[str, Any]] = []
    unread_messages: List[Dict[str, Any]] = []
    upcoming_events: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}


# ==================== Batch Models & Helpers ====================

class UnifiedSender(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class InputMessage(BaseModel):
    id: Optional[str] = None
    source: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[Any] = None  # aggregator sends string; allow Any for safety
    timestamp: Optional[str] = None
    sender: Optional[UnifiedSender] = None

class SummarizeBatchRequest(BaseModel):
    messages: List[InputMessage]
    mode: Literal["executive", "bullets", "paragraph"] = "executive"
    max_words: int = 200
    store: bool = False
    session_id: Optional[str] = None

class SummarizeBatchResponse(BaseModel):
    summary: str
    bullets: List[str] = []
    token_usage: Dict[str, Any] = {}

class ActionItemModel(BaseModel):
    description: str
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    category: Optional[str] = "task"
    priority: Literal["low", "medium", "high"] = "medium"
    priority_score: float = 0.5
    source_id: Optional[str] = None

def _plain_text(val: Optional[Any]) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return val.strip()
    try:
        # handle dict-like bodies {content, contentType}
        content = val.get("content") if isinstance(val, dict) else str(val)
        return str(content or "").strip()
    except Exception:
        return str(val).strip()

def flatten_messages(messages: List[InputMessage]) -> str:
    try:
        ordered = sorted(messages, key=lambda m: (m.timestamp or ""))
    except Exception:
        ordered = messages
    lines: List[str] = []
    for m in ordered:
        prefix = f"[{(m.source or '').strip()}]" if m.source else ""
        sender = (m.sender.name or m.sender.email) if m.sender else None
        who = f" {sender}:" if sender else ""
        subj = (m.subject or "").strip()
        body = _plain_text(m.body)
        if subj and body:
            lines.append(f"{prefix}{who} {subj} — {body}")
        elif body:
            lines.append(f"{prefix}{who} {body}")
        elif subj:
            lines.append(f"{prefix}{who} {subj}")
    return "\n".join([ln.strip() for ln in lines if ln and ln.strip()])


# ==================== Core Endpoints ====================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "llm_service",
        "memory": "qdrant + redis (langchain)"
    }


@app.post("/store")
async def store(req: StoreRequest):
    """
    Store a message in the unified memory system.
    
    Process:
    1. Summarize the text using LangChain + OpenAI
    2. Store embedding in Qdrant (for semantic search)
    3. Add to Redis chat history (if session_id provided)
    
    Args:
        req: StoreRequest with message details
        
    Returns:
        Status and summary
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        # Validate input
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Empty text cannot be stored")
        
        # Generate summary using LangChain
        summary = generate_summary(req.text)
        
        # Store in unified memory (Qdrant + Redis)
        success = retriever.store_message_with_context(
            message_id=req.id,
            text=summary,  # Store summary for better semantic search
            sender=req.sender,
            session_id=req.session_id,
            role=req.role,
            entities=req.entities,
            metadata=req.metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store in memory systems")
        
        stored_in = ["qdrant", "redis"] if req.session_id else ["qdrant"]
        
        return {
            "status": "success",
            "id": req.id,
            "summary": summary,
            "stored_in": stored_in,
            "metadata": req.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(req: QueryRequest):
    """
    Query similar content using semantic search.
    
    Uses Qdrant vector similarity search powered by LangChain + OpenAI embeddings.
    
    Args:
        req: QueryRequest with query text
        
    Returns:
        List of similar documents with scores
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        if not req.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = retriever.embeddings.query_similar(
            query_text=req.query,
            top_k=req.top_k
        )
        
        return {
            "query": req.query,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying similar content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_class=StreamingResponse)
async def ingest_aggregated(
    payload: AggregatedPayload,
    session_id: Optional[str] = Query(None, description="Optional session id to attach messages to"),
):
    """
    Ingest unified JSON from the Aggregator, summarize, embed, and stream progress.

    - Reads `priority_messages`, `unread_messages`, and `upcoming_events`
    - Summarizes text via LangChain
    - Stores embeddings in Qdrant and chat history in Redis
    - Streams NDJSON progress lines
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")

    def normalize_message(msg: Dict[str, Any]) -> Dict[str, Any]:
        sender = msg.get("sender") or {}
        sender_email = sender.get("email") if isinstance(sender, dict) else None
        subject = msg.get("subject", "")
        body = msg.get("body", "")
        text = f"{subject}\n\n{body}".strip() if subject else body
        metadata = {
            "source": msg.get("source"),
            "labels": msg.get("labels", []),
            "attachments": msg.get("attachments", []),
            "importance_score": msg.get("importance_score"),
            "is_read": msg.get("is_read"),
            "timestamp": msg.get("timestamp"),
        }
        return {
            "id": msg.get("id") or f"msg_{uuid4().hex}",
            "text": text,
            "sender": sender_email or "unknown",
            "role": "user",
            "metadata": metadata,
        }

    def normalize_event(ev: Dict[str, Any]) -> Dict[str, Any]:
        title = ev.get("title", "Event")
        start = ev.get("start")
        end = ev.get("end")
        location = ev.get("location")
        organizer = ev.get("organizer") or {}
        description = ev.get("description", "")
        attendees = ev.get("attendees", [])
        # Create a concise textual form of the event for embedding
        parts = [
            f"Title: {title}",
            f"Start: {start}",
            f"End: {end}",
        ]
        if location:
            parts.append(f"Location: {location}")
        if description:
            parts.append(f"Details: {description}")
        if attendees:
            parts.append(f"Attendees: {len(attendees)}")
        text = "\n".join([p for p in parts if p])
        metadata = {
            "source": ev.get("source", "calendar"),
            "organizer": organizer,
            "attendees": attendees,
            "timestamp": start,
            "type": "calendar_event",
        }
        return {
            "id": ev.get("id") or f"event_{datetime.utcnow().timestamp()}",
            "text": text,
            "sender": organizer.get("email") if isinstance(organizer, dict) else "unknown",
            "role": "user",
            "metadata": metadata,
        }

    def event_stream():
        try:
            # Flatten inputs
            msg_items = list(payload.priority_messages or []) + list(payload.unread_messages or [])
            event_items = list(payload.upcoming_events or [])
            total = len(msg_items) + len(event_items)
            started_at = datetime.utcnow().isoformat()
            yield json.dumps({
                "event": "start",
                "total_items": total,
                "started_at": started_at
            }) + "\n"

            # Process messages
            for raw in msg_items:
                item = normalize_message(raw)
                try:
                    summary = generate_summary(item["text"], max_length=220)
                    ok = retriever.store_message_with_context(
                        message_id=item["id"],
                        text=summary,
                        sender=item["sender"],
                        session_id=session_id,
                        role=item["role"],
                        entities=None,
                        metadata=item["metadata"],
                    )
                    yield json.dumps({
                        "event": "stored",
                        "kind": "message",
                        "id": item["id"],
                        "stored": bool(ok)
                    }) + "\n"
                except Exception as e:  # continue on failure, but report
                    yield json.dumps({
                        "event": "error",
                        "kind": "message",
                        "id": item.get("id"),
                        "error": str(e)
                    }) + "\n"

            # Process events
            for raw in event_items:
                item = normalize_event(raw)
                try:
                    summary = generate_summary(item["text"], max_length=220)
                    ok = retriever.store_message_with_context(
                        message_id=item["id"],
                        text=summary,
                        sender=item["sender"],
                        session_id=session_id,
                        role=item["role"],
                        entities=None,
                        metadata=item["metadata"],
                    )
                    yield json.dumps({
                        "event": "stored",
                        "kind": "event",
                        "id": item["id"],
                        "stored": bool(ok)
                    }) + "\n"
                except Exception as e:
                    yield json.dumps({
                        "event": "error",
                        "kind": "event",
                        "id": item.get("id"),
                        "error": str(e)
                    }) + "\n"

            yield json.dumps({
                "event": "complete",
                "completed_at": datetime.utcnow().isoformat()
            }) + "\n"
        except Exception as e:
            yield json.dumps({"event": "fatal", "error": str(e)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

@app.get("/context")
async def get_context(
    query: str = Query(..., description="Query text"),
    session_id: str = Query(..., description="Session ID for conversation context"),
    top_k: int = Query(5, description="Number of semantic search results"),
    include_conversation: bool = Query(True, description="Include chat history")
):
    """
    Get unified context for a query.
    
    Combines:
    - Qdrant: Semantically relevant information
    - Redis: Recent conversation history (via LangChain)
    
    This is the main endpoint for chatbot context retrieval.
    
    Args:
        query: User query
        session_id: Session ID
        top_k: Number of semantic search results
        include_conversation: Whether to include chat history
        
    Returns:
        Combined context from all memory systems
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        context_data = retriever.get_context_for_query(
            query=query,
            session_id=session_id,
            top_k=top_k,
            include_conversation=include_conversation
        )
        
        return context_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/status")
async def get_memory_status():
    """
    Get status of memory systems (Qdrant + Redis).
    
    Returns:
        Status information for each system
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        status = retriever.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error getting memory status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memory/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session from Redis.
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        Success status
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Memory system not initialized")
    
    try:
        success = retriever.clear_session(session_id)
        
        if success:
            return {"status": "success", "session_id": session_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear session")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Legacy/Additional Endpoints ====================

class SummarizeRequest(BaseModel):
    """Request model for standalone summarization."""
    text: str
    max_length: int = 150

class SummarizeResponse(BaseModel):
    """Response model for summarization."""
    summary: str
    confidence: float = 0.85

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Generate a concise summary using LangChain + OpenAI.
    
    Args:
        request: SummarizeRequest with text and max_length
        
    Returns:
        Summary and confidence score
    """
    logger.info(f"Summarizing text of length {len(request.text)}")
    
    try:
        summary = generate_summary(request.text, max_length=request.max_length)
        return SummarizeResponse(summary=summary, confidence=0.85)
    except Exception as e:
        logger.error(f"Summarization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== New Endpoints ====================

@app.post("/summarize-batch", response_model=SummarizeBatchResponse)
async def summarize_batch(request: SummarizeBatchRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages[] is required")
    text = flatten_messages(request.messages)
    if not text.strip():
        return SummarizeBatchResponse(summary="", bullets=[], token_usage={})
    try:
        # reuse existing generate_summary for simplicity
        summary = generate_summary(text, max_length=request.max_words)
        bullets: List[str] = []
        if request.mode != "paragraph":
            try:
                # quick bulletization via a small heuristic split
                for line in summary.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    bullets.append(line)
                bullets = bullets[:8]
            except Exception:
                bullets = []
        return SummarizeBatchResponse(summary=summary, bullets=bullets, token_usage={})
    except Exception as e:
        logger.error(f"Batch summarize error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class CalendarDescribeRequest(BaseModel):
    title: str
    context: Optional[str] = None
    participants: Optional[List[str]] = None
    tone: Literal["concise", "detailed", "brief"] = "concise"
    duration_min: Optional[int] = 30

class CalendarDescribeResponse(BaseModel):
    description: str
    agenda: List[str] = []
    suggested_duration_min: int = 30
    suggested_tags: List[str] = []


@app.post("/calendar/describe", response_model=CalendarDescribeResponse)
async def calendar_describe(request: CalendarDescribeRequest):
    if not request.title or not request.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    try:
        # Use existing summarization as a light LLM call to craft description
        context_bits = []
        if request.context:
            context_bits.append(f"Context: {request.context}")
        if request.participants:
            context_bits.append(f"Participants: {', '.join(request.participants)}")
        tone_map = {
            "concise": "Write in 1-2 compact sentences.",
            "brief": "Write a short paragraph.",
            "detailed": "Write 3-5 sentences."
        }
        preface = f"{tone_map.get(request.tone, 'Write in 1-2 compact sentences.')}\nTitle: {request.title}\n" + ("\n".join(context_bits) if context_bits else "")
        description = generate_summary(preface, max_length=120)
        # naive agenda suggestion
        agenda = []
        for chunk in ["Introductions", "Objectives", "Discussion", "Decisions", "Next steps"]:
            if len(agenda) < 6:
                agenda.append(chunk)
        duration = request.duration_min or 30
        tags = [t for t in ["meeting", "planning", "sync"] if t]
        return CalendarDescribeResponse(
            description=description.strip() or request.title,
            agenda=agenda,
            suggested_duration_min=duration,
            suggested_tags=tags
        )
    except Exception as e:
        logger.error(f"Calendar describe error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
class ExtractActionsRequest(BaseModel):
    """Request model for action extraction."""
    text: Optional[str] = None
    messages: Optional[List[InputMessage]] = None
    context: str = ""
    priority_mode: Literal["heuristic", "llm", "hybrid"] = "hybrid"

class ExtractActionsResponse(BaseModel):
    """Response model for action extraction."""
    actions: List[Dict[str, Any]]

@app.post("/extract-actions", response_model=ExtractActionsResponse)
async def extract_actions(request: ExtractActionsRequest):
    """
    Extract action items from text using LangChain + OpenAI.
    
    Args:
        request: ExtractActionsRequest with text
        
    Returns:
        List of extracted actions
    """
    try:
        # Determine input
        if not request.text and not request.messages:
            raise HTTPException(status_code=400, detail="Provide text or messages[]")
        combined_text = request.text or flatten_messages(request.messages or [])
        logger.info(f"Extracting actions from text length {len(combined_text)}")

        # Base extraction via existing extractor
        actions = extract_action_items(combined_text, context=request.context)

        # Optional priority enrichment
        if heuristic_priority_score and label_from_score:
            enriched: List[Dict[str, Any]] = []
            for a in actions:
                score = heuristic_priority_score(a)
                label = label_from_score(score)
                enriched.append({
                    **a,
                    "priority": label,
                    "priority_score": score,
                })
            actions = enriched

        return ExtractActionsResponse(actions=actions)
    except Exception as e:
        logger.error(f"Action extraction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
