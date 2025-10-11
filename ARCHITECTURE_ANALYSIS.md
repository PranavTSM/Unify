# 🏗️ Complete Architecture Analysis - Unify System

## 📊 System Overview

Your system has **3 microservices** + **5 external dependencies**:

### **Services:**
1. **MCP Server** (Port 8000) - Backend API Gateway
2. **Aggregator** (Port 8001) - Orchestration Layer
3. **LLM Service** (Port 8002) - AI Processing

### **External Dependencies:**
1. **Google APIs** (Gmail, Calendar)
2. **Microsoft Graph** (Outlook, Teams, Calendar)
3. **OpenAI API** (GPT models)
4. **Qdrant** (Vector database - Port 6333)
5. **Redis** (Cache/Memory - Port 6379)

---

## 🔄 Complete Connection Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL APIS                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Google APIs  │  │   MS Graph   │  │  OpenAI API  │              │
│  │  - Gmail     │  │  - Outlook   │  │  - GPT-3.5   │              │
│  │  - Calendar  │  │  - Teams     │  │  - GPT-4     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          ▼                  ▼                  │
┌─────────────────────────────────────────┐    │
│   MCP SERVER (Backend)                  │    │
│   Port: 8000                            │    │
│   Network: unify_network                │    │
│  ┌────────────────────────────────────┐ │    │
│  │ ENDPOINTS:                         │ │    │
│  │  GET /gmail/messages               │ │    │
│  │  GET /outlook/messages             │ │    │
│  │  GET /teams/messages               │ │    │
│  │  GET /calendars/{id}/events        │ │    │
│  │  GET /health                       │ │    │
│  │                                    │ │    │
│  │ AUTHENTICATION:                    │ │    │
│  │  - Google OAuth2 (credentials)     │ │    │
│  │  - MS Graph OAuth2 (MSAL)          │ │    │
│  │                                    │ │    │
│  │ STORES:                            │ │    │
│  │  - .gcp-saved-tokens.json          │ │    │
│  │  - .msgraph-tokens.json            │ │    │
│  └────────────────────────────────────┘ │    │
└───────────┬─────────────────────────────┘    │
            │                                   │
            │ HTTP Requests                     │
            ▼                                   │
┌─────────────────────────────────────────┐    │
│   AGGREGATOR (Orchestrator)             │    │
│   Port: 8001                            │    │
│   Network: unify_network                │    │
│  ┌────────────────────────────────────┐ │    │
│  │ COMPONENTS:                        │ │    │
│  │  1. UnifiedAggregator              │ │    │
│  │     - GmailFetcher   ────┐         │ │    │
│  │     - OutlookFetcher ────┼─────────┼────> MCP Server
│  │     - TeamsFetcher   ────┤         │ │    (Fetches raw data)
│  │     - CalendarFetcher ───┘         │ │    
│  │                                    │ │    
│  │  2. AggregatorService              │ │    
│  │     - Normalizers                  │ │    
│  │     - Merger (dedup/sort)          │ │    
│  │     - Scoring                      │ │    
│  │                                    │ │    
│  │  3. LLMServiceClient               │ │    
│  │     - Summarization requests ──────┼────┐ 
│  │     - Action extraction requests ──┼────┤ 
│  │                                    │ │   │ 
│  │ ENDPOINTS:                         │ │   │ 
│  │  GET  /unified/inbox               │ │   │ 
│  │  GET  /unified/calendar            │ │   │ 
│  │  POST /unified/inbox/summarize     │ │   │ 
│  │  POST /unified/inbox/extract-actns │ │   │ 
│  │  GET  /health                      │ │   │ 
│  └────────────────────────────────────┘ │   │ 
└─────────────────────────────────────────┘   │ 
                                              │ 
            HTTP Requests                     │ 
            ▼                                 │ 
