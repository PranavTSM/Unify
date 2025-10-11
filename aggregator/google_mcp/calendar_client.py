"""
Calendar MCP Client - Connects to the MCP server Calendar endpoints.
Provides all Calendar operations available in the MCP server.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# MCP server base URL
MCP_BASE_URL = "http://localhost:8000"

def list_calendars(min_access_role: Optional[str] = None) -> Dict[str, Any]:
    """
    List all calendars from MCP server.
    
    Args:
        min_access_role: Minimum access role ('reader', 'writer', 'owner')
        
    Returns:
        Dictionary with calendars data
    """
    try:
        params = {}
        if min_access_role:
            params["min_access_role"] = min_access_role
            
        response = requests.get(f"{MCP_BASE_URL}/calendars", params=params)
        response.raise_for_status()
        
        calendars = response.json().get('items', [])
        logger.info(f"Fetched {len(calendars)} calendars")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to list calendars: {e}")
        return {"error": str(e), "items": []}

def create_calendar(summary: str) -> Dict[str, Any]:
    """
    Create a new calendar via MCP server.
    
    Args:
        summary: Calendar title/name
        
    Returns:
        Created calendar details
    """
    try:
        data = {"summary": summary}
        response = requests.post(f"{MCP_BASE_URL}/calendars", json=data)
        response.raise_for_status()
        
        logger.info(f"Created calendar: {summary}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create calendar: {e}")
        return {"error": str(e)}

def fetch_calendar_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    query: Optional[str] = None,
    max_results: int = 50,
    single_events: bool = True,
    order_by: str = "startTime"
) -> Dict[str, Any]:
    """
    Fetch calendar events from the MCP server.
    
    Args:
        calendar_id: Calendar identifier (default 'primary')
        time_min: Start time (ISO format)
        time_max: End time (ISO format)
        query: Free text search query
        max_results: Maximum number of events to fetch
        single_events: Expand recurring events
        order_by: Order by 'startTime' or 'updated'
        
    Returns:
        Dictionary with events data from MCP server
    """
    try:
        params = {
            "max_results": max_results,
            "single_events": single_events,
            "order_by": order_by
        }
        if time_min:
            params["time_min"] = time_min
        if time_max:
            params["time_max"] = time_max
        if query:
            params["q"] = query
            
        response = requests.get(f"{MCP_BASE_URL}/calendars/{calendar_id}/events", params=params)
        response.raise_for_status()
        
        events = response.json().get('items', [])
        logger.info(f"Fetched {len(events)} calendar events")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch calendar events: {e}")
        return {"error": str(e), "items": []}

def create_calendar_event(
    calendar_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    send_notifications: bool = True
) -> Dict[str, Any]:
    """
    Create a calendar event via MCP server.
    
    Args:
        calendar_id: Calendar identifier
        summary: Event title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        description: Event description
        location: Event location
        attendees: List of attendee email addresses
        send_notifications: Whether to send notifications
        
    Returns:
        Created event details
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
        if attendees:
            data["attendees"] = attendees
            
        params = {"send_notifications": send_notifications}
        
        response = requests.post(
            f"{MCP_BASE_URL}/calendars/{calendar_id}/events",
            json=data,
            params=params
        )
        response.raise_for_status()
        
        logger.info(f"Created event: {summary}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create event: {e}")
        return {"error": str(e)}

def quick_add_event(
    calendar_id: str,
    text: str,
    send_notifications: bool = False
) -> Dict[str, Any]:
    """
    Create event from natural language text via MCP server.
    
    Args:
        calendar_id: Calendar identifier
        text: Natural language event description (e.g., "Meeting tomorrow at 2pm")
        send_notifications: Whether to send notifications
        
    Returns:
        Created event details
    """
    try:
        data = {"text": text}
        params = {"send_notifications": send_notifications}
        
        response = requests.post(
            f"{MCP_BASE_URL}/calendars/{calendar_id}/events/quickAdd",
            json=data,
            params=params
        )
        response.raise_for_status()
        
        logger.info(f"Quick added event: {text}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to quick add event: {e}")
        return {"error": str(e)}

