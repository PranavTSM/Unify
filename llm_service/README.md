# LLM Service (LangChain + Qdrant + Redis)

A lightweight microservice that provides:
- Summarization via LangChain ChatOpenAI
- Long‑term semantic memory via Qdrant (vector store)
- Short‑term conversation memory via Redis (LangChain RedisChatMessageHistory)
- Unified context retrieval combining semantic search + recent chat

Neo4j and knowledge graph have been removed.

## Table of Contents
- Overview
- Architecture
- File Structure
- Setup
- Running
- API
- Environment Variables
- Troubleshooting

## Overview
The service accepts text, summarizes it, stores the summary as an embedding in Qdrant for semantic retrieval, and optionally logs the message into a Redis‑backed chat history for session context. You can then query similar items and get a hybrid context for a chatbot.

## Architecture
- API Layer (FastAPI): `app.py`
- Business Logic:
  - Summarization: `summarizer.py` (LangChain ChatOpenAI)
  - Action extraction: `action_extractor.py` (optional)
  - Orchestration: `memory/retriever.py`
- Data Layer:
  - Embeddings + Vector store: `memory/embeddings_manager.py` (LangChain OpenAIEmbeddings + Qdrant)
  - Chat history: `memory/redis_memory.py` (LangChain RedisChatMessageHistory)

## File Structure
```
llm_service/
├─ app.py                 # FastAPI app and routes
├─ summarizer.py          # LangChain summarization
├─ action_extractor.py    # (optional) action extraction via LangChain
├─ prompts/
│  ├─ summarize_prompt.txt
│  └─ extract_actions_prompt.txt
└─ memory/
   ├─ embeddings_manager.py  # Qdrant integration (vectors)
   ├─ redis_memory.py        # Redis chat history (LangChain)
   └─ retriever.py           # Hybrid context orchestration
```

## Setup
1) Python env
```bash
cd llm_service/..
python -m venv venv
source venv/bin/activate
pip install -r llm_service/requirements.txt
```

2) Services
- Qdrant: `docker-compose up -d qdrant` (or Podman)
- Redis: `docker-compose up -d redis`

3) Environment
Create `.env` in repo root (same level as `llm_service/`):
```
OPENAI_API_KEY=sk-...
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
```

## Running
```bash
./venv/bin/python -m uvicorn llm_service.app:app --host 0.0.0.0 --port 8002
```

Health check:
```bash
curl http://localhost:8002/health
```

## API
- POST `/store`
  - Stores summarized text in Qdrant and (optionally) appends to Redis session.
  - Body:
    ```json
    {
      "id": "msg_001",
      "text": "Full text...",
      "metadata": {"source": "gmail"},
      "session_id": "u1",
      "sender": "alice@org.com",
      "role": "user"
    }
    ```
  - Response: `{ "status": "success", "id": "...", "stored_in": ["qdrant", "redis"] }`

- POST `/query`
  - Semantic search in Qdrant.
  - Body: `{ "query": "product roadmap", "top_k": 5 }`

- GET `/context`
  - Hybrid context from Qdrant + Redis.
  - Query params: `?query=...&session_id=...&top_k=5`

- GET `/memory/status`
  - Returns Qdrant and Redis connectivity + counts.

- DELETE `/memory/session/{session_id}`
  - Clears conversation history for a session.

## Environment Variables
- `OPENAI_API_KEY`: OpenAI key for LangChain (ChatOpenAI + OpenAIEmbeddings)
- `QDRANT_URL`: Qdrant endpoint (e.g., `http://localhost:6333`)
- `REDIS_URL`: Redis endpoint (e.g., `redis://localhost:6379`)

## Troubleshooting
- Free a busy port:
  ```bash
  lsof -ti:8002 | xargs kill -9
  ```
- Verify services:
  ```bash
  curl http://localhost:6333/readyz   # Qdrant
  redis-cli ping                      # Redis
  curl http://localhost:8002/health   # LLM service
  ```
- Qdrant UUID error: we convert string IDs to UUID internally before upsert.
- Empty search results: ensure embeddings are stored (check `/memory/status` vectors_count) and your query is non-empty.
