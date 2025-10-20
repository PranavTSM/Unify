# 🚀 Simple Startup Guide - Fixed & Ready

## ✅ What's Been Fixed

1. **MongoDB connection** - Now loads `.env` properly ✅
2. **Repository bug** - Fixed `if self.db is not None` ✅  
3. **Parallel fetching** - Already implemented ✅
4. **Gmail batch API** - Already implemented ✅

---

## 📋 Start Services (Open 3 Terminals)

### Terminal 1: MCP Server (Port 8000)
```bash
cd C:\Users\pathe\Desktop\Unify\mcp_server
..\.venv\Scripts\python.exe app.py
```
**Wait for**: `Uvicorn running on http://127.0.0.1:8000`

---

### Terminal 2: LLM Service (Port 8002) 
```bash
cd C:\Users\pathe\Desktop\Unify\llm_service
..\.venv\Scripts\python.exe app.py
```
**Wait for**: `Uvicorn running on http://127.0.0.1:8002`

**Note**: You'll see Qdrant warnings - that's OK! Service will work without it.

---

### Terminal 3: Aggregator (Port 8001)
```bash
cd C:\Users\pathe\Desktop\Unify\aggregator
..\.venv\Scripts\python.exe app.py
```

**Look for these logs** (✅ = success):
```
INFO:__main__:Initializing MongoDB connection...
INFO:db.mongo_client:✅ MongoDB connected: unify_aggregator
INFO:db.mongo_client:✅ MongoDB indexes created
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

## 🧪 Test Everything Works

### 1. Test Health
```bash
curl http://localhost:8001/health
```

**Should show**:
```json
{
  "mongodb": {"healthy": true, "enabled": true}
}
```

### 2. Fetch Messages (This creates MongoDB collections!)
```bash
curl "http://localhost:8001/unified/messages?max_per_source=20"
```

**Watch the logs** - should show:
```
🚀 Fetching messages from all sources IN PARALLEL...
✅ gmail: fetched 20 messages
✅ outlook: fetched 15 messages
✅ teams: fetched 45 messages
⚡ PARALLEL FETCH COMPLETE: 80 messages in 3.45s
💾 MongoDB: Saved 80 messages
```

### 3. Check MongoDB Atlas

Go to your MongoDB Atlas → **Browse Collections**

You should NOW see:
- **Database**: `unify_aggregator`
  - ✅ **messages** collection (with ~80 documents)
  - ✅ **events** collection
  - ✅ **fetch_logs** collection

---

## 📊 Test Pagination

```bash
# Get first page
curl "http://localhost:8001/messages/paginated?page=1&page_size=10"

# Get Teams messages only
curl "http://localhost:8001/messages/paginated?source=teams"

# Search
curl "http://localhost:8001/messages/paginated?search=meeting"

# MongoDB statistics
curl "http://localhost:8001/statistics/mongodb"
```

---

## 🐛 If You See Errors

### "MongoDB not available"
- Check `.env` has `MONGO_URI` (your Atlas URI)
- Check `.env` has `MONGO_DB_NAME=unify_aggregator`
- Restart aggregator

### "Port already in use"
```bash
# Kill all Python processes
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force
```

### "MCP server refused connection"
- Make sure Terminal 1 (MCP server) is running
- Check `http://localhost:8000/health`

---

## ✅ Success Criteria

After starting all 3 services:

- [ ] MCP server running (port 8000)
- [ ] LLM service running (port 8002) 
- [ ] Aggregator running (port 8001)
- [ ] MongoDB shows `healthy: true`
- [ ] First fetch creates `unify_aggregator` database
- [ ] MongoDB has 3 collections (messages, events, fetch_logs)
- [ ] Parallel fetching completes in 3-5 seconds
- [ ] Pagination endpoints work

---

## 🎯 Your Collections Will Be

**Database**: `unify_aggregator`

**Collections**:
1. **messages** - All emails, chats (Gmail + Outlook + Teams)
2. **events** - Calendar events (Google + Microsoft)
3. **fetch_logs** - Operation logs for monitoring

All created automatically on first successful fetch! 🚀

---

**Now start the services in order and test!** The MongoDB collections will appear after the first successful fetch.

