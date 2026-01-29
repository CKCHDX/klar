"""
Performance Profiler - Performance profiling and analysis
"""

import logging
import time
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Performance profiling system"""
    
    def __init__(self):
        """Initialize performance profiler"""
        self.profiles = {}
        logger.info("PerformanceProfiler initialized")
    
    @contextmanager
    def profile(self, operation_name: str):
        """
        Context manager for profiling operations
        
        Args:
            operation_name: Name of operation to profile
        
        Example:
            with profiler.profile('search_query'):
                # code to profile
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            self._record_profile(operation_name, elapsed)
    
    def _record_profile(self, operation: str, elapsed: float) -> None:
        """Record profile data"""
        if operation not in self.profiles:
            self.profiles[operation] = {
                'count': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }
        
        profile = self.profiles[operation]
        profile['count'] += 1
        profile['total_time'] += elapsed
        profile['min_time'] = min(profile['min_time'], elapsed)
        profile['max_time'] = max(profile['max_time'], elapsed)
    
    def get_profile(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get profile for specific operation"""
        if operation not in self.profiles:
            return None
        
        profile = self.profiles[operation]
        return {
            'operation': operation,
            'count': profile['count'],
            'total_time': profile['total_time'],
            'avg_time': profile['total_time'] / profile['count'],
            'min_time': profile['min_time'],
            'max_time': profile['max_time']
        }
    
    def get_all_profiles(self) -> Dict[str, Any]:
        """Get all profiles"""
        return {
            op: self.get_profile(op)
            for op in self.profiles
        }
    
    def reset(self) -> None:
        """Reset all profiles"""
        self.profiles.clear()
        logger.info("Performance profiles reset")


def profile_function(profiler: PerformanceProfiler):
    """Decorator for profiling functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with profiler.profile(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator
