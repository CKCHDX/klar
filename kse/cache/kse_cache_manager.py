"""
Cache Manager - Cache orchestration for KSE
Manages in-memory caching for search results and processed queries
"""

import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """Main cache orchestration layer"""
    
    def __init__(self, max_size_mb: int = 100, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.max_size_mb = max_size_mb
        self.default_ttl = default_ttl
        self.caches = {}
        
        # Initialize specialized caches
        from kse.cache.kse_memory_cache import MemoryCache
        from kse.cache.kse_cache_policy import CachePolicy
        
        self.search_cache = MemoryCache(name="search", max_size_mb=max_size_mb // 2)
        self.query_cache = MemoryCache(name="query", max_size_mb=max_size_mb // 4)
        self.result_cache = MemoryCache(name="result", max_size_mb=max_size_mb // 4)
        
        self.policy = CachePolicy()
        
        logger.info(f"CacheManager initialized (max_size={max_size_mb}MB, ttl={default_ttl}s)")
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            cache_name: Name of cache ('search', 'query', 'result')
            key: Cache key
        
        Returns:
            Cached value or None
        """
        cache = self._get_cache(cache_name)
        if cache:
            value = cache.get(key)
            if value is not None:
                logger.debug(f"Cache HIT: {cache_name}/{key}")
                return value
            logger.debug(f"Cache MISS: {cache_name}/{key}")
        return None
    
    def set(
        self,
        cache_name: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache
        
        Args:
            cache_name: Name of cache
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        cache = self._get_cache(cache_name)
        if cache:
            ttl = ttl or self.default_ttl
            cache.set(key, value, ttl)
            logger.debug(f"Cache SET: {cache_name}/{key} (ttl={ttl}s)")
    
    def _get_cache(self, cache_name: str):
        """Get cache instance by name"""
        if cache_name == 'search':
            return self.search_cache
        elif cache_name == 'query':
            return self.query_cache
        elif cache_name == 'result':
            return self.result_cache
        return None
    
    def clear(self, cache_name: Optional[str] = None) -> None:
        """
        Clear cache(s)
        
        Args:
            cache_name: Specific cache to clear (clears all if None)
        """
        if cache_name:
            cache = self._get_cache(cache_name)
            if cache:
                cache.clear()
                logger.info(f"Cleared cache: {cache_name}")
        else:
            self.search_cache.clear()
            self.query_cache.clear()
            self.result_cache.clear()
            logger.info("Cleared all caches")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        from kse.cache.kse_cache_stats import CacheStats
        stats = CacheStats()
        
        return {
            'search_cache': self.search_cache.get_stats(),
            'query_cache': self.query_cache.get_stats(),
            'result_cache': self.result_cache.get_stats(),
            'total_size_mb': (
                self.search_cache.get_size_mb() +
                self.query_cache.get_size_mb() +
                self.result_cache.get_size_mb()
            )
        }
    
    def cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        self.search_cache.cleanup_expired()
        self.query_cache.cleanup_expired()
        self.result_cache.cleanup_expired()
        logger.info("Cleaned up expired cache entries")
