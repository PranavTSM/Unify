# 🚀 Quick Startup Guide

## ⚡ **Fastest Way to Start Everything**

### **Method 1: Automated Script (Recommended)**

```bash
.\start_all_services.bat
```

This starts all 4 services in separate windows.

**Wait 15 seconds**, then open: **http://localhost:5174**

---

### **Method 2: Docker (Production)**

```bash
docker-compose up -d
```

**Wait 60 seconds**, then open: **http://localhost:3000**

---

## 📋 **Manual Startup (If Needed)**

If you prefer to start services manually:

### **Terminal 1: MCP Server**
```bash
cd mcp_server
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### **Terminal 2: LLM Service**
```bash
cd llm_service
python -m uvicorn app:app --host 0.0.0.0 --port 8002
```

### **Terminal 3: Aggregator**
```bash
cd aggregator
python app.py
```

### **Terminal 4: Frontend**
```bash
cd frontend
npm run dev
```

**Then open:** http://localhost:5174

---

## ✅ **Service Check**

After starting, verify all are running:

```bash
curl http://localhost:8000/health  # Should return JSON
curl http://localhost:8001/health  # Should return JSON
curl http://localhost:8002/health  # Should return JSON
curl http://localhost:5174         # Should return HTML
```

---

## 🎯 **What to Expect**

### **After All Services Start:**

**Browser Console (F12):**
```
✅ 🔗 API Base URL: http://localhost:8001
✅ 📤 API Request: GET /unified/inbox
✅ ✅ API Response: {priority_messages: [...], unread_messages: [...]}
```

**Frontend UI:**
```
✅ Dashboard shows real message count
✅ Recent messages displayed  
✅ Inbox loads unified messages
✅ Can filter and search
✅ AI features work (View Details page)
```

---

## 🐛 **If Something Goes Wrong**

### **CORS Error Still Showing:**
```bash
# Make sure aggregator restarted
# Stop it (Ctrl+C) and restart:
cd aggregator
python app.py
```

### **No Data Loading:**
```bash
# Check if MCP server has data:
curl http://localhost:8001/unified/inbox

# Should return JSON with messages
```

### **AI Features Not Working:**
```bash
# Check if LLM service is running:
curl http://localhost:8002/health

# If not, start it:
cd llm_service
python -m uvicorn app:app --host 0.0.0.0 --port 8002
```

---

## 🎉 **Success Criteria**

All these should work:
- [ ] Dashboard loads without errors
- [ ] Shows real message count
- [ ] Recent messages displayed
- [ ] Inbox shows unified emails
- [ ] Filter buttons work
- [ ] Search works
- [ ] Can view message details
- [ ] AI summary appears
- [ ] Action items extracted
- [ ] No CORS errors in console

---

## 📚 **Help Files**

| File | Purpose |
|------|---------|
| `start_all_services.bat` | Start all services |
| `FIX_ALL_ERRORS.md` | Error analysis & fixes |
| `QUICK_FIX.md` | CORS quick fix |
| `CURRENT_STATUS_AND_FIX.md` | Current status |

---

**Everything is ready! Just run the startup script! 🚀**

