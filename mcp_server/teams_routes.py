"""
Microsoft Teams routes and business logic for MCP server.
Handles Microsoft Graph Teams and Chats API interactions.
"""

import os
import logging
import requests
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from mcp_server.utils.msgraph_auth import get_msgraph_headers

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create router for Teams endpoints
router = APIRouter(prefix="/teams", tags=["Microsoft Teams"])

# Microsoft Graph API base URL
MSGRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Default Team/Channel IDs from environment (optional)
DEFAULT_TEAM_ID = os.getenv('TEAM_ID')
DEFAULT_CHANNEL_ID = os.getenv('CHANNEL_ID')

# --- Teams Models ---

class TeamsMessage(BaseModel):
    """Represents a Teams channel message"""
    id: Optional[str] = None
    messageType: Optional[str] = None
    createdDateTime: Optional[str] = None
    lastModifiedDateTime: Optional[str] = None
    deletedDateTime: Optional[str] = None
    subject: Optional[str] = None
    summary: Optional[str] = None
    importance: Optional[str] = None
    from_: Optional[Dict[str, Any]] = Field(None, alias='from')
    body: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class ChatMessage(BaseModel):
    """Represents a Teams chat message"""
    id: Optional[str] = None
    messageType: Optional[str] = None
    createdDateTime: Optional[str] = None
    lastModifiedDateTime: Optional[str] = None
    from_: Optional[Dict[str, Any]] = Field(None, alias='from')
    body: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class SendChannelMessageRequest(BaseModel):
    """Request to send a message to a Teams channel"""
    content: str = Field(..., description="Message content")
    content_type: Optional[str] = Field("text", description="text or html")


class SendChatMessageRequest(BaseModel):
    """Request to send a message to a Teams chat"""
    content: str = Field(..., description="Message content")
    content_type: Optional[str] = Field("text", description="text or html")


# --- Teams Business Logic ---