def update_calendar_event(
    calendar_id: str,
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    send_notifications: bool = True
) -> Dict[str, Any]:
    """
    Update a calendar event via MCP server.
    
    Args:
        calendar_id: Calendar identifier
        event_id: Event identifier
        summary: New event title
        start_time: New start time (ISO format)
        end_time: New end time (ISO format)
        description: New description
        location: New location
        send_notifications: Whether to send notifications
        
    Returns:
        Updated event details
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
            
        params = {"send_notifications": send_notifications}
        
        response = requests.patch(
            f"{MCP_BASE_URL}/calendars/{calendar_id}/events/{event_id}",
            json=data,
            params=params
        )
        response.raise_for_status()
        
        logger.info(f"Updated event: {event_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update event: {e}")
        return {"error": str(e)}

def delete_calendar_event(
    calendar_id: str,
    event_id: str,
    send_notifications: bool = True
) -> bool:
    """
    Delete a calendar event via MCP server.
    
    Args:
        calendar_id: Calendar identifier
        event_id: Event identifier
        send_notifications: Whether to send notifications
        
    Returns:
        True if successful, False otherwise
    """
    try:
        params = {"send_notifications": send_notifications}
        
        response = requests.delete(
            f"{MCP_BASE_URL}/calendars/{calendar_id}/events/{event_id}",
            params=params
        )
        response.raise_for_status()
        
        logger.info(f"Deleted event: {event_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to delete event: {e}")
        return False

def add_event_attendees(
    calendar_id: str,
    event_id: str,
    attendee_emails: List[str],
    send_notifications: bool = True
) -> Dict[str, Any]:
    """
    Add attendees to an event via MCP server.
    
    Args:
        calendar_id: Calendar identifier
        event_id: Event identifier
        attendee_emails: List of email addresses to add
        send_notifications: Whether to send notifications
        
    Returns:
        Updated event details
    """
    try:
        data = {"attendee_emails": attendee_emails}
        params = {"send_notifications": send_notifications}
        
        response = requests.post(
            f"{MCP_BASE_URL}/calendars/{calendar_id}/events/{event_id}/attendees",
            json=data,
            params=params
        )
        response.raise_for_status()
        
        logger.info(f"Added attendees to event: {event_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to add attendees: {e}")
        return {"error": str(e)}

def check_attendee_status(
    event_id: str,
    calendar_id: str = "primary",
    attendee_emails: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Check attendee response status for an event via MCP server.
    
    Args:
        event_id: Event identifier
        calendar_id: Calendar identifier (default 'primary')
        attendee_emails: Optional list of specific attendees to check
        
    Returns:
        Dictionary mapping attendee emails to their status
    """
    try:
        data = {
            "event_id": event_id,
            "calendar_id": calendar_id
        }
        if attendee_emails:
            data["attendee_emails"] = attendee_emails
            
        response = requests.post(f"{MCP_BASE_URL}/events/check_attendee_status", json=data)
        response.raise_for_status()
        
        logger.info(f"Checked attendee status for event: {event_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check attendee status: {e}")
        return {"error": str(e)}

def query_free_busy(
    calendar_ids: List[str],
    time_min: str,
    time_max: str
) -> Dict[str, Any]:
    """
    Query free/busy information for calendars via MCP server.
    
    Args:
        calendar_ids: List of calendar identifiers
        time_min: Start time (ISO format)
        time_max: End time (ISO format)
        
    Returns:
        Free/busy information for each calendar
    """
    try:
        data = {
            "time_min": time_min,
            "time_max": time_max,
            "items": [{"id": cal_id} for cal_id in calendar_ids]
        }
        
        response = requests.post(f"{MCP_BASE_URL}/freeBusy", json=data)
        response.raise_for_status()
        
        logger.info(f"Queried free/busy for {len(calendar_ids)} calendars")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to query free/busy: {e}")
        return {"error": str(e)}

def schedule_mutual_meeting(
    attendee_calendar_ids: List[str],
    time_min: str,
    time_max: str,
    duration_minutes: int,
    summary: str,
    description: Optional[str] = None,
    organizer_calendar_id: str = "primary",
    send_notifications: bool = True
) -> Dict[str, Any]:
    """
    Find mutual availability and schedule a meeting via MCP server.
    
    Args:
        attendee_calendar_ids: List of attendee calendar IDs
        time_min: Search start time (ISO format)
        time_max: Search end time (ISO format)
        duration_minutes: Meeting duration in minutes
        summary: Meeting title
        description: Meeting description
        organizer_calendar_id: Organizer's calendar ID (default 'primary')
        send_notifications: Whether to send notifications
        
    Returns:
        Created meeting event details
    """
    try:
        data = {
            "attendee_calendar_ids": attendee_calendar_ids,
            "time_min": time_min,
            "time_max": time_max,
            "duration_minutes": duration_minutes,
            "event_details": {
                "summary": summary,
                "start": {"date": "1970-01-01"},  # Placeholder, will be replaced
                "end": {"date": "1970-01-01"}
            },
            "organizer_calendar_id": organizer_calendar_id,
            "send_notifications": send_notifications
        }
        
        if description:
            data["event_details"]["description"] = description
            
        response = requests.post(f"{MCP_BASE_URL}/schedule_mutual", json=data)
        response.raise_for_status()
        
        logger.info(f"Scheduled mutual meeting: {summary}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to schedule mutual meeting: {e}")
        return {"error": str(e)}

def analyze_calendar_busyness(
    time_min: str,
    time_max: str,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Analyze calendar busyness (event count and duration per day) via MCP server.
    
    Args:
        time_min: Analysis start time (ISO format)
        time_max: Analysis end time (ISO format)
        calendar_id: Calendar identifier (default 'primary')
        
    Returns:
        Busyness analysis data by date
    """
    try:
        data = {
            "time_min": time_min,
            "time_max": time_max,
            "calendar_id": calendar_id
        }
        
        response = requests.post(f"{MCP_BASE_URL}/analyze_busyness", json=data)
        response.raise_for_status()
        
        logger.info(f"Analyzed busyness for calendar: {calendar_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to analyze busyness: {e}")
        return {"error": str(e)}

def project_recurring_events(
    time_min: str,
    time_max: str,
    calendar_id: str = "primary",
    event_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Project recurring event occurrences via MCP server.
    
    Args:
        time_min: Projection start time (ISO format)
        time_max: Projection end time (ISO format)
        calendar_id: Calendar identifier (default 'primary')
        event_query: Optional query to filter recurring events
        
    Returns:
        Projected event occurrences
    """
    try:
        data = {
            "time_min": time_min,
            "time_max": time_max,
            "calendar_id": calendar_id
        }
        if event_query:
            data["event_query"] = event_query
            
        response = requests.post(f"{MCP_BASE_URL}/project_recurring", json=data)
        response.raise_for_status()
        
        logger.info(f"Projected recurring events for calendar: {calendar_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to project recurring events: {e}")
        return {"error": str(e)}
