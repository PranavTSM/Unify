"""
Data Normalizer - Converts messages and events from different sources to a unified format
"""
 
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from html import unescape
import base64
 
logger = logging.getLogger(__name__)
 
def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub('<[^<]+?>', '', text)
    # Unescape HTML entities
    clean = unescape(clean)
    # Remove extra whitespace
    clean = ' '.join(clean.split())
    return clean
 
def parse_email_address(email_obj: Any) -> Dict[str, str]:
    """Parse email address from various formats."""
    if isinstance(email_obj, dict):
        email = email_obj.get('email') or email_obj.get('address', '')
        name = email_obj.get('name') or email_obj.get('displayName', '')
        return {"email": email, "name": name}
    elif isinstance(email_obj, str):
        return {"email": email_obj, "name": ""}
    return {"email": "", "name": ""}
 
def normalize_gmail_message(gmail_msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Gmail message to unified format.
   
    Returns unified message format compatible with UnifiedMessage model.
    """
    try:
        msg_id = gmail_msg.get('id', '')
        thread_id = gmail_msg.get('threadId', '')
       
        # Parse headers
        headers = {h['name']: h['value'] for h in gmail_msg.get('payload', {}).get('headers', [])}
       
        # Extract sender
        from_header = headers.get('From', '')
        sender_match = re.match(r'(.+?)\s*<(.+?)>', from_header)
        if sender_match:
            sender = {"name": sender_match.group(1).strip(), "email": sender_match.group(2).strip()}
        else:
            sender = {"name": "", "email": from_header.strip()}
       
        # Extract recipients
        to_header = headers.get('To', '')
        recipients = []
        if to_header:
            for email in to_header.split(','):
                match = re.match(r'(.+?)\s*<(.+?)>', email.strip())
                if match:
                    recipients.append({"name": match.group(1).strip(), "email": match.group(2).strip()})
                else:
                    recipients.append({"name": "", "email": email.strip()})
       
        # Get subject
        subject = headers.get('Subject', '(No Subject)')
       
        # Extract body
        body = ""
        payload = gmail_msg.get('payload', {})
       
        def extract_body(part):
            """Recursively extract body from message parts."""
            if 'body' in part and 'data' in part['body']:
                data = part['body']['data']
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                return strip_html(decoded)
           
            if 'parts' in part:
                for subpart in part['parts']:
                    if subpart.get('mimeType') == 'text/plain':
                        return extract_body(subpart)
                # Fallback to HTML if no plain text
                for subpart in part['parts']:
                    if 'text/html' in subpart.get('mimeType', ''):
                        return extract_body(subpart)
            return ""
       
        body = extract_body(payload)
       
        # Parse timestamp
        internal_date = int(gmail_msg.get('internalDate', 0)) / 1000
        timestamp = datetime.fromtimestamp(internal_date).isoformat() if internal_date else datetime.now().isoformat()
       
        # Extract labels
        labels = gmail_msg.get('labelIds', [])
       
        # Extract attachments
        attachments = []
        def find_attachments(part):
            if part.get('filename'):
                attachments.append({
                    "name": part['filename'],
                    "size": part.get('body', {}).get('size', 0),
                    "mime_type": part.get('mimeType'),
                    "attachment_id": part.get('body', {}).get('attachmentId')
                })
            if 'parts' in part:
                for subpart in part['parts']:
                    find_attachments(subpart)
       
        find_attachments(payload)
       
        # Check read status
        is_read = 'UNREAD' not in labels
       
        return {
            "id": msg_id,
            "source": "gmail",
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "body": body[:1000],  # Limit body size
            "timestamp": timestamp,
            "labels": labels,
            "attachments": attachments,
            "thread_id": thread_id,
            "is_read": is_read,
            "importance_score": 0.5,
            "summary": None
        }
   
    except Exception as e:
        logger.error(f"Error normalizing Gmail message {gmail_msg.get('id')}: {e}")
        return {
            "id": gmail_msg.get('id', 'unknown'),
            "source": "gmail",
            "error": str(e),
            "raw": gmail_msg
        }
 
def normalize_outlook_message(outlook_msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Outlook message to unified format.
    """
    try:
        msg_id = outlook_msg.get('id', '')
       
        # Extract sender
        from_obj = outlook_msg.get('from', {}).get('emailAddress', {})
        sender = parse_email_address(from_obj)
       
        # Extract recipients
        recipients = []
        for recipient in outlook_msg.get('toRecipients', []):
            recipients.append(parse_email_address(recipient.get('emailAddress', {})))
       
        # Get subject
        subject = outlook_msg.get('subject', '(No Subject)')
       
        # Extract body
        body_obj = outlook_msg.get('body', {})
        body_content = body_obj.get('content', '')
        if body_obj.get('contentType') == 'html':
            body = strip_html(body_content)
        else:
            body = body_content
       
        # Parse timestamp
        timestamp_str = outlook_msg.get('receivedDateTime') or outlook_msg.get('sentDateTime') or outlook_msg.get('createdDateTime')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).isoformat()
        else:
            timestamp = datetime.now().isoformat()
       
        # Extract categories (labels)
        labels = outlook_msg.get('categories', [])
       
        # Check importance
        importance = outlook_msg.get('importance', 'normal')
        importance_score = 0.8 if importance == 'high' else 0.5 if importance == 'normal' else 0.3
       
        # Extract attachments
        attachments = []
        if outlook_msg.get('hasAttachments'):
            for att in outlook_msg.get('attachments', []):
                attachments.append({
                    "name": att.get('name', ''),
                    "size": att.get('size', 0),
                    "mime_type": att.get('contentType'),
                    "url": att.get('@odata.mediaContentType')
                })
       
        # Check read status
        is_read = outlook_msg.get('isRead', False)
       
        # Thread/conversation ID
        thread_id = outlook_msg.get('conversationId', '')
       
        return {
            "id": msg_id,
            "source": "outlook",
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "body": body[:1000],  # Limit body size
            "timestamp": timestamp,
            "labels": labels,
            "attachments": attachments,
            "thread_id": thread_id,
            "is_read": is_read,
            "importance_score": importance_score,
            "summary": None
        }
   
    except Exception as e:
        logger.error(f"Error normalizing Outlook message {outlook_msg.get('id')}: {e}")
        return {
            "id": outlook_msg.get('id', 'unknown'),
            "source": "outlook",
            "error": str(e),
            "raw": outlook_msg
        }
 
