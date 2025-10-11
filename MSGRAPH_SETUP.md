# Microsoft Graph MCP Server Setup Guide

This guide will help you set up and configure the Microsoft Graph MCP (Model Context Protocol) server for Outlook and Teams integration.

## Overview

The MCP server now supports both Google services (Gmail, Calendar) and Microsoft services (Outlook, Teams) through a unified API.

## Prerequisites

1. Python 3.8+
2. A Microsoft account (personal or work/school)
3. Azure AD application registration (free)

## Step 1: Register Your Application in Azure Portal

### 1.1 Navigate to Azure Portal
1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign in with your Microsoft account
3. Search for "Azure Active Directory" or "Microsoft Entra ID"

### 1.2 Create a New App Registration
1. In the left menu, click **App registrations**
2. Click **+ New registration**
3. Fill in the details:
   - **Name**: `Unified Inbox MCP Server` (or any name you prefer)
   - **Supported account types**: 
     - Choose "Accounts in any organizational directory and personal Microsoft accounts" for multi-tenant support
     - Or choose "Personal Microsoft accounts only" if you only need personal account access
   - **Redirect URI**: 
     - Platform: **Public client/native (mobile & desktop)**
     - URI: `http://localhost:8081`
4. Click **Register**

### 1.3 Note Your Application (Client) ID
- After registration, you'll see the **Overview** page
- Copy the **Application (client) ID** - you'll need this for your `.env` file

### 1.4 Configure API Permissions
1. In the left menu, click **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add the following permissions:
   - `Mail.ReadWrite` - Read and write access to user mail
   - `Mail.Send` - Send mail as a user
   - `Calendars.ReadWrite` - Read and write user calendars
   - `ChannelMessage.Read.All` - Read all channel messages
   - `Chat.Read` - Read user chat messages
   - `User.Read` - Sign in and read user profile
6. Click **Add permissions**
7. (Optional) Click **Grant admin consent** if you have admin rights

### 1.5 Enable Public Client Flow
1. In the left menu, click **Authentication**
2. Scroll down to **Advanced settings**
3. Under **Allow public client flows**, toggle to **Yes**
4. Click **Save**

## Step 2: Configure Environment Variables

### 2.1 Create Your .env File
Copy `example.env` to `.env`:
```bash
cp example.env .env
```

### 2.2 Update Microsoft Graph Settings
Edit your `.env` file and add:

```env
# Microsoft Azure AD Application Credentials
MSFT_CLIENT_ID='your-application-client-id-here'
MSFT_TENANT_ID='common'  # Use 'common' for multi-tenant support

# Path to store Microsoft Graph OAuth tokens
MSGRAPH_TOKEN_FILE='.msgraph-tokens.json'

# Port for Microsoft OAuth callback (must match Azure redirect URI)
MSGRAPH_CALLBACK_PORT=8081
```

**Important Notes:**
- Replace `your-application-client-id-here` with the Application (client) ID from Step 1.3
- Keep `MSFT_TENANT_ID='common'` for personal and work accounts
- Use your specific tenant ID if you only want to support your organization
- The `MSGRAPH_CALLBACK_PORT` must match the redirect URI you registered in Azure (Step 1.2)

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Key Microsoft Graph dependencies:
- `msal==1.26.0` - Microsoft Authentication Library
- `requests==2.31.0` - HTTP library for API calls

## Step 4: Start the MCP Server

Run the MCP server:

```bash
cd mcp_server
python -m uvicorn app:app --reload --port 8000
```

Or from the root directory:

```bash
uvicorn mcp_server.app:app --reload --port 8000
```

## Step 5: Authenticate with Microsoft

### First-Time Authentication
1. When you first access any Microsoft Graph endpoint, the server will initiate OAuth flow
2. A browser window will automatically open
3. Sign in with your Microsoft account
4. Grant the requested permissions
5. You'll be redirected to a success page
6. The authentication token will be cached in `.msgraph-tokens.json`

### Subsequent Requests
- The server will use the cached token automatically
- Tokens are automatically refreshed when expired
- No need to re-authenticate unless you clear the token cache

## Step 6: Test the Integration

### Check Server Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "google_authentication": "authenticated",
  "msgraph_authentication": "authenticated"
}
```

### Test Outlook API
List your Outlook inbox messages:
```bash
curl http://localhost:8000/outlook/messages?folder=inbox&max_results=10
```

### Test Teams API
List your Teams:
```bash
curl http://localhost:8000/teams
```

## Available API Endpoints

### Outlook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/outlook/messages` | List messages from a folder |
| GET | `/outlook/messages/{message_id}` | Get a specific message |
| POST | `/outlook/messages/send` | Send an email |
| POST | `/outlook/messages/draft` | Create a draft email |
| PATCH | `/outlook/messages/{message_id}` | Update message (mark as read, etc.) |
| DELETE | `/outlook/messages/{message_id}` | Delete a message |
| POST | `/outlook/messages/{message_id}/move` | Move message to folder |
| GET | `/outlook/folders` | List all mail folders |

