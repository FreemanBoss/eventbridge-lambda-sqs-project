"""
Idempotent processing to ensure same event processed multiple times = same outcome.
Uses simple in-memory cache for demo; production uses DynamoDB.
"""

import time
from typing import Optional
from datetime import datetime, timedelta

class IdempotencyCache:
    """
    Simple in-memory cache for idempotent processing.
    In production, replace with DynamoDB with TTL.

    Key: eventId
    Value: (datetime_processed, result)
    """
    
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def has_processed(self, event_id: str) -> bool:
        """Check if event has already been processed."""
        if event_id not in self.cache:
            return False

        timestamp, _ = self.cache[event_id]
        if datetime.utcnow() - timestamp > self.ttl:
            # Entry expired, clean it up
            del self.cache[event_id]
            return False

        return True
    
    def mark_processed(self, event_id: str, result: dict):
        """Mark event as processed and store result."""
        self.cache[event_id] = (datetime.utcnow(), result)
    
    def get_result(self, event_id: str) -> Optional[dict]:
        """Retrieve cached result for event."""
        if event_id in self.cache:
            _, result = self.cache[event_id]
            return result
        return None
    
    def cleanup_expired(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        expired = [
            event_id for event_id, (ts, _) in self.cache.items()
            if now - ts > self.ttl
        ]
        for event_id in expired:
            del self.cache[event_id]

# Global cache instance (reused across Lambda invocations within same container)
_idempotency_cache = IdempotencyCache()

def is_duplicate(event_id: str) -> bool:
    """Check if event has been processed before."""
    return _idempotency_cache.has_processed(event_id)

def mark_as_processed(event_id: str, result: dict):
    """Mark event as processed."""
    _idempotency_cache.mark_processed(event_id, result)

def get_cached_result(event_id: str) -> Optional[dict]:
    """Get cached result for duplicate event."""
    return _idempotency_cache.get_result(event_id)
