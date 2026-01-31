"""
Cache Policy - Cache eviction policies
Defines strategies for cache eviction and retention
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CachePolicy:
    """Cache eviction and retention policies"""
    
    def __init__(self):
        """Initialize cache policy manager"""
        self.policies = {
            'lru': self._lru_policy,
            'lfu': self._lfu_policy,
            'ttl': self._ttl_policy
        }
        logger.info("CachePolicy initialized")
    
    def _lru_policy(self, cache_data: Dict[str, Any]) -> List[str]:
        """
        Least Recently Used policy
        
        Args:
            cache_data: Cache metadata
        
        Returns:
            List of keys to evict
        """
        # Sort by last access time
        sorted_items = sorted(
            cache_data.items(),
            key=lambda x: x[1].get('last_access', datetime.min)
        )
        
        # Return oldest 10%
        evict_count = max(1, len(sorted_items) // 10)
        return [key for key, _ in sorted_items[:evict_count]]
    
    def _lfu_policy(self, cache_data: Dict[str, Any]) -> List[str]:
        """
        Least Frequently Used policy
        
        Args:
            cache_data: Cache metadata
        
        Returns:
            List of keys to evict
        """
        # Sort by access count
        sorted_items = sorted(
            cache_data.items(),
            key=lambda x: x[1].get('access_count', 0)
        )
        
        # Return least frequently used 10%
        evict_count = max(1, len(sorted_items) // 10)
        return [key for key, _ in sorted_items[:evict_count]]
    
    def _ttl_policy(self, cache_data: Dict[str, Any]) -> List[str]:
        """
        Time-To-Live policy
        
        Args:
            cache_data: Cache metadata
        
        Returns:
            List of expired keys to evict
        """
        expired_keys = []
        now = datetime.now()
        
        for key, metadata in cache_data.items():
            timestamp = metadata.get('timestamp')
            ttl = metadata.get('ttl', 3600)
            
            if timestamp:
                from datetime import timedelta
                expiry = timestamp + timedelta(seconds=ttl)
                if now > expiry:
                    expired_keys.append(key)
        
        return expired_keys
    
    def apply_policy(self, policy_name: str, cache_data: Dict[str, Any]) -> List[str]:
        """
        Apply eviction policy
        
        Args:
            policy_name: Name of policy to apply
            cache_data: Cache metadata
        
        Returns:
            List of keys to evict
        """
        policy_func = self.policies.get(policy_name)
        if not policy_func:
            logger.warning(f"Unknown cache policy: {policy_name}")
            return []
        
        keys_to_evict = policy_func(cache_data)
        logger.debug(f"Policy '{policy_name}' selected {len(keys_to_evict)} keys for eviction")
        return keys_to_evict
