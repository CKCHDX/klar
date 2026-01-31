"""
KSE Singleton - Singleton pattern implementation for shared resources
"""
from typing import Any, Dict


class Singleton(type):
    """Metaclass for implementing singleton pattern"""
    
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
    @classmethod
    def clear_instances(mcs):
        """Clear all singleton instances (useful for testing)"""
        mcs._instances.clear()