┌─────────────────────────────────────────┐  │ 
│   LLM SERVICE (AI Processing)           │  │ 
│   Port: 8002                            │  │ 
│   Network: unify_network                │  │ 
│  ┌────────────────────────────────────┐ │  │ 
│  │ COMPONENTS:                        │ │  │ 
│  │  1. Summarizer (LangChain)         │ │  │ 
│  │     - generate_summary() ──────────┼──┼──┘
│  │                                    │ │  OpenAI API
│  │  2. Action Extractor (LangChain)   │ │  
│  │     - extract_action_items() ──────┼──┼──> OpenAI API
│  │                                    │ │  
│  │  3. Memory System:                 │ │  
│  │     a) Qdrant (Vector Store) ──────┼────> Qdrant (6333)
│  │        - Semantic search           │ │  
│  │        - Embedding storage          │ │  
│  │                                    │ │  
│  │     b) Redis (Chat Memory) ────────┼────> Redis (6379)
│  │        - Conversation history      │ │  
│  │        - Session management         │ │  
│  │                                    │ │  
│  │  4. UnifiedRetriever               │ │  
│  │     - Combines Qdrant + Redis      │ │  
│  │     - Context retrieval            │ │  
│  │                                    │ │  
│  │ ENDPOINTS:                         │ │  
│  │  POST /summarize-batch             │ │  
│  │  POST /extract-actions             │ │  
│  │  POST /ingest                      │ │  
│  │  POST /store                       │ │  
│  │  POST /query                       │ │  
│  │  GET  /context                     │ │  
│  │  GET  /health                      │ │  
│  │  GET  /memory/status               │ │  
│  └────────────────────────────────────┘ │  
└─────────────────────────────────────────┘  
```

---

## 🔗 Connection Details

### **1. MCP Server ↔ External APIs**

**Google APIs:**
```
MCP Server
  ├─ Uses: google-auth-oauthlib, google-api-python-client
  ├─ Auth: OAuth2 flow with credentials.json
  ├─ Tokens: Stored in .gcp-saved-tokens.json
  ├─ Endpoints:
  │   ├─ GET /gmail/messages → Gmail API
  │   └─ GET /calendars/{id}/events → Calendar API
  └─ Environment:
      ├─ GOOGLE_CLIENT_ID
      ├─ GOOGLE_CLIENT_SECRET
      └─ GOOGLE_SCOPES
```

**Microsoft Graph:**
```
MCP Server
  ├─ Uses: msal (Microsoft Authentication Library)
  ├─ Auth: OAuth2 flow with Azure AD
  ├─ Tokens: Stored in .msgraph-tokens.json
  ├─ Endpoints:
  │   ├─ GET /outlook/messages → Graph API /me/messages
  │   ├─ GET /teams/messages → Graph API /teams/{id}/channels/{id}/messages
  │   └─ GET /calendar/events → Graph API /me/calendar/events
  └─ Environment:
      ├─ MSFT_CLIENT_ID (or OUT_CLIENT_ID)
      ├─ MSFT_CLIENT_SECRET (optional)
      └─ MSFT_TENANT_ID
```

---

### **2. Aggregator ↔ MCP Server**

**Connection Method:** HTTP REST API

**Aggregator → MCP:**
```python
# In aggregator/fetchers.py
class MCPFetcher:
    def __init__(self, mcp_base_url="http://localhost:8000"):
        self.base_url = mcp_base_url
        self.session = requests.Session()
    
    def _get(self, endpoint, params):
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return response.json()

# Fetchers
GmailFetcher → GET {MCP}/gmail/messages
OutlookFetcher → GET {MCP}/outlook/messages
TeamsFetcher → GET {MCP}/teams/messages
CalendarFetcher → GET {MCP}/calendars/{id}/events
```

**Docker Configuration:**
```yaml
aggregator:
  environment:
    - MCP_SERVER_URL=http://mcp_server:8000  # Docker internal DNS
  depends_on:
    - mcp_server
  networks:
    - unify_network
```

**Data Flow:**
```
1. User calls Aggregator: GET /unified/inbox
2. Aggregator.aggregate_messages() calls:
   → UnifiedAggregator.fetch_all_messages()
3. UnifiedAggregator calls:
   → GmailFetcher.fetch_messages() → GET mcp_server:8000/gmail/messages
   → OutlookFetcher.fetch_messages() → GET mcp_server:8000/outlook/messages
   → TeamsFetcher.fetch_messages() → GET mcp_server:8000/teams/messages
4. Returns raw JSON data
5. Aggregator normalizes, merges, scores
6. Returns unified response
```

---

### **3. Aggregator ↔ LLM Service**

**Connection Method:** HTTP REST API

**Aggregator → LLM:**
```python
# In aggregator/llm_client/llm_service_client.py
class LLMServiceClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def summarize_batch(self, messages, mode, max_words):
        response = self.session.post(
            f"{self.base_url}/summarize-batch",
            json={"messages": messages, "mode": mode, "max_words": max_words}
        )
        return response.json()
```

**Docker Configuration:**
```yaml
aggregator:
  environment:
    - LLM_SERVICE_URL=http://llm_service:8002  # Docker internal DNS
  depends_on:
    - llm_service
```

**Data Flow:**
```
1. User calls: POST /unified/inbox/summarize
2. Aggregator:
   a. Fetches messages from MCP
   b. Normalizes messages
   c. Formats for LLM service
3. Aggregator → LLMServiceClient.summarize_batch()
4. LLM Service:
   a. Receives messages
   b. Calls OpenAI via LangChain
   c. Generates summary
   d. Optionally stores in Qdrant/Redis
