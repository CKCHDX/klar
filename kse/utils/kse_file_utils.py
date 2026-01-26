"""kse_file_utils.py - File Handling Utilities

Utilities for file operations:
- Safe file I/O
- File size formatting
- Path handling
- File validation
"""

import logging
from typing import Optional
from pathlib import Path
import os

from kse.core import get_logger

logger = get_logger('utils')


class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists
        
        Args:
            path: Directory path
            
        Returns:
            True if successful
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.warning(f"Failed to create directory: {e}")
            return False
    
    @staticmethod
    def safe_read_file(path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Safely read file
        
        Args:
            path: File path
            encoding: File encoding
            
        Returns:
            File contents or None
        """
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read file: {e}")
            return None
    
    @staticmethod
    def safe_write_file(path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Safely write file
        
        Args:
            path: File path
            content: Content to write
            encoding: File encoding
            
        Returns:
            True if successful
        """
        try:
            FileUtils.ensure_directory(os.path.dirname(path))
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.warning(f"Failed to write file: {e}")
            return False
    
    @staticmethod
    def get_file_size(path: str) -> Optional[int]:
        """Get file size in bytes
        
        Args:
            path: File path
            
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(path)
        except Exception as e:
            logger.warning(f"Failed to get file size: {e}")
            return None
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size for display
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        
        return f"{bytes_size:.2f} PB"
    
    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists
        
        Args:
            path: File path
            
        Returns:
            True if exists
        """
        return os.path.isfile(path)
    
    @staticmethod
    def directory_exists(path: str) -> bool:
        """Check if directory exists
        
        Args:
            path: Directory path
            
        Returns:
            True if exists
        """
        return os.path.isdir(path)
    
    @staticmethod
    def get_extension(filename: str) -> str:
        """Get file extension
        
        Args:
            filename: Filename
            
        Returns:
            Extension (with dot)
        """
        return os.path.splitext(filename)[1]


__all__ = ["FileUtils"]
