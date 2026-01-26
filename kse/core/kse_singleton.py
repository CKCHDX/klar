"""
kse_singleton.py - Singleton Pattern Implementation for Shared Resources

This module provides singleton pattern implementations for shared application
resources that should only have one instance throughout the application lifetime.

Includes:
- Singleton metaclass for automatic singleton implementation
- Pre-configured singleton instances for ConfigManager and LoggerManager
- Thread-safe initialization
- Reset/cleanup utilities for testing

Key Singletons:
- config: Global ConfigManager instance
- logger: Global logger setup

Usage:
    >>> from kse.core import config, logger
    >>> config.get('crawler.timeout')
    >>> logger = get_logger('module_name')

    # Or use decorator:
    >>> from kse.core.kse_singleton import Singleton
    >>> @Singleton
    ... class MyService:
    ...     pass
    >>> service = MyService.get_instance()

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import threading
from typing import Any, Dict, Optional, Type, TypeVar
import logging

T = TypeVar('T')


class SingletonMeta(type):
    """
    Metaclass for implementing the Singleton pattern.
    
    Thread-safe implementation using double-checked locking pattern.
    Ensures that only one instance of a class exists throughout
    the application lifetime.
    
    Usage:
        class MyService(metaclass=SingletonMeta):
            def __init__(self):
                self.data = {}
        
        instance1 = MyService()
        instance2 = MyService()
        assert instance1 is instance2  # Same instance!
    """
    
    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs) -> Any:
        """
        Create or return existing singleton instance.
        
        Uses double-checked locking pattern:
        1. First check without lock (fast path)
        2. Acquire lock if needed (slow path)
        3. Check again after acquiring lock
        4. Create instance if needed
        
        Args:
            *args: Positional arguments for class __init__
            **kwargs: Keyword arguments for class __init__
            
        Returns:
            Singleton instance of the class
        """
        # Fast path: check if instance already exists
        if cls not in cls._instances:
            # Slow path: acquire lock and check again
            with cls._lock:
                # Double-check: another thread might have created it
                if cls not in cls._instances:
                    # Create new instance
                    instance = super(SingletonMeta, cls).__call__(
                        *args, **kwargs
                    )
                    cls._instances[cls] = instance
        
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls: Type[T]) -> None:
        """
        Reset/delete singleton instance (for testing).
        
        Args:
            cls: Class whose instance should be reset
            
        Example:
            >>> SingletonMeta.reset_instance(MyService)
        """
        with mcs._lock:
            if cls in mcs._instances:
                del mcs._instances[cls]
    
    @classmethod
    def get_instance(mcs, cls: Type[T]) -> Optional[T]:
        """
        Get existing instance without creating one.
        
        Args:
            cls: Class to get instance of
            
        Returns:
            Instance if it exists, None otherwise
        """
        return mcs._instances.get(cls)
    
    @classmethod
    def clear_all(mcs) -> None:
        """Clear all singleton instances (for testing)"""
        with mcs._lock:
            mcs._instances.clear()


class Singleton(metaclass=SingletonMeta):
    """
    Convenience base class for implementing Singleton pattern.
    
    Any class that inherits from Singleton automatically becomes
    a singleton with thread-safe initialization.
    
    Usage:
        class MyService(Singleton):
            def __init__(self):
                self.initialized = True
        
        s1 = MyService()
        s2 = MyService()
        assert s1 is s2  # True
    """
    
    _initialized: bool = False
    
    def __init__(self):
        """Initialize singleton base"""
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'Singleton':
        """
        Get or create singleton instance.
        
        Returns:
            Singleton instance of this class
        """
        return cls()
    
    @classmethod
    def reset(cls) -> None:
        """Reset/delete singleton instance (for testing)"""
        SingletonMeta.reset_instance(cls)
        cls._initialized = False


# ============================================================================
# GLOBAL SINGLETON INSTANCES
# ============================================================================

class GlobalSingletons:
    """Container for all global singleton instances"""
    
    _config: Optional[Any] = None
    _logger_manager: Optional[Any] = None
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def get_config(cls):
        """
        Get or create global ConfigManager instance.
        
        Returns:
            ConfigManager singleton
        """
        if cls._config is None:
            with cls._lock:
                if cls._config is None:
                    # Import here to avoid circular imports
                    from .kse_config import ConfigManager
                    cls._config = ConfigManager()
        
        return cls._config
    
    @classmethod
    def get_logger_manager(cls):
        """
        Get or create global LoggerManager instance.
        
        Returns:
            LoggerManager singleton
        """
        if cls._logger_manager is None:
            with cls._lock:
                if cls._logger_manager is None:
                    # Import here to avoid circular imports
                    from .kse_logger import LoggerManager
                    cls._logger_manager = LoggerManager
        
        return cls._logger_manager
    
    @classmethod
    def reset(cls) -> None:
        """Reset all singleton instances (for testing)"""
        with cls._lock:
            cls._config = None
            cls._logger_manager = None
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all singleton instances"""
        return {
            'config': cls._config,
            'logger_manager': cls._logger_manager,
        }


