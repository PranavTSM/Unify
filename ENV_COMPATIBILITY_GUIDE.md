# Environment Variable Compatibility Guide

## ✅ Your .env File is Now Compatible!

The MCP server has been updated to work with your existing environment variable naming scheme.

---

## 📋 Your Current .env Structure (WORKS!)

```env
# Google OAuth 2.0 Client Credentials
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
TOKEN_FILE_PATH='.gcp-saved-tokens.json'
OAUTH_CALLBACK_PORT=8080
CALENDAR_SCOPES='https://www.googleapis.com/auth/calendar'
GOOGLE_SCOPES='https://www.googleapis.com/auth/gmail.modify'

# Outlook/Microsoft Graph (just need to fill in CLIENT_ID and TENANT_ID)
PORT=3000                    # ⚠️ Not used by MCP server (kept for compatibility)
CLIENT_ID=your-azure-app-id  # ✅ USED - Maps to MSFT_CLIENT_ID
CLIENT_SECRET=               # ⚠️ Not needed (public OAuth), but won't cause issues
REDIRECT_URI=                # ⚠️ Auto-generated, but can override if set
SESSION_SECRET=              # ⚠️ Not used by MCP server

# Teams/Microsoft Graph
TENANT_ID=common             # ✅ USED - Maps to MSFT_TENANT_ID (use 'common' for multi-tenant)
# CLIENT_ID (already above)  # Note: Don't duplicate CLIENT_ID
# CLIENT_SECRET (already above)
TEAM_ID=                     # ⚠️ Not an env var - pass as API parameter
CHANNEL_ID=                  # ⚠️ Not an env var - pass as API parameter
```

---

## 🎯 What You Need to Do

### 1. **Fill in CLIENT_ID** (Required)
This is your Azure Application (client) ID:
```env
CLIENT_ID=12345678-1234-1234-1234-123456789abc
```

### 2. **Set TENANT_ID** (Recommended)
```env
TENANT_ID=common  # For personal + work accounts
# OR
TENANT_ID=your-tenant-id  # For organization-only
```

### 3. **Everything Else is Optional/Ignored**
- `CLIENT_SECRET` - Not needed (ignored)
- `REDIRECT_URI` - Auto-generated as `http://localhost:8081`
- `SESSION_SECRET` - Not used
- `PORT` - Not used (MCP server runs on port 8000)
- `TEAM_ID`, `CHANNEL_ID` - Pass as API parameters, not env vars

---

## 🔄 Variable Mapping

The code automatically maps your variables:

| Your Variable | Maps To Internal | Status |
|--------------|------------------|--------|
| `CLIENT_ID` | `MSFT_CLIENT_ID` | ✅ Used |
| `TENANT_ID` | `MSFT_TENANT_ID` | ✅ Used |
| `REDIRECT_URI` | Overrides auto-generated URI | 🟡 Optional |
| `CLIENT_SECRET` | *(not used)* | ⚠️ Ignored |
| `SESSION_SECRET` | *(not used)* | ⚠️ Ignored |
| `PORT` | *(not used)* | ⚠️ Ignored |
| `TEAM_ID` | *(not used)* | ❌ Pass as API param |
| `CHANNEL_ID` | *(not used)* | ❌ Pass as API param |

---

## 📝 Recommended .env File (Clean Version)

Here's a cleaned-up version with just what matters:

```env
# ============================================
# Google Services
# ============================================
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-secret-here
TOKEN_FILE_PATH='.gcp-saved-tokens.json'
OAUTH_CALLBACK_PORT=8080
CALENDAR_SCOPES='https://www.googleapis.com/auth/calendar'
GOOGLE_SCOPES='https://www.googleapis.com/auth/gmail.modify'

# ============================================
# Microsoft Graph (Outlook & Teams)
# ============================================

# Required: Azure Application (client) ID
CLIENT_ID=your-azure-client-id-here

# Required: Tenant ID ('common' for multi-tenant)
TENANT_ID=common

# Optional: Override default redirect URI
# REDIRECT_URI=http://localhost:8081

# These are safe to keep but not used:
# CLIENT_SECRET=
# SESSION_SECRET=
# PORT=3000
```

---

## 🚀 How to Get CLIENT_ID and TENANT_ID