### Teams Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | List all teams |
| GET | `/teams/{team_id}` | Get team details |
| GET | `/teams/{team_id}/channels` | List channels in a team |
| GET | `/teams/{team_id}/channels/{channel_id}/messages` | List channel messages |
| GET | `/teams/{team_id}/channels/{channel_id}/messages/{message_id}` | Get a specific channel message |
| POST | `/teams/{team_id}/channels/{channel_id}/messages` | Send a channel message |
| GET | `/teams/chats` | List all chats |
| GET | `/teams/chats/{chat_id}` | Get chat details |
| GET | `/teams/chats/{chat_id}/messages` | List chat messages |
| POST | `/teams/chats/{chat_id}/messages` | Send a chat message |

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these interfaces to explore and test all available endpoints.

## Example Usage

### Send an Email via Outlook

```python
import requests

url = "http://localhost:8000/outlook/messages/send"
payload = {
    "subject": "Hello from MCP Server",
    "body": "This is a test email sent via the MCP server.",
    "to_recipients": ["recipient@example.com"],
    "importance": "normal",
    "content_type": "text"
}

response = requests.post(url, json=payload)
print(response.json())
```

### List Teams Messages

```python
import requests

# First, get list of teams
teams_response = requests.get("http://localhost:8000/teams")
teams = teams_response.json()["value"]
team_id = teams[0]["id"]

# Get channels
channels_response = requests.get(f"http://localhost:8000/teams/{team_id}/channels")
channels = channels_response.json()["value"]
channel_id = channels[0]["id"]

# Get messages
messages_response = requests.get(
    f"http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages",
    params={"max_results": 20}
)
messages = messages_response.json()["value"]
print(f"Found {len(messages)} messages")
```

## Troubleshooting

### Authentication Issues

**Problem**: "Failed to get Microsoft Graph access token"
- **Solution**: Check that your `MSFT_CLIENT_ID` is correct in `.env`
- **Solution**: Ensure you've enabled "Allow public client flows" in Azure (Step 1.5)
- **Solution**: Delete `.msgraph-tokens.json` and re-authenticate

**Problem**: "AADSTS7000215: Invalid client secret is provided"
- **Solution**: This app uses Public Client flow and doesn't need a client secret
- **Solution**: Ensure redirect URI matches exactly: `http://localhost:8081`

### Permission Issues

**Problem**: "Insufficient privileges to complete the operation"
- **Solution**: Ensure all required permissions are granted in Azure (Step 1.4)
- **Solution**: If using work account, ask admin to grant consent
- **Solution**: Delete token cache and re-authenticate to get new permissions

### Port Already in Use

**Problem**: "Address already in use" error
- **Solution**: Change the port in your startup command: `--port 8001`
- **Solution**: Find and kill the process using port 8000: 
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`
  - Linux/Mac: `lsof -ti:8000 | xargs kill`

### Browser Doesn't Open

**Problem**: Browser doesn't open for authentication
- **Solution**: Manually open the URL shown in the console
- **Solution**: Check firewall settings aren't blocking port 8081

## Security Considerations

1. **Token Storage**: Tokens are stored locally in `.msgraph-tokens.json`
   - Keep this file secure and never commit it to version control
   - Add to `.gitignore` (already configured)

2. **Scopes**: The app requests these permissions:
   - Mail.ReadWrite - Full access to user's email
   - Calendars.ReadWrite - Full access to user's calendar
   - Consider reducing scopes if you don't need all features

3. **Public Client Flow**: 
   - This is appropriate for desktop/local applications
   - For production web apps, use confidential client flow instead

4. **Network Security**:
   - The server runs on localhost by default
   - Only accessible from your local machine
   - For remote access, implement proper authentication

## Advanced Configuration

### Using a Specific Tenant

If you only want to support your organization:

```env
MSFT_TENANT_ID='your-tenant-id-here'
```

Get your tenant ID from:
- Azure Portal → Azure Active Directory → Overview → Tenant ID

### Custom Token Cache Location

```env
MSGRAPH_TOKEN_FILE='/path/to/custom/token-cache.json'
```

### Custom Callback Port

```env
MSGRAPH_CALLBACK_PORT=9090
```

**Important**: Must also update redirect URI in Azure to `http://localhost:9090`

## Additional Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Microsoft Graph Permissions Reference](https://docs.microsoft.com/en-us/graph/permissions-reference)

## Support

For issues specific to:
- **Microsoft Graph API**: Check [Microsoft Q&A](https://docs.microsoft.com/en-us/answers/products/)
- **MCP Server**: Create an issue in the project repository
- **Azure Configuration**: Consult [Azure Documentation](https://docs.microsoft.com/en-us/azure/)

## Next Steps

1. ✅ Complete Azure app registration
2. ✅ Configure environment variables
3. ✅ Install dependencies
4. ✅ Start the server and authenticate
5. ✅ Test the API endpoints
6. 🚀 Integrate with your application

Now you're ready to use Microsoft Graph services in your unified inbox!

