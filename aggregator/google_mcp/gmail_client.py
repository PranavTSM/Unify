"""
Gmail MCP Client - Connects to the MCP server Gmail endpoints.
Provides all Gmail operations available in the MCP server.
"""

import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# MCP server base URL
MCP_BASE_URL = "http://localhost:8000"

def fetch_gmail_messages(
    query: Optional[str] = None,
    max_results: int = 50,
    label_ids: Optional[List[str]] = None,
    user_id: str = 'me'
) -> Dict[str, Any]:
    """
    Fetch Gmail messages from the MCP server.
    
    Args:
        query: Gmail search query
        max_results: Maximum number of messages to fetch
        label_ids: Filter by label IDs
        user_id: Gmail user id (default 'me')
        
    Returns:
        Dictionary with messages data from MCP server
    """
    try:
        params = {"max_results": max_results, "user_id": user_id}
        if query:
            params["q"] = query
        if label_ids:
            params["label_ids"] = label_ids
            
        response = requests.get(f"{MCP_BASE_URL}/gmail/messages", params=params)
        response.raise_for_status()
        
        messages = response.json().get('messages', [])
        logger.info(f"Fetched {len(messages)} Gmail messages")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Gmail messages: {e}")
        return {"error": str(e), "messages": []}

def get_gmail_message_detail(
    message_id: str, 
    format: str = "full",
    user_id: str = 'me'
) -> Dict[str, Any]:
    """
    Get detailed Gmail message from MCP server.
    
    Args:
        message_id: Gmail message ID
        format: Message format (minimal, full, raw, metadata)
        user_id: Gmail user id (default 'me')
        
    Returns:
        Message details
    """
    try:
        params = {"format": format, "user_id": user_id}
        response = requests.get(f"{MCP_BASE_URL}/gmail/messages/{message_id}", params=params)
        response.raise_for_status()
        
        logger.info(f"Fetched Gmail message {message_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Gmail message {message_id}: {e}")
        return {"error": str(e)}

def send_gmail_raw(
    raw_message: str,
    user_id: str = 'me'
) -> Dict[str, Any]:
    """
    Send a raw RFC 2822 formatted message via MCP server.
    
    Args:
        raw_message: Base64url-encoded RFC 2822 message
        user_id: Gmail user id (default 'me')
        
    Returns:
        Sent message details
    """
    try:
        data = {"raw": raw_message, "user_id": user_id}
        response = requests.post(f"{MCP_BASE_URL}/gmail/messages:sendRaw", json=data)
        response.raise_for_status()
        
        logger.info("Sent Gmail message successfully")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Gmail message: {e}")
        return {"error": str(e)}

def compose_and_send_gmail(
    from_addr: str,
    to_addrs: List[str],
    subject: str,
    body_text: str,
    user_id: str = 'me'
) -> Dict[str, Any]:
    """
    Compose and send a simple text email via MCP server.
    
    Args:
        from_addr: Sender email address
        to_addrs: List of recipient email addresses
        subject: Email subject
        body_text: Plain text body
        user_id: Gmail user id (default 'me')
        
    Returns:
        Sent message details
    """
    try:
        data = {
            "from_addr": from_addr,
            "to_addrs": to_addrs,
            "subject": subject,
            "body_text": body_text,
            "user_id": user_id
        }
        response = requests.post(f"{MCP_BASE_URL}/gmail/messages:composeAndSend", json=data)
        response.raise_for_status()
        
        logger.info(f"Composed and sent email: {subject}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to compose and send email: {e}")
        return {"error": str(e)}

def modify_gmail_labels(
    message_id: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    user_id: str = 'me'
) -> Dict[str, Any]:
    """
    Modify labels on a Gmail message via MCP server.
    
    Args:
        message_id: Gmail message ID
        add_labels: Labels to add (e.g., ['INBOX', 'UNREAD', 'Label_XXXX'])
        remove_labels: Labels to remove
        user_id: Gmail user id (default 'me')
        
    Returns:
        Modified message details
    """
    try:
        data = {"user_id": user_id}
        if add_labels:
            data["add_labels"] = add_labels
        if remove_labels:
            data["remove_labels"] = remove_labels
            
        response = requests.post(
            f"{MCP_BASE_URL}/gmail/messages/{message_id}:modify",
            json=data
        )
        response.raise_for_status()
        
        logger.info(f"Modified labels for message {message_id}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to modify labels for message {message_id}: {e}")
        return {"error": str(e)}

def list_gmail_labels(user_id: str = 'me') -> Dict[str, Any]:
    """
    List all Gmail labels from MCP server.
    
    Args:
        user_id: Gmail user id (default 'me')
        
    Returns:
        Dictionary with labels data
    """
    try:
        params = {"user_id": user_id}
        response = requests.get(f"{MCP_BASE_URL}/gmail/labels", params=params)
        response.raise_for_status()
        
        labels = response.json().get('labels', [])
        logger.info(f"Fetched {len(labels)} Gmail labels")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to list Gmail labels: {e}")
        return {"error": str(e), "labels": []}

def search_gmail_messages(
    query: str,
    max_results: int = 50,
    user_id: str = 'me'
) -> List[Dict[str, Any]]:
    """
    Search Gmail messages with a query.
    
    Args:
        query: Gmail search query (e.g., "from:john subject:report")
        max_results: Maximum number of results
        user_id: Gmail user id (default 'me')
        
    Returns:
        List of message dictionaries
    """
    result = fetch_gmail_messages(query=query, max_results=max_results, user_id=user_id)
    return result.get('messages', [])

def get_unread_gmail_messages(
    max_results: int = 50,
    user_id: str = 'me'
) -> List[Dict[str, Any]]:
    """
    Get unread Gmail messages.
    
    Args:
        max_results: Maximum number of results
        user_id: Gmail user id (default 'me')
        
    Returns:
        List of unread messages
    """
    result = fetch_gmail_messages(label_ids=['UNREAD'], max_results=max_results, user_id=user_id)
    return result.get('messages', [])

def mark_gmail_as_read(message_id: str, user_id: str = 'me') -> Dict[str, Any]:
    """
    Mark a Gmail message as read.
    
    Args:
        message_id: Gmail message ID
        user_id: Gmail user id (default 'me')
        
    Returns:
        Modified message details
    """
    return modify_gmail_labels(message_id, remove_labels=['UNREAD'], user_id=user_id)

def mark_gmail_as_unread(message_id: str, user_id: str = 'me') -> Dict[str, Any]:
    """
    Mark a Gmail message as unread.
    
    Args:
        message_id: Gmail message ID
        user_id: Gmail user id (default 'me')
        
    Returns:
        Modified message details
    """
    return modify_gmail_labels(message_id, add_labels=['UNREAD'], user_id=user_id)
