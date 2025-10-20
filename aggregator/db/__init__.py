"""
MongoDB Database Integration
"""

from .mongo_client import get_db, init_mongo, close_mongo
from .models import Message, Event, FetchLog

__all__ = ['get_db', 'init_mongo', 'close_mongo', 'Message', 'Event', 'FetchLog']

