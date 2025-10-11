"""
Outlook routes and business logic for MCP server.
Handles Outlook/Microsoft Graph Mail API interactions.
"""

import logging
import requests
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field, EmailStr

from mcp_server.utils.msgraph_auth import get_msgraph_headers

logger = logging.getLogger(__name__)

# Create router for Outlook endpoints
router = APIRouter(prefix="/outlook", tags=["Outlook"])

# Microsoft Graph API base URL
MSGRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# --- Outlook Models ---

class OutlookMessage(BaseModel):
    """Represents an Outlook email message"""
    id: Optional[str] = None
    subject: Optional[str] = None
    bodyPreview: Optional[str] = None
    from_: Optional[Dict[str, Any]] = Field(None, alias='from')
    toRecipients: Optional[List[Dict[str, Any]]] = None
    ccRecipients: Optional[List[Dict[str, Any]]] = None
    receivedDateTime: Optional[str] = None
    sentDateTime: Optional[str] = None
    hasAttachments: Optional[bool] = None
    importance: Optional[str] = None
    isRead: Optional[bool] = None
    webLink: Optional[str] = None
    
    class Config:
        populate_by_name = True


class SendEmailRequest(BaseModel):
    """Request to send an email"""
    subject: str
    body: str
    to_recipients: List[EmailStr] = Field(..., description="List of recipient email addresses")
    cc_recipients: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    importance: Optional[str] = Field("normal", description="normal, low, or high")
    content_type: Optional[str] = Field("text", description="text or html")


class CreateDraftRequest(BaseModel):
    """Request to create a draft email"""
    subject: str
    body: str
    to_recipients: List[EmailStr]
    cc_recipients: Optional[List[EmailStr]] = None
    importance: Optional[str] = "normal"
    content_type: Optional[str] = "text"


class UpdateMessageRequest(BaseModel):
    """Request to update message properties"""
    is_read: Optional[bool] = Field(None, alias='isRead')
    categories: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True


class MoveMessageRequest(BaseModel):
    """Request to move a message to a folder"""
    destination_folder_id: str = Field(..., description="ID of the destination folder")


# --- Outlook Business Logic ---

