"""
Pydantic models for the Aggregator service
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UnifiedContact(BaseModel):
    """Unified contact representation across sources."""
    email: EmailStr
    name: Optional[str] = None

class UnifiedAttachment(BaseModel):
    """Unified attachment representation."""
    name: str
    size: int
    mime_type: Optional[str] = None
    url: Optional[str] = None

class UnifiedMessage(BaseModel):
    """Unified message format for all sources."""
    id: str
    source: str  # gmail, outlook, teams
    sender: UnifiedContact
    recipients: List[UnifiedContact] = []
    subject: str
    body: str
    timestamp: datetime
    labels: List[str] = []
    attachments: List[UnifiedAttachment] = []
    thread_id: Optional[str] = None
    importance_score: float = 0.5
    is_read: bool = False
    summary: Optional[str] = None  # AI-generated summary

class UnifiedEvent(BaseModel):
    """Unified calendar event format."""
    id: str
    source: str  # google_calendar, microsoft_calendar
    title: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    attendees: List[Dict[str, Any]] = []
    description: Optional[str] = None
    organizer: Optional[UnifiedContact] = None
    status: str = "confirmed"

class ActionItem(BaseModel):
    """Extracted action item from a message."""
    id: str
    source_message_id: str
    description: str
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    assignee: Optional[str] = None
    completed: bool = False

