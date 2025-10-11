"""
MongoDB Data Models and Schemas
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Sender(BaseModel):
    """Sender/organizer information."""
    email: str
    name: str = ""


class Recipient(BaseModel):
    """Recipient/attendee information."""
    email: str
    name: str = ""
    status: Optional[str] = None


class Attachment(BaseModel):
    """Attachment information."""
    name: str
    size: int = 0
    mime_type: Optional[str] = None
    url: Optional[str] = None


class Message(BaseModel):
    """Unified Message Model for MongoDB storage."""
    
    # Core fields
    id: str = Field(..., description="Unique message ID")
    source: str = Field(..., description="Source: gmail, outlook, teams")
    
    # Content
    subject: str
    body: str
    body_preview: str = ""
    
    # People
    sender: Sender
    recipients: List[Recipient] = []
    
    # Metadata
    timestamp: str  # ISO format
    labels: List[str] = []
    attachments: List[Attachment] = []
    thread_id: Optional[str] = None
    is_read: bool = True
    importance_score: float = 0.5
    
    # AI features
    summary: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = {}
    
    # Storage metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_123",
                "source": "gmail",
                "subject": "Meeting Tomorrow",
                "body": "Let's meet at 10am",
                "body_preview": "Let's meet...",
                "sender": {"email": "user@example.com", "name": "John"},
                "recipients": [],
                "timestamp": "2025-10-11T10:00:00Z",
                "labels": [],
                "attachments": [],
                "is_read": False,
                "importance_score": 0.7
            }
        }


class Event(BaseModel):
    """Unified Event Model for MongoDB storage."""
    
    # Core fields
    id: str = Field(..., description="Unique event ID")
    source: str = Field(..., description="Source: google_calendar, microsoft_calendar")
    
    # Content
    title: str
    description: str = ""
    location: str = ""
    
    # Time
    start: str  # ISO format
    end: str  # ISO format
    
    # People
    organizer: Sender
    attendees: List[Recipient] = []
    
    # Metadata
    status: str = "confirmed"
    
    # Storage metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "event_123",
                "source": "google_calendar",
                "title": "Team Meeting",
                "description": "Weekly sync",
                "location": "Conference Room A",
                "start": "2025-10-11T10:00:00Z",
                "end": "2025-10-11T11:00:00Z",
                "organizer": {"email": "manager@example.com", "name": "Manager"},
                "attendees": [],
                "status": "confirmed"
            }
        }


class FetchLog(BaseModel):
    """Log of data fetches for tracking and debugging."""
    
    source: str
    fetch_type: str  # "messages" or "events"
    count: int
    success: bool
    error_message: Optional[str] = None
    duration_seconds: float
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "gmail",
                "fetch_type": "messages",
                "count": 20,
                "success": True,
                "error_message": None,
                "duration_seconds": 2.5,
                "fetched_at": "2025-10-11T10:00:00Z"
            }
        }

