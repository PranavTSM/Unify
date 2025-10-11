# How to Start All Services

## ✅ **Fixed Issues:**
1. ✅ Timezone error in merger - FIXED
2. ✅ Missing Teams endpoints (`/teams/joined` and `/teams/chats`) - ADDED
3. ✅ LLM service import error - FIXED

---

## **Start Services in Order:**

### **1. MCP Server (Port 8000)**
```powershell
python run_server.py --mode fastapi
```

### **2. LLM Service (Port 8002)**
```powershell
# Option 1: From project root (RECOMMENDED)
$env:PYTHONPATH="C:\Users\pathe\Desktop\Unify"
python llm_service/app.py

# Option 2: One-liner
$env:PYTHONPATH="C:\Users\pathe\Desktop\Unify"; python llm_service/app.py
```

### **3. Aggregator Service (Port 8001)**
```powershell
cd aggregator
python app.py
```

### **4. Frontend (Port 5173)**
```powershell
cd frontend
npm run dev
```

---

## **Or Use Batch Script (All at Once):**

Create `start_all.bat`:
```batch
@echo off
echo Starting all services...

start "MCP Server" cmd /k "python run_server.py --mode fastapi"
timeout /t 3 /nobreak >nul

start "LLM Service" cmd /k "set PYTHONPATH=%CD% && python llm_service/app.py"
timeout /t 3 /nobreak >nul

start "Aggregator" cmd /k "cd aggregator && python app.py"
timeout /t 3 /nobreak >nul

start "Frontend" cmd /k "cd frontend && npm run dev"

echo All services started!
```

---

## **Verify Services:**

```powershell
# Check all ports
netstat -ano | findstr ":8000 "  # MCP
netstat -ano | findstr ":8001 "  # Aggregator
netstat -ano | findstr ":8002 "  # LLM
netstat -ano | findstr ":5173 "  # Frontend

# Test health endpoints
Invoke-WebRequest -Uri "http://localhost:8000/health"
Invoke-WebRequest -Uri "http://localhost:8001/health"
Invoke-WebRequest -Uri "http://localhost:8002/health"
```

---

## **What Was Fixed:**

### **1. Timezone Error (aggregator/utils/merger.py)**
- **Before**: Mixed timezone-naive and timezone-aware datetimes
- **After**: All timestamps are now timezone-aware (UTC)

### **2. Missing Teams Endpoints (mcp_server/teams_routes.py)**
- **Added**: `GET /teams/joined` - Lists teams user has joined
- **Fixed**: `GET /teams/chats` - Already existed but wasn't being called correctly

### **3. LLM Service Import (llm_service/app.py)**
- **Before**: `ModuleNotFoundError: No module named 'llm_service'`
- **After**: Try/except import that works from both project root and llm_service directory

---

## **New Features Added:**

### **Backend:**
1. ✅ **Caching** (30s for messages, 60s for events)
2. ✅ **Message Actions** (mark read, star, archive, delete)
3. ✅ **Bulk Actions** (operate on multiple messages)
4. ✅ **Snooze** (snooze messages for later)
5. ✅ **Search** (search across all messages)
6. ✅ **Analytics** (inbox statistics and insights)
7. ✅ **Teams Integration** (chats + groups + channels)

### **Frontend:**
1. ✅ **MessageActions** component (quick actions on messages)
2. ✅ **Analytics** page (dashboard with charts)
3. ✅ **Bulk selection** mode in Inbox
4. ✅ **Enhanced priority** display with context

---

## **Endpoints Available:**

### **Message Actions:**
- `POST /messages/action` - Single message action
- `POST /messages/bulk-action` - Bulk operations
- `POST /messages/snooze` - Snooze message
- `GET /messages/snoozed` - Get snoozed messages
- `DELETE /messages/snooze/{id}` - Unsnooze

### **Search & Analytics:**
- `GET /search?query=...` - Search messages
- `GET /analytics/stats` - Get inbox statistics

### **Teams (NEW):**
- `GET /teams/joined` - User's joined teams
- `GET /teams/chats` - User's 1:1 chats
- `GET /teams/chats/{id}/messages` - Chat messages

---

## **Ready to Start!** 🚀

