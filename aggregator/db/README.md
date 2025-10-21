# MongoDB Database Layer 💾

This directory contains the MongoDB integration for persistent storage of messages and events.

## 📁 Structure

```
aggregator/db/
├── __init__.py           # Package exports
├── mongo_client.py       # MongoDB connection management
├── models.py            # Data models (Message, Event, FetchLog)
└── repository.py        # Data access layer (CRUD operations)
```

## 🔧 Components

### 1. mongo_client.py
MongoDB connection manager with both async and sync clients.

**Functions:**
- `init_mongo()` - Initialize MongoDB connections
- `get_db()` - Get async database instance
- `get_sync_db()` - Get sync database instance
- `close_mongo()` - Close connections
- `mongo_health_check()` - Check if MongoDB is healthy

**Configuration:**
```python
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "unify_aggregator")
```

### 2. models.py
Pydantic data models for type safety.

**Models:**
- `Message` - Email/chat message structure
- `Event` - Calendar event structure  
- `FetchLog` - API fetch operation log

### 3. repository.py
Data access layer with three repository classes.

#### MessageRepository
**Methods:**
- `save_messages(messages)` - Bulk upsert messages
- `get_messages(page, page_size, filters)` - Paginated query with filtering
- `get_message_by_id(message_id)` - Get single message
- `delete_old_messages(days_old)` - Clean up old data
- `get_statistics()` - Get message statistics

**Features:**
- ✅ Bulk upsert (no duplicates)
- ✅ Pagination support
- ✅ Filtering by source, read status, importance
- ✅ Full-text search in subject/body/sender
- ✅ Automatic timestamps (created_at, updated_at)

#### EventRepository
**Methods:**
- `save_events(events)` - Bulk upsert events
- `get_events(page, page_size, filters)` - Paginated query

**Features:**
- ✅ Calendar event storage
- ✅ Date-based filtering
- ✅ Source filtering

#### FetchLogRepository
**Methods:**
- `log_fetch(source, type, count, success, duration)` - Log API operations

**Features:**
- ✅ Track API fetch operations
- ✅ Monitor performance and errors

## 🚀 Usage

### Setup

1. **Start MongoDB:**
```bash
# Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas (cloud)
```

2. **Configure environment:**
```env
MONGO_URI='mongodb://localhost:27017'
MONGO_DB_NAME='unify_aggregator'
```

3. **Initialize in application:**
```python
from db.mongo_client import init_mongo
from db.repository import MessageRepository, EventRepository

# Initialize MongoDB (call this FIRST)
init_mongo()

# Then create repositories
message_repo = MessageRepository()
event_repo = EventRepository()
```

⚠️ **IMPORTANT**: Always call `init_mongo()` BEFORE creating repository instances!

### Saving Data

```python
# Save messages
messages = [
    {
        "id": "msg_123",
        "source": "gmail",
        "subject": "Hello",
        "sender": {"email": "user@example.com", "name": "User"},
        "timestamp": "2024-01-01T12:00:00Z",
        "is_read": False,
        "importance_score": 0.75
    }
]

saved_count = message_repo.save_messages(messages)
print(f"Saved {saved_count} messages")
```

### Querying Data

```python
# Paginated query with filters
result = message_repo.get_messages(
    page=1,
    page_size=20,
    source="gmail",              # Filter by source
    is_read=False,               # Only unread
    min_score=0.7,               # Importance >= 0.7
    search_query="urgent"        # Text search
)

messages = result["messages"]
total_count = result["total_count"]
total_pages = result["total_pages"]
```

### Get Single Message

```python
message = message_repo.get_message_by_id("msg_123")
if message:
    print(f"Subject: {message['subject']}")
```

### Statistics

```python
stats = message_repo.get_statistics()
print(f"Total messages: {stats['total_messages']}")
print(f"By source: {stats['by_source']}")
print(f"Unread: {stats['unread_count']}")
```

## 📊 Database Schema

### Collections

#### messages
```javascript
{
  _id: ObjectId("..."),           // MongoDB ID
  id: "msg_123",                  // Unique message ID (indexed)
  source: "gmail",                // Source: gmail, outlook, teams
  subject: "Hello",               // Message subject
  body: "Message content...",     // Full body
  body_preview: "Preview...",     // Short preview
  sender: {
    email: "user@example.com",
    name: "User"
  },
  timestamp: ISODate("..."),      // Message timestamp (indexed)
  is_read: false,                 // Read status (indexed)
  importance_score: 0.75,         // 0.0-1.0 (indexed)
  created_at: ISODate("..."),     // When saved to DB
  updated_at: ISODate("...")      // Last updated
}
```