def list_messages(
    folder: str = "inbox",
    max_results: int = 20,
    filter_query: Optional[str] = None,
    search: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    List messages from an Outlook folder.
    
    Args:
        folder: Folder name (inbox, sentitems, drafts, deleteditems)
        max_results: Maximum number of messages to return
        filter_query: OData filter query
        search: Search query string
    """
    logger.info(f"[OUTLOOK] Listing messages from folder: {folder}, max_results: {max_results}")
    
    headers = get_msgraph_headers()
    if not headers:
        logger.error("[OUTLOOK] Failed to get authentication headers - headers are empty")
        logger.error("[OUTLOOK] This usually means CLIENT_ID is not configured or authentication failed")
        return None
    
    logger.debug(f"[OUTLOOK] Got authentication headers: {list(headers.keys())}")
    
    # Build URL based on folder
    if folder.lower() == "inbox":
        url = f"{MSGRAPH_BASE_URL}/me/mailFolders/inbox/messages"
    elif folder.lower() == "sentitems":
        url = f"{MSGRAPH_BASE_URL}/me/mailFolders/sentitems/messages"
    elif folder.lower() == "drafts":
        url = f"{MSGRAPH_BASE_URL}/me/mailFolders/drafts/messages"
    else:
        # Try as folder ID or name
        url = f"{MSGRAPH_BASE_URL}/me/mailFolders/{folder}/messages"
    
    params = {
        "$top": max_results,
        "$orderby": "receivedDateTime DESC"
    }
    
    if filter_query:
        params["$filter"] = filter_query
    
    if search:
        params["$search"] = f'"{search}"'
    
    logger.info(f"[OUTLOOK] Making request to: {url}")
    logger.debug(f"[OUTLOOK] Request params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"[OUTLOOK] Response status code: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        logger.info(f"[OUTLOOK] Successfully retrieved {len(data.get('value', []))} messages")
        return data
    except requests.exceptions.HTTPError as e:
        logger.error(f"[OUTLOOK] HTTP error listing messages: {e}", exc_info=True)
        logger.error(f"[OUTLOOK] Response status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
        logger.error(f"[OUTLOOK] Response body: {e.response.text if hasattr(e, 'response') else 'unknown'}")
        return None
    except Exception as e:
        logger.error(f"[OUTLOOK] Unexpected error listing messages: {e}", exc_info=True)
        return None


def get_message(message_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific message by ID"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/messages/{message_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error getting message: {e}", exc_info=True)
        return None


def send_email(
    subject: str,
    body: str,
    to_recipients: List[str],
    cc_recipients: Optional[List[str]] = None,
    importance: str = "normal",
    content_type: str = "text"
) -> bool:
    """Send an email via Outlook"""
    headers = get_msgraph_headers()
    if not headers:
        return False
    
    url = f"{MSGRAPH_BASE_URL}/me/sendMail"
    
    # Build recipient list
    to_list = [{"emailAddress": {"address": email}} for email in to_recipients]
    cc_list = [{"emailAddress": {"address": email}} for email in (cc_recipients or [])]
    
    message_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML" if content_type.lower() == "html" else "Text",
                "content": body
            },
            "toRecipients": to_list,
            "importance": importance
        }
    }
    
    if cc_list:
        message_data["message"]["ccRecipients"] = cc_list
    
    try:
        response = requests.post(url, headers=headers, json=message_data)
        response.raise_for_status()
        logger.info(f"Email sent successfully to {to_recipients}")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error sending email: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        return False


def create_draft(
    subject: str,
    body: str,
    to_recipients: List[str],
    cc_recipients: Optional[List[str]] = None,
    importance: str = "normal",
    content_type: str = "text"
) -> Optional[Dict[str, Any]]:
    """Create a draft email"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/messages"
    
    to_list = [{"emailAddress": {"address": email}} for email in to_recipients]
    cc_list = [{"emailAddress": {"address": email}} for email in (cc_recipients or [])]
    
    draft_data = {
        "subject": subject,
        "body": {
            "contentType": "HTML" if content_type.lower() == "html" else "Text",
            "content": body
        },
        "toRecipients": to_list,
        "importance": importance
    }
    
    if cc_list:
        draft_data["ccRecipients"] = cc_list
    
    try:
        response = requests.post(url, headers=headers, json=draft_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error creating draft: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error creating draft: {e}", exc_info=True)
        return None


def update_message(message_id: str, is_read: Optional[bool] = None, categories: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Update message properties (mark as read, add categories, etc.)"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/messages/{message_id}"
    
    update_data = {}
    if is_read is not None:
        update_data["isRead"] = is_read
    if categories is not None:
        update_data["categories"] = categories
    
    if not update_data:
        logger.warning("No update data provided")
        return None
    
    try:
        response = requests.patch(url, headers=headers, json=update_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error updating message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error updating message: {e}", exc_info=True)
        return None


def delete_message(message_id: str) -> bool:
    """Delete a message"""
    headers = get_msgraph_headers()
    if not headers:
        return False
    
    url = f"{MSGRAPH_BASE_URL}/me/messages/{message_id}"
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Message {message_id} deleted successfully")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error deleting message: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Error deleting message: {e}", exc_info=True)
        return False


def move_message(message_id: str, destination_folder_id: str) -> Optional[Dict[str, Any]]:
    """Move a message to another folder"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/messages/{message_id}/move"
    
    move_data = {
        "destinationId": destination_folder_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=move_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error moving message: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error moving message: {e}", exc_info=True)
        return None


def list_folders() -> Optional[Dict[str, Any]]:
    """List all mail folders"""
    headers = get_msgraph_headers()
    if not headers:
        return None
    
    url = f"{MSGRAPH_BASE_URL}/me/mailFolders"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error listing folders: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error listing folders: {e}", exc_info=True)
        return None


# --- Outlook Endpoints ---

@router.get(
    "/messages",
    summary="List Outlook messages",
    operation_id="outlook_list_messages"
)
def outlook_list_messages_endpoint(
    folder: str = Query("inbox", description="Folder name (inbox, sentitems, drafts, deleteditems)"),
    max_results: int = Query(20, ge=1, le=1000, description="Maximum number of messages"),
    filter_query: Optional[str] = Query(None, description="OData filter query"),
    search: Optional[str] = Query(None, description="Search query")
):
    """List messages from an Outlook folder"""
    result = list_messages(folder=folder, max_results=max_results, filter_query=filter_query, search=search)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list Outlook messages")
    return result


@router.get(
    "/messages/{message_id}",
    summary="Get Outlook message",
    operation_id="outlook_get_message"
)
def outlook_get_message_endpoint(
    message_id: str = Path(..., description="Message ID")
):
    """Get a specific Outlook message by ID"""
    result = get_message(message_id=message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Message not found or API error")
    return result


@router.post(
    "/messages/send",
    summary="Send email via Outlook",
    operation_id="outlook_send_email"
)
def outlook_send_email_endpoint(
    request: SendEmailRequest
):
    """Send an email via Outlook"""
    success = send_email(
        subject=request.subject,
        body=request.body,
        to_recipients=request.to_recipients,
        cc_recipients=request.cc_recipients,
        importance=request.importance,
        content_type=request.content_type
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"status": "sent", "message": "Email sent successfully"}


@router.post(
    "/messages/draft",
    summary="Create draft email",
    operation_id="outlook_create_draft"
)
def outlook_create_draft_endpoint(
    request: CreateDraftRequest
):
    """Create a draft email in Outlook"""
    result = create_draft(
        subject=request.subject,
        body=request.body,
        to_recipients=request.to_recipients,
        cc_recipients=request.cc_recipients,
        importance=request.importance,
        content_type=request.content_type
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create draft")
    return result


@router.patch(
    "/messages/{message_id}",
    summary="Update message properties",
    operation_id="outlook_update_message"
)
def outlook_update_message_endpoint(
    message_id: str = Path(..., description="Message ID"),
    request: UpdateMessageRequest = Body(...)
):
    """Update message properties (e.g., mark as read)"""
    result = update_message(
        message_id=message_id,
        is_read=request.is_read,
        categories=request.categories
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to update message")
    return result


@router.delete(
    "/messages/{message_id}",
    status_code=204,
    summary="Delete message",
    operation_id="outlook_delete_message"
)
def outlook_delete_message_endpoint(
    message_id: str = Path(..., description="Message ID")
):
    """Delete an Outlook message"""
    success = delete_message(message_id=message_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    return None


@router.post(
    "/messages/{message_id}/move",
    summary="Move message to folder",
    operation_id="outlook_move_message"
)
def outlook_move_message_endpoint(
    message_id: str = Path(..., description="Message ID"),
    request: MoveMessageRequest = Body(...)
):
    """Move a message to another folder"""
    result = move_message(message_id=message_id, destination_folder_id=request.destination_folder_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to move message")
    return result


@router.get(
    "/folders",
    summary="List mail folders",
    operation_id="outlook_list_folders"
)
def outlook_list_folders_endpoint():
    """List all Outlook mail folders"""
    result = list_folders()
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to list folders")
    return result

