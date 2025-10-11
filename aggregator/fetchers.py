"""
Data Fetchers - Fetch raw JSON from MCP server endpoints
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    
    def _post(self, endpoint: str, json_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make POST request to MCP server."""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Posting to: {url}")
            response = self.session.post(url, json=json_data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(f"Bad request for {endpoint}: {e.response.text}")
            elif e.response.status_code == 404:
                logger.warning(f"Endpoint not found: {endpoint}")
            else:
                logger.error(f"HTTP error posting to {endpoint}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting to {endpoint}: {e}")
            return None
 
 
class GmailFetcher(MCPFetcher):
    """Fetch Gmail messages from MCP server."""
   
    def fetch_messages(self, max_results: int = 20, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch Gmail messages using BATCH fetching for better performance.
       
        Args:
            max_results: Maximum number of messages to fetch (default: 20)
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
        
        # Extract just the IDs
        ids_to_fetch = [msg.get("id") for msg in message_ids[:max_results] if msg.get("id")]
        
        if not ids_to_fetch:
            logger.warning("No valid message IDs to fetch")
            return []
        
        # Step 2: Batch fetch all messages in ONE request (much faster!)
        logger.info(f"Batch fetching {len(ids_to_fetch)} Gmail messages...")
        batch_data = self._post("/gmail/messages:batchGet", json_data={
            "message_ids": ids_to_fetch,
            "format": "full",
            "user_id": "me"
        })
        
        if not batch_data or "messages" not in batch_data:
            logger.warning("Batch fetch failed, falling back to individual fetches")
            # Fallback: fetch individually if batch fails
            return self._fetch_messages_individually(ids_to_fetch)
        
        full_messages = batch_data["messages"]
        logger.info(f"Successfully batch fetched {len(full_messages)} Gmail messages (with body)")
        return full_messages
    
    def _fetch_messages_individually(self, message_ids: List[str]) -> List[Dict[str, Any]]:
        """Fallback method: fetch messages one by one if batch fails."""
        logger.info("Using fallback: fetching messages individually...")
        full_messages = []
        for msg_id in message_ids:
            try:
                full_msg = self._get(f"/gmail/messages/{msg_id}", params={"format": "full"})
                if full_msg:
                    full_messages.append(full_msg)
            except Exception as e:
                logger.warning(f"Failed to fetch Gmail message {msg_id}: {e}")
                continue
        return full_messages
 
 
class OutlookFetcher(MCPFetcher):
    """Fetch Outlook messages from MCP server."""
   
    def fetch_messages(self, folder: str = "inbox", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch Outlook messages.
       
        Args:
            folder: Folder to fetch from (inbox, sent, drafts, etc.)
            max_results: Maximum number of messages to fetch (default: 20)
           
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
                      max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch Teams channel messages.
       
        Args:
            team_id: Team ID (uses default if not provided)
            channel_id: Channel ID (uses default if not provided)
            max_results: Maximum number of messages to fetch (default: 20)
           
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
    
    def fetch_chats(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch Teams 1:1 chats.
        
        Args:
            max_results: Maximum number of chats to fetch (default: 20)
            
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
    
    def fetch_chat_messages(self, chat_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific chat.
        
        Args:
            chat_id: Chat ID
            max_results: Maximum number of messages (default: 20)
            
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
        OPTIMIZED: Fetch all Teams messages using the new async endpoint.
        Gets 1:1 and group chats in ONE fast API call.
        
        Args:
            max_per_team: Maximum messages per chat
            
        Returns:
            Combined list of all Teams messages from chats and groups
        """
        try:
            # Use the new optimized endpoint that fetches everything concurrently
            logger.info("Using optimized /teams/chats/all/messages endpoint")
            
            data = self._get("/teams/chats/all/messages", params={
                "max_chats": 20,
                "max_messages_per_chat": max_per_team
            })
            
            if data and "value" in data:
                messages = data["value"]
                total = data.get("total_messages", len(messages))
                logger.info(f"Fetched {total} Teams messages via optimized endpoint (1:1 + groups)")
                return messages
            
            logger.warning("No messages from optimized endpoint, falling back...")
            return self._fetch_teams_messages_fallback(max_per_team)
            
        except Exception as e:
            logger.error(f"Error in fetch_all_teams_messages: {e}")
            return self._fetch_teams_messages_fallback(max_per_team)
    
    def _fetch_teams_messages_fallback(self, max_per_chat: int = 20) -> List[Dict[str, Any]]:
        """Fallback method if optimized endpoint fails"""
        logger.info("Using fallback method for Teams messages")
        all_messages = []
        seen_ids = set()
        
        try:
            # Fetch chats (1:1 and groups)
            chats = self.fetch_chats(max_results=10)
            for chat in chats[:10]:
                chat_id = chat.get('id')
                if chat_id:
                    try:
                        chat_messages = self.fetch_chat_messages(chat_id, max_results=max_per_chat)
                        for msg in chat_messages:
                            msg_id = msg.get('id')
                            if msg_id and msg_id not in seen_ids:
                                seen_ids.add(msg_id)
                                all_messages.append(msg)
                    except Exception as e:
                        logger.warning(f"Error fetching chat {chat_id}: {e}")
        except Exception as e:
            logger.warning(f"Error in fallback: {e}")
        
        logger.info(f"Fallback fetched {len(all_messages)} messages")
        return all_messages
 
 
class CalendarFetcher(MCPFetcher):
    """Fetch calendar events from MCP server."""
   
    def fetch_google_events(self, calendar_id: str = "primary",
                           time_min: Optional[str] = None,
                           time_max: Optional[str] = None,
                           max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch Google Calendar events.
       
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time (ISO format)
            time_max: End time (ISO format)
            max_results: Maximum number of events (default: 20)
           
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
   
    def fetch_all_messages(self, max_per_source: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch messages from all sources IN PARALLEL for maximum speed.
       
        Args:
            max_per_source: Maximum messages per source (default: 20)
       
        Returns:
            Dictionary with keys: 'gmail', 'outlook', 'teams'
            Each containing list of raw messages
        """
        logger.info("🚀 Fetching messages from all sources IN PARALLEL...")
        start_time = datetime.now()
       
        results = {
            "gmail": [],
            "outlook": [],
            "teams": []
        }
        
        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all fetch tasks simultaneously
            future_to_source = {
                executor.submit(self._fetch_gmail_safe, max_per_source): "gmail",
                executor.submit(self._fetch_outlook_safe, max_per_source): "outlook",
                executor.submit(self._fetch_teams_safe, max_per_source): "teams"
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results[source] = future.result()
                    logger.info(f"✅ {source}: fetched {len(results[source])} messages")
                except Exception as e:
                    logger.error(f"❌ {source}: Error - {e}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        total = sum(len(msgs) for msgs in results.values())
        logger.info(f"⚡ PARALLEL FETCH COMPLETE: {total} messages in {elapsed:.2f}s")
       
        return results
    
    def _fetch_gmail_safe(self, max_results: int) -> List[Dict[str, Any]]:
        """Safe wrapper for Gmail fetching with error handling."""
        try:
            return self.gmail_fetcher.fetch_messages(max_results=max_results)
        except Exception as e:
            logger.error(f"Error fetching Gmail: {e}")
            return []
    
    def _fetch_outlook_safe(self, max_results: int) -> List[Dict[str, Any]]:
        """Safe wrapper for Outlook fetching with error handling."""
        try:
            return self.outlook_fetcher.fetch_messages(max_results=max_results)
        except Exception as e:
            logger.error(f"Error fetching Outlook: {e}")
            return []
    
    def _fetch_teams_safe(self, max_results: int) -> List[Dict[str, Any]]:
        """Safe wrapper for Teams fetching with error handling."""
        try:
            return self.teams_fetcher.fetch_all_teams_messages(max_per_team=max_results)
        except Exception as e:
            logger.error(f"Error fetching Teams: {e}")
            return []
   
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