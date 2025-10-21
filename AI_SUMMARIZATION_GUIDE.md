# AI Inbox Summarization Guide 🤖

## Overview

Get AI-powered summaries of your inbox organized by source (Gmail, Outlook, Teams). Each source gets its own dedicated summary showing you what's important in each communication channel.

---

## 🚀 Quick Start

### Simple Request

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=20&mode=executive"
```

This will:
1. Fetch 20 messages from Gmail, Outlook, and Teams
2. Generate AI summaries for each source using GPT-4o mini
3. Return organized summaries with message details

---

## 📋 Endpoint Details

### POST `/unified/inbox/summarize-by-source`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_per_source` | int | 20 | Messages to fetch per source (1-100) |
| `mode` | string | "executive" | Summary mode: executive, bullets, paragraph |
| `max_words` | int | 200 | Maximum words per summary (50-500) |

**Response Structure:**

```json
{
  "status": "success",
  "summaries_by_source": {
    "gmail": {
      "summary": "AI-generated summary of Gmail messages...",
      "bullets": ["Key point 1", "Key point 2", ...],
      "message_count": 20,
      "messages": [
        {
          "id": "msg_123",
          "subject": "Project Update",
          "sender": "John Doe",
          "timestamp": "2024-01-15T10:30:00Z",
          "importance_score": 0.85,
          "is_read": false,
          "body_preview": "Quick update on..."
        }
      ],
      "status": "success"
    },
    "outlook": { ... },
    "teams": { ... }
  },
  "total_messages": 60,
  "mode": "executive",
  "max_words": 200,
  "timestamp": "2024-01-15T12:00:00Z",
  "sources": {
    "gmail": 20,
    "outlook": 20,
    "teams": 20
  }
}
```

---

## 🎯 Summary Modes

### 1. Executive Mode (Recommended)
**Best for:** Quick overview, busy professionals

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=executive"
```

**Output:**
```
Gmail (15 messages): 
Mostly project updates from the team. Key items include Q4 planning 
meetings, design review requests, and deadline notifications. Priority 
items: design approval needed by Friday, budget review pending.
```

### 2. Bullets Mode
**Best for:** Scannable lists, action-oriented summaries

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=bullets"
```

**Output:**
```
Gmail (15 messages):
• 3 project update emails from Sarah
• 2 design review requests (deadline: Friday)
• Budget review needed this week
• Team meeting scheduled for Monday
• 4 notifications from GitHub
```

### 3. Paragraph Mode
**Best for:** Detailed understanding, context

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=paragraph"
```

**Output:**
```
Gmail (15 messages):
Your Gmail inbox contains primarily work-related communications from 
the past 24 hours. The main themes are project updates and scheduling. 
Sarah has sent multiple updates on the Q4 project, highlighting progress 
on design work and upcoming deliverables. There are two urgent design 
review requests that require attention before Friday's deadline...
```

---

## 💡 Use Cases

### 1. Morning Briefing

Get a quick overview of what happened overnight:

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=50&mode=executive"
```

**Best for:**
- Starting your day
- Catching up after time off
- Quick inbox triage

### 2. Per-Source Deep Dive

Focus on one communication channel:

```bash
# Just check Teams messages
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=30&mode=bullets"
```

Then look at the `summaries_by_source.teams` section.

**Best for:**
- Team chat catch-up
- Channel-specific updates
- Focused review

### 3. Priority Detection

Get detailed summaries to find important items:

```bash
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=100&mode=paragraph&max_words=300"
```

**Best for:**
- Finding urgent items
- Understanding context
- Decision making

---

## 📊 Example Responses

### Example 1: Balanced Inbox

```json
{
  "status": "success",
  "summaries_by_source": {
    "gmail": {
      "summary": "15 work emails including 3 urgent project updates, 2 meeting invites, and various notifications. Key action: approve design by Friday.",
      "bullets": [
        "Project deadline reminder from Sarah",
        "Design review requested",
        "Budget approval needed",
        "Team meeting scheduled Monday"
      ],
      "message_count": 15,
      "status": "success"
    },
    "outlook": {
      "summary": "8 corporate emails focusing on quarterly planning and compliance training. No urgent actions required.",
      "bullets": [
        "Q4 planning kickoff invitation",
        "Compliance training reminder",
        "HR policy update"
      ],
      "message_count": 8,
      "status": "success"
    },
    "teams": {
      "summary": "22 team chat messages across 3 channels. Active discussion on feature launch, some questions for you.",
      "bullets": [
        "Feature launch discussion ongoing",
        "2 questions awaiting your response",
        "Design team seeking feedback"
      ],
      "message_count": 22,
      "status": "success"
    }
  },
  "total_messages": 45
}
```

