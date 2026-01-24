"""
Enterprise Logging System

Provides structured logging with file rotation, levels, and formatters.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class KSELogger:
    """
    Centralized logging configuration for KSE.
    
    Features:
    - Multiple log levels
    - File rotation
    - Structured formatting
    - Performance tracking
    """
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    _configured = False
    _loggers = {}
    
    @classmethod
    def configure(
        cls,
        log_dir: str = "data/logs",
        level: int = logging.INFO,
        console_enabled: bool = True,
        file_enabled: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ) -> None:
        """Configure global logging.
        
        Args:
            log_dir: Directory for log files
            level: Logging level
            console_enabled: Enable console output
            file_enabled: Enable file logging
            max_bytes: Max size before rotation (bytes)
            backup_count: Number of rotated files to keep
        """
        if cls._configured:
            return
        
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        root_logger.handlers = []
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if file_enabled:
            log_file = log_path / "kse.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create logger for module.
        
        Args:
            name: Logger name (typically __name__)
        
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]
    
    @classmethod
    def add_file_handler(
        cls,
        logger_name: str,
        filename: str,
        level: int = logging.DEBUG
    ) -> None:
        """Add file handler for specific logger.
        
        Args:
            logger_name: Logger name
            filename: Log filename
            level: Handler log level
        """
        logger = cls.get_logger(logger_name)
        
        # Create handler
        handler = logging.FileHandler(filename)
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    @classmethod
    def add_rotating_file_handler(
        cls,
        logger_name: str,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        level: int = logging.DEBUG
    ) -> None:
        """Add rotating file handler for specific logger.
        
        Args:
            logger_name: Logger name
            filename: Log filename
            max_bytes: Max file size before rotation
            backup_count: Number of backup files
            level: Handler log level
        """
        logger = cls.get_logger(logger_name)
        
        # Create handler
        handler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)


# Initialize logger on module import
KSELogger.configure()
