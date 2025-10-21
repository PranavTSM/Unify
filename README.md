# Unify - Universal Inbox Aggregator 📧

<div align="center">

**A unified inbox that aggregates Gmail, Outlook, Teams, and Calendar events**  
**Powered by AI for smart summaries and action extraction**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green.svg)](https://www.mongodb.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)

</div>

---

## 🌟 Overview

**Unify** is a comprehensive unified inbox system that brings together all your communication channels into one intelligent interface:

- 📧 **Gmail** - Read, search, and manage emails
- 📨 **Outlook** - Microsoft email integration
- 💬 **Microsoft Teams** - Team chat and channel messages
- 📅 **Calendars** - Google Calendar & Microsoft Calendar events
- 🤖 **AI-Powered** - Smart summaries and action extraction using GPT-4o mini
- 💾 **MongoDB Storage** - Persistent data with fast search and pagination
- 🎨 **Modern UI** - Beautiful React frontend with real-time updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                     http://localhost:5173                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Aggregator Service (FastAPI)                  │
│                     http://localhost:8001                       │
│  • Fetches & normalizes messages from all sources               │
│  • Scores & ranks by importance                                 │
│  • Stores in MongoDB for persistence                            │
└──────┬─────────────────────┬─────────────────────┬──────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│ MCP Server   │    │ LLM Service  │    │ MongoDB Database     │
│ Port: 8000   │    │ Port: 8002   │    │ Port: 27017          │
│              │    │              │    │                      │
│ • Google API │    │ • OpenAI     │    │ • Messages           │
│ • MS Graph   │    │ • Summarize  │    │ • Events             │
│ • Auth       │    │ • Actions    │    │ • Search Index       │
└──────────────┘    └──────────────┘    └──────────────────────┘
```

See [SYSTEM_DIAGRAM.txt](SYSTEM_DIAGRAM.txt) for detailed architecture.

---

## ✨ Features

### 📧 Multi-Source Email Integration
- **Gmail** - Full email access via Google API
- **Outlook** - Microsoft 365 email via MS Graph
- **Teams** - Channel messages and chats
- **Unified View** - All messages in one place

### 🤖 AI-Powered Intelligence
- **Smart Summaries** - GPT-4o mini generates concise email summaries
- **Action Extraction** - Automatically detect tasks, deadlines, and priorities
- **Importance Scoring** - ML-based ranking of messages
- **Context-Aware** - Remembers conversation history

### 💾 Persistent Storage
- **MongoDB Integration** - All data stored permanently
- **Fast Pagination** - Handle thousands of messages efficiently
- **Full-Text Search** - Find anything instantly
- **Advanced Filtering** - Filter by source, status, importance, date

### 📅 Calendar Management
- **Google Calendar** - View and manage events
- **Microsoft Calendar** - Microsoft 365 calendar integration
- **Free/Busy** - Check availability across calendars
- **Smart Scheduling** - AI-suggested meeting times

### ⚡ Advanced Features
- **Message Actions** - Mark read, star, archive, delete
- **Snooze** - Temporarily hide messages
- **Labels & Categories** - Organize messages
- **Bulk Operations** - Act on multiple messages at once
- **Real-Time Updates** - Live data synchronization

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+** (for frontend)
- **MongoDB** (local or cloud)
- **OpenAI API Key** (for AI features)
- **Google Cloud Project** (for Gmail/Calendar)
- **Azure AD App** (for Outlook/Teams)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/unify.git
cd unify
```

### 2️⃣ Configure Environment

Copy `example.env` to `.env` and fill in your credentials:

```env
# MongoDB
MONGO_URI='mongodb://localhost:27017'
MONGO_DB_NAME='unify_aggregator'

# OpenAI
OPENAI_API_KEY='sk-proj-your-key-here'

# Google OAuth (for Gmail & Google Calendar)
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret'
GOOGLE_SCOPES='https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/gmail.readonly'

# Microsoft Azure (for Outlook & Teams)
OUT_CLIENT_ID='your-azure-client-id'
OUT_CLIENT_SECRET='your-azure-client-secret'
OUT_TENANT_ID='common'
```

### 3️⃣ Start MongoDB

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

### 4️⃣ Install Dependencies

```bash
# Backend services
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 5️⃣ Start Services

**Option A: Individual Services** (for development)

```bash
# Terminal 1: MCP Server (Google & Microsoft APIs)
cd mcp_server
python app.py
# Running on http://localhost:8000

# Terminal 2: LLM Service (AI features)
cd llm_service
python app.py
# Running on http://localhost:8002

# Terminal 3: Aggregator (Main backend)
cd aggregator
python app.py
# Running on http://localhost:8001

# Terminal 4: Frontend
cd frontend
npm run dev
# Running on http://localhost:5173
```

**Option B: Docker Compose** (for production)

```bash
docker-compose up -d
```

### 6️⃣ Open in Browser

Navigate to: **http://localhost:5173**

---

## 📖 Documentation

### Quick Start Guides
- 📘 [README_IMPORTANT.md](README_IMPORTANT.md) - Recent fixes and important updates
- 🚀 [SIMPLE_STARTUP_GUIDE.md](SIMPLE_STARTUP_GUIDE.md) - Step-by-step startup instructions
- ⚡ [Aggregator Quick Start](aggregator/QUICK_START.md) - Backend API quick start

### Service Documentation
- 🔌 [Aggregator API Guide](aggregator/API_INTEGRATION_GUIDE.md) - REST API reference
- 🤖 [LLM Service README](llm_service/README.md) - AI features and configuration
- 📊 [MongoDB Integration](aggregator/db/README.md) - Database usage and queries
- 🎨 [Frontend README](frontend/README.md) - UI development guide
- ✨ [Frontend Features](frontend/FEATURES.md) - Complete feature list

### Setup Guides
- 🔐 [Google Authentication](mcp_server/google_auth_routes.py) - Gmail/Calendar OAuth setup
- 🔐 [Microsoft Authentication](MSGRAPH_SETUP.md) - Outlook/Teams OAuth setup
- 📅 [Microsoft Graph Quick Start](MSGRAPH_QUICK_START.md) - MS Graph API setup
- 🔧 [Microsoft Graph Implementation](MSGRAPH_IMPLEMENTATION.md) - Technical details

### Architecture & Advanced
- 🏗️ [Architecture Analysis](ARCHITECTURE_ANALYSIS.md) - System design and patterns
- 🏗️ [System Diagram](SYSTEM_DIAGRAM.txt) - Visual architecture overview
- 💾 [MongoDB & Performance Guide](MONGODB_AND_PERFORMANCE_GUIDE.md) - Database optimization
- 💬 [Teams Implementation](ASYNC_TEAMS_IMPLEMENTATION.md) - Microsoft Teams integration
- 🔗 [Frontend Integration](frontend/INTEGRATION_README.md) - API integration patterns

---

## 🔑 API Keys & Authentication

### OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Create a new secret key
3. Add to `.env`: `OPENAI_API_KEY='sk-proj-...'`

**Pricing**: GPT-4o mini costs ~$0.50/month for 100 emails/day (70% cheaper than GPT-3.5!)

### Google Cloud (Gmail & Calendar)
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable APIs:
   - Google Calendar API
   - Gmail API
4. Create OAuth 2.0 credentials (Desktop App)
5. Add redirect URI: `http://localhost:8080/oauth2callback`
6. Download credentials and add to `.env`

### Microsoft Azure (Outlook & Teams)
1. Go to: https://portal.azure.com/
2. Navigate to **Azure Active Directory** → **App registrations**
3. Create new registration
4. Add redirect URI: `http://localhost:8081`
5. Generate client secret
6. Grant permissions:
   - Mail.ReadWrite
   - Calendars.ReadWrite
   - ChannelMessage.Read.All
   - Chat.Read
7. Add credentials to `.env`

---

## 🛠️ API Endpoints

### Aggregator Service (Port 8001)

#### Messages & Inbox
```bash
# Get unified inbox with priority messages
GET /unified/inbox?priority_threshold=0.6

# Get all messages (paginated)
GET /unified/messages?max_per_source=20

# Get messages from MongoDB (paginated with search)
GET /messages/paginated?page=1&page_size=20&search=urgent

# Get single message
GET /messages/{message_id}

# Summarize inbox with AI
POST /unified/inbox/summarize
{
  "mode": "executive",  # executive, bullets, paragraph
  "max_words": 200
}

# Extract action items with AI
POST /unified/inbox/extract-actions
{
  "priority_mode": "hybrid"  # heuristic, llm, hybrid
}
```

#### Calendar Events
```bash
# Get unified calendar
GET /unified/calendar?days_ahead=7

# Get events (paginated)
GET /events/paginated?page=1&page_size=20

# Get all data (messages + events)
GET /unified/all
```

#### Message Actions
```bash
# Perform action on message
POST /messages/action
{
  "message_id": "msg_123",
  "source": "gmail",
  "action": "mark_read"  # mark_read, mark_unread, star, archive, delete
}

# Bulk action
POST /messages/bulk-action
{
  "message_ids": ["msg_1", "msg_2"],
  "source": "gmail",
  "action": "mark_read"
}

# Snooze message
POST /messages/snooze
{
  "message_id": "msg_123",
  "snooze_minutes": 60
}
```

#### Search & Analytics
```bash
# Search messages
GET /search?query=urgent&sources=gmail,outlook&max_results=50

# Get statistics
GET /analytics/stats

# MongoDB statistics
GET /statistics/mongodb
```

### LLM Service (Port 8002)

```bash
# Summarize text
POST /summarize
{
  "text": "Long email content...",
  "max_length": 150
}

# Extract actions from text
POST /extract-actions
{
  "text": "Email with tasks...",
  "context": "Project discussion"
}

# Batch summarize messages
POST /summarize-batch
{
  "messages": [...],
  "mode": "executive"
}

# Store in memory (for context)
POST /store
{
  "id": "msg_123",
  "text": "...",
  "session_id": "user_session"
}

# Query context
GET /context?query=project&session_id=user_session
```

### MCP Server (Port 8000)

```bash
# Google Calendar
GET /calendars
GET /calendars/{calendar_id}/events
POST /calendars/{calendar_id}/events
PUT /calendars/{calendar_id}/events/{event_id}
DELETE /calendars/{calendar_id}/events/{event_id}

# Gmail
GET /gmail/messages
GET /gmail/messages/{message_id}
POST /gmail/messages:send
POST /gmail/messages/{message_id}:modify

# Microsoft Calendar
GET /msgraph/calendar/events
POST /msgraph/calendar/events

# Outlook
GET /msgraph/outlook/messages
GET /msgraph/outlook/messages/{message_id}

# Teams
GET /msgraph/teams
GET /msgraph/teams/{team_id}/channels
GET /msgraph/teams/{team_id}/channels/{channel_id}/messages
```

See [API_INTEGRATION_GUIDE.md](aggregator/API_INTEGRATION_GUIDE.md) for complete API reference.

---

## 🎨 Frontend

Built with **React + Vite + TailwindCSS**

### Features
- 📱 **Responsive Design** - Works on desktop, tablet, mobile
- 🎨 **Modern UI** - Clean, intuitive interface
- ⚡ **Real-Time Updates** - Live data synchronization
- 🔍 **Advanced Search** - Filter and search across all sources
- 📊 **Dashboard** - Analytics and statistics
- 🎯 **Smart Inbox** - AI-prioritized messages
- 📅 **Calendar View** - Integrated calendar
- ⚙️ **Settings** - Customize your experience

### Development

```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

See [frontend/README.md](frontend/README.md) for more details.

---

## 💾 MongoDB Integration

### Features
- ✅ **Persistent Storage** - All messages and events stored permanently
- ✅ **Fast Queries** - Optimized indexes for sub-second queries
- ✅ **Pagination** - Handle 100,000+ messages efficiently
- ✅ **Full-Text Search** - Search across subject, body, sender
- ✅ **Advanced Filtering** - Filter by source, date, importance, read status
- ✅ **Deduplication** - Automatic upsert to prevent duplicates
- ✅ **Statistics** - Real-time analytics and insights

### Collections
- `messages` - Email and chat messages
- `events` - Calendar events
- `fetch_logs` - API operation logs

See [aggregator/db/README.md](aggregator/db/README.md) for database documentation.

---

## 🤖 AI Features (OpenAI GPT-4o Mini)

### Configuration
```python
Model: "gpt-4o-mini"        # Fast & cost-effective
Temperature: 0.3            # Balanced creativity
Max Tokens: 200             # Concise responses
```

### Capabilities

#### 1. Email Summarization
- **Executive Mode** - Brief overview with key points
- **Bullets Mode** - Bullet-point list
- **Paragraph Mode** - Detailed paragraph summary

#### 2. Action Item Extraction
- Automatically detect tasks and to-dos
- Extract due dates and deadlines
- Identify assignees
- Prioritize actions (high/medium/low)
- Categorize (task/meeting/followup/decision)

#### 3. Smart Features
- Context-aware summaries
- Multi-email thread understanding
- Meeting invitation parsing
- Deadline detection
- Priority scoring

### Cost Estimate
- **100 emails/day**: ~$0.50/month
- **1000 emails/day**: ~$5/month
- **70% cheaper** than GPT-3.5 Turbo!

---

## 🔧 Configuration

### Environment Variables

```env
# ==================== MongoDB ====================
MONGO_URI='mongodb://localhost:27017'
MONGO_DB_NAME='unify_aggregator'

# ==================== OpenAI ====================
OPENAI_API_KEY='sk-proj-...'

# ==================== Google ====================
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret'
TOKEN_FILE_PATH='.gcp-saved-tokens.json'
OAUTH_CALLBACK_PORT=8080
GOOGLE_SCOPES='https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.labels'

# ==================== Microsoft ====================
OUT_CLIENT_ID='your-azure-client-id'
OUT_CLIENT_SECRET='your-azure-client-secret'
OUT_TENANT_ID='common'
MSGRAPH_TOKEN_FILE='.msgraph-tokens.json'
MSGRAPH_CALLBACK_PORT=8081

# ==================== Service URLs ====================
MCP_SERVER_URL='http://localhost:8000'
LLM_SERVICE_URL='http://localhost:8002'
AGGREGATOR_URL='http://localhost:8001'
```

See [example.env](example.env) for complete configuration template.

---

## 🧪 Testing

### Test Scripts

```bash
# Test MongoDB integration
python test_mongodb_fix.py

# Test aggregator endpoints
curl http://localhost:8001/health

# Test LLM service
curl http://localhost:8002/health

# Test MCP server
curl http://localhost:8000/health

# Integration test
python test_integration.py
```

### Health Checks

```bash
# Check all services
curl http://localhost:8001/health  # Aggregator
curl http://localhost:8002/health  # LLM Service
curl http://localhost:8000/health  # MCP Server
```

---

## 📊 Performance

### Benchmarks
- **Message Fetch**: ~2-5 seconds for 100 messages across all sources
- **MongoDB Query**: <10ms for paginated queries
- **AI Summarization**: ~1-2 seconds per email
- **Full Inbox Load**: ~5-10 seconds for complete unified view

### Optimization
- Automatic caching (30-60 seconds TTL)
- Lazy loading and pagination
- Indexed database queries
- Parallel API calls
- Connection pooling

---

## 🛡️ Security

### Best Practices
- ✅ OAuth 2.0 for all API access
- ✅ Tokens stored securely in local files
- ✅ Environment variables for credentials
- ✅ HTTPS recommended for production
- ✅ Rate limiting on API endpoints
- ✅ Input validation and sanitization

### Production Checklist
- [ ] Use HTTPS for all services
- [ ] Enable MongoDB authentication
- [ ] Set OpenAI usage limits
- [ ] Configure CORS properly
- [ ] Use secret management (e.g., AWS Secrets Manager)
- [ ] Enable audit logging
- [ ] Regular security updates

---

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Not Connecting
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify connection string in .env
MONGO_URI='mongodb://localhost:27017'
```

#### OpenAI API Errors
```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check usage and limits
https://platform.openai.com/usage
```

#### Google OAuth Issues
- Verify redirect URI matches: `http://localhost:8080/oauth2callback`
- Check OAuth consent screen is configured
- Ensure APIs are enabled in Google Cloud Console
- Delete `.gcp-saved-tokens.json` and re-authenticate

#### Microsoft Graph Issues
- Verify redirect URI: `http://localhost:8081`
- Check app permissions in Azure AD
- Ensure "Allow public client flows" is enabled
- Delete `.msgraph-tokens.json` and re-authenticate

---

## 📈 Roadmap

### Planned Features
- [ ] **Slack Integration** - Add Slack messages
- [ ] **Mobile App** - Native iOS/Android apps
- [ ] **Email Templates** - Quick reply templates
- [ ] **Smart Rules** - Automatic message routing
- [ ] **Voice Commands** - Voice-activated actions
- [ ] **Browser Extension** - Quick access from browser
- [ ] **Multi-User** - Team accounts and sharing
- [ ] **Advanced Analytics** - ML-powered insights
- [ ] **Webhook Support** - Real-time push notifications
- [ ] **Plugin System** - Extensible architecture

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **React** - UI library
- **OpenAI** - AI/LLM capabilities
- **MongoDB** - Database
- **Google APIs** - Gmail & Calendar
- **Microsoft Graph** - Outlook & Teams
- **LangChain** - LLM framework

---

## 📞 Support

### Documentation
- 📘 [Complete Documentation Index](#-documentation)
- 🚀 [Quick Start Guide](#-quick-start)
- 🆘 [Troubleshooting](#-troubleshooting)

### Get Help
- 🐛 Report bugs via GitHub Issues
- 💬 Ask questions in Discussions
- 📧 Contact: support@yourproject.com

---

<div align="center">

**Made with ❤️ using Python, React, and AI**

**Unify - One Inbox to Rule Them All** 📧

[Documentation](#-documentation) • [Quick Start](#-quick-start) • [Features](#-features) • [API](#-api-endpoints)

</div>
