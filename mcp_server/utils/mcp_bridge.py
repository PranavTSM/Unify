import requests
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure logging
logger = logging.getLogger(__name__)

# Base URL for the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

def create_mcp_server():
    """Creates and configures the MCP server with tools that map to the FastAPI endpoints."""
    mcp = FastMCP("calendar-mcp")
    
    @mcp.tool()
    async def list_calendars(min_access_role: str = None) -> str:
        """Lists the calendars on the user's calendar list.
        
        Args:
            min_access_role: Minimum access role ('reader', 'writer', 'owner').
        """
        try:
            params = {}
            if min_access_role:
                params["min_access_role"] = min_access_role
            
            response = requests.get(f"{BASE_URL}/calendars", params=params)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            # Ensure we're returning clean JSON
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})

    @mcp.tool()
    async def find_events(calendar_id: str, time_min: str = None, 
                         time_max: str = None, query: str = None,
                         max_results: int = 50) -> str:
        """Find events in a specified calendar.
        
        Args:
            calendar_id: Calendar identifier (e.g., 'primary', email address, or calendar ID).
            time_min: Start time (inclusive, ISO format).
            time_max: End time (exclusive, ISO format).
            query: Free text search query.
            max_results: Maximum number of events to return (default 50).
        """
        try:
            params = {"max_results": max_results}
            if time_min:
                params["time_min"] = time_min
            if time_max:
                params["time_max"] = time_max
            if query:
                params["q"] = query
            
            response = requests.get(f"{BASE_URL}/calendars/{calendar_id}/events", params=params)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})

    @mcp.tool()
    async def create_event(calendar_id: str, summary: str, start_time: str, 
                          end_time: str, description: str = None,
                          location: str = None, 
                          attendee_emails: List[str] = None) -> str:
        """Creates a new event with detailed information.
        
        Args:
            calendar_id: Calendar identifier.
            summary: Title of the event.
            start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS).
            end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS).
            description: Optional description for the event.
            location: Optional location for the event.
            attendee_emails: Optional list of attendee email addresses.
        """
        try:
            data = {
                "summary": summary,
                "start": {"dateTime": start_time},
                "end": {"dateTime": end_time}
            }
            
            if description:
                data["description"] = description
            if location:
                data["location"] = location
            if attendee_emails:
                data["attendees"] = attendee_emails
            
            response = requests.post(
                f"{BASE_URL}/calendars/{calendar_id}/events", 
                json=data
            )
            if response.status_code != 201:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def quick_add_event(calendar_id: str, text: str) -> str:
        """Creates an event based on a simple text string using Google's natural language parser.
        
        Args:
            calendar_id: Calendar identifier.
            text: The text description of the event (e.g., "Meeting with John tomorrow at 2pm").
        """
        try:
            data = {"text": text}
            response = requests.post(
                f"{BASE_URL}/calendars/{calendar_id}/events/quickAdd", 
                json=data
            )
            if response.status_code != 201:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def update_event(calendar_id: str, event_id: str, summary: str = None, 
                          start_time: str = None, end_time: str = None,
                          description: str = None, location: str = None) -> str:
        """Updates an existing event.
        
        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
            summary: New title for the event.
            start_time: New start time in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ' or 'YYYY-MM-DDTHH:MM:SS+HH:MM').
            end_time: New end time in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ' or 'YYYY-MM-DDTHH:MM:SS+HH:MM').
            description: New description for the event.
            location: New location for the event.
        """
        try:
            data = {}
            if summary:
                data["summary"] = summary
            if start_time:
                data["start"] = {"dateTime": start_time}
            if end_time:
                data["end"] = {"dateTime": end_time}
            if description:
                data["description"] = description
            if location:
                data["location"] = location
            
            response = requests.patch(
                f"{BASE_URL}/calendars/{calendar_id}/events/{event_id}", 
                json=data
            )
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def delete_event(calendar_id: str, event_id: str) -> str:
        """Deletes an event.
        
        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
        """
        try:
            response = requests.delete(f"{BASE_URL}/calendars/{calendar_id}/events/{event_id}")
            if response.status_code != 204:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps({"success": "Event successfully deleted."})
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def add_attendee(calendar_id: str, event_id: str, attendee_emails: List[str]) -> str:
        """Adds one or more attendees to an existing event.
        
        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
            attendee_emails: List of email addresses to add as attendees.
        """
        try:
            data = {"attendee_emails": attendee_emails}
            response = requests.post(
                f"{BASE_URL}/calendars/{calendar_id}/events/{event_id}/attendees", 
                json=data
            )
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def check_attendee_status(event_id: str, calendar_id: str = "primary", 
                                   attendee_emails: List[str] = None) -> str:
        """Checks the response status for attendees of a specific event.
        
        Args:
            event_id: Event identifier.
            calendar_id: Calendar identifier (default: primary).
            attendee_emails: Optional list of specific attendees to check.
        """
        try:
            data = {
                "event_id": event_id,
                "calendar_id": calendar_id
            }
            if attendee_emails:
                data["attendee_emails"] = attendee_emails
            
            response = requests.post(f"{BASE_URL}/events/check_attendee_status", json=data)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def query_free_busy(calendar_ids: List[str], time_min: str, time_max: str) -> str:
        """Queries the free/busy information for a list of calendars over a time period.
        
        Args:
            calendar_ids: List of calendar identifiers to query.
            time_min: Start of the time range (ISO format).
            time_max: End of the time range (ISO format).
        """
        try:
            data = {
                "time_min": time_min,
                "time_max": time_max,
                "items": [{"id": cal_id} for cal_id in calendar_ids]
            }
            response = requests.post(f"{BASE_URL}/freeBusy", json=data)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def schedule_mutual(attendee_calendar_ids: List[str], time_min: str, 
                             time_max: str, duration_minutes: int, 
                             summary: str, description: str = None) -> str:
        """Finds the first available time slot for multiple attendees and schedules an event.
        
        Args:
            attendee_calendar_ids: List of calendar IDs for attendees.
            time_min: Start of the search window (ISO format).
            time_max: End of the search window (ISO format).
            duration_minutes: Required duration of the event in minutes.
            summary: Title for the event.
            description: Optional description for the event.
        """
        try:
            data = {
                "attendee_calendar_ids": attendee_calendar_ids,
                "time_min": time_min,
                "time_max": time_max,
                "duration_minutes": duration_minutes,
                "event_details": {
                    "summary": summary,
                    "start": {"date": "1970-01-01"},
                    "end": {"date": "1970-01-01"}
                }
            }
            if description:
                data["event_details"]["description"] = description
            
            response = requests.post(f"{BASE_URL}/schedule_mutual", json=data)
            if response.status_code != 201:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    async def analyze_busyness(time_min: str, time_max: str, calendar_id: str = "primary") -> str:
        """Analyzes event count and total duration per day within a specified time window.
        
        Args:
            time_min: Start of the analysis window (ISO format).
            time_max: End of the analysis window (ISO format).
            calendar_id: Calendar identifier (default: primary).
        """
        try:
            data = {
                "time_min": time_min,
                "time_max": time_max,
                "calendar_id": calendar_id
            }
            response = requests.post(f"{BASE_URL}/analyze_busyness", json=data)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    # --- Gmail tools ---
    @mcp.tool()
    async def gmail_list_messages(q: str = None, max_results: int = 50, label_ids: List[str] = None, user_id: str = 'me') -> str:
        """List Gmail messages for the user.
        
        Args:
            q: Gmail search query (e.g., 'from:someone subject:Report')
            max_results: Maximum messages to return (1-500)
            label_ids: Optional list of label IDs (e.g., ['INBOX','UNREAD'] or custom 'Label_XXXX')
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            params: Dict[str, Any] = {"max_results": max_results, "user_id": user_id}
            if q:
                params["q"] = q
            if label_ids:
                for lid in label_ids:
                    params.setdefault('label_ids', []).append(lid)
            resp = requests.get(f"{BASE_URL}/gmail/messages", params=params)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_list_messages error", exc_info=True)
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def gmail_get_message(message_id: str, format: str = 'full', user_id: str = 'me') -> str:
        """Get a Gmail message.
        
        Args:
            message_id: Gmail message ID
            format: One of 'minimal','full','raw','metadata'
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            params = {"format": format, "user_id": user_id}
            resp = requests.get(f"{BASE_URL}/gmail/messages/{message_id}", params=params)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_get_message error", exc_info=True)
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def gmail_send_raw(raw_base64url: str, user_id: str = 'me') -> str:
        """Send an email using a base64url-encoded RFC 2822 message.
        
        Args:
            raw_base64url: base64url-encoded raw message (use build tools to compose)
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            data = {"raw": raw_base64url, "user_id": user_id}
            resp = requests.post(f"{BASE_URL}/gmail/messages:sendRaw", json=data)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_send_raw error", exc_info=True)
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def gmail_compose_and_send(from_addr: str, to_addrs: List[str], subject: str, body_text: str, user_id: str = 'me') -> str:
        """Compose and send a simple text email.
        
        Args:
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            subject: Email subject
            body_text: Plain text body
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            data = {
                "from_addr": from_addr,
                "to_addrs": to_addrs,
                "subject": subject,
                "body_text": body_text,
                "user_id": user_id,
            }
            resp = requests.post(f"{BASE_URL}/gmail/messages:composeAndSend", json=data)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_compose_and_send error", exc_info=True)
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def gmail_modify_labels(message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None, user_id: str = 'me') -> str:
        """Add and/or remove labels from a Gmail message.
        
        Args:
            message_id: Gmail message ID
            add_labels: Labels to add (e.g., ['INBOX','UNREAD','Label_XXXX'])
            remove_labels: Labels to remove
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            data: Dict[str, Any] = {"user_id": user_id}
            if add_labels is not None:
                data["add_labels"] = add_labels
            if remove_labels is not None:
                data["remove_labels"] = remove_labels
            resp = requests.post(f"{BASE_URL}/gmail/messages/{message_id}:modify", json=data)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_modify_labels error", exc_info=True)
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def gmail_list_labels(user_id: str = 'me') -> str:
        """List Gmail labels for the user.
        
        Args:
            user_id: Gmail user id; 'me' refers to the authenticated user
        """
        try:
            params = {"user_id": user_id}
            resp = requests.get(f"{BASE_URL}/gmail/labels", params=params)
            if resp.status_code != 200:
                return json.dumps({"error": f"{resp.status_code}: {resp.text}"})
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            logger.error("gmail_list_labels error", exc_info=True)
            return json.dumps({"error": str(e)})
    
    return mcp 