#### events
```javascript
{
  _id: ObjectId("..."),
  id: "event_123",                // Unique event ID (indexed)
  source: "google_calendar",      // Source
  title: "Meeting",               // Event title
  description: "...",             // Event description
  start: ISODate("..."),          // Start time (indexed)
  end: ISODate("..."),            // End time
  location: "Room 101",           // Location
  attendees: [...],               // List of attendees
  created_at: ISODate("..."),
  updated_at: ISODate("...")
}
```

#### fetch_logs
```javascript
{
  _id: ObjectId("..."),
  source: "gmail",                // Data source
  fetch_type: "messages",         // Type of fetch
  count: 50,                      // Items fetched
  success: true,                  // Success status
  error_message: null,            // Error if failed
  duration_seconds: 2.5,          // Operation duration
  fetched_at: ISODate("...")      // Timestamp (indexed)
}
```

### Indexes

The following indexes are automatically created for performance:

**messages:**
- `id` (unique)
- `source`
- `timestamp` (descending)
- `sender.email`
- `is_read`
- `importance_score`

**events:**
- `id` (unique)
- `source`
- `start` (ascending)

**fetch_logs:**
- `fetched_at` (descending)
- `source`

## 🔄 Upsert Behavior

Both repositories use **upsert** operations (update or insert):
- If a document with the same `id` exists → **update** it
- If no document with that `id` exists → **insert** new one
- This prevents duplicate messages/events

```python
# These will not create duplicates:
message_repo.save_messages([{"id": "msg_123", ...}])  # Insert
message_repo.save_messages([{"id": "msg_123", ...}])  # Update (same ID)
```

## 🏥 Health Check

```python
from db.mongo_client import mongo_health_check

if mongo_health_check():
    print("✅ MongoDB is healthy")
else:
    print("❌ MongoDB is not available")
```

## 🧹 Cleanup

```python
# Delete messages older than 30 days
deleted = message_repo.delete_old_messages(days_old=30)
print(f"Deleted {deleted} old messages")
```

## 🐛 Troubleshooting

### Issue: "MongoDB not available" warnings
**Solution:** Make sure MongoDB is running and `init_mongo()` is called before creating repositories.

### Issue: No data being saved
**Solution:** Check initialization order. See `MONGODB_INITIALIZATION_FIX.md` for details.

### Issue: Connection errors
**Solution:** Verify `MONGO_URI` in `.env` and ensure MongoDB is accessible.

### Issue: Slow queries
**Solution:** Indexes are automatically created. Check query patterns and consider adding custom indexes.

## 📈 Performance Tips

1. **Use pagination** instead of loading all data at once
2. **Add indexes** for frequently queried fields
3. **Use filtering** to reduce result sets
4. **Batch operations** when possible (use `save_messages` for bulk)
5. **Monitor** using fetch_logs to track performance

## 🔒 Security

- Use authentication in production: `mongodb://user:pass@host:27017`
- Enable SSL/TLS for connections: `mongodb://host:27017/?ssl=true`
- Use MongoDB Atlas for managed security
- Never commit credentials to version control

## 📚 References

- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Motor (Async) Documentation](https://motor.readthedocs.io/)
- [MongoDB Query Operators](https://docs.mongodb.com/manual/reference/operator/query/)
- [MongoDB Indexes](https://docs.mongodb.com/manual/indexes/)

## ✅ Testing

Run the test suite to verify MongoDB integration:

```bash
# Quick test
python test_mongodb_fix.py

# Or use batch file
test_mongodb.bat
```

## 🎯 Summary

This MongoDB layer provides:
- ✅ **Persistent storage** for messages and events
- ✅ **Fast queries** with indexing and pagination
- ✅ **Flexible filtering** by multiple criteria
- ✅ **Full-text search** across message content
- ✅ **Duplicate prevention** via upsert operations
- ✅ **Performance tracking** via fetch logs
- ✅ **Clean API** with repository pattern

All data is automatically saved and can be queried efficiently even with large datasets!

