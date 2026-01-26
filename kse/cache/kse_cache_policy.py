"""
kse_cache_policy.py - Cache Eviction Policies

Implements various cache eviction strategies:
- LRU (Least Recently Used)
- LFU (Least Frequently Used)

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from enum import Enum

from kse.core import get_logger

logger = get_logger('cache')


class EvictionPolicy(Enum):
    """Available eviction policies"""
    LRU = 'lru'      # Least Recently Used
    LFU = 'lfu'      # Least Frequently Used


class CachePolicy:
    """
    Cache eviction policy handler.
    
    Implements LRU and LFU strategies for cache eviction
    when maximum capacity is reached.
    """
    
    def __init__(self, policy: str = 'lru'):
        """
        Initialize cache policy.
        
        Args:
            policy: 'lru' (Least Recently Used) or 'lfu' (Least Frequently Used)
        """
        if policy.lower() not in [p.value for p in EvictionPolicy]:
            raise ValueError(f"Unknown policy: {policy}")
        
        self.policy = policy.lower()
        logger.debug(f"CachePolicy initialized: {self.policy.upper()}")
    
    def select_victim(self, entries: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Select entry to evict based on policy.
        
        Args:
            entries: Cache entries dict mapping key -> entry_data
            
        Returns:
            Key of entry to evict, or None if empty
        """
        if not entries:
            return None
        
        if self.policy == 'lru':
            return self._select_lru(entries)
        else:  # lfu
            return self._select_lfu(entries)
    
    def _select_lru(self, entries: Dict[str, Dict[str, Any]]) -> str:
        """
        Select least recently used entry.
        
        Args:
            entries: Cache entries
            
        Returns:
            Key of LRU entry
        """
        victim = min(
            entries.keys(),
            key=lambda k: datetime.fromisoformat(
                entries[k].get('accessed_at', entries[k]['created_at'])
            )
        )
        
        logger.debug(f"LRU eviction selected: {victim}")
        return victim
    
    def _select_lfu(self, entries: Dict[str, Dict[str, Any]]) -> str:
        """
        Select least frequently used entry.
        
        Args:
            entries: Cache entries
            
        Returns:
            Key of LFU entry
        """
        victim = min(
            entries.keys(),
            key=lambda k: entries[k].get('access_count', 0)
        )
        
        logger.debug(f"LFU eviction selected: {victim}")
        return victim
    
    def calculate_score(
        self,
        key: str,
        entry: Dict[str, Any],
    ) -> float:
        """
        Calculate eviction score for entry.
        
        Lower score = higher priority for eviction.
        
        Args:
            key: Entry key
            entry: Entry data
            
        Returns:
            Eviction score
        """
        if self.policy == 'lru':
            # Convert timestamp to unix for numeric comparison
            accessed_at = entry.get('accessed_at', entry['created_at'])
            timestamp = datetime.fromisoformat(accessed_at).timestamp()
            return timestamp
        
        else:  # lfu
            # Access count is the score
            return float(entry.get('access_count', 0))
    
    def get_candidates(
        self,
        entries: Dict[str, Dict[str, Any]],
        count: int = 5,
    ) -> list:
        """
        Get top N candidates for eviction.
        
        Args:
            entries: Cache entries
            count: Number of candidates to return
            
        Returns:
            List of (key, score) tuples
        """
        scores = [
            (key, self.calculate_score(key, entry))
            for key, entry in entries.items()
        ]
        
        # Sort by score (ascending)
        scores.sort(key=lambda x: x[1])
        
        return scores[:count]
    
    def should_evict(
        self,
        current_size: int,
        max_size: int,
    ) -> bool:
        """
        Determine if eviction is needed.
        
        Args:
            current_size: Current number of cache entries
            max_size: Maximum allowed size
            
        Returns:
            True if eviction needed
        """
        return current_size >= max_size


class LRUPolicy(CachePolicy):
    """Least Recently Used eviction policy"""
    
    def __init__(self):
        """Initialize LRU policy"""
        super().__init__('lru')


class LFUPolicy(CachePolicy):
    """Least Frequently Used eviction policy"""
    
    def __init__(self):
        """Initialize LFU policy"""
        super().__init__('lfu')


class AdaptivePolicy(CachePolicy):
    """
    Adaptive policy that switches between LRU and LFU.
    
    Uses LRU for temporal locality and switches to LFU
    when frequency pattern is detected.
    """
    
    def __init__(self):
        """Initialize adaptive policy"""
        super().__init__('lru')
        self._access_patterns: Dict[str, int] = {}
        self._pattern_threshold = 10
    
    def record_access(self, key: str) -> None:
        """
        Record access for pattern detection.
        
        Args:
            key: Accessed key
        """
        self._access_patterns[key] = self._access_patterns.get(key, 0) + 1
    
    def detect_pattern(self) -> str:
        """
        Detect access pattern.
        
        Returns:
            'temporal' if LRU-like, 'frequency' if LFU-like
        """
        if not self._access_patterns:
            return 'temporal'
        
        # If few entries have high access counts, favor frequency
        high_freq = sum(1 for count in self._access_patterns.values()
                       if count > self._pattern_threshold)
        
        if high_freq > 0:
            return 'frequency'
        return 'temporal'
    
    def select_victim(self, entries: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Select victim using adaptive logic.
        
        Args:
            entries: Cache entries
            
        Returns:
            Key to evict
        """
        pattern = self.detect_pattern()
        
        if pattern == 'frequency':
            self.policy = 'lfu'
            logger.debug("Adaptive policy switched to LFU")
        else:
            self.policy = 'lru'
            logger.debug("Adaptive policy using LRU")
        
        return super().select_victim(entries)


def get_policy(policy_name: str) -> CachePolicy:
    """
    Get cache policy by name.
    
    Args:
        policy_name: 'lru', 'lfu', or 'adaptive'
        
    Returns:
        CachePolicy instance
    """
    if policy_name.lower() == 'lru':
        return LRUPolicy()
    elif policy_name.lower() == 'lfu':
        return LFUPolicy()
    elif policy_name.lower() == 'adaptive':
        return AdaptivePolicy()
    else:
        raise ValueError(f"Unknown policy: {policy_name}")


__all__ = [
    "CachePolicy",
    "EvictionPolicy",
    "LRUPolicy",
    "LFUPolicy",
    "AdaptivePolicy",
    "get_policy",
]