5. Returns summary to Aggregator
6. Aggregator returns to user
```

---

### **4. LLM Service ↔ OpenAI**

**Connection Method:** HTTPS API (via LangChain)

**LLM → OpenAI:**
```python
# In llm_service/summarizer.py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
response = llm.invoke(messages)
```

**Environment:**
```yaml
llm_service:
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**API Calls:**
- Summarization → `gpt-3.5-turbo` model
- Action extraction → `gpt-3.5-turbo` model
- Embeddings → `text-embedding-3-small` model

---

### **5. LLM Service ↔ Qdrant**

**Connection Method:** HTTP REST API (via LangChain)

**LLM → Qdrant:**
```python
# In llm_service/memory/embeddings_manager.py
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

client = QdrantClient(url="http://localhost:6333")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Store embedding
vectorstore = Qdrant(client=client, embeddings=embeddings)
vectorstore.add_texts(texts=[text], metadatas=[metadata])

# Query similar
results = client.search(
    collection_name="unify_memory",
    query_vector=embeddings.embed_query(query),
    limit=top_k
)
```

**Environment:**
```python
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
```

**Purpose:**
- Store message/summary embeddings (1536-dimensional vectors)
- Semantic search for context retrieval
- Long-term memory for chatbot

**⚠️ NOTE:** Qdrant is **NOT in docker-compose.yml** - needs to be added!

---

### **6. LLM Service ↔ Redis**

**Connection Method:** Redis Protocol (via LangChain)

**LLM → Redis:**
```python
# In llm_service/memory/redis_memory.py
from langchain_community.chat_message_histories import RedisChatMessageHistory

history = RedisChatMessageHistory(
    session_id=session_id,
    url="redis://localhost:6379",
    ttl=3600 * 24  # 24 hours
)

# Store message
history.add_message(HumanMessage(content=text))

# Retrieve messages
messages = history.messages
```

**Environment:**
```python
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
```

**Purpose:**
- Store conversation history per session
- Short-term memory (24h TTL)
- Context for chatbot queries

**⚠️ NOTE:** Redis is **NOT in docker-compose.yml** - needs to be added!

---

## ✅ What's Working

### **Fully Implemented:**
1. ✅ MCP Server → Google APIs (Gmail, Calendar)
2. ✅ MCP Server → Microsoft Graph (Outlook, Teams)
3. ✅ Aggregator → MCP Server (HTTP REST)
4. ✅ Aggregator → LLM Service (HTTP REST)
5. ✅ LLM Service → OpenAI (via LangChain)
6. ✅ LLM Service → Qdrant (code ready)
7. ✅ LLM Service → Redis (code ready)
8. ✅ Docker networking between services

### **Data Flows:**
✅ User → Aggregator → MCP → External APIs  
✅ User → Aggregator → LLM Service → OpenAI  
✅ Aggregator fetches, normalizes, merges, scores  
✅ LLM Service summarizes and extracts actions  

---

## ⚠️ Missing Components

### **1. Qdrant Service** ❌
**Issue:** Not in docker-compose.yml

**Fix Needed:**
```yaml
# Add to docker-compose.yml
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    networks:
      - unify_network

volumes:
  qdrant_storage:
```

**Update LLM service:**
```yaml
llm_service:
  environment:
    - QDRANT_URL=http://qdrant:6333
  depends_on:
    - qdrant
```

---

### **2. Redis Service** ❌
**Issue:** Not in docker-compose.yml

**Fix Needed:**
```yaml
# Add to docker-compose.yml
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - unify_network
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

**Update LLM service:**
```yaml
llm_service:
  environment:
    - REDIS_URL=redis://redis:6379
  depends_on:
    - redis
```

---

## 🔧 Configuration Requirements

### **Environment Variables Needed:**

**MCP Server (.env):**
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_SCOPES=https://www.googleapis.com/auth/gmail.readonly,...

MSFT_CLIENT_ID=your_azure_client_id
MSFT_CLIENT_SECRET=your_azure_client_secret (optional)
MSFT_TENANT_ID=common
```

**Aggregator (.env):**
```env
MCP_SERVER_URL=http://mcp_server:8000
LLM_SERVICE_URL=http://llm_service:8002
```

**LLM Service (.env):**
```env
OPENAI_API_KEY=sk-...your_openai_key
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
```

---

## 🧪 Verification Checklist

### **Network Connectivity:**
- [x] Aggregator can reach MCP Server (unify_network)
- [x] Aggregator can reach LLM Service (unify_network)
- [ ] LLM Service can reach Qdrant (needs Qdrant service)
- [ ] LLM Service can reach Redis (needs Redis service)

