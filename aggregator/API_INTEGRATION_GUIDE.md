# Aggregator Service - LLM Integration Guide

## 🚀 New AI-Powered Endpoints

The aggregator service now integrates with the LLM service to provide AI-powered summarization and action extraction.

---

## 📋 Available Endpoints

### 1. **POST /unified/inbox/summarize**

Generate AI-powered summaries of your messages.

#### Request Body

```json
{
  "message_ids": ["msg_123", "msg_456"],  // Optional: specific message IDs
  "mode": "executive",                     // 'executive', 'bullets', 'paragraph'
  "max_words": 200,                        // Maximum words in summary
  "include_messages": false,               // Include message details in response
  "store_in_memory": false,                // Store in LLM service memory
  "session_id": "user_session_123"         // Optional: for memory storage
}
```

#### Response

```json
{
  "status": "success",
  "summary": "Summary of the 5 priority messages: Team meeting scheduled for tomorrow...",
  "bullets": [
    "Team meeting scheduled for tomorrow at 2 PM",
    "Project deadline extended by 2 days",
    "New design mockups ready for review"
  ],
  "message_count": 5,
  "mode": "executive",
  "timestamp": "2025-10-11T10:30:00.123456"
}
```

#### Usage Examples

**Summarize Priority Messages (Auto-fetch)**
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "bullets",
    "max_words": 150
  }'
```

**Summarize Specific Messages**
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "message_ids": ["18c3f4e5a2b8d1f9", "18c3f4e5a2b8d200"],
    "mode": "executive",
    "include_messages": true
  }'
```

**Store Summary in Memory**
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "paragraph",
    "store_in_memory": true,
    "session_id": "user_john_session"
  }'
```

---

### 2. **POST /unified/inbox/extract-actions**

Extract actionable items from messages using AI.

#### Request Body

```json
{
  "message_ids": ["msg_123", "msg_456"],  // Optional: specific message IDs
  "context": "Project Alpha launch",      // Additional context for extraction
  "priority_mode": "hybrid",              // 'heuristic', 'llm', 'hybrid'
  "include_messages": false,              // Include message details in response
  "min_priority": "medium"                // Filter: 'low', 'medium', 'high'
}
```

#### Response

```json
{
  "status": "success",
  "actions": [
    {
      "description": "Review and approve the Q4 budget proposal",
      "due_date": "2025-10-15T17:00:00Z",
      "assignee": "John Doe",
      "category": "task",
      "priority": "high",
      "priority_score": 0.85,
      "source_id": "msg_123"
    },
    {
      "description": "Schedule meeting with design team",
      "due_date": null,
      "assignee": null,
      "category": "meeting",
      "priority": "medium",
      "priority_score": 0.6,
      "source_id": "msg_456"
    }
  ],
  "message_count": 10,
  "summary": {
    "total_actions": 2,
    "by_priority": {
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "by_category": {
      "task": 1,
      "meeting": 1
    },
    "priority_mode": "hybrid"
  },
  "timestamp": "2025-10-11T10:30:00.123456"
}
```

#### Usage Examples

**Extract Actions from Unread Messages (Auto-fetch)**
```bash
curl -X POST "http://localhost:8001/unified/inbox/extract-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "priority_mode": "hybrid",
    "min_priority": "medium"
  }'
```

**Extract Actions from Specific Messages**
```bash
curl -X POST "http://localhost:8001/unified/inbox/extract-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "message_ids": ["18c3f4e5a2b8d1f9", "18c3f4e5a2b8d200"],
    "context": "Project Alpha launch preparation",
    "include_messages": true
  }'
```

**High Priority Actions Only**
```bash
curl -X POST "http://localhost:8001/unified/inbox/extract-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "min_priority": "high",
    "priority_mode": "llm"
  }'
```

---

## 🔄 Complete Workflow Example

Here's a complete workflow using all services:

### Step 1: Get Unified Inbox
```bash
curl "http://localhost:8001/unified/inbox?max_per_source=20"
```

Response includes `priority_messages` with IDs.

### Step 2: Summarize Priority Messages
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "bullets",
    "max_words": 200,
    "store_in_memory": true,
    "session_id": "workflow_session_1"
  }'
```

### Step 3: Extract Actions from Unread
```bash
curl -X POST "http://localhost:8001/unified/inbox/extract-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "priority_mode": "hybrid",
    "min_priority": "medium"
  }'
```

### Step 4: Query Context from Memory
```bash
curl "http://localhost:8002/context?query=What%20are%20my%20urgent%20tasks&session_id=workflow_session_1&top_k=5"
```

---

