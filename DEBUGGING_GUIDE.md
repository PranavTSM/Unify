# 🔍 Email API Debugging Guide

## Issue: "Email API not getting called in Inbox"

### ✅ **What We Fixed:**

1. **Added Debug Logging** to track API calls:
   - `frontend/src/services/inbox.js` - Shows API params and response
   - `frontend/src/pages/Inbox.jsx` - Shows fetch flow step-by-step

### 🔎 **How to Debug:**

#### **1. Open Browser Console** (F12 → Console Tab)

Look for these logs when Inbox loads:

```
🔄 Inbox: Starting fetch messages...
📡 Inbox: Calling getUnifiedInbox...
📨 Calling /unified/inbox with params: {...}
✅ /unified/inbox response: {...}
📊 Messages count: {priority: 20, unread: 50, events: 5}
✅ Inbox: Got inbox data: {...}
📦 Inbox: Combined messages count: 70
✨ Inbox: Unique messages after dedup: 65
🔄 Inbox: Transformed messages: 65
✅ Inbox: Fetch complete!
```

#### **2. Check Network Tab** (F12 → Network Tab)

- Filter: `inbox`
- Look for: `GET http://localhost:8001/unified/inbox?max_per_source=50...`
- Status should be: **200 OK**
- Response should have: `priority_messages`, `unread_messages`, `summary`

---

### ⚠️ **Common Issues:**

#### **Issue 1: API Not Called at All**
**Symptoms:**
- No logs in console
- No requests in Network tab

**Causes:**
```javascript
// Component not mounted
// useEffect dependencies wrong
// Service not imported
```

**Fix:**
```javascript
import { getUnifiedInbox } from '@/services/inbox';

useEffect(() => {
  fetchMessages();
}, []); // Empty deps = run on mount
```

---

#### **Issue 2: CORS Error**
**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Fix:**
Check `aggregator/app.py` has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### **Issue 3: Wrong Base URL**
**Symptoms:**
```
Cannot connect to http://localhost:3000
```

**Fix:**
Check `frontend/src/services/config.js`:
```javascript
export const API_URLS = {
  AGGREGATOR_API_URL: import.meta.env.VITE_AGGREGATOR_URL || 'http://localhost:8001',
};
```

And `frontend/src/services/api.js`:
```javascript
const api = axios.create({
  baseURL: API_BASE_URL, // Should be http://localhost:8001
  timeout: 60000,
});
```

---

#### **Issue 4: Backend Not Running**
**Symptoms:**
```
ERR_CONNECTION_REFUSED
Network Error
```

**Fix:**
```powershell
# Check if aggregator is running
netstat -ano | findstr ":8001"

# Start if not running
cd aggregator
python app.py
```

---

#### **Issue 5: Empty Response**
**Symptoms:**
- 200 OK status
- But `priority_messages: []` and `unread_messages: []`

**Possible Causes:**
1. **MCP Server not running** → No data sources
2. **Gmail API not authenticated** → No Gmail data
3. **Outlook API not configured** → No Outlook data

**Fix:**
```powershell
# Check MCP server
netstat -ano | findstr ":8000"

# Start if not running
python run_server.py --mode fastapi

# Test MCP endpoints
Invoke-WebRequest -Uri "http://localhost:8000/gmail/messages?max_results=5"
Invoke-WebRequest -Uri "http://localhost:8000/outlook/messages?max_results=5"
```

---

### 🔧 **Quick Test Commands:**

#### **Test Backend Directly:**
```powershell
# 1. Test aggregator health
Invoke-WebRequest -Uri "http://localhost:8001/health"

# 2. Test unified inbox endpoint
Invoke-WebRequest -Uri "http://localhost:8001/unified/inbox?max_per_source=10"

# 3. Test unified messages endpoint
Invoke-WebRequest -Uri "http://localhost:8001/unified/messages?max_per_source=10"
```

#### **Expected Response:**
```json
{
  "priority_messages": [...],
  "unread_messages": [...],
  "upcoming_events": [...],
  "summary": {
    "total_messages": 150,
    "priority_count": 20,
    "unread_count": 50,
    "by_source": {
      "Gmail": 50,
      "Outlook": 100,
      "Teams": 0
    }
  }
}
```

---

### 📊 **Check Data Flow:**

```
Frontend (Inbox.jsx)
    ↓ calls
getUnifiedInbox() [frontend/src/services/inbox.js]
    ↓ axios.get
/unified/inbox [aggregator/app.py:73]
    ↓ calls
aggregator_service.get_unified_inbox() [aggregator/aggregator_service.py:230]
    ↓ calls
aggregator_service.aggregate_messages()
    ↓ calls
UnifiedAggregator.fetch_all_messages() [aggregator/fetchers.py:323]
    ↓ calls MCP endpoints
    ├─ /gmail/messages [MCP Server:8000]
    ├─ /outlook/messages [MCP Server:8000]
    └─ /teams/... [MCP Server:8000]
```

---

### ✅ **Verify Complete Setup:**

```powershell
# 1. All services running?
netstat -ano | findstr ":8000 :8001 :8002 :5173"

# Should see:
# 8000 - MCP Server
# 8001 - Aggregator
# 8002 - LLM Service
# 5173 - Frontend

# 2. Check logs show data
# Aggregator logs should show:
INFO:fetchers:Fetched 50 Gmail messages
INFO:fetchers:Fetched 100 Outlook messages
INFO:aggregator_service:Aggregation complete: 150 total messages

# 3. Frontend console should show:
✅ /unified/inbox response: {priority_messages: Array(20), ...}
```

---

### 🎯 **Most Likely Cause:**

Based on "Email API not getting called":

1. **Check Console** - Any React errors preventing component mount?
2. **Check Network** - Is the request actually being made?
3. **Check Base URL** - Is frontend pointing to correct backend?
4. **Check CORS** - Any CORS errors blocking the request?

---

### 🚀 **Quick Fix:**

```powershell
# Stop all services
taskkill /F /FI "WINDOWTITLE eq *MCP*"
taskkill /F /FI "WINDOWTITLE eq *Aggregator*"
taskkill /F /FI "WINDOWTITLE eq *LLM*"

# Start fresh
python run_server.py --mode fastapi
# Wait 3 seconds
cd aggregator; python app.py
# Wait 3 seconds
cd ../frontend; npm run dev
```

Then check browser console for the emoji debug logs! 📨✅📊

