"""
KSE Logger - Enterprise logging system for Klar Search Engine
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class KSELogger:
    """Centralized logging system for KSE"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup(cls, log_dir: Path, level: str = "INFO", enable_console: bool = True) -> None:
        """
        Set up the logging system
        
        Args:
            log_dir: Directory for log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Whether to log to console
        """
        if cls._initialized:
            return
        
        # Create log directory
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # File handler for main log
        main_log_file = log_dir / "kse.log"
        file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level))
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level))
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Error log file
        error_log_file = log_dir / "errors.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        cls._initialized = True
        root_logger.info("KSE logging system initialized")
    
    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger
        
        Args:
            name: Logger name (typically __name__)
            log_file: Optional separate log file for this logger
        
        Returns:
            Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Add separate file handler if specified
        if log_file:
            from kse.core.kse_constants import DEFAULT_LOG_DIR
            log_path = DEFAULT_LOG_DIR / log_file
            handler = logging.FileHandler(log_path, encoding='utf-8')
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        cls._loggers[name] = logger
        return logger


def setup_logging(log_dir: Optional[Path] = None, level: str = "INFO", enable_console: bool = True) -> None:
    """
    Convenience function to set up logging with sensible defaults
    
    Args:
        log_dir: Directory for log files (defaults to DEFAULT_LOG_DIR)
        level: Logging level (defaults to INFO)
        enable_console: Whether to log to console (defaults to True)
    """
    if log_dir is None:
        from kse.core.kse_constants import DEFAULT_LOG_DIR
        log_dir = DEFAULT_LOG_DIR
    
    KSELogger.setup(log_dir, level, enable_console)


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name
        log_file: Optional separate log file
    
    Returns:
        Logger instance
    """
    return KSELogger.get_logger(name, log_file)
