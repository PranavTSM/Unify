"""
Simple in-memory cache for aggregator service
Prevents repeated API calls to MCP server
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)


class SimpleCache:
    """Thread-safe in-memory cache with TTL"""
    
    def __init__(self, default_ttl_seconds: int = 30):
        """
        Initialize cache.
        
        Args:
            default_ttl_seconds: Default time-to-live for cache entries
        """
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        logger.info(f"Cache initialized with TTL={default_ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/not found
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            expires_at = entry.get('expires_at')
            
            # Check if expired
            if datetime.now() > expires_at:
                logger.debug(f"Cache expired for key: {key}")
                del self._cache[key]
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return entry.get('value')
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional custom TTL (uses default if not provided)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            logger.debug(f"Cache set for key: {key}, TTL={ttl}s")
    
    def clear(self, key: Optional[str] = None):
        """
        Clear cache entry or entire cache.
        
        Args:
            key: Optional specific key to clear (clears all if None)
        """
        with self._lock:
            if key:
                if key in self._cache:
                    del self._cache[key]
                    logger.debug(f"Cleared cache for key: {key}")
            else:
                self._cache.clear()
                logger.info("Cleared entire cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_entries = len(self._cache)
            expired = sum(
                1 for entry in self._cache.values()
                if datetime.now() > entry.get('expires_at', datetime.min)
            )
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired,
                'expired_entries': expired,
                'default_ttl_seconds': self.default_ttl
            }


# Global cache instance
_cache = SimpleCache(default_ttl_seconds=30)


def get_cache() -> SimpleCache:
    """Get the global cache instance."""
    return _cache

