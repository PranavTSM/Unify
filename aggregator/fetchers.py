"""
Data Fetchers - Fetch raw JSON from MCP server endpoints
"""
 
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
 
logger = logging.getLogger(__name__)
 
 
class MCPFetcher:
    """Base class for fetching data from MCP server."""
   
    def __init__(self, mcp_base_url: str = "http://localhost:8000"):
        self.base_url = mcp_base_url
        self.session = requests.Session()
   
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make GET request to MCP server."""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Fetching from: {url}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(f"Bad request for {endpoint}: {e.response.text}")
            elif e.response.status_code == 404:
                logger.warning(f"Endpoint not found: {endpoint}")
            else:
                logger.error(f"HTTP error fetching from {endpoint}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from {endpoint}: {e}")
            return None
 
 
class GmailFetcher(MCPFetcher):
    """Fetch Gmail messages from MCP server."""
   
    def fetch_messages(self, max_results: int = 50, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch Gmail messages.
       
        Args:
            max_results: Maximum number of messages to fetch
            query: Gmail search query
           
        Returns:
            List of raw Gmail message objects
        """
        params = {"maxResults": max_results}
        if query:
            params["q"] = query
       
        data = self._get("/gmail/messages", params=params)
        if data and "messages" in data:
            logger.info(f"Fetched {len(data['messages'])} Gmail messages")
            return data["messages"]
        return []
 
 
class OutlookFetcher(MCPFetcher):
    """Fetch Outlook messages from MCP server."""
   
    def fetch_messages(self, folder: str = "inbox", max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Outlook messages.
       
        Args:
            folder: Folder to fetch from (inbox, sent, drafts, etc.)
            max_results: Maximum number of messages to fetch
           
        Returns:
            List of raw Outlook message objects
        """
        params = {"folder": folder, "max_results": max_results}
       
        data = self._get("/outlook/messages", params=params)
        if data and isinstance(data, list):
            logger.info(f"Fetched {len(data)} Outlook messages")
            return data
        elif data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} Outlook messages")
            return data["value"]
        return []
 
 
class TeamsFetcher(MCPFetcher):
    """Fetch Teams messages from MCP server."""
   
    def fetch_messages(self, team_id: Optional[str] = None, channel_id: Optional[str] = None,
                      max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Teams channel messages.
       
        Args:
            team_id: Team ID (uses default if not provided)
            channel_id: Channel ID (uses default if not provided)
            max_results: Maximum number of messages to fetch
           
        Returns:
            List of raw Teams message objects
        """
        # If no team_id or channel_id provided, use default endpoint
        if not team_id or not channel_id:
            endpoint = "/teams/default/messages"
        else:
            endpoint = f"/teams/{team_id}/channels/{channel_id}/messages"
       
        params = {"max_results": max_results}
       
        data = self._get(endpoint, params=params)
        if data and isinstance(data, list):
            logger.info(f"Fetched {len(data)} Teams messages")
            return data
        elif data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} Teams messages")
            return data["value"]
        return []
   
    def fetch_all_teams(self) -> List[Dict[str, Any]]:
        """Fetch list of all teams."""
        data = self._get("/teams")
        if data and "value" in data:
            return data["value"]
        return []
   
    def fetch_channels(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch channels for a team."""
        if not team_id:
            endpoint = "/teams/default/channels"
        else:
            endpoint = f"/teams/{team_id}/channels"
       
        data = self._get(endpoint)
        if data and "value" in data:
            return data["value"]
        return []
 
 
class CalendarFetcher(MCPFetcher):
    """Fetch calendar events from MCP server."""
   
    def fetch_google_events(self, calendar_id: str = "primary",
                           time_min: Optional[str] = None,
                           time_max: Optional[str] = None,
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch Google Calendar events.
       
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time (ISO format)
            time_max: End time (ISO format)
            max_results: Maximum number of events
           
        Returns:
            List of raw Google Calendar event objects
        """
        params = {"max_results": max_results}
        if time_min:
            params["time_min"] = time_min
        if time_max:
            params["time_max"] = time_max
       
        data = self._get(f"/calendars/{calendar_id}/events", params=params)
        if data and "items" in data:
            logger.info(f"Fetched {len(data['items'])} Google Calendar events")
            return data["items"]
        return []
   
    def fetch_microsoft_events(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch Microsoft Calendar events.
       
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
           
        Returns:
            List of raw Microsoft Calendar event objects
        """
        params = {}
        if start_date:
            params["startDateTime"] = start_date
        if end_date:
            params["endDateTime"] = end_date
       
        # Note: Implement when Microsoft Calendar endpoints are added to MCP server
        logger.warning("Microsoft Calendar fetching not yet implemented in MCP server")
        return []
 
 
class UnifiedAggregator:
    """
    Unified aggregator that fetches and normalizes data from all sources.
    """
   
    def __init__(self, mcp_base_url: str = "http://localhost:8000"):
        self.gmail_fetcher = GmailFetcher(mcp_base_url)
        self.outlook_fetcher = OutlookFetcher(mcp_base_url)
        self.teams_fetcher = TeamsFetcher(mcp_base_url)
        self.calendar_fetcher = CalendarFetcher(mcp_base_url)
   
    def fetch_all_messages(self, max_per_source: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch messages from all sources.
       
        Returns:
            Dictionary with keys: 'gmail', 'outlook', 'teams'
            Each containing list of raw messages
        """
        logger.info("Fetching messages from all sources...")
       
        results = {
            "gmail": [],
            "outlook": [],
            "teams": []
        }
       
        # Fetch Gmail
        try:
            results["gmail"] = self.gmail_fetcher.fetch_messages(max_results=max_per_source)
        except Exception as e:
            logger.error(f"Error fetching Gmail: {e}")
       
        # Fetch Outlook
        try:
            results["outlook"] = self.outlook_fetcher.fetch_messages(max_results=max_per_source)
        except Exception as e:
            logger.error(f"Error fetching Outlook: {e}")
       
        # Fetch Teams
        try:
            results["teams"] = self.teams_fetcher.fetch_messages(max_results=max_per_source)
        except Exception as e:
            logger.error(f"Error fetching Teams: {e}")
       
        total = sum(len(msgs) for msgs in results.values())
        logger.info(f"Fetched total of {total} messages from all sources")
       
        return results
   
    def fetch_all_events(self, days_ahead: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch calendar events from all sources.
       
        Args:
            days_ahead: Number of days ahead to fetch events for
           
        Returns:
            Dictionary with keys: 'google_calendar', 'microsoft_calendar'
            Each containing list of raw events
        """
        logger.info(f"Fetching calendar events for next {days_ahead} days...")
       
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
       
        results = {
            "google_calendar": [],
            "microsoft_calendar": []
        }
       
        # Fetch Google Calendar
        try:
            results["google_calendar"] = self.calendar_fetcher.fetch_google_events(
                time_min=time_min,
                time_max=time_max
            )
        except Exception as e:
            logger.error(f"Error fetching Google Calendar: {e}")
       
        # Fetch Microsoft Calendar
        try:
            results["microsoft_calendar"] = self.calendar_fetcher.fetch_microsoft_events(
                start_date=time_min,
                end_date=time_max
            )
        except Exception as e:
            logger.error(f"Error fetching Microsoft Calendar: {e}")
       
        total = sum(len(events) for events in results.values())
        logger.info(f"Fetched total of {total} events from all sources")
       
        return results