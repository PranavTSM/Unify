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
        Fetch Gmail messages (2-step: get IDs, then fetch full messages).
       
        Args:
            max_results: Maximum number of messages to fetch
            query: Gmail search query
           
        Returns:
            List of full Gmail message objects
        """
        # Step 1: Get message IDs
        params = {"max_results": max_results}
        if query:
            params["q"] = query
       
        data = self._get("/gmail/messages", params=params)
        if not data or "messages" not in data:
            logger.warning("No Gmail messages found")
            return []
        
        message_ids = data["messages"]
        logger.info(f"Found {len(message_ids)} Gmail message IDs")
        
        # Step 2: Fetch full message details for each ID (with format=full to get body)
        full_messages = []
        for msg_stub in message_ids[:max_results]:  # Limit to max_results
            msg_id = msg_stub.get("id")
            if not msg_id:
                continue
            
            try:
                # IMPORTANT: format=full includes payload with headers and body
                full_msg = self._get(f"/gmail/messages/{msg_id}", params={"format": "full"})
                if full_msg:
                    full_messages.append(full_msg)
                else:
                    logger.warning(f"Empty response for Gmail message {msg_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch Gmail message {msg_id}: {e}")
                continue
        
        logger.info(f"Fetched {len(full_messages)} full Gmail messages (with body)")
        return full_messages
 
 
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
            logger.info(f"Fetched {len(data)} Teams channel messages")
            return data
        elif data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} Teams channel messages")
            return data["value"]
        return []
    
    def fetch_chats(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Teams 1:1 chats.
        
        Args:
            max_results: Maximum number of chats to fetch
            
        Returns:
            List of raw Teams chat objects
        """
        endpoint = "/teams/chats"
        params = {"max_results": max_results}
        
        data = self._get(endpoint, params=params)
        if data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} Teams chats")
            return data["value"]
        return []
    
    def fetch_chat_messages(self, chat_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific chat.
        
        Args:
            chat_id: Chat ID
            max_results: Maximum number of messages
            
        Returns:
            List of chat messages
        """
        endpoint = f"/teams/chats/{chat_id}/messages"
        params = {"max_results": max_results}
        
        data = self._get(endpoint, params=params)
        if data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} messages from chat {chat_id}")
            return data["value"]
        return []
    
    def fetch_all_joined_teams(self) -> List[Dict[str, Any]]:
        """Fetch all teams the user has joined."""
        data = self._get("/teams/joined")
        if data and "value" in data:
            logger.info(f"Fetched {len(data['value'])} joined teams")
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
    
    def fetch_all_teams_messages(self, max_per_team: int = 20) -> List[Dict[str, Any]]:
        """
        Optimized: Fetch messages from all joined teams and channels.
        Prevents over-fetching with smart limits.
        
        Args:
            max_per_team: Maximum messages per team/channel
            
        Returns:
            Combined list of all Teams messages (deduplicated)
        """
        all_messages = []
        seen_ids = set()  # Prevent duplicates
        
        try:
            # Fetch 1:1 chats first (higher priority)
            try:
                chats = self.fetch_chats(max_results=5)  # Reduced from 10
                for chat in chats[:5]:
                    chat_id = chat.get('id')
                    if chat_id:
                        try:
                            chat_messages = self.fetch_chat_messages(chat_id, max_results=10)  # Reduced from 20
                            for msg in chat_messages:
                                msg_id = msg.get('id')
                                if msg_id and msg_id not in seen_ids:
                                    seen_ids.add(msg_id)
                                    all_messages.append(msg)
                        except Exception as e:
                            logger.warning(f"Error fetching chat {chat_id}: {e}")
            except Exception as e:
                logger.warning(f"Error fetching chats: {e}")
            
            # Then fetch team channels (limit total to prevent timeout)
            teams = self.fetch_all_joined_teams()
            logger.info(f"Fetching from {min(len(teams), 3)} teams")  # Reduced from 5
            
            for team in teams[:3]:  # Reduced from 5
                team_id = team.get('id')
                if not team_id:
                    continue
                
                channels = self.fetch_channels(team_id)
                
                for channel in channels[:2]:  # Reduced from 3
                    channel_id = channel.get('id')
                    if not channel_id:
                        continue
                    
                    try:
                        messages = self.fetch_messages(team_id, channel_id, 10)  # Reduced per channel
                        for msg in messages:
                            msg_id = msg.get('id')
                            if msg_id and msg_id not in seen_ids:
                                seen_ids.add(msg_id)
                                all_messages.append(msg)
                    except Exception as e:
                        logger.warning(f"Error fetching from team {team_id}, channel {channel_id}: {e}")
                        continue
            
            logger.info(f"Fetched {len(all_messages)} unique Teams messages")
            return all_messages
            
        except Exception as e:
            logger.error(f"Error in fetch_all_teams_messages: {e}")
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
       
        # Fetch Teams (all joined teams + channels + chats)
        try:
            results["teams"] = self.teams_fetcher.fetch_all_teams_messages(max_per_team=max_per_source)
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