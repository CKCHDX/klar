"""
kse/cache/__init__.py - Cache Layer Public API

Exposes the complete cache layer interface for other modules.

Components:
  - CacheManager: Main orchestration layer
  - MemoryCache: In-memory cache implementation
  - CachePolicy: Eviction strategies (LRU, LFU, Adaptive)
  - CacheStatistics: Performance monitoring

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_cache_manager import CacheManager, KSECacheException
from .kse_memory_cache import MemoryCache
from .kse_cache_policy import (
    CachePolicy,
    EvictionPolicy,
    LRUPolicy,
    LFUPolicy,
    AdaptivePolicy,
    get_policy,
)
from .kse_cache_stats import CacheStatistics, CachePerformanceMonitor

__all__ = [
    # Main classes
    "CacheManager",
    "MemoryCache",
    "CachePolicy",
    "CacheStatistics",
    "CachePerformanceMonitor",
    
    # Policies
    "EvictionPolicy",
    "LRUPolicy",
    "LFUPolicy",
    "AdaptivePolicy",
    "get_policy",
    
    # Exceptions
    "KSECacheException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Cache Layer

1. Basic cache manager:
    from kse.cache import CacheManager
    
    cache = CacheManager(max_size=1000, policy='lru', ttl_seconds=3600)
    cache.set('key', 'value')
    value = cache.get('key')
    stats = cache.get_stats()

2. Simple memory cache:
    from kse.cache import MemoryCache
    
    cache = MemoryCache(ttl_seconds=3600)
    cache.put('search_results', results)
    cached_results = cache.get('search_results')

3. With specific policy:
    from kse.cache import get_policy
    
    policy = get_policy('lfu')
    victim = policy.select_victim(cache_entries)

4. Monitor performance:
    from kse.cache import CacheStatistics
    
    stats = CacheStatistics()
    stats.record_hit()
    stats.record_miss()
    report = stats.get_summary()
    print(stats.get_detailed_report())

5. Advanced - Get or compute:
    from kse.cache import MemoryCache
    
    cache = MemoryCache()
    
    def compute_expensive():
        # Expensive operation
        return expensive_result
    
    result = cache.get_or_compute(
        'expensive_key',
        compute_expensive,
        ttl_seconds=7200
    )

ARCHITECTURE:

kse/cache/
├── kse_cache_manager.py      Main orchestration + TTL support
├── kse_memory_cache.py       In-memory storage + expiration
├── kse_cache_policy.py       Eviction strategies (LRU/LFU/Adaptive)
├── kse_cache_stats.py        Statistics & monitoring
└── __init__.py               Public API exports

INTEGRATION POINTS:

- Phase 1 (core): Uses config, logging, exceptions
- Phase 4 (crawler): Uses cache for URL dedup
- Phase 8 (search): Uses cache for result caching
- Phase 9 (server): Uses cache for API responses

CACHE STRATEGIES:

LRU (Least Recently Used):
  - Evicts entries accessed longest ago
  - Good for temporal locality patterns
  - Use when: Access patterns are time-based

LFU (Least Frequently Used):
  - Evicts entries accessed least often
  - Good for frequency-based patterns
  - Use when: Some entries are more valuable

Adaptive:
  - Switches between LRU/LFU dynamically
  - Detects access pattern
  - Use when: Pattern is unknown

STATISTICS:

Hit Rate:      % of cache hits vs total requests
Miss Rate:     % of cache misses vs total requests
Eviction Rate: % of evictions per operation
Expiration:    Count of TTL-expired entries

PERFORMANCE:

Typical hit rates:
  Search results:    70-85% (users repeat searches)
  URL cache:         60-80% (many duplicate URLs)
  Query cache:       80-95% (common queries)

MONITORING:

- Track hit/miss rates over time
- Detect performance degradation
- Monitor memory usage trends
- Analyze eviction patterns

CONFIGURATION:

Max Size:      Number of entries before eviction
Policy:        LRU, LFU, or Adaptive
TTL:           Time-to-live for entries (seconds)
Cleanup:       Automatic expiration cleanup
Statistics:    Built-in performance tracking
"""

# Convenient global instances
_global_cache = None
_global_stats = None


def get_global_cache(
    max_size: int = 1000,
    policy: str = 'lru',
    ttl_seconds: int = 3600,
) -> CacheManager:
    """
    Get or create global cache instance.
    
    Args:
        max_size: Maximum cache entries
        policy: Eviction policy
        ttl_seconds: TTL for entries
        
    Returns:
        Global CacheManager instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager(max_size, policy, ttl_seconds)
    return _global_cache


def get_global_stats() -> CacheStatistics:
    """
    Get or create global statistics instance.
    
    Returns:
        Global CacheStatistics instance
    """
    global _global_stats
    if _global_stats is None:
        _global_stats = CacheStatistics()
    return _global_stats
