# Authentication Endpoints Guide

## 🎯 New Explicit Authentication Routes

I've added dedicated authentication routes so you can **manually trigger OAuth** and check status before using APIs!

---

## 🔵 Google Authentication Endpoints

### 1. Check Status
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/google/status" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Response:**
```json
{
  "authenticated": true,
  "client_id_configured": true,
  "client_secret_configured": true,
  "message": "Authenticated successfully"
}
```

### 2. Login (Trigger OAuth)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/google/login" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

**What happens:**
- 🌐 Browser opens for Google login
- ✅ You grant permissions
- 💾 Token cached to `.gcp-saved-tokens.json`

### 3. Logout (Clear Token)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/google/logout" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 4. Check Configuration
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/google/config" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 5. Get Help
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/google/help" -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 🟢 Microsoft Graph Authentication Endpoints

### 1. Check Status
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/status" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Response:**
```json
{
  "authenticated": false,
  "client_id_configured": true,
  "tenant_id": "common",
  "message": "No token cache found. Please authenticate using /auth/msgraph/login"
}
```

### 2. Login (Trigger OAuth)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/login" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

**What happens:**
- 🌐 Browser opens for Microsoft login
- ✅ You grant permissions
- 💾 Token cached to `.msgraph-tokens.json`

### 3. Logout (Clear Token)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/logout" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 4. Check Configuration
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/config" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Example Response:**
```json
{
  "client_id_configured": true,
  "client_id_length": 36,
  "tenant_id": "common",
  "token_cache_file": ".msgraph-tokens.json",
  "token_cache_exists": false,
  "redirect_uri": "http://localhost:8081",
  "callback_port": "8081",
  "client_id_warning": "CLIENT_ID looks like a placeholder..."
}
```

### 5. Get Help
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/help" -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 🚀 Your Setup Workflow

### Step 1: Fix Your .env File

Make sure it has (NO spaces around `=`):

```env
# Google
GOOGLE_CLIENT_ID="your-google-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-secret"
GOOGLE_SCOPES="https://www.googleapis.com/auth/gmail.modify"
CALENDAR_SCOPES="https://www.googleapis.com/auth/calendar"

# Microsoft
CLIENT_ID="fba176b9-ab0a-47ba-9a67-9d449db48fdd"
TENANT_ID="common"
TEAM_ID="f4c00439-546a-4af6-8fd8-de9eed82e1fb"
```

**Important:** Remove any duplicate CLIENT_ID lines!

### Step 2: Restart Server
```bash
# Stop with Ctrl+C, then:
python run_server.py
```

### Step 3: Check Configuration
```powershell
# Check MS Graph config
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/config" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Look for warnings** like:
- "CLIENT_ID looks like a placeholder"
- "CLIENT_ID seems too short"

### Step 4: Authenticate with Microsoft Graph
```powershell
# Trigger MS Graph OAuth
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/login" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Browser will open:**
1. Sign in with your Microsoft account
2. Grant requested permissions
3. Browser shows "Authentication Successful!"
4. Close browser and return to terminal

### Step 5: Verify Authentication
```powershell
# Check status
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/status" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Should show:**
```json
{
  "authenticated": true,
  "message": "Authenticated successfully"
}
```

### Step 6: Test Outlook API
```powershell
# Now this should work!
Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages?folder=inbox&max_results=5" -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 🎨 Interactive API Documentation

Visit: **http://localhost:8000/docs**

You'll see new sections:
- **Google Authentication** - All Google auth endpoints
- **Microsoft Graph Authentication** - All MS Graph auth endpoints

You can test authentication directly from the browser!

---

## 📊 Complete Endpoint Reference

