# 🎨 Frontend Integration Plan

## 📊 Current State Analysis

### **Frontend Stack**
- **Framework**: React 18.3 + Vite 5.4
- **Routing**: React Router DOM 6.26
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React
- **Data**: Mock data (`mockData.js`) - **NEEDS REPLACEMENT**
- **Port**: 5173 (Vite default)

### **Backend Services Available**
1. **MCP Server** (Port 8000)
   - Raw API gateway
   - Direct access to Gmail, Outlook, Teams
   
2. **Aggregator** (Port 8001) ⭐ **PRIMARY API**
   - Unified inbox orchestration
   - Normalized data format
   - AI-powered features
   
3. **LLM Service** (Port 8002)
   - Direct AI processing
   - Memory system access

---

## 🎯 Integration Strategy

### **Approach**: Connect Frontend → Aggregator (Port 8001)

**Why Aggregator?**
- ✅ Single endpoint for all data
- ✅ Pre-normalized format
- ✅ Built-in deduplication
- ✅ Importance scoring
- ✅ AI features included

---

## 📋 API Mapping: Frontend → Backend

### **1. Dashboard Page**

| Frontend Need | Backend Endpoint | Method | Purpose |
|---------------|-----------------|--------|---------|
| Total Messages Count | `GET /unified/inbox` | GET | Get all messages |
| Unread Count | `GET /unified/inbox` | GET | Filter `is_read: false` |
| Recent Messages (5) | `GET /unified/inbox?max_per_source=20` | GET | Get recent messages |
| Today's Events | `GET /unified/calendar?days_ahead=1` | GET | Get today's events |

**Current Mock Data**:
```javascript
{
  dashboardStats: [
    { title: 'Total Messages', value: '1,284', ... },
    { title: 'Unread', value: '23', ... },
    ...
  ],
  messages: [...],
  calendarEvents: [...]
}
```

**Real API Response**:
```javascript
GET /unified/inbox
{
  priority_messages: [...],
  unread_messages: [...],
  upcoming_events: [...],
  summary: {
    total_messages: 1284,
    unread_count: 23,
    by_source: { gmail: 500, outlook: 600, teams: 184 }
  }
}
```

---

### **2. Inbox Page**

| Frontend Need | Backend Endpoint | Method | Purpose |
|---------------|-----------------|--------|---------|
| All Messages | `GET /unified/inbox` | GET | Get unified inbox |
| Filter by Source | `GET /unified/inbox` | GET | Use `by_source` field |
| Message Preview | Client-side | - | Already in response |
| Search Messages | `GET /unified/messages?min_score=0.5` | GET | Get filtered messages |

**Current Mock Data**:
```javascript
messages = [
  {
    id: 1,
    sender: 'Alice Johnson',
    subject: 'Project Alpha',
    preview: '...',
    content: '...',
    time: Date,
    read: false,
    hasAttachment: true,
    category: 'Teams',
    avatar: 'AJ'
  }
]
```

**Real API Response**:
```javascript
{
  "id": "18c3f4e5a2b8d1f9",
  "source": "gmail",
  "subject": "Project Alpha",
  "body": "...",
  "sender": {
    "name": "Alice Johnson",
    "email": "alice@example.com"
  },
  "timestamp": "2025-10-11T10:30:00Z",
  "is_read": false,
  "labels": ["IMPORTANT"],
  "attachments": [{ name: "file.pdf", size: 245000 }],
  "importance_score": 0.85
}
```

**Mapping Required**:
- `sender` object → `sender.name`
- `body` → `preview` (truncate to 150 chars)
- `source` → `category`
- `attachments.length > 0` → `hasAttachment`
- Generate `avatar` from `sender.name` initials

---

### **3. View Details Page (AI-Powered)**

| Frontend Need | Backend Endpoint | Method | Purpose |
|---------------|-----------------|--------|---------|
| Full Message | `GET /unified/inbox` | GET | Get message by ID |
| **AI Summary** ⭐ | `POST /unified/inbox/summarize` | POST | AI-generated summary |
| **Key Points** ⭐ | `POST /unified/inbox/summarize` | POST | Bullet points mode |
| **Action Items** ⭐ | `POST /unified/inbox/extract-actions` | POST | Extract actions |
| Priority/Sentiment | Computed | - | Use `importance_score` |

**Current**: Mock AI summary
**Real API**:

```javascript
// Summarization
POST /unified/inbox/summarize
{
  "message_ids": ["18c3f4e5a2b8d1f9"],
  "mode": "bullets",
  "max_words": 200
}

Response:
{
  "status": "success",
  "summary": "This message discusses...",
  "bullets": [
    "Meeting notes attached for Project Alpha",
    "Finalize mockups by end-of-week",
    "Prepare client presentation"
  ],
  "message_count": 1
}

// Action Extraction
POST /unified/inbox/extract-actions
{
  "message_ids": ["18c3f4e5a2b8d1f9"],
  "min_priority": "medium"
}

Response:
{
  "status": "success",
  "actions": [
    {
      "description": "Finalize mockups",
      "due_date": "2025-10-15T17:00:00Z",
      "priority": "high",
      "category": "task",
      "assignee": null
    }
  ],
  "summary": {
    "total_actions": 1,
    "by_priority": { "high": 1, "medium": 0, "low": 0 }
  }
}
```

