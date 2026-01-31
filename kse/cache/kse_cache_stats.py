"""
Cache Statistics - Cache statistics and monitoring
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CacheStats:
    """Cache statistics collector"""
    
    def __init__(self):
        """Initialize cache statistics"""
        self.total_hits = 0
        self.total_misses = 0
        self.total_evictions = 0
        logger.info("CacheStats initialized")
    
    def record_hit(self) -> None:
        """Record a cache hit"""
        self.total_hits += 1
    
    def record_miss(self) -> None:
        """Record a cache miss"""
        self.total_misses += 1
    
    def record_eviction(self) -> None:
        """Record a cache eviction"""
        self.total_evictions += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary of statistics
        """
        total_requests = self.total_hits + self.total_misses
        hit_rate = (self.total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_hits': self.total_hits,
            'total_misses': self.total_misses,
            'total_evictions': self.total_evictions,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2)
        }
    
    def reset(self) -> None:
        """Reset all statistics"""
        self.total_hits = 0
        self.total_misses = 0
        self.total_evictions = 0
        logger.info("Cache statistics reset")
