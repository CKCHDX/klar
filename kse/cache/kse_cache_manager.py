"""
kse_cache_manager.py - Cache Management Orchestration

Main cache orchestration layer coordinating cache operations,
policy enforcement, and lifecycle management.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional, Type
from datetime import datetime, timedelta

from kse.core import (
    get_logger,
    KSEException,
)

logger = get_logger('cache')


class KSECacheException(KSEException):
    """Base cache exception"""
    pass


class CacheManager:
    """
    Main cache management orchestration layer.
    
    Coordinates cache operations, policy enforcement,
    eviction strategies, and statistics collection.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        policy: str = 'lru',
        ttl_seconds: Optional[int] = 3600,
    ):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cache entries (default: 1000)
            policy: Eviction policy - 'lru' or 'lfu' (default: 'lru')
            ttl_seconds: Time-to-live in seconds (None for no expiry)
        """
        if max_size <= 0:
            raise KSECacheException(f"max_size must be positive, got {max_size}")
        
        if policy not in ('lru', 'lfu'):
            raise KSECacheException(f"policy must be 'lru' or 'lfu', got {policy}")
        
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise KSECacheException(f"ttl_seconds must be positive, got {ttl_seconds}")
        
        self.max_size = max_size
        self.policy = policy
        self.ttl_seconds = ttl_seconds
        
        # Cache storage: key -> (value, metadata)
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'created_at': datetime.now().isoformat(),
        }
        
        logger.debug(
            f"CacheManager initialized: max_size={max_size}, "
            f"policy={policy}, ttl={ttl_seconds}s"
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        self._cleanup_expired()
        
        if key not in self._cache:
            self._stats['misses'] += 1
            logger.debug(f"Cache miss for key: {key}")
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if self.ttl_seconds and entry['expires_at']:
            if datetime.fromisoformat(entry['expires_at']) < datetime.now():
                self._stats['expirations'] += 1
                del self._cache[key]
                logger.debug(f"Cache entry expired: {key}")
                return None
        
        # Update metadata for LRU/LFU
        entry['last_accessed'] = datetime.now().isoformat()
        entry['access_count'] += 1
        
        self._stats['hits'] += 1
        logger.debug(f"Cache hit for key: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cleanup_expired()
        
        # Evict if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_one()
        
        # Calculate expiration
        expires_at = None
        if self.ttl_seconds:
            expires_at = (datetime.now() + timedelta(seconds=self.ttl_seconds)).isoformat()
        
        # Store entry
        self._cache[key] = {
            'value': value,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 0,
            'expires_at': expires_at,
        }
        
        logger.debug(f"Cache set for key: {key}")
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache entry deleted: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared ({count} entries removed)")
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists and not expired
        """
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        
        # Check expiration
        if self.ttl_seconds and entry['expires_at']:
            if datetime.fromisoformat(entry['expires_at']) < datetime.now():
                del self._cache[key]
                return False
        
        return True
    
    def _evict_one(self) -> None:
        """Evict one entry based on policy."""
        if not self._cache:
            return
        
        if self.policy == 'lru':
            # Evict least recently used
            key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]['last_accessed']
            )
        else:  # lfu
            # Evict least frequently used
            key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]['access_count']
            )
        
        del self._cache[key]
        self._stats['evictions'] += 1
        logger.debug(f"Cache eviction ({self.policy}): {key}")
    
    def _cleanup_expired(self) -> None:
        """Remove all expired entries."""
        if not self.ttl_seconds:
            return
        
        expired_keys = []
        for key, entry in self._cache.items():
            if entry['expires_at']:
                if datetime.fromisoformat(entry['expires_at']) < datetime.now():
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self._stats['expirations'] += 1
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        self._cleanup_expired()
        
        hit_rate = 0.0
        total_requests = self._stats['hits'] + self._stats['misses']
        if total_requests > 0:
            hit_rate = (self._stats['hits'] / total_requests) * 100
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'policy': self.policy,
            'ttl_seconds': self.ttl_seconds,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': hit_rate,
            'evictions': self._stats['evictions'],
            'expirations': self._stats['expirations'],
            'created_at': self._stats['created_at'],
        }
    
    def get_size(self) -> int:
        """
        Get current cache size.
        
        Returns:
            Number of entries in cache
        """
        self._cleanup_expired()
        return len(self._cache)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get cache information.
        
        Returns:
            Dictionary with cache info
        """
        return {
            'max_size': self.max_size,
            'current_size': self.get_size(),
            'policy': self.policy,
            'ttl_seconds': self.ttl_seconds,
            'stats': self.get_stats(),
        }


__all__ = ["CacheManager", "KSECacheException"]