---

### **4. Calendar Page**

| Frontend Need | Backend Endpoint | Method | Purpose |
|---------------|-----------------|--------|---------|
| Calendar Events | `GET /unified/calendar?days_ahead=30` | GET | Get month events |
| Today's Events | `GET /unified/calendar?days_ahead=1` | GET | Get today only |
| Upcoming Events | `GET /unified/calendar?days_ahead=7` | GET | Get next 7 days |

**Current Mock Data**:
```javascript
calendarEvents = [
  {
    id: 1,
    title: 'Team Standup',
    date: Date,
    duration: '30 min',
    type: 'meeting',
    attendees: ['John', 'Jane']
  }
]
```

**Real API Response**:
```javascript
{
  "normalized": [
    {
      "id": "evt_123",
      "source": "google_calendar",
      "title": "Team Standup",
      "start": "2025-10-11T09:00:00Z",
      "end": "2025-10-11T09:30:00Z",
      "location": "Zoom",
      "attendees": [
        { "email": "john@example.com", "name": "John Doe" }
      ],
      "organizer": {
        "email": "manager@example.com",
        "name": "Manager"
      }
    }
  ],
  "by_source": {
    "google_calendar": [...],
    "microsoft_calendar": [...]
  },
  "summary": {
    "total_events": 4
  }
}
```

**Mapping Required**:
- Calculate `duration` from `start` and `end`
- Determine `type` (meeting/presentation) from title or metadata
- Format attendees array

---

## 🏗️ Implementation Plan

### **Phase 1: Setup API Service Layer** ✅

Create API service files:

```
frontend/src/
├── services/
│   ├── api.js          # Base API client (axios/fetch)
│   ├── inbox.js        # Inbox API functions
│   ├── calendar.js     # Calendar API functions
│   ├── ai.js           # AI features (summarize, extract)
│   └── config.js       # API endpoints configuration
```

---

### **Phase 2: Replace Mock Data**

**Files to Update**:
1. `Dashboard.jsx` - Replace mock stats with real API
2. `Inbox.jsx` - Replace mock messages with real API
3. `ViewDetails.jsx` - Add real AI integration
4. `Calendar.jsx` - Replace mock events with real API

---

### **Phase 3: Add Loading & Error States**

Create components:
```
frontend/src/
├── components/
│   ├── LoadingSpinner.jsx
│   ├── ErrorMessage.jsx
│   ├── EmptyState.jsx
```

---

### **Phase 4: Docker Integration**

Update `docker-compose.yml`:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    - VITE_AGGREGATOR_URL=http://aggregator:8001
  depends_on:
    - aggregator
  networks:
    - unify_network
```

---

## 🔧 Technical Implementation Details

### **1. API Client Setup**

**frontend/src/services/api.js**:
```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_AGGREGATOR_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

---

### **2. Inbox Service**

**frontend/src/services/inbox.js**:
```javascript
import api from './api';

export const getUnifiedInbox = async (params = {}) => {
  const {
    max_per_source = 20,
    days_ahead = 3,
    priority_threshold = 0.6
  } = params;

  const response = await api.get('/unified/inbox', {
    params: {
      max_per_source,
      days_ahead,
      priority_threshold
    }
  });

  return response.data;
};

export const getAllMessages = async (params = {}) => {
  const response = await api.get('/unified/messages', { params });
  return response.data;
};
```

---

### **3. AI Service**

**frontend/src/services/ai.js**:
```javascript
import api from './api';

export const summarizeMessages = async (messageIds, options = {}) => {
  const {
    mode = 'bullets',
    max_words = 200,
    store_in_memory = false,
    session_id = null
  } = options;

  const response = await api.post('/unified/inbox/summarize', {
    message_ids: messageIds,
    mode,
    max_words,
    store_in_memory,
    session_id
  });

  return response.data;
};

export const extractActions = async (messageIds, options = {}) => {
  const {
    context = '',
    priority_mode = 'hybrid',
    min_priority = null
  } = options;

  const response = await api.post('/unified/inbox/extract-actions', {
    message_ids: messageIds,
    context,
    priority_mode,
    min_priority
  });

  return response.data;
};
```

---

### **4. Data Transformation Utils**

