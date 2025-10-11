"""
Gmail routes and business logic for MCP server.
Handles Gmail API interactions and operations.
"""

import base64
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field, EmailStr
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Create router for Gmail endpoints
router = APIRouter(prefix="/gmail", tags=["Gmail"])

# --- Helper: Build Gmail service ---

def _get_gmail_service(credentials: Credentials):
    try:
        service = build('gmail', 'v1', credentials=credentials)
        logger.debug("Gmail service client created successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}", exc_info=True)
        raise

# --- Gmail Models ---

class SendRawEmailRequest(BaseModel):
    raw: str = Field(..., description="base64url-encoded RFC 2822 message")
    user_id: str = Field('me', description="Gmail user id (default 'me')")

class ComposeAndSendRequest(BaseModel):
    from_addr: EmailStr
    to_addrs: List[EmailStr]
    subject: str
    body_text: str
    user_id: str = 'me'

class ModifyLabelsRequest(BaseModel):
    add_labels: Optional[List[str]] = Field(None, description="Label IDs to add (e.g., INBOX, UNREAD, Label_XXXX)")
    remove_labels: Optional[List[str]] = Field(None, description="Label IDs to remove")
    user_id: str = 'me'

# --- Gmail Actions (Business Logic) ---

def list_messages(credentials: Credentials, user_id: str = 'me', query: Optional[str] = None, max_results: int = 50, label_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        kwargs: Dict[str, Any] = {"userId": user_id, "maxResults": max_results}
        if query:
            kwargs["q"] = query
        if label_ids:
            kwargs["labelIds"] = label_ids
        resp = service.users().messages().list(**kwargs).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (list_messages): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in list_messages: {e}", exc_info=True)
        return None


def get_message(credentials: Credentials, message_id: str, user_id: str = 'me', format: str = 'full') -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        resp = service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (get_message): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_message: {e}", exc_info=True)
        return None


def send_message_raw(credentials: Credentials, raw_message_base64url: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    """
    Send a message using a base64url-encoded raw RFC 2822 message.
    Caller is responsible for composing and encoding the raw message.
    """
    service = _get_gmail_service(credentials)
    try:
        body = {"raw": raw_message_base64url}
        resp = service.users().messages().send(userId=user_id, body=body).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (send_message_raw): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in send_message_raw: {e}", exc_info=True)
        return None


def list_labels(credentials: Credentials, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        resp = service.users().labels().list(userId=user_id).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (list_labels): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in list_labels: {e}", exc_info=True)
        return None


def build_raw_message(from_addr: str, to_addrs: List[str], subject: str, body_text: str) -> str:
    """
    Helper to compose a simple text email and return base64url-encoded raw string suitable for send_message_raw.
    """
    from email.mime.text import MIMEText

    mime = MIMEText(body_text)
    mime['to'] = ', '.join(to_addrs)
    mime['from'] = from_addr
    mime['subject'] = subject
    raw_bytes = base64.urlsafe_b64encode(mime.as_bytes())
    return raw_bytes.decode('utf-8')


def modify_message_labels(credentials: Credentials, message_id: str, add_labels: Optional[List[str]] = None, remove_labels: Optional[List[str]] = None, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    """Adds and/or removes labels from a Gmail message.

    Args:
        credentials: OAuth2 credentials
        message_id: Gmail message ID
        add_labels: List of label IDs to add (e.g., ['INBOX','UNREAD'] or custom Label_XXXX)
        remove_labels: List of label IDs to remove
        user_id: Gmail user, default 'me'
    """
    service = _get_gmail_service(credentials)
    try:
        body: Dict[str, Any] = {}
        if add_labels:
            body['addLabelIds'] = add_labels
        if remove_labels:
            body['removeLabelIds'] = remove_labels
        resp = service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (modify_message_labels): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in modify_message_labels: {e}", exc_info=True)
        return None

# --- Gmail Endpoints (will be registered with credentials dependency) ---
# These will be added to the router in app.py with the credentials dependency

def register_endpoints(get_current_credentials):
    """
    Register Gmail endpoints with the router.
    Called from app.py to inject the credentials dependency.
    """
    
    @router.get(
        "/messages",
        summary="List Gmail messages",
        operation_id="gmail_list_messages"
    )
    def gmail_list_messages_endpoint(
        q: Optional[str] = Query(None, description="Gmail search query"),
        max_results: int = Query(50, ge=1, le=500),
        label_ids: Optional[List[str]] = Query(None, description="Filter by label IDs"),
        user_id: str = Query('me', description="User id"),
        creds: Credentials = Depends(get_current_credentials)
    ):
        result = list_messages(credentials=creds, user_id=user_id, query=q, max_results=max_results, label_ids=label_ids)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to list Gmail messages")
        return result

    @router.get(
        "/messages/{message_id}",
        summary="Get Gmail message",
        operation_id="gmail_get_message"
    )
    def gmail_get_message_endpoint(
        message_id: str = Path(..., description="Message ID"),
        format: str = Query('full', description="Gmail message format (minimal, full, raw, metadata)"),
        user_id: str = Query('me', description="User id"),
        creds: Credentials = Depends(get_current_credentials)
    ):
        result = get_message(credentials=creds, message_id=message_id, user_id=user_id, format=format)
        if result is None:
            raise HTTPException(status_code=404, detail="Message not found or API error")
        return result

    @router.post(
        "/messages:sendRaw",
        summary="Send Gmail message (raw)",
        operation_id="gmail_send_raw"
    )
    def gmail_send_raw_endpoint(
        request: SendRawEmailRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        result = send_message_raw(credentials=creds, raw_message_base64url=request.raw, user_id=request.user_id)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to send Gmail message")
        return result

    @router.post(
        "/messages:composeAndSend",
        summary="Compose and send simple text email",
        operation_id="gmail_compose_send"
    )
    def gmail_compose_send_endpoint(
        request: ComposeAndSendRequest,
        creds: Credentials = Depends(get_current_credentials)
    ):
        raw = build_raw_message(
            from_addr=request.from_addr,
            to_addrs=request.to_addrs,
            subject=request.subject,
            body_text=request.body_text,
        )
        result = send_message_raw(credentials=creds, raw_message_base64url=raw, user_id=request.user_id)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to send Gmail message")
        return result

    @router.post(
        "/messages/{message_id}:modify",
        summary="Modify message labels",
        operation_id="gmail_modify_labels"
    )
    def gmail_modify_labels_endpoint(
        message_id: str = Path(..., description="Message ID"),
        request: ModifyLabelsRequest = Body(...),
        creds: Credentials = Depends(get_current_credentials)
    ):
        result = modify_message_labels(
            credentials=creds,
            message_id=message_id,
            add_labels=request.add_labels,
            remove_labels=request.remove_labels,
            user_id=request.user_id
        )
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to modify message labels")
        return result

    @router.get(
        "/labels",
        summary="List Gmail labels",
        operation_id="gmail_list_labels"
    )
    def gmail_list_labels_endpoint(
        user_id: str = Query('me', description="User id"),
        creds: Credentials = Depends(get_current_credentials)
    ):
        result = list_labels(credentials=creds, user_id=user_id)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to list Gmail labels")
        return result

