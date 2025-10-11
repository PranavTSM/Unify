"""
Message Actions - Commercial features for message management
Provides: mark as read/unread, star, archive, snooze, bulk operations
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MessageActionService:
    """Handles message actions across different providers."""
    
    def __init__(self, mcp_base_url: str = "http://localhost:8000"):
        self.mcp_base_url = mcp_base_url
        
    def _call_mcp(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Helper to call MCP server."""
        try:
            url = f"{self.mcp_base_url}{endpoint}"
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {"success": True}
        except Exception as e:
            logger.error(f"MCP call failed {method} {endpoint}: {e}")
            return None
    
    def mark_as_read(self, message_id: str, source: str) -> bool:
        """Mark message as read."""
        try:
            if source.lower() == "gmail":
                # Gmail uses labels
                result = self._call_mcp(
                    "POST",
                    f"/gmail/messages/{message_id}:modify",
                    json={
                        "remove_labels": ["UNREAD"],
                        "user_id": "me"
                    }
                )
            elif source.lower() == "outlook":
                result = self._call_mcp(
                    "PATCH",
                    f"/outlook/messages/{message_id}",
                    json={"is_read": True}
                )
            else:
                logger.warning(f"Mark as read not supported for {source}")
                return False
            
            return result is not None
        except Exception as e:
            logger.error(f"Error marking as read: {e}")
            return False
    
    def mark_as_unread(self, message_id: str, source: str) -> bool:
        """Mark message as unread."""
        try:
            if source.lower() == "gmail":
                result = self._call_mcp(
                    "POST",
                    f"/gmail/messages/{message_id}:modify",
                    json={
                        "add_labels": ["UNREAD"],
                        "user_id": "me"
                    }
                )
            elif source.lower() == "outlook":
                result = self._call_mcp(
                    "PATCH",
                    f"/outlook/messages/{message_id}",
                    json={"is_read": False}
                )
            else:
                return False
            
            return result is not None
        except Exception as e:
            logger.error(f"Error marking as unread: {e}")
            return False
    
    def star_message(self, message_id: str, source: str, starred: bool = True) -> bool:
        """Star/unstar a message."""
        try:
            if source.lower() == "gmail":
                labels = ["STARRED"] if starred else []
                result = self._call_mcp(
                    "POST",
                    f"/gmail/messages/{message_id}:modify",
                    json={
                        "add_labels": labels if starred else [],
                        "remove_labels": [] if starred else ["STARRED"],
                        "user_id": "me"
                    }
                )
            elif source.lower() == "outlook":
                result = self._call_mcp(
                    "PATCH",
                    f"/outlook/messages/{message_id}",
                    json={"categories": ["Important"] if starred else []}
                )
            else:
                return False
            
            return result is not None
        except Exception as e:
            logger.error(f"Error starring message: {e}")
            return False
    
    def archive_message(self, message_id: str, source: str) -> bool:
        """Archive a message."""
        try:
            if source.lower() == "gmail":
                # Remove INBOX label
                result = self._call_mcp(
                    "POST",
                    f"/gmail/messages/{message_id}:modify",
                    json={
                        "remove_labels": ["INBOX"],
                        "user_id": "me"
                    }
                )
            elif source.lower() == "outlook":
                # Move to Archive folder (if exists)
                result = self._call_mcp(
                    "PATCH",
                    f"/outlook/messages/{message_id}",
                    json={"categories": ["Archived"]}
                )
            else:
                return False
            
            return result is not None
        except Exception as e:
            logger.error(f"Error archiving message: {e}")
            return False
    
    def delete_message(self, message_id: str, source: str) -> bool:
        """Delete a message."""
        try:
            if source.lower() == "gmail":
                # Move to trash
                result = self._call_mcp(
                    "POST",
                    f"/gmail/messages/{message_id}:modify",
                    json={
                        "add_labels": ["TRASH"],
                        "remove_labels": ["INBOX"],
                        "user_id": "me"
                    }
                )
            elif source.lower() == "outlook":
                result = self._call_mcp(
                    "DELETE",
                    f"/outlook/messages/{message_id}"
                )
            else:
                return False
            
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    def bulk_action(self, message_ids: List[str], action: str, source: str) -> Dict[str, Any]:
        """Perform bulk action on multiple messages."""
        results = {
            "success": [],
            "failed": [],
            "total": len(message_ids)
        }
        
        for msg_id in message_ids:
            try:
                success = False
                if action == "mark_read":
                    success = self.mark_as_read(msg_id, source)
                elif action == "mark_unread":
                    success = self.mark_as_unread(msg_id, source)
                elif action == "star":
                    success = self.star_message(msg_id, source, True)
                elif action == "unstar":
                    success = self.star_message(msg_id, source, False)
                elif action == "archive":
                    success = self.archive_message(msg_id, source)
                elif action == "delete":
                    success = self.delete_message(msg_id, source)
                
                if success:
                    results["success"].append(msg_id)
                else:
                    results["failed"].append(msg_id)
            except Exception as e:
                logger.error(f"Bulk action failed for {msg_id}: {e}")
                results["failed"].append(msg_id)
        
        results["success_count"] = len(results["success"])
        results["failed_count"] = len(results["failed"])
        
        return results


# In-memory snooze storage (in production, use Redis/database)
_snoozed_messages = {}


def snooze_message(message_id: str, until: datetime, metadata: Dict[str, Any] = None):
    """Snooze a message until a specific time."""
    _snoozed_messages[message_id] = {
        "until": until.isoformat(),
        "metadata": metadata or {},
        "snoozed_at": datetime.utcnow().isoformat()
    }
    logger.info(f"Snoozed message {message_id} until {until}")


def get_snoozed_messages() -> List[Dict[str, Any]]:
    """Get all snoozed messages."""
    return [
        {
            "message_id": msg_id,
            **data
        }
        for msg_id, data in _snoozed_messages.items()
    ]


def get_due_snoozed_messages() -> List[str]:
    """Get messages whose snooze time has passed."""
    now = datetime.utcnow()
    due = []
    
    for msg_id, data in list(_snoozed_messages.items()):
        until = datetime.fromisoformat(data["until"])
        if now >= until:
            due.append(msg_id)
            del _snoozed_messages[msg_id]
    
    return due


def unsnooze_message(message_id: str) -> bool:
    """Remove snooze from a message."""
    if message_id in _snoozed_messages:
        del _snoozed_messages[message_id]
        return True
    return False