## 🏗️ Architecture Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────┐
│     AGGREGATOR (Port 8001)              │
│  ┌────────────────────────────────────┐ │
│  │ 1. Get unified inbox data          │ │
│  │ 2. Filter/fetch specific messages  │ │
│  │ 3. Call LLM service via client     │ │
│  │ 4. Return processed results        │ │
│  └────────────────────────────────────┘ │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│     LLM SERVICE (Port 8002)             │
│  ┌────────────────────────────────────┐ │
│  │ 1. Receive messages/text           │ │
│  │ 2. Call OpenAI via LangChain       │ │
│  │ 3. Generate summaries/extract      │ │
│  │ 4. Store in Qdrant/Redis           │ │
│  │ 5. Return results                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

**Aggregator (.env)**
```env
MCP_SERVER_URL=http://localhost:8000
LLM_SERVICE_URL=http://localhost:8002
```

**LLM Service (.env)**
```env
OPENAI_API_KEY=your_openai_key_here
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
```

**Docker Compose**
```yaml
aggregator:
  environment:
    - LLM_SERVICE_URL=http://llm_service:8002
  depends_on:
    - llm_service
```

---

## 🧪 Testing

### Check Service Health
```bash
# Check aggregator and its dependencies
curl http://localhost:8001/health

# Response:
{
  "status": "ok",
  "service": "aggregator",
  "dependencies": {
    "mcp_server": "http://localhost:8000",
    "llm_service": {
      "url": "http://localhost:8002",
      "healthy": true
    }
  }
}
```

### Test LLM Service Directly
```bash
# Check LLM service
curl http://localhost:8002/health

# Check memory status
curl http://localhost:8002/memory/status
```

---

## 🚨 Error Handling

### LLM Service Unavailable
```json
{
  "detail": "LLM service is not available"
}
```

**Solution**: Ensure LLM service is running and accessible.

### No Messages Found
```json
{
  "status": "success",
  "summary": "No priority messages to summarize",
  "message_count": 0,
  "bullets": []
}
```

### Message IDs Not Found
```json
{
  "detail": "No messages found with provided IDs"
}
```

---

## 📊 Response Modes

### Summarization Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `executive` | Concise overview in 2-3 sentences | Quick briefings |
| `bullets` | Bullet-point list | Action items, key points |
| `paragraph` | Detailed paragraph | Full context |

### Priority Modes (Action Extraction)

| Mode | Description | Accuracy |
|------|-------------|----------|
| `heuristic` | Fast, keyword-based | Good, instant |
| `llm` | AI-powered analysis | Best, slower |
| `hybrid` | Combines both approaches | Great, balanced |

---

## 🎯 Best Practices

1. **Use Auto-fetch for Daily Summaries**
   - Don't specify `message_ids` to get recent priority messages

2. **Store Important Summaries in Memory**
   - Set `store_in_memory: true` with a `session_id`
   - Later query using `/context` endpoint

3. **Filter Actions by Priority**
   - Use `min_priority: "high"` for urgent tasks only

4. **Batch Processing**
   - Process up to 20 messages at once for best performance

5. **Context is Key**
   - Add `context` when extracting actions for better accuracy

---

## 🔐 Security Notes

- Ensure `OPENAI_API_KEY` is properly secured
- Use environment variables, not hardcoded values
- Consider rate limiting for production deployments
- LLM service should not be directly exposed to internet

---

## 📈 Performance Tips

- **Caching**: LLM service stores embeddings in Qdrant for semantic search
- **Session Management**: Use session IDs to maintain conversation context
- **Timeout Handling**: Requests timeout after 60s by default
- **Parallel Processing**: Services can scale independently

---

## 🐛 Troubleshooting

### Issue: Timeout errors
**Solution**: Reduce number of messages or increase timeout in `llm_service_client.py`

### Issue: Out of memory
**Solution**: Reduce `max_per_source` parameter

### Issue: Poor quality summaries
**Solution**: 
- Ensure messages have good content (not just "FYI" or links)
- Try different `mode` options
- Increase `max_words` for more context

---

## 📚 Additional Resources

- **OpenAPI Docs**: http://localhost:8001/docs
- **LLM Service Docs**: http://localhost:8002/docs
- **Architecture**: See main README.md
- **Prompts**: `llm_service/prompts/` for customization

---

## 🚀 Quick Start

```bash
# 1. Start all services
docker-compose up -d

# 2. Check health
curl http://localhost:8001/health

# 3. Get unified inbox
curl http://localhost:8001/unified/inbox | jq

# 4. Summarize priority messages
curl -X POST http://localhost:8001/unified/inbox/summarize \
  -H "Content-Type: application/json" \
  -d '{"mode": "bullets"}' | jq

# 5. Extract actions
curl -X POST http://localhost:8001/unified/inbox/extract-actions \
  -H "Content-Type: application/json" \
  -d '{"min_priority": "medium"}' | jq
```

🎉 **You're all set!** Your unified inbox now has AI superpowers!