def normalize_teams_message(teams_msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Teams message to unified format.
    Handles both channel messages and chat messages.
    """
    try:
        # Handle None or invalid messages gracefully
        if teams_msg is None or not isinstance(teams_msg, dict):
            logger.warning(f"⚠️ Invalid Teams message: {type(teams_msg)}")
            return None  # Will be filtered out in merger
        
        msg_id = teams_msg.get('id', f'teams_{hash(str(teams_msg))}')
        
        # Debug: Log COMPLETE first valid message to understand structure
        if not hasattr(normalize_teams_message, '_logged_first'):
            import json
            logger.info("="*80)
            logger.info("📝 COMPLETE Teams Message Sample (first valid message):")
            logger.info("="*80)
            try:
                # Pretty print the entire message
                logger.info(json.dumps(teams_msg, indent=2, default=str))
            except:
                logger.info(str(teams_msg))
            logger.info("="*80)
            logger.info(f"Available keys: {list(teams_msg.keys())}")
            logger.info("="*80)
            normalize_teams_message._logged_first = True
       
        # Extract sender - be VERY forgiving, accept ANY name
        sender_name = "Teams User"
        sender_email = ""
        
        # Try to extract sender from ANY available field
        from_obj = teams_msg.get('from', {})
        if isinstance(from_obj, dict):
            # Try nested user object
            if 'user' in from_obj:
                user = from_obj['user']
                sender_name = user.get('displayName') or user.get('name') or sender_name
                sender_email = user.get('userPrincipalName', '') or user.get('mail', '') or user.get('id', '')
            # Try direct fields
            else:
                sender_name = from_obj.get('displayName') or from_obj.get('name') or sender_name
                sender_email = from_obj.get('userPrincipalName', '') or from_obj.get('id', '')
        
        # Try other possible sender fields
        if sender_name == "Teams User":
            if teams_msg.get('sender'):
                s = teams_msg['sender']
                sender_name = s.get('displayName') or s.get('name') or sender_name
                sender_email = s.get('email', '') or s.get('userPrincipalName', '')
            elif teams_msg.get('createdBy'):
                cb = teams_msg['createdBy']
                sender_name = cb.get('displayName') or cb.get('name') or sender_name
                sender_email = cb.get('email', '') or cb.get('userPrincipalName', '')
        
        sender = {"name": sender_name, "email": sender_email}
       
        # Teams messages don't have traditional recipients
        recipients = []
       
        # Get body/content - be VERY forgiving
        body = ""
        
        # Try body object
        body_obj = teams_msg.get('body')
        if isinstance(body_obj, dict):
            body_content = body_obj.get('content', '')
            if body_obj.get('contentType') == 'html' and body_content:
                body = strip_html(body_content)
            else:
                body = body_content
        elif isinstance(body_obj, str):
            body = body_obj
        
        # Try other fields
        if not body:
            body = teams_msg.get('content', '') or teams_msg.get('bodyPreview', '') or teams_msg.get('summary', '')
        
        # Last resort: show SOMETHING
        if not body:
            body = f"Teams message {msg_id}"
       
        # Create subject from body
        subject = body[:50] + '...' if len(body) > 50 else body
       
        # Parse timestamp - be VERY forgiving
        timestamp_str = (teams_msg.get('createdDateTime') or 
                        teams_msg.get('lastModifiedDateTime') or 
                        teams_msg.get('timestamp') or
                        teams_msg.get('receivedDateTime'))
        
        timestamp = datetime.now().isoformat()  # Default to now
        if timestamp_str:
            try:
                # Handle ISO format with Z
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).isoformat()
            except:
                pass  # Keep default
       
        # Labels (message type, etc.)
        labels = []
        msg_type = teams_msg.get('messageType')
        if msg_type:
            labels.append(f"type:{msg_type}")
       
        if teams_msg.get('importance'):
            labels.append(f"importance:{teams_msg['importance']}")
       
        # Extract attachments
        attachments = []
        for att in teams_msg.get('attachments', []):
            attachments.append({
                "name": att.get('name', ''),
                "size": 0,  # Teams API doesn't always provide size
                "mime_type": att.get('contentType'),
                "url": att.get('contentUrl')
            })
       
        # Teams messages are always "read" from API perspective
        is_read = True
       
        # Channel/chat ID as thread (handle None values safely)
        channel_identity = teams_msg.get('channelIdentity') or {}
        thread_id = channel_identity.get('channelId', '') or teams_msg.get('chatId', '') or ''
       
        normalized = {
            "id": msg_id,
            "source": "teams",
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "body": body[:1000],  # Limit body size
            "timestamp": timestamp,
            "labels": labels,
            "attachments": attachments,
            "thread_id": thread_id,
            "is_read": is_read,
            "importance_score": 0.5,
            "summary": None
        }
        
        # Debug: Log first successful normalization
        if not hasattr(normalize_teams_message, '_logged_success'):
            logger.info("✅ First successfully normalized Teams message:")
            logger.info(f"   ID: {msg_id}")
            logger.info(f"   Sender: {sender['name']}")
            logger.info(f"   Subject: {subject[:50]}")
            logger.info(f"   Body: {body[:100]}...")
            logger.info(f"   Timestamp: {timestamp}")
            normalize_teams_message._logged_success = True
        
        return normalized
   
    except Exception as e:
        logger.error(f"❌ Error normalizing Teams message {teams_msg.get('id') if isinstance(teams_msg, dict) else 'N/A'}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None  # Will be filtered out in merger
 
def normalize_messages(messages: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
    """
    Normalize a list of messages based on their source.
   
    Args:
        messages: List of raw messages
        source: Source identifier (gmail, outlook, teams)
       
    Returns:
        List of normalized messages
    """
    logger.info(f"📥 Normalizing {len(messages)} messages from {source}")
   
    normalizers = {
        "gmail": normalize_gmail_message,
        "outlook": normalize_outlook_message,
        "teams": normalize_teams_message,
    }
   
    normalizer = normalizers.get(source)
    if not normalizer:
        logger.error(f"No normalizer found for source: {source}")
        return []
   
    # Normalize all messages
    normalized = [normalizer(msg) for msg in messages]
    
    # Filter out None values
    valid = [msg for msg in normalized if msg is not None]
    none_count = len(normalized) - len(valid)
    
    if none_count > 0:
        logger.warning(f"⚠️ {source}: {none_count} messages failed normalization (returned None)")
    
    logger.info(f"✅ {source}: Successfully normalized {len(valid)}/{len(messages)} messages")
    
    return valid
 
def normalize_calendar_event(event: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Normalize calendar event to unified format for both Google and Microsoft calendars.
    """
    try:
        if source == "google_calendar":
            return normalize_google_calendar_event(event)
        elif source == "microsoft_calendar":
            return normalize_microsoft_calendar_event(event)
        else:
            logger.error(f"Unknown calendar source: {source}")
            return {"error": f"Unknown source: {source}", "raw": event}
    except Exception as e:
        logger.error(f"Error normalizing calendar event: {e}")
        return {
            "id": event.get('id', 'unknown'),
            "source": source,
            "error": str(e),
            "raw": event
        }
 
def normalize_google_calendar_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Google Calendar event."""
    event_id = event.get('id', '')
    title = event.get('summary', '(No Title)')
   
    # Parse start and end times
    start_obj = event.get('start', {})
    end_obj = event.get('end', {})
    start = start_obj.get('dateTime') or start_obj.get('date')
    end = end_obj.get('dateTime') or end_obj.get('date')
   
    # Location
    location = event.get('location', '')
   
    # Organizer
    organizer_obj = event.get('organizer', {})
    organizer = {
        "email": organizer_obj.get('email', ''),
        "name": organizer_obj.get('displayName', organizer_obj.get('email', ''))
    }
   
    # Attendees
    attendees = []
    for attendee in event.get('attendees', []):
        attendees.append({
            "email": attendee.get('email', ''),
            "name": attendee.get('displayName', attendee.get('email', '')),
            "status": attendee.get('responseStatus', 'needsAction')
        })
   
    # Description
    description = event.get('description', '')
   
    # Status
    status = event.get('status', 'confirmed')
   
    return {
        "id": event_id,
        "source": "google_calendar",
        "title": title,
        "start": start,
        "end": end,
        "location": location,
        "organizer": organizer,
        "attendees": attendees,
        "description": description,
        "status": status
    }
 
def normalize_microsoft_calendar_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Microsoft Calendar event."""
    event_id = event.get('id', '')
    title = event.get('subject', '(No Title)')
   
    # Parse start and end times
    start_obj = event.get('start', {})
    end_obj = event.get('end', {})
    start = start_obj.get('dateTime') if start_obj else None
    end = end_obj.get('dateTime') if end_obj else None
   
    # Location
    location_obj = event.get('location', {})
    location = location_obj.get('displayName', '')
   
    # Organizer
    organizer_obj = event.get('organizer', {}).get('emailAddress', {})
    organizer = parse_email_address(organizer_obj)
   
    # Attendees
    attendees = []
    for attendee in event.get('attendees', []):
        email_obj = attendee.get('emailAddress', {})
        attendees.append({
            "email": email_obj.get('address', ''),
            "name": email_obj.get('name', ''),
            "status": attendee.get('status', {}).get('response', 'none')
        })
   
    # Description
    body_obj = event.get('body', {})
    description = body_obj.get('content', '')
    if body_obj.get('contentType') == 'html':
        description = strip_html(description)
   
    # Status
    status = event.get('responseStatus', {}).get('response', 'confirmed')
   
    return {
        "id": event_id,
        "source": "microsoft_calendar",
        "title": title,
        "start": start,
        "end": end,
        "location": location,
        "organizer": organizer,
        "attendees": attendees,
        "description": description,
        "status": status
    }