def list_teams() -> Optional[Dict[str, Any]]:
    """List all teams the user is a member of"""
    logger.info("[TEAMS] Listing all teams user is member of")
    
    headers = get_msgraph_headers()
    if not headers:
        logger.error("[TEAMS] Failed to get authentication headers - headers are empty")
        logger.error("[TEAMS] This usually means CLIENT_ID is not configured or authentication failed")
        return None
    
    logger.debug(f"[TEAMS] Got authentication headers: {list(headers.keys())}")
    url = f"{MSGRAPH_BASE_URL}/me/joinedTeams"
    logger.info(f"[TEAMS] Making request to: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"[TEAMS] Response status code: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        logger.info(f"[TEAMS] Successfully retrieved {len(data.get('value', []))} teams")
        return data
    except requests.exceptions.HTTPError as e:
        logger.error(f"[TEAMS] HTTP error listing teams: {e}", exc_info=True)
        logger.error(f"[TEAMS] Response status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
        logger.error(f"[TEAMS] Response body: {e.response.text if hasattr(e, 'response') else 'unknown'}")
        return None
    except Exception as e:
        logger.error(f"[TEAMS] Unexpected error listing teams: {e}", exc_info=True)
        return None


def get_team(team_id: str) -> Optional[Dict[str, Any]]:
    """Get details of a specific team"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/teams/{team_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting team: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error getting team: {e}", exc_info=True)
        return None


def list_channels(team_id: str) -> Optional[Dict[str, Any]]:
    """List all channels in a team"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/teams/{team_id}/channels"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing channels: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error listing channels: {e}", exc_info=True)
        return None


def list_channel_messages(
    team_id: str,
    channel_id: str,
    max_results: int = 20
) -> Optional[Dict[str, Any]]:
    """
    List messages from a Teams channel.
    
    Args:
        team_id: Team ID
        channel_id: Channel ID
        max_results: Maximum number of messages to return (default: 20)
    """
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/teams/{team_id}/channels/{channel_id}/messages"
    params = {"$top": max_results}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing channel messages: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error listing channel messages: {e}", exc_info=True)
        return None


def get_channel_message(
    team_id: str,
    channel_id: str,
    message_id: str
) -> Optional[Dict[str, Any]]:
    """Get a specific channel message"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting channel message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error getting channel message: {e}", exc_info=True)
        return None


def send_channel_message(
    team_id: str,
    channel_id: str,
    content: str,
    content_type: str = "text"
) -> Optional[Dict[str, Any]]:
    """Send a message to a Teams channel"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/teams/{team_id}/channels/{channel_id}/messages"
    
    message_data = {
        "body": {
            "contentType": "html" if content_type.lower() == "html" else "text",
            "content": content
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=message_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error sending channel message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error sending channel message: {e}", exc_info=True)
        return None


def list_chats(max_results: int = 20) -> Optional[Dict[str, Any]]:
    """List all chats the user is part of (both 1:1 and group chats)"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats"
    params = {"$top": max_results, "$expand": "members"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing chats: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error listing chats: {e}", exc_info=True)
        return None


async def list_chats_async(max_results: int = 20) -> Optional[Dict[str, Any]]:
    """Async: List all chats (1:1 and group)"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats"
    params = {"$top": str(max_results), "$expand": "members"}
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"HTTP {response.status} listing chats: {error_text}")
                    return None
                return await response.json()
    except Exception as e:
        logger.error(f"Error listing chats async: {e}", exc_info=True)
        return None


def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    """Get details of a specific chat"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats/{chat_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting chat: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error getting chat: {e}", exc_info=True)
        return None


def list_chat_messages(
    chat_id: str,
    max_results: int = 20
) -> Optional[Dict[str, Any]]:
    """List messages from a specific chat"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats/{chat_id}/messages"
    params = {"$top": max_results}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing chat messages: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error listing chat messages: {e}", exc_info=True)
        return None


async def list_chat_messages_async(
    chat_id: str,
    max_results: int = 20,
    session: aiohttp.ClientSession = None
) -> Optional[Dict[str, Any]]:
    """Async: List messages from a specific chat"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats/{chat_id}/messages"
    params = {"$top": str(max_results)}
    
    try:
        close_session = False
        if session is None:
            session = aiohttp.ClientSession(headers=headers)
            close_session = True
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.warning(f"HTTP {response.status} for chat {chat_id}: {error_text[:200]}")
                    return {"value": []}  # Return empty instead of None
                
                data = await response.json()
                # Add chat_id to each message for tracking
                if data and "value" in data:
                    for msg in data["value"]:
                        msg["_chatId"] = chat_id
                return data
        finally:
            if close_session:
                await session.close()
    except Exception as e:
        logger.warning(f"Error listing chat messages async for {chat_id}: {e}")
        return {"value": []}  # Return empty instead of None


async def get_all_chat_messages_async(
    max_chats: int = 20,
    max_messages_per_chat: int = 30
) -> List[Dict[str, Any]]:
    """
    Async: Get all messages from all chats (1:1 and group chats).
    Optimized with concurrent requests.
    
    Args:
        max_chats: Maximum number of chats to fetch from
        max_messages_per_chat: Maximum messages per chat
        
    Returns:
        Combined list of all chat messages
    """
    # Step 1: Get all chats
    chats_data = await list_chats_async(max_results=max_chats)
    if not chats_data or "value" not in chats_data:
        logger.warning("No chats found or failed to fetch chats")
        return []
    
    chats = chats_data["value"]
    logger.info(f"Found {len(chats)} chats (1:1 and groups)")
    
    if not chats:
        return []
    
    # Step 2: Fetch messages from all chats concurrently
    all_messages = []
    headers = get_msgraph_headers()
    if not headers:
        logger.error("No auth headers available")
        return []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Create tasks for all chats
        tasks = []
        for chat in chats[:max_chats]:
            chat_id = chat.get("id")
            if chat_id:
                task = list_chat_messages_async(chat_id, max_messages_per_chat, session)
                tasks.append((chat_id, chat, task))
        
        if not tasks:
            logger.warning("No chat tasks to execute")
            return []
        
        # Execute all tasks concurrently
        logger.info(f"Fetching messages from {len(tasks)} chats concurrently...")
        results = await asyncio.gather(*[task for _, _, task in tasks], return_exceptions=True)
        
        # Process results
        for (chat_id, chat, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.warning(f"Exception fetching from chat {chat_id}: {result}")
                continue
            
            if not result or "value" not in result:
                logger.debug(f"No messages in chat {chat_id}")
                continue
                
            messages = result["value"]
            if not messages:
                continue
            
            # Enrich messages with chat context
            chat_type = chat.get("chatType", "unknown")
            chat_topic = chat.get("topic", "")
            
            for msg in messages:
                msg["_chatId"] = chat_id
                msg["_chatType"] = chat_type  # "oneOnOne" or "group"
                msg["_chatTopic"] = chat_topic
                
            all_messages.extend(messages)
            logger.debug(f"Added {len(messages)} messages from chat {chat_id} (type: {chat_type})")
    
    logger.info(f"Total messages fetched: {len(all_messages)} from {len(tasks)} chats")
    return all_messages


def get_chat_message(
    chat_id: str,
    message_id: str
) -> Optional[Dict[str, Any]]:
    """Get a specific chat message"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats/{chat_id}/messages/{message_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting chat message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error getting chat message: {e}", exc_info=True)
        return None


def send_chat_message(
    chat_id: str,
    content: str,
    content_type: str = "text"
) -> Optional[Dict[str, Any]]:
    """Send a message to a Teams chat"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/chats/{chat_id}/messages"
    
    message_data = {
        "body": {
            "contentType": "html" if content_type.lower() == "html" else "text",
            "content": content
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=message_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error sending chat message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error sending chat message: {e}", exc_info=True)
        return None


# --- Teams Endpoints ---

@router.get(
    "",
    summary="List Teams",
    operation_id="teams_list_teams"
)
def teams_list_teams_endpoint():
    """List all teams the user is a member of"""
    result = list_teams()
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list teams")
    return result


@router.get(
    "/{team_id}",
    summary="Get Team",
    operation_id="teams_get_team"
)
def teams_get_team_endpoint(
    team_id: str = Path(..., description="Team ID")
):
    """Get details of a specific team"""
    result = get_team(team_id=team_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Team not found or API error")
    return result


@router.get(
    "/{team_id}/channels",
    summary="List Channels",
    operation_id="teams_list_channels"
)
def teams_list_channels_endpoint(
    team_id: str = Path(..., description="Team ID")
):
    """List all channels in a team"""
    result = list_channels(team_id=team_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list channels")
    return result


@router.get(
    "/{team_id}/channels/{channel_id}/messages",
    summary="List Channel Messages",
    operation_id="teams_list_channel_messages"
)
def teams_list_channel_messages_endpoint(
    team_id: str = Path(..., description="Team ID"),
    channel_id: str = Path(..., description="Channel ID"),
    max_results: int = Query(20, ge=1, le=1000, description="Maximum number of messages")
):
    """List messages from a Teams channel"""
    result = list_channel_messages(team_id=team_id, channel_id=channel_id, max_results=max_results)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list channel messages")
    return result


@router.get(
    "/{team_id}/channels/{channel_id}/messages/{message_id}",
    summary="Get Channel Message",
    operation_id="teams_get_channel_message"
)
def teams_get_channel_message_endpoint(
    team_id: str = Path(..., description="Team ID"),
    channel_id: str = Path(..., description="Channel ID"),
    message_id: str = Path(..., description="Message ID")
):
    """Get a specific channel message"""
    result = get_channel_message(team_id=team_id, channel_id=channel_id, message_id=message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Message not found or API error")
    return result


@router.post(
    "/{team_id}/channels/{channel_id}/messages",
    summary="Send Channel Message",
    operation_id="teams_send_channel_message"
)
def teams_send_channel_message_endpoint(
    team_id: str = Path(..., description="Team ID"),
    channel_id: str = Path(..., description="Channel ID"),
    request: SendChannelMessageRequest = Body(...)
):
    """Send a message to a Teams channel"""
    result = send_channel_message(
        team_id=team_id,
        channel_id=channel_id,
        content=request.content,
        content_type=request.content_type
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to send channel message")
    return result


@router.get(
    "/joined",
    summary="List Joined Teams",
    operation_id="teams_list_joined"
)
def teams_list_joined_endpoint():
    """List all teams the user has joined (same as list teams)"""
    result = list_teams()
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list joined teams")
    return result


@router.get(
    "/chats",
    summary="List Chats",
    operation_id="teams_list_chats"
)
def teams_list_chats_endpoint(
    max_results: int = Query(20, ge=1, le=1000, description="Maximum number of chats")
):
    """List all chats the user is part of (1:1 and group chats)"""
    result = list_chats(max_results=max_results)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list chats")
    return result


@router.get(
    "/chats/all/messages",
    summary="Get All Chat Messages (Optimized)",
    operation_id="teams_get_all_chat_messages"
)
async def teams_get_all_chat_messages_endpoint(
    max_chats: int = Query(20, ge=1, le=50, description="Maximum number of chats to fetch from"),
    max_messages_per_chat: int = Query(30, ge=1, le=100, description="Maximum messages per chat")
):
    """
    Get all messages from all chats (1:1 and group chats) in one optimized call.
    Uses async/concurrent requests for speed.
    
    Returns combined messages from all chats with chat context.
    """
    try:
        messages = await get_all_chat_messages_async(
            max_chats=max_chats,
            max_messages_per_chat=max_messages_per_chat
        )
        
        return {
            "value": messages,
            "total_messages": len(messages),
            "note": "Messages from both 1:1 and group chats"
        }
    except Exception as e:
        logger.error(f"Error in get_all_chat_messages endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat messages: {str(e)}")


@router.get(
    "/chats/{chat_id}",
    summary="Get Chat",
    operation_id="teams_get_chat"
)
def teams_get_chat_endpoint(
    chat_id: str = Path(..., description="Chat ID")
):
    """Get details of a specific chat"""
    result = get_chat(chat_id=chat_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Chat not found or API error")
    return result


@router.get(
    "/chats/{chat_id}/messages",
    summary="List Chat Messages",
    operation_id="teams_list_chat_messages"
)
def teams_list_chat_messages_endpoint(
    chat_id: str = Path(..., description="Chat ID"),
    max_results: int = Query(20, ge=1, le=1000, description="Maximum number of messages")
):
    """List messages from a specific chat"""
    result = list_chat_messages(chat_id=chat_id, max_results=max_results)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list chat messages")
    return result


@router.get(
    "/chats/{chat_id}/messages/{message_id}",
    summary="Get Chat Message",
    operation_id="teams_get_chat_message"
)
def teams_get_chat_message_endpoint(
    chat_id: str = Path(..., description="Chat ID"),
    message_id: str = Path(..., description="Message ID")
):
    """Get a specific chat message"""
    result = get_chat_message(chat_id=chat_id, message_id=message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Message not found or API error")
    return result


@router.post(
    "/chats/{chat_id}/messages",
    summary="Send Chat Message",
    operation_id="teams_send_chat_message"
)
def teams_send_chat_message_endpoint(
    chat_id: str = Path(..., description="Chat ID"),
    request: SendChatMessageRequest = Body(...)
):
    """Send a message to a Teams chat"""
    result = send_chat_message(
        chat_id=chat_id,
        content=request.content,
        content_type=request.content_type
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to send chat message")
    return result


# --- Convenience Endpoints Using Default TEAM_ID/CHANNEL_ID from Environment ---

@router.get(
    "/default/channels",
    summary="List Channels (Default Team)",
    operation_id="teams_list_default_channels"
)
def teams_list_default_channels_endpoint():
    """List channels in the default team (from TEAM_ID env var)"""
    if not DEFAULT_TEAM_ID:
        raise HTTPException(
            status_code=400,
            detail="TEAM_ID not set in environment. Either set TEAM_ID in .env or use /teams/{team_id}/channels endpoint."
        )
    result = list_channels(team_id=DEFAULT_TEAM_ID)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list channels")
    return result


@router.get(
    "/default/messages",
    summary="List Messages (Default Team/Channel)",
    operation_id="teams_list_default_messages"
)
def teams_list_default_messages_endpoint(
    max_results: int = Query(20, ge=1, le=1000, description="Maximum number of messages")
):
    """List messages from the default team/channel (from TEAM_ID and CHANNEL_ID env vars)"""
    if not DEFAULT_TEAM_ID:
        raise HTTPException(
            status_code=400,
            detail="TEAM_ID not set in environment. Set TEAM_ID in .env or use the full endpoint."
        )
    if not DEFAULT_CHANNEL_ID:
        raise HTTPException(
            status_code=400,
            detail="CHANNEL_ID not set in environment. Set CHANNEL_ID in .env or use the full endpoint."
        )
    result = list_channel_messages(
        team_id=DEFAULT_TEAM_ID,
        channel_id=DEFAULT_CHANNEL_ID,
        max_results=max_results
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list channel messages")
    return result


@router.post(
    "/default/messages",
    summary="Send Message (Default Team/Channel)",
    operation_id="teams_send_default_message"
)
def teams_send_default_message_endpoint(
    request: SendChannelMessageRequest = Body(...)
):
    """Send a message to the default team/channel (from TEAM_ID and CHANNEL_ID env vars)"""
    if not DEFAULT_TEAM_ID:
        raise HTTPException(
            status_code=400,
            detail="TEAM_ID not set in environment. Set TEAM_ID in .env or use the full endpoint."
        )
    if not DEFAULT_CHANNEL_ID:
        raise HTTPException(
            status_code=400,
            detail="CHANNEL_ID not set in environment. Set CHANNEL_ID in .env or use the full endpoint."
        )
    result = send_channel_message(
        team_id=DEFAULT_TEAM_ID,
        channel_id=DEFAULT_CHANNEL_ID,
        content=request.content,
        content_type=request.content_type
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to send channel message")
    return result


@router.get(
    "/default/info",
    summary="Get Default Team/Channel Info",
    operation_id="teams_default_info"
)
def teams_default_info_endpoint():
    """Show the current default TEAM_ID and CHANNEL_ID from environment"""
    return {
        "team_id": DEFAULT_TEAM_ID,
        "channel_id": DEFAULT_CHANNEL_ID,
        "configured": bool(DEFAULT_TEAM_ID and DEFAULT_CHANNEL_ID),
        "message": "Set TEAM_ID and CHANNEL_ID in .env to use /teams/default/* endpoints"
    }

