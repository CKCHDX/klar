"""
kse_memory_cache.py - In-Memory Cache Implementation

Provides a simple in-memory cache with TTL support,
entry metadata tracking, and basic statistics.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta

from kse.core import get_logger

logger = get_logger('cache')


class MemoryCache:
    """
    Simple in-memory cache implementation.
    
    Provides:
    - TTL (Time-To-Live) support
    - Entry metadata tracking
    - Statistics collection
    - Expiration checking
    """
    
    def __init__(self, ttl_seconds: Optional[int] = 3600):
        """
        Initialize memory cache.
        
        Args:
            ttl_seconds: Default TTL for all entries (None for no expiry)
        """
        self.default_ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        logger.debug(f"MemoryCache initialized with TTL={ttl_seconds}s")
    
    def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Store value in cache with optional TTL override.
        
        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Optional TTL override (None uses default)
        """
        # Use provided TTL or default
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        
        # Calculate expiration
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        self._cache[key] = {
            'value': value,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'accessed_at': datetime.now().isoformat(),
            'access_count': 0,
        }
        
        logger.debug(f"MemoryCache: stored key '{key}' (TTL={ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            logger.debug(f"MemoryCache: cache miss for key '{key}'")
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if entry['expires_at']:
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() > expires_at:
                del self._cache[key]
                logger.debug(f"MemoryCache: key '{key}' expired")
                return None
        
        # Update access metadata
        entry['accessed_at'] = datetime.now().isoformat()
        entry['access_count'] += 1
        
        logger.debug(f"MemoryCache: cache hit for key '{key}'")
        return entry['value']
    
    def get_or_compute(
        self,
        key: str,
        compute_fn,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """
        Get from cache or compute and store.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if missing
            ttl_seconds: Optional TTL
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = compute_fn()
        self.put(key, value, ttl_seconds)
        
        logger.debug(f"MemoryCache: computed and cached key '{key}'")
        return value
    
    def delete(self, key: str) -> bool:
        """
        Remove value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"MemoryCache: deleted key '{key}'")
            return True
        logger.debug(f"MemoryCache: key '{key}' not found for deletion")
        return False
    
    def contains(self, key: str) -> bool:
        """
        Check if key exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists and valid
        """
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        
        # Check expiration
        if entry['expires_at']:
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() > expires_at:
                del self._cache[key]
                return False
        
        return True
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"MemoryCache: cleared {count} entries")
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries cleaned up
        """
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry['expires_at']:
                expires_at = datetime.fromisoformat(entry['expires_at'])
                if datetime.now() > expires_at:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"MemoryCache: cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_size(self) -> int:
        """
        Get current cache size.
        
        Returns:
            Number of entries in cache
        """
        self.cleanup_expired()
        return len(self._cache)
    
    def get_entries(self) -> List[str]:
        """
        Get all cache keys.
        
        Returns:
            List of cache keys
        """
        self.cleanup_expired()
        return list(self._cache.keys())
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Entry metadata or None if not found
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if entry['expires_at']:
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() > expires_at:
                del self._cache[key]
                return None
        
        # Return metadata without value
        return {
            'key': key,
            'created_at': entry['created_at'],
            'expires_at': entry['expires_at'],
            'accessed_at': entry['accessed_at'],
            'access_count': entry['access_count'],
            'size': len(str(entry['value'])),
        }
    
    def get_all_info(self) -> Dict[str, Any]:
        """
        Get information about all cache entries.
        
        Returns:
            Dictionary with all entries info
        """
        self.cleanup_expired()
        
        entries_info = []
        total_size = 0
        
        for key in self._cache.keys():
            info = self.get_entry_info(key)
            if info:
                entries_info.append(info)
                total_size += info['size']
        
        return {
            'entry_count': len(entries_info),
            'total_size_bytes': total_size,
            'entries': entries_info,
        }


__all__ = ["MemoryCache"]
