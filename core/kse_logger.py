"""
kse_logger.py - Enterprise-Grade Logging System for KSE

This module provides centralized logging configuration and management for all
KSE components. Features include:

- Multiple log outputs (console, file)
- Separate log files per module (crawler, indexer, search, etc)
- Colored console output for readability
- JSON-formatted file logs for parsing
- Log rotation by size
- Log level management
- Thread-safe logging

Log Files:
- kse.log: Main application log
- crawler.log: Crawler operations
- indexer.log: Indexing operations
- search.log: Search queries and results
- server.log: API server events
- errors.log: Errors only
- audit.log: Admin actions and system changes

Usage:
    >>> from kse.core import LoggerManager
    >>> LoggerManager.setup()
    >>> logger = logging.getLogger(__name__)
    >>> logger.info("Application started")
    >>> logger.error("An error occurred", exc_info=True)

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from .kse_constants import (
    LOGS_DIR,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_FORMAT_CONSOLE,
    LOG_FORMAT_FILE,
    LOG_ROTATION_SIZE,
    LOG_RETENTION_DAYS,
    LOG_FILE_MAIN,
    LOG_FILE_CRAWLER,
    LOG_FILE_INDEXER,
    LOG_FILE_SEARCH,
    LOG_FILE_SERVER,
    LOG_FILE_ERRORS,
    LOG_FILE_AUDIT,
    APP_NAME,
    APP_VERSION,
)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console logging"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        levelname = record.levelname
        
        # Add color to level name
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)


class LoggerManager:
    """Centralized logging management for KSE"""
    
    _initialized: bool = False
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def setup(cls, logs_dir: Optional[Path] = None) -> None:
        """
        Initialize logging system for entire application.
        
        Sets up:
        - Console logging (INFO level by default)
        - File logging for each module (DEBUG level)
        - Log rotation by size
        - Color-coded output
        
        Args:
            logs_dir: Directory for log files (default: LOGS_DIR from constants)
            
        Example:
            >>> LoggerManager.setup()
            >>> logger = logging.getLogger('kse.crawler')
        """
        if cls._initialized:
            return
        
        if logs_dir is None:
            logs_dir = LOGS_DIR
        
        # Ensure logs directory exists
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Setup console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL_CONSOLE))
        console_formatter = ColoredFormatter(LOG_FORMAT_CONSOLE)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Setup main log file (DEBUG level)
        main_log_path = logs_dir / LOG_FILE_MAIN
        main_handler = cls._create_rotating_file_handler(
            main_log_path,
            logging.DEBUG
        )
        root_logger.addHandler(main_handler)
        
        # Setup module-specific file handlers
        module_handlers = {
            'crawler': logs_dir / LOG_FILE_CRAWLER,
            'indexer': logs_dir / LOG_FILE_INDEXER,
            'search': logs_dir / LOG_FILE_SEARCH,
            'server': logs_dir / LOG_FILE_SERVER,
        }
        
        for module_name, log_file in module_handlers.items():
            logger = logging.getLogger(f'kse.{module_name}')
            handler = cls._create_rotating_file_handler(log_file, logging.DEBUG)
            logger.addHandler(handler)
            logger.propagate = False
        
        # Setup error-only log file
        error_log_path = logs_dir / LOG_FILE_ERRORS
        error_handler = cls._create_rotating_file_handler(
            error_log_path,
            logging.ERROR
        )
        root_logger.addHandler(error_handler)
        
        # Setup audit log file
        audit_log_path = logs_dir / LOG_FILE_AUDIT
        audit_handler = cls._create_rotating_file_handler(
            audit_log_path,
            logging.INFO
        )
        audit_logger = logging.getLogger('kse.audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.propagate = False
        
        cls._initialized = True
        
        # Log initialization
        root_logger.info("=" * 70)
        root_logger.info(
            f"{APP_NAME} v{APP_VERSION} - Logging initialized"
        )
        root_logger.info(f"Log directory: {logs_dir}")
        root_logger.info("=" * 70)
    
    @classmethod
    def _create_rotating_file_handler(
        cls,
        log_file: Path,
        level: int
    ) -> logging.handlers.RotatingFileHandler:
        """
        Create a rotating file handler for a log file.
        
        Args:
            log_file: Path to log file
            level: Logging level
            
        Returns:
            RotatingFileHandler configured for the log file
        """
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=LOG_ROTATION_SIZE,
            backupCount=LOG_RETENTION_DAYS,
            encoding='utf-8'
        )
        
        handler.setLevel(level)
        formatter = logging.Formatter(LOG_FORMAT_FILE)
        handler.setFormatter(formatter)
        
        return handler
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Automatically prefixes with 'kse.' if not already present.
        
        Args:
            name: Logger name (will be prefixed with 'kse.')
            
        Returns:
            logging.Logger instance
            
        Example:
            >>> logger = LoggerManager.get_logger('crawler')
            >>> logger.info("Starting crawl")
        """
        if not name.startswith('kse.'):
            name = f'kse.{name}'
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str, module: Optional[str] = None) -> None:
        """
        Set logging level for root logger or specific module.
        
        Args:
            level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            module: Module name (e.g., 'crawler', 'search') or None for root
            
        Example:
            >>> LoggerManager.set_level('DEBUG')  # All modules
            >>> LoggerManager.set_level('ERROR', 'crawler')  # Crawler only
        """
        level_value = getattr(logging, level.upper(), logging.INFO)
        
        if module:
            if not module.startswith('kse.'):
                module = f'kse.{module}'
            logger = logging.getLogger(module)
            logger.setLevel(level_value)
        else:
            logging.getLogger().setLevel(level_value)
    
    @classmethod
    def log_event(
        cls,
        level: str,
        message: str,
        module: str = "app",
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Log an event with optional metadata.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Event message
            module: Module name
            metadata: Additional metadata dict
            
        Example:
            >>> LoggerManager.log_event(
            ...     'INFO',
            ...     'Crawl completed',
            ...     module='crawler',
            ...     metadata={'pages_crawled': 1000}
            ... )
        """
        logger = cls.get_logger(module)
        level_func = getattr(logger, level.lower(), logger.info)
        
        if metadata:
            message = f"{message} | metadata: {metadata}"
        
        level_func(message)
    
    @classmethod
    def log_error(
        cls,
        message: str,
        exception: Optional[Exception] = None,
        module: str = "app"
    ) -> None:
        """
        Log an error with optional exception traceback.
        
        Args:
            message: Error message
            exception: Exception that occurred (for traceback)
            module: Module name
            
        Example:
            >>> try:
            ...     risky_operation()
            ... except Exception as e:
            ...     LoggerManager.log_error("Operation failed", e, module='crawler')
        """
        logger = cls.get_logger(module)
        if exception:
            logger.error(message, exc_info=exception)
        else:
            logger.error(message)
    
    @classmethod
    def log_audit(
        cls,
        action: str,
        user: str,
        resource: str,
        status: str,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log an audit event (admin action).
        
        Args:
            action: Action performed (e.g., 'index_rebuild', 'config_change')
            user: User who performed action
            resource: Resource affected
            status: Status (success, failure)
            details: Additional details
            
        Example:
            >>> LoggerManager.log_audit(
            ...     action='index_rebuild',
            ...     user='admin',
            ...     resource='main_index',
            ...     status='success',
            ...     details={'pages': 5000, 'time_ms': 3600}
            ... )
        """
        logger = logging.getLogger('kse.audit')
        
        log_message = (
            f"ACTION={action} | USER={user} | RESOURCE={resource} | "
            f"STATUS={status}"
        )
        
        if details:
            log_message += f" | DETAILS={details}"
        
        logger.info(log_message)
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if logging system is initialized"""
        return cls._initialized
    
    @classmethod
    def get_all_loggers(cls) -> Dict[str, logging.Logger]:
        """Get all active loggers"""
        return cls._loggers.copy()


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Automatically initializes LoggerManager if needed.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module loaded")
    """
    if not LoggerManager.is_initialized():
        LoggerManager.setup()
    
    return LoggerManager.get_logger(name)


__all__ = [
    "LoggerManager",
    "ColoredFormatter",
    "get_logger",
]
