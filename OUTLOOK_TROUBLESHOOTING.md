# Outlook API Not Working - Troubleshooting Guide

## 🔍 Issue Identified

Your health check shows:
```json
{
  "google_authentication": "authenticated",
  "msgraph_authentication": "authentication_failed_or_pending"
}
```

This means **Microsoft Graph OAuth hasn't been completed yet**.

---

## ✅ Quick Fix Steps

### Step 1: Verify Your .env File

Make sure these are set:
```env
CLIENT_ID=fba176b9-ab0a-47ba-9a67-9d449db48fdd
TENANT_ID=common
```

### Step 2: Verify Azure App Configuration

Your app must have:

#### A) Redirect URI
- Type: **Public client/native (mobile & desktop)**
- URI: `http://localhost:8081`

#### B) API Permissions (Delegated)
- ✅ Mail.ReadWrite
- ✅ Mail.Send
- ✅ Calendars.ReadWrite
- ✅ ChannelMessage.Read.All
- ✅ Chat.Read
- ✅ User.Read

#### C) Allow Public Client Flows
- Go to **Authentication** → Advanced settings
- Set **Allow public client flows** to **Yes**

### Step 3: Trigger OAuth Flow

The OAuth flow starts when you make your **first API call**:

```bash
# This will open your browser for Microsoft login
Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages?folder=inbox&max_results=5" -UseBasicParsing
```

**What happens:**
1. 🌐 Browser opens automatically
2. 🔐 Sign in with your Microsoft account
3. ✅ Grant permissions
4. 💾 Token is cached in `.msgraph-tokens.json`
5. ✨ Future requests work automatically

---

## 🐛 Common Issues & Solutions

### Issue 1: "MSFT_CLIENT_ID not configured"

**Symptom:** Error in logs saying CLIENT_ID is missing

**Solution:**
```bash
# Check if .env file exists and has CLIENT_ID
cat .env | grep CLIENT_ID

# If missing, add it:
# CLIENT_ID=fba176b9-ab0a-47ba-9a67-9d449db48fdd
```

Then restart server:
```bash
python run_server.py
```

---

### Issue 2: "Failed to get Microsoft Graph access token"

**Symptom:** Authentication fails when making API calls

**Possible Causes & Solutions:**

#### A) Wrong CLIENT_ID
```bash
# Verify CLIENT_ID matches Azure Portal
# Go to: Azure Portal → App registrations → Your app → Overview
# Copy Application (client) ID
```

#### B) Public Client Flow Not Enabled
```bash
# In Azure Portal:
# Your app → Authentication → Advanced settings
# Set "Allow public client flows" = Yes
```

#### C) Wrong Redirect URI
```bash
# In Azure Portal:
# Your app → Authentication → Platform configurations
# Should have: http://localhost:8081 (Public client/native)
```

#### D) Missing Permissions
```bash
# In Azure Portal:
# Your app → API permissions
# Ensure all required permissions are added
# Click "Grant admin consent" if available
```

---

### Issue 3: Browser Doesn't Open

**Symptom:** No browser window opens during OAuth

**Solution:**

Check server logs for the authentication URL:
```bash
# Look for a line like:
# INFO - Opening browser for authentication: https://login.microsoftonline.com/...
```

Manually copy and open that URL in your browser.

---

### Issue 4: "Access Denied" or Permission Errors

**Symptom:** OAuth succeeds but API calls fail with permission errors

**Solution:**

1. **Check Scopes** - Ensure all required permissions are granted in Azure
2. **Re-authenticate** - Delete token cache and try again:
   ```bash
   Remove-Item .msgraph-tokens.json
   ```
3. **Admin Consent** - If using work account, ask IT admin to grant consent

---

### Issue 5: Token Cache Issues

**Symptom:** Random authentication failures

**Solution:**

Clear the token cache and re-authenticate:
```bash
# Delete token file
Remove-Item .msgraph-tokens.json -Force

# Restart server
python run_server.py

# Make an API call to trigger OAuth
Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages" -UseBasicParsing
```

---

## 🧪 Testing Step-by-Step

### Test 1: Check Server Status
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected:**
```json
{
  "status": "ok",
  "google_authentication": "authenticated",
  "msgraph_authentication": "authenticated"  // Should show this after OAuth
}
```

### Test 2: List Outlook Folders (Simple Test)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/outlook/folders" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected:** List of your mail folders (inbox, sent, drafts, etc.)

### Test 3: List Inbox Messages
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages?folder=inbox&max_results=5" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected:** JSON with your recent emails

### Test 4: Send a Test Email
```powershell
$body = @{
    subject = "Test from MCP Server"
    body = "This is a test email"
    to_recipients = @("your-email@example.com")
    content_type = "text"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages/send" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -UseBasicParsing
```

**Expected:** Status 200 with success message

---

## 📋 Complete Checklist

Before troubleshooting, verify ALL of these:

### Azure Configuration
- [ ] App registered in Azure Portal
- [ ] CLIENT_ID copied from Azure
- [ ] Redirect URI: `http://localhost:8081` (Public client/native)
- [ ] API Permissions added (Mail.ReadWrite, Mail.Send, etc.)
- [ ] "Allow public client flows" = Yes

### Environment Configuration
- [ ] `.env` file exists
- [ ] `CLIENT_ID=fba176b9-ab0a-47ba-9a67-9d449db48fdd`
- [ ] `TENANT_ID=common`

### Server Status
- [ ] Server running on port 8000
- [ ] No errors in startup logs
- [ ] Health endpoint responds

### OAuth Flow
- [ ] First API call triggers browser
- [ ] Successfully logged in to Microsoft
- [ ] Granted permissions
- [ ] Token cached in `.msgraph-tokens.json`

---

## 🔍 Debug Mode

To see detailed logs, check the server output when making requests.

### Enable Debug Logging

Edit `mcp_server/utils/msgraph_auth.py` temporarily:
```python
# Change line 20 from:
logging.basicConfig(level=logging.INFO)

# To:
logging.basicConfig(level=logging.DEBUG)
```

Restart server and watch for detailed authentication logs.

---

## 💡 Quick Diagnostic Commands

### Check if .env is loaded
```powershell
# Run from project root
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('CLIENT_ID:', os.getenv('CLIENT_ID'))"
```

### Check if MSAL is installed
```powershell
python -c "import msal; print('MSAL version:', msal.__version__)"
```

### Check if server is running
```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

---

## 🆘 Still Not Working?

### Collect This Information:

1. **Server startup logs** (first 20 lines)
2. **Error message** when calling Outlook endpoint
3. **Azure app configuration** screenshot
4. **.env file** (hide sensitive values)

### Then check:
- Port 8081 is not blocked by firewall
- Your Microsoft account type (personal vs. work)
- If work account: check with IT if app registration is allowed

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Health endpoint shows: `"msgraph_authentication": "authenticated"`
2. ✅ `.msgraph-tokens.json` file exists
3. ✅ Outlook endpoints return your actual data
4. ✅ No authentication errors in logs

---

## 🚀 Next Steps After Fix

Once working:
1. Test all Outlook endpoints (`/outlook/messages`, `/outlook/folders`)
2. Test Teams endpoints (`/teams`, `/teams/default/channels`)
3. Set up CHANNEL_ID for Teams default endpoints
4. Integrate with your application!

Good luck! 🎉

