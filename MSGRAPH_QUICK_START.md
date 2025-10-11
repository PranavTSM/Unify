# Microsoft Graph MCP - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Azure App Registration
```
1. Go to: https://portal.azure.com/
2. Navigate to: Azure Active Directory → App registrations
3. Click: + New registration
4. Set Name: "Unified Inbox MCP"
5. Account types: "Accounts in any organizational directory and personal Microsoft accounts"
6. Redirect URI: 
   - Type: Public client/native
   - URI: http://localhost:8081
7. Click: Register
8. Copy the Application (client) ID
```

### 2. Configure Permissions
```
1. Go to: API permissions
2. Add permission → Microsoft Graph → Delegated permissions
3. Add: Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, 
        ChannelMessage.Read.All, Chat.Read, User.Read
4. Enable public client: Authentication → Allow public client flows → Yes
```

### 3. Update .env File
```env
MSFT_CLIENT_ID='paste-your-client-id-here'
MSFT_TENANT_ID='common'
MSGRAPH_TOKEN_FILE='.msgraph-tokens.json'
MSGRAPH_CALLBACK_PORT=8081
```

### 4. Install & Run
```bash
pip install -r requirements.txt
uvicorn mcp_server.app:app --reload --port 8000
```

### 5. Test
```bash
# Check health
curl http://localhost:8000/health

# List Outlook messages (will trigger OAuth on first request)
curl http://localhost:8000/outlook/messages?folder=inbox&max_results=5
```

---

## 📧 Outlook API Examples

### List Inbox Messages
```bash
curl "http://localhost:8000/outlook/messages?folder=inbox&max_results=10"
```

### Search Emails
```bash
curl "http://localhost:8000/outlook/messages?folder=inbox&search=meeting"
```

### Get Specific Message
```bash
curl "http://localhost:8000/outlook/messages/{message_id}"
```

### Send Email
```bash
curl -X POST "http://localhost:8000/outlook/messages/send" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Email",
    "body": "Hello from MCP Server!",
    "to_recipients": ["recipient@example.com"],
    "importance": "normal",
    "content_type": "text"
  }'
```

### Create Draft
```bash
curl -X POST "http://localhost:8000/outlook/messages/draft" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Draft Email",
    "body": "This is a draft",
    "to_recipients": ["someone@example.com"]
  }'
```

### Mark as Read
```bash
curl -X PATCH "http://localhost:8000/outlook/messages/{message_id}" \
  -H "Content-Type: application/json" \
  -d '{"isRead": true}'
```

### Delete Message
```bash
curl -X DELETE "http://localhost:8000/outlook/messages/{message_id}"
```

### List Folders
```bash
curl "http://localhost:8000/outlook/folders"
```

---

## 💬 Teams API Examples

### List All Teams
```bash
curl "http://localhost:8000/teams"
```

### Get Team Details
```bash
curl "http://localhost:8000/teams/{team_id}"
```

### List Channels in Team
```bash
curl "http://localhost:8000/teams/{team_id}/channels"
```

### List Channel Messages
```bash
curl "http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages?max_results=20"
```

### Get Specific Channel Message
```bash
curl "http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
```

### Send Message to Channel
```bash
curl -X POST "http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello team!",
    "content_type": "text"
  }'
```

### List All Chats
```bash
curl "http://localhost:8000/teams/chats?max_results=50"
```

### Get Chat Details
```bash
curl "http://localhost:8000/teams/chats/{chat_id}"
```

### List Chat Messages
```bash
curl "http://localhost:8000/teams/chats/{chat_id}/messages?max_results=20"
```

### Send Message to Chat
```bash
curl -X POST "http://localhost:8000/teams/chats/{chat_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hi there!",
    "content_type": "text"
  }'
```

---

## 🐍 Python Examples

### Outlook - Send Email
```python
import requests

url = "http://localhost:8000/outlook/messages/send"
data = {
    "subject": "Meeting Reminder",
    "body": "Don't forget our meeting at 3 PM!",
    "to_recipients": ["colleague@company.com"],
    "cc_recipients": ["manager@company.com"],
    "importance": "high",
    "content_type": "text"
}

response = requests.post(url, json=data)
print(response.json())
```