# ============================================================================
# CONVENIENCE ACCESSOR FUNCTIONS
# ============================================================================

def get_config():
    """
    Get global ConfigManager instance.
    
    Returns:
        ConfigManager singleton
        
    Example:
        >>> config = get_config()
        >>> timeout = config.get('crawler.timeout')
    """
    return GlobalSingletons.get_config()


def get_logger_manager():
    """
    Get global LoggerManager instance.
    
    Returns:
        LoggerManager singleton
        
    Example:
        >>> lm = get_logger_manager()
        >>> lm.set_level('DEBUG')
    """
    return GlobalSingletons.get_logger_manager()


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance from global LoggerManager.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger instance
        
    Example:
        >>> logger = get_logger('crawler')
        >>> logger.info('Starting crawl')
    """
    manager = get_logger_manager()
    return manager.get_logger(name)


# ============================================================================
# CONTEXT MANAGERS FOR TESTING
# ============================================================================

class SingletonContext:
    """
    Context manager for temporarily resetting singletons.
    
    Useful for unit testing where you want fresh singleton instances.
    
    Example:
        >>> with SingletonContext():
        ...     # Fresh singleton instances within this block
        ...     config = get_config()
        ...     config.load('test_config.yaml')
        ... # Singletons reset after block
    """
    
    def __enter__(self):
        """Reset singletons on context entry"""
        GlobalSingletons.reset()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset singletons on context exit"""
        GlobalSingletons.reset()
        return False


# ============================================================================
# LAZY INITIALIZATION PATTERN
# ============================================================================

class LazyProxy:
    """
    Proxy object for lazy-initialized singletons.
    
    Defers initialization until first use, useful for avoiding
    initialization overhead at module import time.
    
    Example:
        >>> config = LazyProxy(lambda: ConfigManager())
        >>> # ConfigManager not created yet
        >>> timeout = config.get('timeout')
        >>> # Now ConfigManager is created
    """
    
    def __init__(self, factory):
        """
        Initialize lazy proxy.
        
        Args:
            factory: Callable that creates the actual object
        """
        object.__setattr__(self, '_factory', factory)
        object.__setattr__(self, '_obj', None)
    
    def _get_obj(self):
        """Get or create the actual object"""
        obj = object.__getattribute__(self, '_obj')
        if obj is None:
            factory = object.__getattribute__(self, '_factory')
            obj = factory()
            object.__setattr__(self, '_obj', obj)
        return obj
    
    def __getattr__(self, name):
        """Delegate attribute access to actual object"""
        return getattr(self._get_obj(), name)
    
    def __setattr__(self, name, value):
        """Delegate attribute setting to actual object"""
        if name in ('_factory', '_obj'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._get_obj(), name, value)
    
    def __call__(self, *args, **kwargs):
        """Delegate calls to actual object"""
        return self._get_obj()(*args, **kwargs)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Classes
    "SingletonMeta",
    "Singleton",
    "GlobalSingletons",
    "SingletonContext",
    "LazyProxy",
    # Functions
    "get_config",
    "get_logger_manager",
    "get_logger",
]
