# Fix Admin Consent Issue

## Problem
Getting "Need admin approval" error when authenticating with Microsoft Graph.

## Solution 1: Grant Admin Consent (Recommended)

### If You Have Admin Rights:

1. **Go to Azure Portal**
   - https://portal.azure.com/

2. **Navigate to Your App**
   - Azure Active Directory → App registrations
   - Find your app: `teammsgreader` (or whatever you named it)

3. **Grant Admin Consent**
   - Click on **API permissions** (left menu)
   - You'll see all the permissions listed
   - Click **"Grant admin consent for [your organization]"** button
   - Confirm by clicking **"Yes"**

4. **Verify**
   - You should see green checkmarks next to all permissions
   - Status column should show "Granted for [your organization]"

5. **Try Again**
   - Clear your token cache: `Remove-Item .msgraph-tokens.json`
   - Re-authenticate: `POST /auth/msgraph/login`

---

## Solution 2: Use Personal Microsoft Account

Instead of work account, use a personal Microsoft account (like Outlook.com, Hotmail.com):

1. **Logout current session**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/logout" -Method POST -UseBasicParsing
   ```

2. **Delete token cache**
   ```powershell
   Remove-Item C:\Users\pathe\Desktop\Unified-Inbox\.msgraph-tokens.json -Force
   ```

3. **Login again**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/login" -Method POST -UseBasicParsing
   ```

4. **Use personal account**
   - When browser opens, sign in with personal Microsoft account
   - Personal accounts don't require admin consent

---

## Solution 3: Remove Admin-Required Permissions (Temporary)

If you can't get admin approval and need to test:

### Update the scopes in code:

**Edit: `mcp_server/utils/msgraph_auth.py`**

Find this section (around line 46):
```python
MSGRAPH_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/ChannelMessage.Read.All",  # ← REMOVE THIS
    "https://graph.microsoft.com/Chat.Read",                 # ← REMOVE THIS
    "https://graph.microsoft.com/User.Read",
]
```

**Change to:**
```python
MSGRAPH_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/User.Read",
]
```

**This will:**
- ✅ Enable Outlook (email)
- ✅ Enable Calendar
- ❌ Disable Teams (channels and chats)

**Then:**
1. Restart server
2. Clear token: `Remove-Item .msgraph-tokens.json`
3. Re-authenticate

---

## Solution 4: Change Azure App Configuration

### Make App Support Multi-Tenant Personal Accounts

1. **Azure Portal** → Your app → **Authentication**

2. **Supported account types**
   - Change to: **"Personal Microsoft accounts only"**
   - OR: **"Accounts in any organizational directory and personal Microsoft accounts"**

3. **Save**

4. **Try authentication again**

---

## Solution 5: Contact Your IT Admin

If you need Teams access and don't have admin rights:

**Email to IT Admin:**
```
Subject: Admin Consent Required for Microsoft Graph App

Hi [Admin Name],

I'm developing an application that needs access to Microsoft Graph APIs (Outlook and Teams).

Could you please grant admin consent for the following app?

App Name: teammsgreader
App ID: fba176b9-ab0a-47ba-9a67-9d449db48fdd

Required Permissions:
- Mail.ReadWrite (Read and write mail)
- Mail.Send (Send mail)
- Calendars.ReadWrite (Read and write calendars)
- ChannelMessage.Read.All (Read Teams channel messages)
- Chat.Read (Read Teams chat messages)
- User.Read (Read basic user profile)

You can grant consent at:
https://portal.azure.com/ → Azure Active Directory → App registrations → [App Name] → API permissions → "Grant admin consent"

Thank you!
```

---

## Quick Check: What Account Type Are You Using?

**Work/School Account (`@company.com`)**
- ⚠️ May require admin consent
- ✅ Can access Teams in your organization
- 🔐 Controlled by IT policies

**Personal Account (`@outlook.com`, `@hotmail.com`)**
- ✅ No admin consent needed
- ⚠️ Limited Teams access (personal Teams only)
- 🔓 Full control

---

## Recommended Approach

### For Development/Testing:
1. ✅ **Use personal Microsoft account** (easiest)
2. ✅ **Remove Teams permissions temporarily** (Outlook will work)

### For Production:
1. ✅ **Get admin consent** (proper way)
2. ✅ **Use work account with all permissions**

---

## Verification Commands

### Check current account type:
```powershell
# After authentication, check token info
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/status" -UseBasicParsing
```

### Clear everything and start fresh:
```powershell
# Stop server
# Delete token
Remove-Item .msgraph-tokens.json -Force

# Restart server
python run_server.py

# Login again with different account
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/login" -Method POST -UseBasicParsing
```

---

## What Works Without Admin Consent?

| Feature | Personal Account | Work Account (No Admin) | Work Account (Admin Consent) |
|---------|------------------|-------------------------|------------------------------|
| Outlook Email | ✅ | ✅ | ✅ |
| Calendar | ✅ | ✅ | ✅ |
| Teams Channels | Limited | ❌ | ✅ |
| Teams Chats | Limited | ❌ | ✅ |
| Send Email | ✅ | ✅ | ✅ |

---

## Choose Your Path:

**Option A: Quick Test (Outlook Only)**
- Remove Teams permissions from code
- Restart and re-auth
- ✅ Outlook works immediately

**Option B: Personal Account**
- Use personal Microsoft account
- ✅ Everything works
- ⚠️ Limited Teams access

**Option C: Get Admin Approval**
- Contact IT admin
- Get consent granted
- ✅ Full access to everything

Which option works best for you?

