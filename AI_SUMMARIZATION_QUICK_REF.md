# AI Summarization Quick Reference 🚀

## 🎯 One-Liner

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=20&mode=executive"
```

---

## 📝 Summary Modes

| Mode | Best For | Example Output |
|------|----------|----------------|
| **executive** | Quick overview | "15 messages: 3 urgent project updates, 2 meetings, deadline Friday" |
| **bullets** | Action lists | "• Project update\n• Design review\n• Budget approval" |
| **paragraph** | Detailed context | "Your inbox contains work communications focusing on..." |

---

## ⚡ Common Commands

### Quick Morning Check (10 messages)
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=10&mode=executive"
```

### Standard Review (20 messages - default)
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source"
```

### Deep Dive (50 messages)
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=50&mode=paragraph"
```

### Bullet Points
```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=bullets"
```

---

## 📊 Response Structure

```json
{
  "summaries_by_source": {
    "gmail": {
      "summary": "AI summary...",
      "bullets": ["point 1", "point 2"],
      "message_count": 20,
      "messages": [...]
    },
    "outlook": {...},
    "teams": {...}
  },
  "total_messages": 60,
  "sources": {
    "gmail": 20,
    "outlook": 20,
    "teams": 20
  }
}
```

---

## 🧪 Testing

### Python Test
```bash
python test_ai_summarization.py
```

### Windows Batch
```bash
test_ai_summarization.bat
```

### Quick Health Check
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

---

## 💰 Cost

**Per Request:** ~$0.003 (less than half a cent!)

**Daily Usage:**
- 1x/day = $0.08/month
- 10x/day = $0.81/month  
- 50x/day = $4.05/month

---

## ⏱️ Performance

| Messages | Time |
|----------|------|
| 10 | 5-10 sec |
| 20 | 10-15 sec |
| 50 | 15-25 sec |
| 100 | 25-40 sec |

---

## 🔧 Setup

### Required Services
1. **Aggregator** - Port 8001
2. **LLM Service** - Port 8002  
3. **MCP Server** - Port 8000

### Required Config (.env)
```env
OPENAI_API_KEY='sk-proj-...'
```

---

## 🆘 Troubleshooting

| Error | Fix |
|-------|-----|
| "LLM service not available" | Start LLM service: `cd llm_service && python app.py` |
| "No messages found" | Authenticate: http://localhost:8000/google/auth |
| Slow response | Reduce `max_per_source` parameter |
| Empty summaries | Check authentication and message availability |

---

## 📚 Documentation

- **Full Guide**: [AI_SUMMARIZATION_GUIDE.md](AI_SUMMARIZATION_GUIDE.md)
- **Test Script**: [test_ai_summarization.py](test_ai_summarization.py)
- **Main README**: [README.md](README.md)

---

## ✨ Quick Example

```python
import requests

response = requests.post(
    "http://localhost:8001/unified/inbox/summarize-by-source",
    params={"max_per_source": 20, "mode": "executive"}
)

data = response.json()

for source, info in data['summaries_by_source'].items():
    print(f"\n{source.upper()}: {info['message_count']} messages")
    print(f"Summary: {info['summary']}")
```

---

**Status**: ✅ Ready to use!  
**Endpoint**: `POST /unified/inbox/summarize-by-source`  
**Model**: GPT-4o mini (fast & cheap)

