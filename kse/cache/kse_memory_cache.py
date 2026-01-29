"""
Memory Cache - In-memory cache implementation
Thread-safe LRU cache with TTL support
"""

import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
import sys

logger = logging.getLogger(__name__)


class MemoryCache:
    """In-memory cache with LRU eviction and TTL"""
    
    def __init__(self, name: str = "default", max_size_mb: int = 50, max_items: int = 10000):
        """
        Initialize memory cache
        
        Args:
            name: Cache name for logging
            max_size_mb: Maximum size in megabytes
            max_items: Maximum number of items
        """
        self.name = name
        self.max_size_mb = max_size_mb
        self.max_items = max_items
        
        self._cache = OrderedDict()
        self._metadata = {}  # Stores TTL and timestamp
        self._lock = threading.Lock()
        
        self.hits = 0
        self.misses = 0
        
        logger.info(f"MemoryCache '{name}' initialized (max_size={max_size_mb}MB, max_items={max_items})")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            # Check if expired
            metadata = self._metadata.get(key)
            if metadata and self._is_expired(metadata):
                del self._cache[key]
                del self._metadata[key]
                self.misses += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            self.hits += 1
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        with self._lock:
            # Remove if exists (to update)
            if key in self._cache:
                del self._cache[key]
            
            # Add new entry
            self._cache[key] = value
            self._metadata[key] = {
                'timestamp': datetime.now(),
                'ttl': ttl,
                'size': sys.getsizeof(value)
            }
            
            # Check size limits and evict if necessary
            self._evict_if_needed()
    
    def _is_expired(self, metadata: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        timestamp = metadata['timestamp']
        ttl = metadata['ttl']
        expiry = timestamp + timedelta(seconds=ttl)
        return datetime.now() > expiry
    
    def _evict_if_needed(self) -> None:
        """Evict entries if cache is over limits"""
        # Check item count limit
        while len(self._cache) > self.max_items:
            # Remove oldest (first item in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            del self._metadata[oldest_key]
            logger.debug(f"Evicted '{oldest_key}' from {self.name} cache (item limit)")
        
        # Check size limit
        current_size_mb = self.get_size_mb()
        while current_size_mb > self.max_size_mb and len(self._cache) > 0:
            # Remove oldest
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            del self._metadata[oldest_key]
            current_size_mb = self.get_size_mb()
            logger.debug(f"Evicted '{oldest_key}' from {self.name} cache (size limit)")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._metadata.clear()
            self.hits = 0
            self.misses = 0
            logger.info(f"Cleared {self.name} cache")
    
    def cleanup_expired(self) -> None:
        """Remove all expired entries"""
        with self._lock:
            expired_keys = [
                key for key, metadata in self._metadata.items()
                if self._is_expired(metadata)
            ]
            
            for key in expired_keys:
                del self._cache[key]
                del self._metadata[key]
            
            if expired_keys:
                logger.info(f"Removed {len(expired_keys)} expired entries from {self.name} cache")
    
    def get_size_mb(self) -> float:
        """Get current cache size in megabytes"""
        total_bytes = sum(
            metadata.get('size', 0)
            for metadata in self._metadata.values()
        )
        return total_bytes / (1024 * 1024)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'name': self.name,
                'items': len(self._cache),
                'size_mb': round(self.get_size_mb(), 2),
                'max_size_mb': self.max_size_mb,
                'max_items': self.max_items,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': round(hit_rate, 2)
            }
