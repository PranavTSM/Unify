"""
MongoDB Repository - Data access layer for messages and events
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .mongo_client import get_sync_db
from .models import Message, Event, FetchLog

logger = logging.getLogger(__name__)


class MessageRepository:
    """Repository for message operations."""
    
    def __init__(self):
        self.db = get_sync_db()
        self.collection = self.db.messages if self.db is not None else None
    
    def save_messages(self, messages: List[Dict[str, Any]]) -> int:
        """
        Save messages to MongoDB (bulk upsert).
        
        Args:
            messages: List of normalized messages
            
        Returns:
            Number of messages saved
        """
        if not self.collection:
            logger.warning("MongoDB not available, skipping save")
            return 0
        
        try:
            if not messages:
                return 0
            
            # Prepare bulk operations
            from pymongo import UpdateOne
            
            operations = []
            for msg in messages:
                # Add storage timestamps
                msg['updated_at'] = datetime.utcnow()
                if 'created_at' not in msg:
                    msg['created_at'] = datetime.utcnow()
                
                # Upsert operation
                operations.append(
                    UpdateOne(
                        {'id': msg['id']},
                        {'$set': msg},
                        upsert=True
                    )
                )
            
            # Execute bulk write
            result = self.collection.bulk_write(operations, ordered=False)
            
            saved = result.upserted_count + result.modified_count
            logger.info(f"💾 Saved {saved} messages to MongoDB")
            
            return saved
            
        except Exception as e:
            logger.error(f"Error saving messages to MongoDB: {e}")
            return 0
    
    def get_messages(
        self,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None,
        is_read: Optional[bool] = None,
        min_score: Optional[float] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get messages with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            source: Filter by source (gmail, outlook, teams)
            is_read: Filter by read status
            min_score: Minimum importance score
            search_query: Text search in subject/body
            
        Returns:
            Dictionary with messages, pagination info, and total count
        """
        if not self.collection:
            logger.warning("MongoDB not available")
            return {
                "messages": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0
            }
        
        try:
            # Build query
            query = {}
            
            if source:
                query['source'] = source
            
            if is_read is not None:
                query['is_read'] = is_read
            
            if min_score is not None:
                query['importance_score'] = {'$gte': min_score}
            
            if search_query:
                query['$or'] = [
                    {'subject': {'$regex': search_query, '$options': 'i'}},
                    {'body': {'$regex': search_query, '$options': 'i'}},
                    {'sender.email': {'$regex': search_query, '$options': 'i'}},
                    {'sender.name': {'$regex': search_query, '$options': 'i'}}
                ]
            
            # Get total count
            total_count = self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Fetch messages
            cursor = self.collection.find(query).sort('timestamp', -1).skip(skip).limit(page_size)
            messages = list(cursor)
            
            # Remove MongoDB _id field
            for msg in messages:
                msg.pop('_id', None)
            
            logger.info(f"📖 Retrieved {len(messages)} messages from MongoDB (page {page}/{total_pages})")
            
            return {
                "messages": messages,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
            
        except Exception as e:
            logger.error(f"Error retrieving messages from MongoDB: {e}")
            return {
                "messages": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0
            }
    
    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a single message by ID."""
        if not self.collection:
            return None
        
        try:
            msg = self.collection.find_one({'id': message_id})
            if msg:
                msg.pop('_id', None)
            return msg
        except Exception as e:
            logger.error(f"Error retrieving message {message_id}: {e}")
            return None
    
    def delete_old_messages(self, days_old: int = 30) -> int:
        """
        Delete messages older than specified days.
        
        Args:
            days_old: Delete messages older than this many days
            
        Returns:
            Number of messages deleted
        """
        if not self.collection:
            return 0
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = self.collection.delete_many({
                'created_at': {'$lt': cutoff_date}
            })
            
            deleted = result.deleted_count
            logger.info(f"🗑️  Deleted {deleted} old messages (>{days_old} days)")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting old messages: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message statistics."""
        if not self.collection:
            return {}
        
        try:
            total = self.collection.count_documents({})
            
            # Count by source
            by_source = {}
            for source in ['gmail', 'outlook', 'teams']:
                count = self.collection.count_documents({'source': source})
                by_source[source] = count
            
            # Count unread
            unread = self.collection.count_documents({'is_read': False})
            
            return {
                "total_messages": total,
                "by_source": by_source,
                "unread_count": unread,
                "read_count": total - unread
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


class EventRepository:
    """Repository for event operations."""
    
    def __init__(self):
        self.db = get_sync_db()
        self.collection = self.db.events if self.db is not None else None
    
    def save_events(self, events: List[Dict[str, Any]]) -> int:
        """Save events to MongoDB (bulk upsert)."""
        if not self.collection:
            logger.warning("MongoDB not available, skipping save")
            return 0
        
        try:
            if not events:
                return 0
            
            from pymongo import UpdateOne
            
            operations = []
            for event in events:
                event['updated_at'] = datetime.utcnow()
                if 'created_at' not in event:
                    event['created_at'] = datetime.utcnow()
                
                operations.append(
                    UpdateOne(
                        {'id': event['id']},
                        {'$set': event},
                        upsert=True
                    )
                )
            
            result = self.collection.bulk_write(operations, ordered=False)
            saved = result.upserted_count + result.modified_count
            logger.info(f"💾 Saved {saved} events to MongoDB")
            
            return saved
            
        except Exception as e:
            logger.error(f"Error saving events to MongoDB: {e}")
            return 0
    
    def get_events(
        self,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None,
        start_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get events with pagination."""
        if not self.collection:
            return {
                "events": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0
            }
        
        try:
            query = {}
            
            if source:
                query['source'] = source
            
            if start_after:
                query['start'] = {'$gte': start_after}
            
            total_count = self.collection.count_documents(query)
            skip = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            cursor = self.collection.find(query).sort('start', 1).skip(skip).limit(page_size)
            events = list(cursor)
            
            for event in events:
                event.pop('_id', None)
            
            return {
                "events": events,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            return {"events": [], "page": page, "page_size": page_size, "total_count": 0, "total_pages": 0}


class FetchLogRepository:
    """Repository for fetch log operations."""
    
    def __init__(self):
        self.db = get_sync_db()
        self.collection = self.db.fetch_logs if self.db is not None else None
    
    def log_fetch(
        self,
        source: str,
        fetch_type: str,
        count: int,
        success: bool,
        duration_seconds: float,
        error_message: Optional[str] = None
    ):
        """Log a fetch operation."""
        if not self.collection:
            return
        
        try:
            log = {
                "source": source,
                "fetch_type": fetch_type,
                "count": count,
                "success": success,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "fetched_at": datetime.utcnow()
            }
            
            self.collection.insert_one(log)
            
        except Exception as e:
            logger.error(f"Error logging fetch: {e}")