### Example 2: Heavy Gmail Day

```json
{
  "status": "success",
  "summaries_by_source": {
    "gmail": {
      "summary": "Very active day with 50+ emails. Multiple threads on project launch, client feedback, and internal updates. 5 urgent items requiring immediate attention.",
      "message_count": 50,
      "status": "success"
    },
    "outlook": {
      "summary": "No Outlook messages available",
      "message_count": 0,
      "status": "success"
    },
    "teams": {
      "summary": "Light Teams activity with 3 status updates and general announcements.",
      "message_count": 3,
      "status": "success"
    }
  },
  "total_messages": 53
}
```

---

## 🎨 Integration Examples

### Python

```python
import requests

def get_inbox_summary(max_per_source=20, mode="executive"):
    """Get AI summary of inbox by source"""
    url = "http://localhost:8001/unified/inbox/summarize-by-source"
    params = {
        "max_per_source": max_per_source,
        "mode": mode,
        "max_words": 200
    }
    
    response = requests.post(url, params=params)
    return response.json()

# Usage
summary = get_inbox_summary()

for source, data in summary['summaries_by_source'].items():
    print(f"\n{source.upper()}:")
    print(f"Messages: {data['message_count']}")
    print(f"Summary: {data['summary']}")
```

### JavaScript

```javascript
async function getInboxSummary(maxPerSource = 20, mode = 'executive') {
  const url = new URL('http://localhost:8001/unified/inbox/summarize-by-source');
  url.searchParams.append('max_per_source', maxPerSource);
  url.searchParams.append('mode', mode);
  
  const response = await fetch(url, { method: 'POST' });
  return await response.json();
}

// Usage
const summary = await getInboxSummary();
console.log('Gmail:', summary.summaries_by_source.gmail.summary);
```

### cURL with jq (Formatted Output)

```bash
curl -s -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=20" | \
  jq -r '.summaries_by_source | to_entries[] | "\n\(.key | ascii_upcase):\nMessages: \(.value.message_count)\nSummary: \(.value.summary)\n"'
```

---

## ⚡ Performance

### Expected Response Times

| Messages per Source | Typical Time | Max Time |
|---------------------|--------------|----------|
| 10 | 5-10 seconds | 15 seconds |
| 20 (default) | 10-15 seconds | 25 seconds |
| 50 | 15-25 seconds | 40 seconds |
| 100 | 25-40 seconds | 60 seconds |

**Factors affecting speed:**
- Number of messages
- Message length
- OpenAI API response time
- Network latency
- Message source availability

### Optimization Tips

1. **Use appropriate limits**: Don't fetch more than needed
   ```bash
   # Quick check (faster)
   max_per_source=10
   
   # Detailed review (slower but comprehensive)
   max_per_source=50
   ```

2. **Cache results**: Store summaries to avoid re-processing
   ```python
   # Cache for 5 minutes
   cached_summary = cache.get('inbox_summary')
   if not cached_summary:
       cached_summary = get_inbox_summary()
       cache.set('inbox_summary', cached_summary, ttl=300)
   ```

3. **Async requests**: Don't block UI while waiting
   ```javascript
   // Show loading state
   setLoading(true);
   const summary = await getInboxSummary();
   setLoading(false);
   ```

---

## 💰 Cost Estimation

### OpenAI API Costs (GPT-4o mini)

**Pricing:** $0.15 per 1M input tokens, $0.60 per 1M output tokens

**Typical request (20 messages per source):**
- Input: ~15,000 tokens
- Output: ~600 tokens
- Cost: **~$0.0027 per request**

**Daily usage examples:**

| Frequency | Daily Cost | Monthly Cost |
|-----------|------------|--------------|
| 1x/day | $0.0027 | $0.08 |
| 3x/day | $0.0081 | $0.24 |
| 10x/day | $0.027 | $0.81 |
| 50x/day | $0.135 | $4.05 |

**Very affordable!** Even heavy users spend less than $5/month.

---

## 🔧 Configuration

### Environment Variables

Required in `.env`:

```env
# OpenAI API Key (required)
OPENAI_API_KEY='sk-proj-your-key-here'

# Optional: LLM Service URL (if not default)
LLM_SERVICE_URL='http://localhost:8002'
```

