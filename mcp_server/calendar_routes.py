"""
Calendar routes and endpoints for MCP server.
Contains all calendar-related business logic and API endpoints.
"""

import logging
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from dateutil import parser

# Import calendar actions and models
import mcp_server.calendar_actions as calendar_actions
from mcp_server.models import (
    GoogleCalendarEvent,
    EventsResponse,
    EventCreateRequest,
    QuickAddEventRequest,
    EventUpdateRequest,
    AddAttendeeRequest,
    CalendarListResponse,
    CalendarListEntry,
    CheckAttendeeStatusRequest, CheckAttendeeStatusResponse,
    FreeBusyRequest, FreeBusyResponse,
    ScheduleMutualRequest,
    ProjectRecurringRequest, ProjectRecurringResponse, ProjectedEventOccurrenceModel,
    AnalyzeBusynessRequest, AnalyzeBusynessResponse, DailyBusynessStats,
    CalendarBusyInfo, TimePeriod, FreeBusyError
)
from mcp_server.analysis import ProjectedEventOccurrence

logger = logging.getLogger(__name__)

# Create router for Calendar endpoints
router = APIRouter(tags=["Calendars"])

class CreateCalendarRequest(BaseModel):
    summary: str

# This function will be called from app.py to register all endpoints
def register_endpoints(get_current_credentials):
    """
    Register all calendar endpoints with the router.
    Called from app.py to inject the credentials dependency.
    """
    
    # --- CalendarList Endpoints ---
    
    @router.get(
        "/calendars",
        response_model=CalendarListResponse,
        summary="List Calendars",
        operation_id="list_calendars"
    )
    def list_calendars_endpoint(
        min_access_role: Optional[str] = Query(None, description="Minimum access role ('reader', 'writer', 'owner')."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Lists the calendars on the user's calendar list."""
        logger.info(f"Endpoint 'list_calendars' called. Params: min_access_role='{min_access_role}'")
        result = calendar_actions.find_calendars(credentials=creds, min_access_role=min_access_role)
        if result is None:
            logger.error("Action 'find_calendars' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to retrieve calendar list from Google API.")
        logger.info(f"Endpoint 'list_calendars' completed successfully. Returning {len(result.items)} calendars.")
        return result

    @router.post(
        "/calendars",
        response_model=CalendarListEntry,
        status_code=201,
        summary="Create Calendar",
        operation_id="create_calendar"
    )
    def create_calendar_endpoint(
        request: CreateCalendarRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Creates a new secondary calendar."""
        logger.info(f"Endpoint 'create_calendar' called. Summary: '{request.summary}'")
        result = calendar_actions.create_calendar(credentials=creds, summary=request.summary)
        if result is None:
            logger.error(f"Action 'create_calendar' for summary '{request.summary}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to create calendar via Google API.")
        logger.info(f"Endpoint 'create_calendar' completed. Calendar ID: {result.id}")
        return result

    # --- Events Endpoints ---
    
    @router.get(
        "/calendars/{calendar_id}/events",
        response_model=EventsResponse,
        summary="Find Events",
        operation_id="find_events"
    )
    def find_events_endpoint(
        calendar_id: str = Path(..., description="Calendar identifier (e.g., 'primary', email address, or calendar ID)."),
        time_min_str: Optional[str] = Query(None, alias="time_min", description="Start time (inclusive, RFC3339 format string)."),
        time_max_str: Optional[str] = Query(None, alias="time_max", description="End time (exclusive, RFC3339 format string)."),
        query: Optional[str] = Query(None, alias="q", description="Free text search query."),
        max_results: int = Query(50, ge=1, le=2500, description="Maximum results per page."),
        single_events: bool = Query(True, description="Expand recurring events."),
        order_by: str = Query('startTime', description="Order results by ('startTime' or 'updated')."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Finds events in a specified calendar."""
        logger.info(f"Endpoint 'find_events' called for calendar '{calendar_id}'.")
        
        time_min_dt: Optional[datetime] = None
        time_max_dt: Optional[datetime] = None
        try:
            if time_min_str:
                time_min_dt = parser.isoparse(time_min_str)
            if time_max_str:
                time_max_dt = parser.isoparse(time_max_str)
        except ValueError as e:
            logger.error(f"Failed to parse time strings: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid time format provided: {e}")

        result = calendar_actions.find_events(
            credentials=creds,
            calendar_id=calendar_id,
            time_min=time_min_dt,
            time_max=time_max_dt,
            query=query,
            max_results=max_results,
            single_events=single_events,
            order_by=order_by
        )
        if result is None:
            logger.error(f"Action 'find_events' for calendar '{calendar_id}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to retrieve events from Google API.")
        logger.info(f"Endpoint 'find_events' for calendar '{calendar_id}' completed. Found {len(result.items)} events.")
        return result

    @router.post(
        "/calendars/{calendar_id}/events",
        response_model=GoogleCalendarEvent,
        status_code=201,
        summary="Create Detailed Event",
        operation_id="create_event"
    )
    def create_event_endpoint(
        event_data: EventCreateRequest,
        calendar_id: str = Path(..., description="Calendar identifier."),
        send_notifications: bool = Query(True, description="Send notifications to attendees."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Creates a new event with detailed information."""
        logger.info(f"Endpoint 'create_event' called for calendar '{calendar_id}'. Summary: '{event_data.summary}'")
        logger.debug(f"Event data: {event_data.dict(exclude_unset=True)}")
        result = calendar_actions.create_event(
            credentials=creds,
            event_data=event_data,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        if result is None:
            logger.error(f"Action 'create_event' for calendar '{calendar_id}', summary '{event_data.summary}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to create event via Google API.")
        logger.info(f"Endpoint 'create_event' completed. Event ID: {result.id}")
        return result

    @router.post(
        "/calendars/{calendar_id}/events/quickAdd",
        response_model=GoogleCalendarEvent,
        status_code=201,
        summary="Quick Add Event",
        operation_id="quick_add_event"
    )
    def quick_add_event_endpoint(
        request_data: QuickAddEventRequest,
        calendar_id: str = Path(..., description="Calendar identifier."),
        send_notifications: bool = Query(False, description="Send notifications to attendees."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Creates an event from a simple text string."""
        logger.info(f"Endpoint 'quick_add_event' called for calendar '{calendar_id}'. Text: '{request_data.text}'")
        result = calendar_actions.quick_add_event(
            credentials=creds,
            text=request_data.text,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        if result is None:
            logger.error(f"Action 'quick_add_event' for calendar '{calendar_id}', text '{request_data.text}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to quick-add event via Google API.")
        logger.info(f"Endpoint 'quick_add_event' completed. Event ID: {result.id}")
        return result

    @router.patch(
        "/calendars/{calendar_id}/events/{event_id}",
        response_model=GoogleCalendarEvent,
        summary="Update Event (Patch)",
        operation_id="update_event"
    )
    def update_event_endpoint(
        update_data: EventUpdateRequest,
        calendar_id: str = Path(..., description="Calendar identifier."),
        event_id: str = Path(..., description="Event identifier."),
        send_notifications: bool = Query(True, description="Send notifications to attendees."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Updates specified fields of an existing event."""
        logger.info(f"Endpoint 'update_event' called for event '{event_id}' in calendar '{calendar_id}'.")
        logger.debug(f"Update data: {update_data.dict(exclude_unset=True)}")
        result = calendar_actions.update_event(
            credentials=creds,
            event_id=event_id,
            update_data=update_data,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        if result is None:
            logger.error(f"Action 'update_event' for event '{event_id}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail=f"Failed to update event '{event_id}'. Check server logs.")
        logger.info(f"Endpoint 'update_event' completed for event '{event_id}'.")
        return result

    @router.delete(
        "/calendars/{calendar_id}/events/{event_id}",
        status_code=204,
        summary="Delete Event",
        operation_id="delete_event"
    )
    def delete_event_endpoint(
        calendar_id: str = Path(..., description="Calendar identifier."),
        event_id: str = Path(..., description="Event identifier."),
        send_notifications: bool = Query(True, description="Send notifications to attendees."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Deletes an event."""
        logger.info(f"Endpoint 'delete_event' called for event '{event_id}' in calendar '{calendar_id}'.")
        success = calendar_actions.delete_event(
            credentials=creds,
            event_id=event_id,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        if not success:
            logger.error(f"Action 'delete_event' for event '{event_id}' returned False. Raising HTTPException.")
            raise HTTPException(status_code=500, detail=f"Failed to delete event '{event_id}'. It might not exist or an API error occurred.")
        logger.info(f"Endpoint 'delete_event' completed successfully for event '{event_id}'.")
        return None

    @router.post(
        "/calendars/{calendar_id}/events/{event_id}/attendees",
        response_model=GoogleCalendarEvent,
        summary="Add Attendee(s)",
        operation_id="add_attendee"
    )
    def add_attendee_endpoint(
        request_data: AddAttendeeRequest,
        calendar_id: str = Path(..., description="Calendar identifier."),
        event_id: str = Path(..., description="Event identifier."),
        send_notifications: bool = Query(True, description="Send notifications to attendees."),
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Adds one or more attendees to an existing event."""
        logger.info(f"Endpoint 'add_attendee' called for event '{event_id}'. Attendees: {request_data.attendee_emails}")
        result = calendar_actions.add_attendee(
            credentials=creds,
            event_id=event_id,
            attendee_emails=request_data.attendee_emails,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        if result is None:
            logger.error(f"Action 'add_attendee' for event '{event_id}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail=f"Failed to add attendees to event '{event_id}'. Check logs.")
        logger.info(f"Endpoint 'add_attendee' completed for event '{event_id}'.")
        return result

    # --- Advanced Scheduling & Analysis Endpoints ---

    @router.post(
        "/events/check_attendee_status",
        response_model=CheckAttendeeStatusResponse,
        tags=["Advanced Scheduling"],
        summary="Check Attendee Response Status",
        operation_id="check_attendee_status"
    )
    def check_attendee_status_endpoint(
        request: CheckAttendeeStatusRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Checks the response status ('accepted', 'declined', etc.) for attendees of a specific event."""
        logger.info(f"Endpoint 'check_attendee_status' called for event '{request.event_id}'. Calendar: '{request.calendar_id}'. Attendees: {request.attendee_emails or 'All'}")
        status_dict = calendar_actions.check_attendee_status(
            credentials=creds,
            event_id=request.event_id,
            calendar_id=request.calendar_id,
            attendee_emails=request.attendee_emails
        )
        if status_dict is None:
            logger.error(f"Action 'check_attendee_status' for event '{request.event_id}' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail=f"Failed to check attendee status for event '{request.event_id}'. Event might not exist or API error.")
        logger.info(f"Endpoint 'check_attendee_status' completed for event '{request.event_id}'. Found status for {len(status_dict)} attendees.")
        return CheckAttendeeStatusResponse(status_map=status_dict)

    @router.post(
        "/freeBusy",
        response_model=FreeBusyResponse,
        tags=["Advanced Scheduling"],
        summary="Query Free/Busy Information",
        operation_id="query_free_busy"
    )
    def query_free_busy_endpoint(
        request: FreeBusyRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Queries the free/busy information for a list of calendars over a time period."""
        calendar_ids = [item.id for item in request.items]
        logger.info(f"Endpoint 'query_free_busy' called. Calendars: {calendar_ids}")
        logger.debug(f"Time range: {request.time_min} to {request.time_max}")

        busy_info_dict = calendar_actions.find_availability(
            credentials=creds,
            time_min=request.time_min,
            time_max=request.time_max,
            calendar_ids=calendar_ids
        )

        if busy_info_dict is None:
            logger.error("Action 'find_availability' returned None. Raising HTTPException.")
            raise HTTPException(status_code=500, detail="Failed to query free/busy information via Google API.")

        # Convert the result from find_availability back into the FreeBusyResponse model structure
        response_calendars: Dict[str, CalendarBusyInfo] = {}
        for cal_id, data in busy_info_dict.items():
            response_calendars[cal_id] = CalendarBusyInfo(
                busy=[TimePeriod(start=p['start'], end=p['end']) for p in data.get('busy', [])],
                errors=[FreeBusyError(**err) for err in data.get('errors', [])]
            )

        return FreeBusyResponse(
            time_min=request.time_min,
            time_max=request.time_max,
            calendars=response_calendars
        )

    @router.post(
        "/schedule_mutual",
        response_model=GoogleCalendarEvent,
        status_code=201,
        tags=["Advanced Scheduling"],
        summary="Find Mutual Availability and Schedule",
        operation_id="schedule_mutual"
    )
    def schedule_mutual_endpoint(
        request: ScheduleMutualRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Finds the first available time slot for multiple attendees and schedules the provided event details."""
        logger.info(f"Endpoint 'schedule_mutual' called. Attendees: {request.attendee_calendar_ids}. Duration: {request.duration_minutes} mins.")
        logger.debug(f"Time range: {request.time_min} to {request.time_max}. Organizer: {request.organizer_calendar_id}. Event Summary: {request.event_details.summary}")
        
        # Parse working hours strings into time objects
        working_hours_start = None
        working_hours_end = None
        try:
            if request.working_hours_start_str:
                working_hours_start = datetime.strptime(request.working_hours_start_str, '%H:%M').time()
            if request.working_hours_end_str:
                working_hours_end = datetime.strptime(request.working_hours_end_str, '%H:%M').time()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid working hours format. Use HH:MM.")

        created_event = calendar_actions.find_mutual_availability_and_schedule(
            credentials=creds,
            attendee_calendar_ids=request.attendee_calendar_ids,
            time_min=request.time_min,
            time_max=request.time_max,
            duration_minutes=request.duration_minutes,
            event_details=request.event_details,
            organizer_calendar_id=request.organizer_calendar_id,
            working_hours_start=working_hours_start,
            working_hours_end=working_hours_end,
            send_notifications=request.send_notifications
        )

        if created_event is None:
            logger.error("Action 'find_mutual_availability_and_schedule' returned None. Raising HTTPException.")
            raise HTTPException(status_code=409, detail="Could not schedule event. No suitable time slot found or event creation failed.")
        logger.info(f"Endpoint 'schedule_mutual' completed successfully. Event ID: {created_event.id}")
        return created_event

    @router.post(
        "/project_recurring",
        response_model=ProjectRecurringResponse,
        tags=["Analysis"],
        summary="Project Recurring Event Occurrences",
        operation_id="project_recurring"
    )
    def project_recurring_endpoint(
        request: ProjectRecurringRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Finds recurring events and projects their future occurrences within a time window."""
        logger.info(f"Endpoint 'project_recurring' called. Calendar: '{request.calendar_id}'. Query: '{request.event_query}'")
        logger.debug(f"Time range: {request.time_min} to {request.time_max}")
        
        occurrences: List[ProjectedEventOccurrence] = calendar_actions.get_projected_recurring_events(
            credentials=creds,
            time_min=request.time_min,
            time_max=request.time_max,
            calendar_id=request.calendar_id,
            event_query=request.event_query
        )

        # Convert ProjectedEventOccurrence to ProjectedEventOccurrenceModel
        response_occurrences = [
            ProjectedEventOccurrenceModel(**occ.__dict__) for occ in occurrences
        ]

        logger.info(f"Endpoint 'project_recurring' completed. Found {len(response_occurrences)} projected occurrences.")
        return ProjectRecurringResponse(projected_occurrences=response_occurrences)

    @router.post(
        "/analyze_busyness",
        response_model=AnalyzeBusynessResponse,
        tags=["Analysis"],
        summary="Analyze Daily Event Count and Duration",
        operation_id="analyze_busyness"
    )
    def analyze_busyness_endpoint(
        request: AnalyzeBusynessRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        """Analyzes event count and total duration per day within a specified time window."""
        logger.info(f"Endpoint 'analyze_busyness' called. Calendar: '{request.calendar_id}'")
        logger.debug(f"Time range: {request.time_min} to {request.time_max}")
        
        busyness_dict = calendar_actions.get_busyness_analysis(
            credentials=creds,
            time_min=request.time_min,
            time_max=request.time_max,
            calendar_id=request.calendar_id
        )

        if busyness_dict is None:
             logger.error("Action 'get_busyness_analysis' returned None. Raising HTTPException.")
             raise HTTPException(status_code=500, detail="Failed to analyze busyness.")

        # Convert date keys to strings (YYYY-MM-DD) for JSON compatibility
        response_data = {
            dt.strftime('%Y-%m-%d'): DailyBusynessStats(**stats)
            for dt, stats in busyness_dict.items()
        }

        return AnalyzeBusynessResponse(busyness_by_date=response_data)