### Outlook - List Unread Messages
```python
import requests

url = "http://localhost:8000/outlook/messages"
params = {
    "folder": "inbox",
    "filter_query": "isRead eq false",
    "max_results": 20
}

response = requests.get(url, params=params)
messages = response.json()["value"]

for msg in messages:
    print(f"From: {msg['from']['emailAddress']['address']}")
    print(f"Subject: {msg['subject']}")
    print(f"Preview: {msg['bodyPreview'][:50]}...")
    print("---")
```

### Teams - Get Latest Channel Messages
```python
import requests

# Get teams
teams_resp = requests.get("http://localhost:8000/teams")
teams = teams_resp.json()["value"]

# Get first team's channels
team_id = teams[0]["id"]
channels_resp = requests.get(f"http://localhost:8000/teams/{team_id}/channels")
channels = channels_resp.json()["value"]

# Get messages from first channel
channel_id = channels[0]["id"]
messages_resp = requests.get(
    f"http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages",
    params={"max_results": 10}
)
messages = messages_resp.json()["value"]

for msg in messages:
    author = msg.get("from", {}).get("user", {}).get("displayName", "Unknown")
    content = msg.get("body", {}).get("content", "")
    print(f"{author}: {content[:100]}...")
    print("---")
```

### Teams - Send Message to Multiple Channels
```python
import requests

message_data = {
    "content": "📢 Important announcement: Server maintenance tonight at 10 PM",
    "content_type": "text"
}

# List of (team_id, channel_id) tuples
channels_to_notify = [
    ("team_id_1", "channel_id_1"),
    ("team_id_2", "channel_id_2"),
]

for team_id, channel_id in channels_to_notify:
    url = f"http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages"
    response = requests.post(url, json=message_data)
    
    if response.status_code == 200:
        print(f"✓ Message sent to channel {channel_id}")
    else:
        print(f"✗ Failed to send to channel {channel_id}")
```

---

## 🔍 Common Query Parameters

### Outlook Messages
- `folder`: inbox, sentitems, drafts, deleteditems (or folder ID)
- `max_results`: Number of messages (1-1000, default 50)
- `filter_query`: OData filter (e.g., `isRead eq false`)
- `search`: Search query string

### Teams
- `max_results`: Number of items (1-1000, default 50)

---

## 📊 Interactive API Documentation

Visit these URLs while the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Complete API documentation
- Interactive endpoint testing
- Request/response schemas
- Example values

---

## 🔧 Troubleshooting

### Token expired or invalid
```bash
# Delete token cache and re-authenticate
rm .msgraph-tokens.json
# Next API call will trigger OAuth flow
```

### Need to re-authenticate
```python
# Python script to clear cache
import os
if os.path.exists('.msgraph-tokens.json'):
    os.remove('.msgraph-tokens.json')
    print("Token cache cleared. Re-authentication required on next request.")
```

### Check authentication status
```bash
curl http://localhost:8000/health
# Look for "msgraph_authentication": "authenticated"
```

---

## 📁 Project Structure

```
mcp_server/
├── app.py                    # Main FastAPI application
├── outlook_routes.py         # Outlook/Mail endpoints
├── teams_routes.py           # Teams/Chat endpoints
├── gmail_routes.py           # Gmail endpoints
├── calendar_routes.py        # Calendar endpoints
└── utils/
    ├── auth.py               # Google OAuth
    └── msgraph_auth.py       # Microsoft OAuth
```

---

## 🎯 Next Steps

1. ✅ Complete Azure setup
2. ✅ Test basic API calls
3. 🔜 Integrate with your application
4. 🔜 Explore advanced features (filters, search, etc.)
5. 🔜 Set up error handling and logging

---

## 📚 Full Documentation

For complete setup instructions and troubleshooting:
- See: `MSGRAPH_SETUP.md`

For API reference:
- Visit: http://localhost:8000/docs

Happy coding! 🚀