### Service Dependencies

Make sure these services are running:

1. **Aggregator** (port 8001)
   ```bash
   cd aggregator && python app.py
   ```

2. **LLM Service** (port 8002)
   ```bash
   cd llm_service && python app.py
   ```

3. **MCP Server** (port 8000)
   ```bash
   cd mcp_server && python app.py
   ```

---

## 🧪 Testing

### Run Test Script

```bash
python test_ai_summarization.py
```

This will:
1. Check all services are running
2. Fetch and summarize 20 messages per source
3. Display detailed results
4. Verify the feature is working

### Manual Testing

```bash
# Test with 10 messages (fast)
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?max_per_source=10&mode=executive"

# Test with bullets mode
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=bullets"

# Test with detailed paragraph
curl -X POST "http://localhost:8001/unified/inbox/summarize-by-source?mode=paragraph&max_words=300"
```

---

## 🆘 Troubleshooting

### Error: "LLM service is not available"

**Cause:** LLM service not running or OpenAI API key missing

**Solution:**
```bash
# Check LLM service
curl http://localhost:8002/health

# If not running, start it
cd llm_service && python app.py

# Verify API key in .env
cat .env | grep OPENAI_API_KEY
```

### Error: "No messages found"

**Cause:** Not authenticated with Gmail/Outlook/Teams

**Solution:**
1. Authenticate with Google: `http://localhost:8000/google/auth`
2. Authenticate with Microsoft: `http://localhost:8000/msgraph/auth`

### Slow Response Times

**Cause:** Large number of messages or slow OpenAI API

**Solutions:**
- Reduce `max_per_source` parameter
- Use shorter `max_words` for summaries
- Check your internet connection
- Verify OpenAI API status

### Empty Summaries

**Cause:** No messages in the time range

**Solution:**
- Increase `max_per_source` to fetch more messages
- Check if messages exist in your accounts
- Verify authentication tokens are valid

---

## 📈 Advanced Features

### Custom Prompts

Modify the system prompt in `llm_service/prompts/summarize_prompt.txt`:

```txt
You are an expert email assistant. Summarize emails clearly and concisely.

Focus on:
- Key action items and deadlines
- Important decisions or requests
- Urgent communications
- Meeting invitations
- Notable updates

Keep summaries under {max_length} words.
```

### Priority Filtering

Combine with importance scoring:

```python
def get_priority_summary(min_importance=0.7):
    """Get summary of high-priority messages only"""
    # First get all messages
    all_messages = aggregator.aggregate_messages(max_per_source=50)
    
    # Filter by importance
    priority_messages = [
        msg for msg in all_messages['normalized']
        if msg.get('importance_score', 0) >= min_importance
    ]
    
    # Summarize filtered messages
    return llm_client.summarize_batch(priority_messages)
```

---

## ✨ Best Practices

### 1. Choose the Right Mode
- **Executive**: Daily briefings, quick checks
- **Bullets**: Action lists, task identification
- **Paragraph**: Deep dives, complex situations

### 2. Optimize Frequency
- **Morning check**: 20-50 messages for overnight activity
- **Midday update**: 10-20 messages for recent items
- **End of day**: 30-100 messages for full review

### 3. Message Limits
- **Quick scan**: 10 messages per source
- **Standard review**: 20 messages (default, recommended)
- **Deep dive**: 50-100 messages

### 4. Combine with Actions
```python
# Get summary
summary = get_inbox_summary()

# Find mentioned actions
actions = extract_actions_from_messages(
    message_ids=get_important_message_ids(summary)
)

# Prioritize your work based on AI insights
```

---

## 🎉 Summary

**What it does:**
- ✅ Fetches messages from Gmail, Outlook, Teams
- ✅ Generates AI summaries per source using GPT-4o mini
- ✅ Shows message details with importance scoring
- ✅ Provides 3 summary modes (executive, bullets, paragraph)
- ✅ Fast and cost-effective (~$0.003 per request)

**When to use:**
- 📅 Daily inbox reviews
- ⏰ After being away
- 🎯 Priority identification
- 🔍 Channel-specific catch-up
- 📊 Understanding trends

**Ready to try?**
```bash
python test_ai_summarization.py
```

---

**Documentation:** `AI_SUMMARIZATION_GUIDE.md`  
**Test Script:** `test_ai_summarization.py`  
**Endpoint:** `POST /unified/inbox/summarize-by-source`  
**Status:** ✅ Ready to use!