### Google Auth
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/auth/google/status` | Check auth status |
| POST | `/auth/google/login` | Trigger OAuth |
| POST | `/auth/google/logout` | Clear token |
| GET | `/auth/google/config` | View config |
| GET | `/auth/google/help` | Get setup help |

### MS Graph Auth
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/auth/msgraph/status` | Check auth status |
| POST | `/auth/msgraph/login` | Trigger OAuth |
| POST | `/auth/msgraph/logout` | Clear token |
| GET | `/auth/msgraph/config` | View config |
| GET | `/auth/msgraph/help` | Get setup help |

### Google APIs
| Method | Endpoint | Requires Auth |
|--------|----------|---------------|
| GET | `/gmail/messages` | ✅ Google |
| GET | `/calendars` | ✅ Google |

### MS Graph APIs
| Method | Endpoint | Requires Auth |
|--------|----------|---------------|
| GET | `/outlook/messages` | ✅ MS Graph |
| GET | `/teams` | ✅ MS Graph |
| GET | `/teams/default/channels` | ✅ MS Graph |

---

## 🔍 Troubleshooting

### Problem: "CLIENT_ID not configured"

**Check config:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/config" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Look for:**
- `client_id_configured: false` → CLIENT_ID not in .env
- `client_id_warning` → CLIENT_ID has issues

**Fix:** Edit .env and restart server

### Problem: "Token expired or invalid"

**Solution:**
```powershell
# Clear token and re-authenticate
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/logout" -Method POST -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:8000/auth/msgraph/login" -Method POST -UseBasicParsing
```

### Problem: Browser doesn't open

**Solution:**
1. Check server logs for the auth URL
2. Manually copy and open in browser
3. Check if port 8081 is blocked

### Problem: "Access denied" or permission errors

**Solution:**
1. Check Azure app has all required permissions
2. Click "Grant admin consent" in Azure
3. Re-authenticate after adding permissions

---

## 🐍 Python Examples

### Check Auth Status
```python
import requests

# Check MS Graph auth
response = requests.get("http://localhost:8000/auth/msgraph/status")
status = response.json()

if status["authenticated"]:
    print("✓ Already authenticated!")
else:
    print("⚠️ Need to authenticate")
    print(f"Message: {status['message']}")
```

### Trigger Authentication
```python
import requests

# Trigger MS Graph OAuth (will open browser)
response = requests.post("http://localhost:8000/auth/msgraph/login")
result = response.json()

if result["success"]:
    print("✓ Authentication successful!")
else:
    print("✗ Authentication failed")
    print(result["message"])
```

### Complete Workflow
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Check status
status = requests.get(f"{BASE_URL}/auth/msgraph/status").json()
print(f"Authenticated: {status['authenticated']}")

# 2. Authenticate if needed
if not status["authenticated"]:
    print("Triggering OAuth flow...")
    auth = requests.post(f"{BASE_URL}/auth/msgraph/login").json()
    
    if auth["success"]:
        print("✓ Authentication successful!")
    else:
        print(f"✗ Authentication failed: {auth['message']}")
        exit(1)

# 3. Use API
messages = requests.get(
    f"{BASE_URL}/outlook/messages",
    params={"folder": "inbox", "max_results": 5}
).json()

print(f"Found {len(messages.get('value', []))} messages")
```

---

## ✅ Summary

| What | Before | Now |
|------|--------|-----|
| **Check auth** | Call API and see if it fails | `GET /auth/msgraph/status` |
| **Authenticate** | First API call triggers OAuth | `POST /auth/msgraph/login` |
| **Debug setup** | Check logs | `GET /auth/msgraph/config` |
| **Clear token** | Delete file manually | `POST /auth/msgraph/logout` |
| **Get help** | Read docs | `GET /auth/msgraph/help` |

---

## 🎯 Next Steps

1. ✅ **Fix .env** - Remove duplicate CLIENT_ID, no spaces
2. ✅ **Restart server**
3. ✅ **Check config** - `/auth/msgraph/config`
4. ✅ **Login** - `/auth/msgraph/login` (opens browser)
5. ✅ **Verify** - `/auth/msgraph/status`
6. ✅ **Test API** - `/outlook/messages`

You're all set! 🚀