### **API Endpoints:**
- [x] MCP Server exposes /gmail/messages
- [x] MCP Server exposes /outlook/messages
- [x] MCP Server exposes /teams/messages
- [x] Aggregator exposes /unified/inbox
- [x] Aggregator exposes /unified/inbox/summarize
- [x] Aggregator exposes /unified/inbox/extract-actions
- [x] LLM Service exposes /summarize-batch
- [x] LLM Service exposes /extract-actions

### **Dependencies:**
- [x] Aggregator depends_on mcp_server
- [x] Aggregator depends_on llm_service
- [ ] LLM Service depends_on qdrant (needs adding)
- [ ] LLM Service depends_on redis (needs adding)

---

## 📊 Complete Data Flow Example

### **Scenario: User requests AI summary**

```
1. CLIENT → Aggregator
   POST http://localhost:8001/unified/inbox/summarize
   Body: {"mode": "bullets"}

2. Aggregator checks LLM health
   GET http://llm_service:8002/health

3. Aggregator fetches priority messages
   Calls: AggregatorService.get_unified_inbox()
   
4. AggregatorService fetches from MCP
   a) GET http://mcp_server:8000/gmail/messages?maxResults=20
   b) GET http://mcp_server:8000/outlook/messages?max_results=20
   c) GET http://mcp_server:8000/teams/messages?max_results=20

5. MCP Server authenticates and calls External APIs
   a) Gmail API: users().messages().list()
   b) MS Graph: GET https://graph.microsoft.com/v1.0/me/messages
   c) MS Graph: GET https://graph.microsoft.com/v1.0/teams/.../messages

6. MCP Server returns raw JSON to Aggregator

7. Aggregator processes data
   a) Normalizes each message format
   b) Calculates importance scores
   c) Merges and deduplicates
   d) Sorts by timestamp

8. Aggregator calls LLM Service
   POST http://llm_service:8002/summarize-batch
   Body: {
     "messages": [...normalized messages...],
     "mode": "bullets",
     "max_words": 200
   }

9. LLM Service processes
   a) Receives messages
   b) Flattens to text
   c) Calls OpenAI via LangChain
      → POST https://api.openai.com/v1/chat/completions
   d) Generates summary
   e) Optionally stores in Qdrant/Redis

10. LLM Service returns summary
    {
      "summary": "...",
      "bullets": [...],
      "token_usage": {...}
    }

11. Aggregator formats response
    {
      "status": "success",
      "summary": "...",
      "bullets": [...],
      "message_count": 5
    }

12. CLIENT receives AI-powered summary
```

---

## 🎯 System Capabilities

### **What Your System Can Do:**

✅ **Data Aggregation:**
- Fetch emails from Gmail
- Fetch emails from Outlook
- Fetch messages from Teams
- Fetch calendar events from Google Calendar
- Normalize all to unified format
- Merge and deduplicate
- Score importance

✅ **AI Processing:**
- Summarize messages (3 modes)
- Extract action items
- Classify by priority
- Identify due dates
- Assign categories

✅ **Memory (when Qdrant/Redis added):**
- Store summaries for semantic search
- Track conversation history
- Retrieve context for queries

---

## 🚨 Critical Issues to Fix

### **Priority 1: Add Qdrant and Redis**
Currently, LLM service will fail when trying to use memory features.

**Impact:**
- `/store` endpoint will fail
- `/query` endpoint will fail
- `/context` endpoint will fail
- `/ingest` endpoint will fail
- Memory storage in summarize/extract-actions will fail

**Solution:** Add Qdrant and Redis to docker-compose.yml (see above)

### **Priority 2: Environment Variables**
Ensure all required env vars are set in `.env` file.

### **Priority 3: External API Credentials**
- Google OAuth credentials configured
- Microsoft Azure AD app configured
- OpenAI API key set

---

## ✅ Corrected Architecture Summary

Your architecture is **ALMOST CORRECT**! Here's the summary:

### **What's Perfect:**
✅ Service separation and responsibilities  
✅ Docker networking setup  
✅ HTTP REST communication between services  
✅ LLM integration with Aggregator  
✅ MCP integration with External APIs  
✅ Code structure and organization  

### **What Needs Fixing:**
❌ Add Qdrant service to docker-compose.yml  
❌ Add Redis service to docker-compose.yml  
❌ Update LLM service dependencies in docker-compose  

### **Once Fixed:**
🎉 All services will be fully connected  
🎉 Memory features will work  
🎉 Complete end-to-end flow functional  
🎉 Production-ready architecture  

---

## 📝 Next Steps

1. **Add Qdrant and Redis to docker-compose.yml**
2. **Update .env with all credentials**
3. **Run: `docker-compose up -d`**
4. **Test: `python test_integration.py`**
5. **Verify memory: `curl http://localhost:8002/memory/status`**

---

**Your architecture is solid! Just need to add the missing infrastructure services. 🚀**

