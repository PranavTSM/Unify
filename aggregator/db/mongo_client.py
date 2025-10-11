"""
MongoDB Client Configuration
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB connection
_mongo_client: Optional[AsyncIOMotorClient] = None
_sync_client: Optional[MongoClient] = None
_database = None

# Get MongoDB URI from environment (after loading .env)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "unify_aggregator")

def init_mongo():
    """Initialize MongoDB connection."""
    global _mongo_client, _sync_client, _database
    
    try:
        # Async client for async operations
        _mongo_client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=10,
            minPoolSize=2,
            serverSelectionTimeoutMS=5000
        )
        
        # Sync client for synchronous operations
        _sync_client = MongoClient(
            MONGO_URI,
            maxPoolSize=10,
            minPoolSize=2,
            serverSelectionTimeoutMS=5000
        )
        
        _database = _mongo_client[DATABASE_NAME]
        
        logger.info(f"✅ MongoDB connected: {DATABASE_NAME}")
        
        # Create indexes
        _create_indexes()
        
        return _database
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.warning("⚠️  Continuing without MongoDB (caching disabled)")
        return None

def _create_indexes():
    """Create database indexes for performance."""
    try:
        db = _sync_client[DATABASE_NAME]
        
        # Messages indexes
        messages = db.messages
        messages.create_index("id", unique=True)
        messages.create_index("source")
        messages.create_index("timestamp")
        messages.create_index([("timestamp", -1)])  # Descending for recent first
        messages.create_index("sender.email")
        messages.create_index("is_read")
        messages.create_index("importance_score")
        
        # Events indexes
        events = db.events
        events.create_index("id", unique=True)
        events.create_index("source")
        events.create_index("start")
        events.create_index([("start", 1)])  # Ascending for upcoming events
        
        # Fetch logs indexes
        fetch_logs = db.fetch_logs
        fetch_logs.create_index([("fetched_at", -1)])
        fetch_logs.create_index("source")
        
        logger.info("✅ MongoDB indexes created")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_db():
    """Get MongoDB database instance."""
    return _database

def get_sync_db():
    """Get synchronous MongoDB database instance."""
    if _sync_client:
        return _sync_client[DATABASE_NAME]
    return None

async def close_mongo():
    """Close MongoDB connection."""
    global _mongo_client, _sync_client
    
    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB async client closed")
    
    if _sync_client:
        _sync_client.close()
        logger.info("MongoDB sync client closed")

# Health check
def mongo_health_check() -> bool:
    """Check if MongoDB is connected and healthy."""
    try:
        if _sync_client:
            _sync_client.admin.command('ping')
            return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
    return False