**frontend/src/utils/dataTransform.js**:
```javascript
// Transform backend message to frontend format
export const transformMessage = (apiMessage) => {
  return {
    id: apiMessage.id,
    sender: apiMessage.sender?.name || apiMessage.sender?.email || 'Unknown',
    subject: apiMessage.subject,
    preview: apiMessage.body?.substring(0, 150) + '...',
    content: apiMessage.body,
    time: new Date(apiMessage.timestamp),
    read: apiMessage.is_read,
    hasAttachment: apiMessage.attachments?.length > 0,
    category: formatSource(apiMessage.source),
    avatar: getInitials(apiMessage.sender?.name),
    importance_score: apiMessage.importance_score
  };
};

// Transform backend event to frontend format
export const transformEvent = (apiEvent) => {
  const start = new Date(apiEvent.start);
  const end = new Date(apiEvent.end);
  const durationMs = end - start;
  const durationMin = Math.floor(durationMs / 60000);

  return {
    id: apiEvent.id,
    title: apiEvent.title,
    date: start,
    duration: formatDuration(durationMin),
    type: detectEventType(apiEvent.title),
    attendees: apiEvent.attendees?.map(a => a.name || a.email) || []
  };
};

const getInitials = (name) => {
  if (!name) return '?';
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
};

const formatSource = (source) => {
  const sourceMap = {
    'gmail': 'Gmail',
    'outlook': 'Outlook',
    'teams': 'Teams'
  };
  return sourceMap[source] || source;
};

const detectEventType = (title) => {
  const title_lower = title.toLowerCase();
  if (title_lower.includes('presentation') || title_lower.includes('demo')) {
    return 'presentation';
  }
  return 'meeting';
};

const formatDuration = (minutes) => {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours} hour${hours > 1 ? 's' : ''}`;
};
```

---

## 🎨 UI Enhancements Needed

### **1. Loading States**
```javascript
// Add to each page
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

// Loading component
{loading && <LoadingSpinner />}
{error && <ErrorMessage error={error} />}
```

### **2. Error Handling**
```javascript
try {
  const data = await getUnifiedInbox();
  setMessages(data.priority_messages);
} catch (error) {
  setError('Failed to load messages. Please try again.');
  console.error(error);
}
```

### **3. Refresh/Polling**
```javascript
// Auto-refresh every 30 seconds
useEffect(() => {
  fetchData();
  const interval = setInterval(fetchData, 30000);
  return () => clearInterval(interval);
}, []);
```

---

## 🐳 Docker Configuration

### **Frontend Dockerfile**

**frontend/Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Install serve to run the app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Run the built app
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### **Environment Variables**

**frontend/.env.production**:
```env
VITE_AGGREGATOR_URL=http://aggregator:8001
VITE_LLM_SERVICE_URL=http://llm_service:8002
```

---

## 🧪 Testing Plan

### **1. Manual Testing Checklist**

- [ ] Dashboard loads with real data
- [ ] Inbox shows unified messages
- [ ] Filter by source (Teams, Outlook, Gmail)
- [ ] Search messages works
- [ ] View details shows full message
- [ ] AI summarization works
- [ ] Action extraction works
- [ ] Calendar shows real events
- [ ] Navigate between months
- [ ] Select date shows events

### **2. Integration Test Endpoints**

```bash
# Test Aggregator
curl http://localhost:8001/health
curl http://localhost:8001/unified/inbox

# Test AI Features
curl -X POST http://localhost:8001/unified/inbox/summarize \
  -H "Content-Type: application/json" \
  -d '{"mode": "bullets"}'
```

---

## ⚠️ Potential Issues & Solutions

### **Issue 1: CORS Errors**
**Solution**: Add CORS headers to aggregator
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Issue 2: Different Data Formats**
**Solution**: Use transformation utils (already planned)

### **Issue 3: Missing Fields**
**Solution**: Provide defaults in transformation layer

### **Issue 4: Slow API Responses**
**Solution**: Add loading states, implement caching

---

## 📦 Dependencies to Add

```bash
cd frontend
npm install axios
npm install @tanstack/react-query  # Optional: for data fetching
```

---

## 🚀 Rollout Plan

### **Step 1**: Setup (30 min)
- ✅ Create API service layer
- ✅ Add axios dependency
- ✅ Create transformation utils
- ✅ Add CORS to aggregator

### **Step 2**: Dashboard Integration (1 hour)
- ✅ Replace mock stats with API
- ✅ Add loading states
- ✅ Test with real data

### **Step 3**: Inbox Integration (1.5 hours)
- ✅ Replace mock messages with API
- ✅ Implement search/filter
- ✅ Add pagination (optional)

### **Step 4**: AI Features Integration (1 hour)
- ✅ Integrate summarization
- ✅ Integrate action extraction
- ✅ Update ViewDetails page

### **Step 5**: Calendar Integration (1 hour)
- ✅ Replace mock events with API
- ✅ Add event filtering
- ✅ Test navigation

### **Step 6**: Docker & Production (30 min)
- ✅ Create Dockerfile
- ✅ Update docker-compose.yml
- ✅ Test full stack

**Total Estimated Time**: 5.5 hours

---

## 📊 Success Criteria

✅ **All pages load real data from backend**
✅ **AI features (summarize, extract actions) working**
✅ **No mock data remaining**
✅ **Loading/error states implemented**
✅ **Docker compose starts entire stack**
✅ **No CORS errors**
✅ **Responsive and performant**

---

## 🎯 Next Steps

1. **Review this plan** - Confirm approach
2. **Start implementation** - Follow phase-by-phase
3. **Test incrementally** - After each phase
4. **Deploy** - Docker compose up

---

**Ready to integrate! 🚀**

