"""
kse_main.py - Main Application Class and Entry Point for KSE

This module contains the main KSEApplication class that orchestrates
the initialization and lifecycle of the entire KSE system.

Responsibilities:
- Initialize all core systems (config, logging, storage, etc)
- Provide centralized access to all subsystems
- Handle application startup and shutdown
- Manage application state
- Provide application metadata and diagnostics

Architecture:
    KSEApplication
    ├── ConfigManager
    ├── LoggerManager
    ├── StorageManager (lazy-loaded)
    ├── CrawlerEngine (lazy-loaded)
    ├── IndexingEngine (lazy-loaded)
    ├── SearchEngine (lazy-loaded)
    └── APIServer (lazy-loaded)

Usage:
    >>> from kse.core import KSEApplication
    >>> app = KSEApplication()
    >>> app.initialize()
    >>> config = app.config
    >>> logger = app.get_logger(__name__)

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .kse_constants import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_ENV,
    BASE_DIR,
    CONFIG_DIR,
    DEFAULT_CONFIG_PATH,
)
from .kse_config import ConfigManager
from .kse_logger import LoggerManager, get_logger
from .kse_exceptions import KSEException
from .kse_singleton import Singleton, GlobalSingletons


class KSEApplication(Singleton):
    """
    Main application class for KSE search engine.
    
    Singleton pattern ensures only one instance exists. Provides
    centralized initialization, configuration, and access to all
    subsystems.
    
    Lifecycle:
        1. Create instance: app = KSEApplication()
        2. Initialize: app.initialize()
        3. Use: app.config, app.get_logger(), etc
        4. Shutdown: app.shutdown()
    """
    
    def __init__(self):
        """Initialize KSE Application"""
        super().__init__()
        
        self._initialized: bool = False
        self._shutdown: bool = False
        self._start_time: Optional[datetime] = None
        self._config: Optional[ConfigManager] = None
        self._logger: Optional[logging.Logger] = None
        
        # Components (lazy-loaded)
        self._components: Dict[str, Any] = {}
    
    def initialize(
        self,
        config_path: Optional[Path] = None,
        setup_logging: bool = True,
        validate_config: bool = True,
    ) -> None:
        """
        Initialize the KSE application.
        
        Sets up:
        1. Logging system
        2. Configuration management
        3. Application metadata
        4. Validation
        
        Args:
            config_path: Path to config file (default: DEFAULT_CONFIG_PATH)
            setup_logging: Whether to setup logging (default: True)
            validate_config: Whether to validate config (default: True)
            
        Raises:
            KSEException: If initialization fails
            
        Example:
            >>> app = KSEApplication()
            >>> app.initialize()
            >>> # Now app is ready to use
        """
        if self._initialized:
            self._logger.warning("Application already initialized")
            return
        
        try:
            # Record start time
            self._start_time = datetime.now()
            
            # Setup logging
            if setup_logging:
                LoggerManager.setup()
            
            self._logger = get_logger('app')
            self._logger.info("=" * 70)
            self._logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")
            self._logger.info(f"Environment: {APP_ENV}")
            self._logger.info("=" * 70)
            
            # Initialize configuration
            self._config = GlobalSingletons.get_config()
            
            # Load config file
            if config_path is None:
                config_path = DEFAULT_CONFIG_PATH
            
            if not Path(config_path).exists():
                self._logger.warning(
                    f"Config file not found: {config_path}, "
                    f"using defaults"
                )
            else:
                self._config.load(config_path)
                self._logger.info(f"Configuration loaded from {config_path}")
            
            # Validate configuration
            if validate_config:
                self._config.validate()
                self._logger.info("Configuration validation passed")
            
            self._initialized = True
            self._logger.info("Application initialization complete")
            
        except Exception as e:
            self._logger.error(f"Application initialization failed: {e}")
            raise
    
    def shutdown(self) -> None:
        """
        Shutdown the KSE application gracefully.
        
        Cleans up resources and closes connections.
        
        Example:
            >>> app.shutdown()
        """
        if self._shutdown:
            return
        
        self._logger.info("Shutting down application")
        
        # Shutdown components in reverse order
        for component_name in reversed(list(self._components.keys())):
            component = self._components.get(component_name)
            if component and hasattr(component, 'shutdown'):
                try:
                    component.shutdown()
                    self._logger.debug(
                        f"Component {component_name} shut down"
                    )
                except Exception as e:
                    self._logger.error(
                        f"Error shutting down {component_name}: {e}"
                    )
        
        self._shutdown = True
        self._logger.info("Application shutdown complete")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name (will be prefixed with 'kse.')
            
        Returns:
            logging.Logger instance
            
        Example:
            >>> logger = app.get_logger('crawler')
        """
        return get_logger(name)
    
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component with the application.
        
        Allows components to be tracked and managed by the application.
        
        Args:
            name: Component name
            component: Component object
            
        Example:
            >>> crawler = CrawlerEngine()
            >>> app.register_component('crawler', crawler)
        """
        self._components[name] = component
        self._logger.debug(f"Component registered: {name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """
        Get a registered component.
        
        Args:
            name: Component name
            
        Returns:
            Component object or None if not registered
            
        Example:
            >>> crawler = app.get_component('crawler')
        """
        return self._components.get(name)
    
    def get_all_components(self) -> Dict[str, Any]:
        """
        Get all registered components.
        
        Returns:
            Dictionary of component name -> component object
        """
        return self._components.copy()
    
    @property
    def config(self) -> ConfigManager:
        """
        Get global configuration manager.
        
        Returns:
            ConfigManager instance
        """
        if self._config is None:
            self._config = GlobalSingletons.get_config()
        return self._config
    
    @property
    def is_initialized(self) -> bool:
        """Check if application is initialized"""
        return self._initialized
    
    @property
    def is_shutdown(self) -> bool:
        """Check if application is shutdown"""
        return self._shutdown
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get application start time"""
        return self._start_time
    
    @property
    def uptime_seconds(self) -> float:
        """Get application uptime in seconds"""
        if self._start_time is None:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get application metadata.
        
        Returns:
            Dictionary with app info
            
        Example:
            >>> meta = app.get_metadata()
            >>> print(meta['version'])
        """
        return {
            "name": APP_NAME,
            "version": APP_VERSION,
            "author": APP_AUTHOR,
            "environment": APP_ENV,
            "initialized": self._initialized,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "uptime_seconds": self.uptime_seconds,
            "components": list(self._components.keys()),
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get application status.
        
        Returns:
            Dictionary with current status
            
        Example:
            >>> status = app.get_status()
            >>> print(status['state'])
        """
        state = "initialized" if self._initialized else "uninitialized"
        if self._shutdown:
            state = "shutdown"
        
        return {
            "state": state,
            "initialized": self._initialized,
            "shutdown": self._shutdown,
            "uptime_seconds": self.uptime_seconds,
            "components_count": len(self._components),
        }
    
    def __repr__(self) -> str:
        """String representation of application"""
        state = "initialized" if self._initialized else "uninitialized"
        return (
            f"<KSEApplication {APP_VERSION} "
            f"({state})>"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        return (
            f"{APP_NAME} v{APP_VERSION} "
            f"({'initialized' if self._initialized else 'uninitialized'})"
        )


# ============================================================================
# MODULE-LEVEL CONVENIENCE
# ============================================================================

_app_instance: Optional[KSEApplication] = None


def get_app() -> KSEApplication:
    """
    Get or create global KSEApplication instance.
    
    Returns:
        KSEApplication singleton
        
    Example:
        >>> from kse.core import get_app
        >>> app = get_app()
        >>> config = app.config
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = KSEApplication()
    return _app_instance


def initialize_app(
    config_path: Optional[Path] = None,
    **kwargs
) -> KSEApplication:
    """
    Initialize and return the global application.
    
    Convenience function for quick app initialization.
    
    Args:
        config_path: Path to config file
        **kwargs: Additional arguments passed to initialize()
        
    Returns:
        Initialized KSEApplication instance
        
    Example:
        >>> from kse.core import initialize_app
        >>> app = initialize_app()
        >>> logger = app.get_logger(__name__)
    """
    app = get_app()
    if not app.is_initialized:
        app.initialize(config_path=config_path, **kwargs)
    return app


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "KSEApplication",
    "get_app",
    "initialize_app",
]
