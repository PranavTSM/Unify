# 🚀 Quick Start Guide - AI-Powered Endpoints

## ⚡ TL;DR

Two new AI endpoints are now available:
- **POST `/unified/inbox/summarize`** - Summarize messages
- **POST `/unified/inbox/extract-actions`** - Extract action items

---

## 🎯 Quick Examples

### 1. Summarize Today's Priority Messages
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "bullets",
    "max_words": 200
  }'
```

**Result**: Bullet-point summary of your top priority messages

---

### 2. Extract High-Priority Actions
```bash
curl -X POST "http://localhost:8001/unified/inbox/extract-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "min_priority": "high"
  }'
```

**Result**: List of urgent action items with due dates

---

### 3. Analyze Specific Email Thread
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "message_ids": ["msg_abc123", "msg_def456"],
    "mode": "executive",
    "include_messages": true
  }'
```

**Result**: Executive summary of specific messages

---

## 📋 Common Use Cases

| Scenario | Endpoint | Parameters |
|----------|----------|------------|
| Morning briefing | `/summarize` | `mode: "executive"` |
| Daily task list | `/extract-actions` | `min_priority: "medium"` |
| Project summary | `/summarize` | `message_ids: [...]` |
| Urgent tasks only | `/extract-actions` | `min_priority: "high"` |

---

## 🎨 Response Examples

### Summarization
```json
{
  "summary": "5 priority messages: Project deadline extended by 2 days, new design mockups ready for review, budget approval needed by EOD...",
  "bullets": [
    "Project deadline extended by 2 days",
    "New design mockups ready for review",
    "Budget approval needed by EOD"
  ],
  "message_count": 5
}
```

### Action Extraction
```json
{
  "actions": [
    {
      "description": "Review Q4 budget proposal",
      "due_date": "2025-10-15T17:00:00Z",
      "priority": "high",
      "category": "task"
    }
  ],
  "summary": {
    "total_actions": 1,
    "by_priority": {"high": 1, "medium": 0, "low": 0}
  }
}
```

---

## 🔧 Configuration

Set these environment variables:

```env
LLM_SERVICE_URL=http://localhost:8002
OPENAI_API_KEY=your_api_key_here
```

---

## 🧪 Test It

```bash
# 1. Check health
curl http://localhost:8001/health

# 2. Try summarization
curl -X POST http://localhost:8001/unified/inbox/summarize \
  -H "Content-Type: application/json" \
  -d '{"mode": "bullets"}'

# 3. Try action extraction
curl -X POST http://localhost:8001/unified/inbox/extract-actions \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 📚 Full Documentation

See `API_INTEGRATION_GUIDE.md` for complete reference.

---

## 🆘 Need Help?

**LLM service not responding?**
```bash
docker-compose logs llm_service
```

**No messages found?**
```bash
curl http://localhost:8001/unified/inbox
```

**Check OpenAPI docs:**
- Aggregator: http://localhost:8001/docs
- LLM Service: http://localhost:8002/docs

---

**Ready to go! 🎉**

