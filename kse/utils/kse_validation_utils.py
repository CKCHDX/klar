"""kse_validation_utils.py - Data Validation Utilities

Utilities for data validation:
- Email validation
- URL validation
- Number validation
- Type checking
"""

import logging
from typing import Any
import re

from kse.core import get_logger

logger = get_logger('utils')


class ValidationUtils:
    """Data validation utilities"""
    
    @staticmethod
    def is_email(email: str) -> bool:
        """Check if valid email format
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid email
        """
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False
    
    @staticmethod
    def is_url(url: str) -> bool:
        """Check if valid URL format
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid URL
        """
        try:
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return bool(re.match(pattern, url, re.IGNORECASE))
        except Exception:
            return False
    
    @staticmethod
    def is_integer(value: Any) -> bool:
        """Check if value is integer
        
        Args:
            value: Value to check
            
        Returns:
            True if integer
        """
        try:
            int(value)
            return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_positive(value: Any) -> bool:
        """Check if value is positive
        
        Args:
            value: Value to check
            
        Returns:
            True if positive
        """
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_in_range(value: Any, min_val: float, max_val: float) -> bool:
        """Check if value is in range
        
        Args:
            value: Value to check
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if in range
        """
        try:
            num = float(value)
            return min_val <= num <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_length(text: str, min_len: int = 0, max_len: int = None) -> bool:
        """Check if text length is valid
        
        Args:
            text: Text to check
            min_len: Minimum length
            max_len: Maximum length
            
        Returns:
            True if valid
        """
        try:
            length = len(text)
            if length < min_len:
                return False
            if max_len and length > max_len:
                return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """Check if value is not empty
        
        Args:
            value: Value to check
            
        Returns:
            True if not empty
        """
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict, tuple)):
            return len(value) > 0
        return True


__all__ = ["ValidationUtils"]