### Step 1: Register Azure App
1. Go to https://portal.azure.com/
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Set:
   - **Name**: Unified Inbox MCP
   - **Account types**: Accounts in any organizational directory and personal Microsoft accounts
   - **Redirect URI**: 
     - Platform: **Public client/native**
     - URI: `http://localhost:8081`
5. Click **Register**

### Step 2: Copy CLIENT_ID
After registration, copy the **Application (client) ID** from the Overview page.

```env
CLIENT_ID=paste-id-here
```

### Step 3: Set TENANT_ID
```env
TENANT_ID=common  # Use this for personal + work accounts
```

If you need organization-only access, copy the **Directory (tenant) ID** from Overview page.

### Step 4: Configure Permissions
1. Go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph** → **Delegated permissions**
4. Add:
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `Calendars.ReadWrite`
   - `ChannelMessage.Read.All`
   - `Chat.Read`
   - `User.Read`
5. Click **Add permissions**

### Step 5: Enable Public Client
1. Go to **Authentication**
2. Scroll to **Advanced settings**
3. Set **Allow public client flows** to **Yes**
4. Click **Save**

---

## 🎯 Using TEAM_ID and CHANNEL_ID

These are **NOT environment variables** - pass them as API parameters:

### Example: List Team Messages

```bash
# Step 1: List all teams (get team IDs)
curl http://localhost:8000/teams

# Step 2: List channels in a team (get channel IDs)
curl http://localhost:8000/teams/{team_id}/channels

# Step 3: List messages in a channel
curl http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages
```

### Example: Python

```python
import requests

# Get teams
teams = requests.get("http://localhost:8000/teams").json()
team_id = teams["value"][0]["id"]

# Get channels
channels = requests.get(f"http://localhost:8000/teams/{team_id}/channels").json()
channel_id = channels["value"][0]["id"]

# Get messages
messages = requests.get(
    f"http://localhost:8000/teams/{team_id}/channels/{channel_id}/messages",
    params={"max_results": 20}
).json()
```

---

## ✅ Testing Your Configuration

### 1. Restart the Server
```bash
# Stop current server (Ctrl+C)
python run_server.py
```

### 2. Check Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "google_authentication": "authenticated",
  "msgraph_authentication": "authenticated"  // After first OAuth
}
```

### 3. Test Outlook (triggers OAuth first time)
```bash
curl http://localhost:8000/outlook/messages?folder=inbox&max_results=5
```

This will:
1. Open browser for Microsoft login
2. Ask for permissions
3. Cache token
4. Return your inbox messages

### 4. Test Teams
```bash
curl http://localhost:8000/teams
```

---

## 🔍 Troubleshooting

### Problem: "MSFT_CLIENT_ID not configured"
**Solution**: Make sure `CLIENT_ID` is set in your .env file
```env
CLIENT_ID=your-azure-app-id-here
```

### Problem: "Failed to get Microsoft Graph access token"
**Solutions**:
1. Check `CLIENT_ID` is correct
2. Check `TENANT_ID` is set (use 'common')
3. Ensure Azure app has "Allow public client flows" enabled
4. Delete token cache and retry: `rm .msgraph-tokens.json`

### Problem: "Browser doesn't open for auth"
**Solution**: 
1. Check if port 8081 is available
2. Look for URL in console logs
3. Manually open the URL in browser

### Problem: "Permission denied errors"
**Solution**:
1. Check API permissions in Azure Portal
2. Grant admin consent if using work account
3. Re-authenticate: delete `.msgraph-tokens.json` and retry

---

## 📊 Summary

| Item | Status | Action |
|------|--------|--------|
| Variable compatibility | ✅ Done | Code updated |
| CLIENT_ID mapping | ✅ Works | Just fill in value |
| TENANT_ID mapping | ✅ Works | Use 'common' |
| CLIENT_SECRET | ⚠️ Ignored | Safe to keep |
| TEAM_ID/CHANNEL_ID | ❌ Not env vars | Pass as params |

---

## 🎉 You're Ready!

Your .env file structure is now fully compatible. Just:
1. ✅ Fill in `CLIENT_ID` from Azure
2. ✅ Set `TENANT_ID='common'`
3. ✅ Restart server
4. ✅ Make first API call (triggers OAuth)

That's it! 🚀

