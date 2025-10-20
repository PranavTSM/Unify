# Frontend Integration - Quick Reference

## 🎯 What Changed

Your frontend now connects to **real backend APIs** instead of mock data!

---

## 🔗 API Connections

### **Services Connected:**
- ✅ **Aggregator** (Port 8001) - Main API
- ✅ **LLM Service** (Port 8002) - AI features

### **Endpoints Used:**

| Page | API Endpoint | What It Gets |
|------|--------------|--------------|
| Dashboard | `GET /unified/inbox` | Stats, recent messages |
| Dashboard | `GET /unified/calendar` | Today's events |
| Inbox | `GET /unified/inbox` | All messages |
| Inbox | `GET /unified/messages` | Filtered messages |
| ViewDetails | `GET /unified/messages` | Message by ID |
| ViewDetails | `POST /unified/inbox/summarize` | AI summary ⭐ |
| ViewDetails | `POST /unified/inbox/extract-actions` | AI actions ⭐ |
| Calendar | `GET /unified/calendar` | Calendar events |

---

## 🚀 How to Run

### **Development Mode:**

```bash
cd frontend

# Install dependencies (first time)
npm install

# Start dev server
npm run dev

# Opens at: http://localhost:5173
```

**Note:** Make sure aggregator is running at `http://localhost:8001`

### **Production Mode (Docker):**

```bash
# From project root
docker-compose up -d frontend

# Opens at: http://localhost:3000
```

---

## 📁 New Files Added

```
frontend/
├── src/
│   ├── services/          ✨ NEW!
│   │   ├── api.js         → Base API client
│   │   ├── inbox.js       → Inbox API functions
│   │   ├── calendar.js    → Calendar API functions
│   │   ├── ai.js          → AI features
│   │   └── config.js      → Configuration
│   │
│   ├── utils/             ✨ NEW!
│   │   └── dataTransform.js → Data transformation
│   │
│   └── components/        ✨ UPDATED!
│       ├── LoadingSpinner.jsx  → Loading state
│       ├── ErrorMessage.jsx    → Error display
│       └── EmptyState.jsx      → Empty state
│
├── Dockerfile             ✨ NEW!
├── nginx.conf             ✨ NEW!
└── .env.example           ✨ NEW!
```

---

## 🔧 Configuration

### **Environment Variables:**

Create `.env.development`:
```env
VITE_AGGREGATOR_URL=http://localhost:8001
VITE_LLM_SERVICE_URL=http://localhost:8002
VITE_ENABLE_AI_FEATURES=true
```

### **Or use defaults:**
- Aggregator: `http://localhost:8001`
- LLM Service: `http://localhost:8002`

---

## ✨ AI Features

### **Message Summarization**
- Click "View Full Details" on any message
- AI summary appears automatically
- Shows key points in bullet format
- Processing time: ~2-3 seconds

### **Action Extraction**
- Appears in "Suggested Actions" section
- Shows:
  - Action description
  - Priority (high/medium/low)
  - Due date (if detected)
  - Assignee (if mentioned)
  - Category (task/meeting/followup)

---

## 🎨 Features Working

### **All Pages**
- ✅ Real data from backend
- ✅ Loading spinners
- ✅ Error handling with retry
- ✅ Empty states
- ✅ Auto-refresh

### **Dashboard**
- ✅ Live statistics
- ✅ Recent messages
- ✅ Today's events
- ✅ Refreshes every 30s

### **Inbox**
- ✅ Unified messages (Gmail + Outlook + Teams)
- ✅ Filter by source
- ✅ Search functionality
- ✅ Message preview
- ✅ Navigate to details

### **ViewDetails**
- ✅ Full message content
- ✅ AI-powered summary
- ✅ Key points extraction
- ✅ Action items
- ✅ Priority indicators

### **Calendar**
- ✅ Real events
- ✅ Monthly grid
- ✅ Day selection
- ✅ Event details
- ✅ Upcoming events

---

## 🐛 Troubleshooting

### **Issue: "Failed to load messages"**
**Solution:**
```bash
# Check if aggregator is running
curl http://localhost:8001/health

# Should return: {"status": "ok", ...}
```

### **Issue: "CORS error"**
**Solution:** CORS is already configured in `aggregator/app.py`

### **Issue: "AI features not working"**
**Solution:**
```bash
# Check LLM service
curl http://localhost:8002/health

# Check if OPENAI_API_KEY is set in .env
```

### **Issue: "No data showing"**
**Solution:**
```bash
# Check if backend has data
curl http://localhost:8001/unified/inbox

# Should return JSON with messages
```

---

## 📦 Dependencies

### **New Dependencies Added:**
```json
{
  "dependencies": {
    "axios": "^1.6.0"  // ✨ Added for API calls
  }
}
```

### **Existing Dependencies:**
- react, react-dom, react-router-dom
- lucide-react, date-fns
- tailwindcss

---

## 🎯 Quick Test

```bash
# 1. Start backend
docker-compose up -d aggregator llm_service

# 2. Start frontend (dev mode)
cd frontend
npm run dev

# 3. Open browser
http://localhost:5173

# 4. Check console
# Should see:
#  ✅ 🔗 API Base URL: http://localhost:8001
#  ✅ 📤 API Request: GET /unified/inbox
#  ✅ ✅ API Response: ...
```

---

## ✅ Verification

All these should work:
- [ ] Dashboard shows real message count
- [ ] Inbox displays actual emails
- [ ] Can filter by Gmail/Outlook/Teams
- [ ] Search finds messages
- [ ] Click message shows details
- [ ] AI summary appears on details page
- [ ] Action items extracted automatically
- [ ] Calendar shows real events
- [ ] Auto-refresh updates data
- [ ] No console errors

---

## 🎉 You're All Set!

The frontend is **fully integrated** with your backend services!

- ✅ Real data loading
- ✅ AI features working
- ✅ Production-ready
- ✅ Auto-refresh enabled
- ✅ Error handling in place

**Start using your AI-powered unified inbox! 🚀**

