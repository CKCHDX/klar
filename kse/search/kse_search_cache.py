"""
Search Result Caching

Caches search results for performance optimization.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime, timedelta
import hashlib

from kse.search.kse_search_executor import ResultSet
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


@dataclass
class CacheEntry:
    """Cache entry for search results."""
    query_hash: str
    query_string: str
    result_set: ResultSet
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    hit_count: int = 0
    ttl_seconds: int = 3600  # 1 hour default
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def update_access(self) -> None:
        """Update access timestamp and hit count."""
        self.accessed_at = datetime.now()
        self.hit_count += 1


class SearchCache:
    """
    Search result cache.
    
    Features:
    - In-memory result caching
    - TTL-based expiration
    - Hit/miss tracking
    - Cache statistics
    - Automatic cleanup
    """
    
    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl_seconds: int = 3600,
    ):
        """
        Initialize cache.
        
        Args:
            max_entries: Maximum cache entries
            default_ttl_seconds: Default time-to-live
        """
        self.max_entries = max_entries
        self.default_ttl = default_ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'puts': 0,
            'evictions': 0,
        }
    
    def get(self, query_string: str) -> Optional[ResultSet]:
        """
        Get cached result for query.
        
        Args:
            query_string: Search query
        
        Returns:
            Cached ResultSet or None
        """
        query_hash = self._hash_query(query_string)
        
        if query_hash not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[query_hash]
        
        # Check expiration
        if entry.is_expired:
            logger.debug(f"Cache entry expired: {query_string}")
            del self.cache[query_hash]
            self.stats['misses'] += 1
            return None
        
        # Update access
        entry.update_access()
        self.stats['hits'] += 1
        
        logger.debug(f"Cache hit: {query_string} (hits: {entry.hit_count})")
        
        return entry.result_set
    
    def put(
        self,
        query_string: str,
        result_set: ResultSet,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Cache search result.
        
        Args:
            query_string: Search query
            result_set: ResultSet to cache
            ttl_seconds: Time-to-live (uses default if None)
        """
        query_hash = self._hash_query(query_string)
        ttl = ttl_seconds or self.default_ttl
        
        # Check if at capacity
        if len(self.cache) >= self.max_entries:
            self._evict_oldest()
        
        entry = CacheEntry(
            query_hash=query_hash,
            query_string=query_string,
            result_set=result_set,
            ttl_seconds=ttl,
        )
        
        self.cache[query_hash] = entry
        self.stats['puts'] += 1
        
        logger.debug(f"Cached query: {query_string}")
    
    def clear(self, query_string: Optional[str] = None) -> None:
        """
        Clear cache entry or entire cache.
        
        Args:
            query_string: Specific query to clear (None = clear all)
        """
        if query_string:
            query_hash = self._hash_query(query_string)
            if query_hash in self.cache:
                del self.cache[query_hash]
                logger.debug(f"Cleared cache entry: {query_string}")
        else:
            self.cache.clear()
            logger.info("Cleared entire cache")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_hashes = [
            h for h, e in self.cache.items()
            if e.is_expired
        ]
        
        for h in expired_hashes:
            del self.cache[h]
        
        if expired_hashes:
            logger.debug(f"Cleaned up {len(expired_hashes)} expired entries")
        
        return len(expired_hashes)
    
    def _evict_oldest(self) -> None:
        """
        Evict oldest cache entry."""
        if not self.cache:
            return
        
        # Find oldest by access time
        oldest_hash = min(
            self.cache.keys(),
            key=lambda h: self.cache[h].accessed_at
        )
        
        del self.cache[oldest_hash]
        self.stats['evictions'] += 1
        
        logger.debug(f"Evicted cache entry (evictions: {self.stats['evictions']})")
    
    def _hash_query(self, query_string: str) -> str:
        """
        Generate hash for query string.
        
        Args:
            query_string: Query to hash
        
        Returns:
            Query hash
        """
        # Normalize query (lowercase, strip)
        normalized = query_string.lower().strip()
        
        # Generate hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_statistics(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (
            self.stats['hits'] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            'entries': len(self.cache),
            'max_entries': self.max_entries,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate_percent': hit_rate,
            'puts': self.stats['puts'],
            'evictions': self.stats['evictions'],
            'total_requests': total_requests,
        }
    
    def get_top_queries(self, limit: int = 10) -> list:
        """
        Get most frequently cached queries.
        
        Args:
            limit: Number of top queries
        
        Returns:
            List of (query, hit_count) tuples
        """
        sorted_entries = sorted(
            self.cache.values(),
            key=lambda e: e.hit_count,
            reverse=True
        )
        
        return [
            (e.query_string, e.hit_count)
            for e in sorted_entries[:limit]
        ]
