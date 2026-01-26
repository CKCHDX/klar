"""kse_time_utils.py - Time and Date Utilities

Utilities for time operations:
- Timestamp formatting
- Duration formatting
- Age calculation
- Time zone handling
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import time

from kse.core import get_logger

logger = get_logger('utils')


class TimeUtils:
    """Time and date utilities"""
    
    @staticmethod
    def get_timestamp() -> float:
        """Get current timestamp
        
        Returns:
            Current Unix timestamp
        """
        return time.time()
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp as string
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted datetime string
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"Failed to format timestamp: {e}")
            return str(timestamp)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration as readable string
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration
        """
        try:
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f}m"
            elif seconds < 86400:
                hours = seconds / 3600
                return f"{hours:.1f}h"
            else:
                days = seconds / 86400
                return f"{days:.1f}d"
        except Exception as e:
            logger.warning(f"Failed to format duration: {e}")
            return str(seconds)
    
    @staticmethod
    def get_age_seconds(timestamp: float) -> float:
        """Get age of timestamp in seconds
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Age in seconds
        """
        return TimeUtils.get_timestamp() - timestamp
    
    @staticmethod
    def get_age_hours(timestamp: float) -> float:
        """Get age of timestamp in hours
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Age in hours
        """
        return TimeUtils.get_age_seconds(timestamp) / 3600
    
    @staticmethod
    def get_age_days(timestamp: float) -> float:
        """Get age of timestamp in days
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Age in days
        """
        return TimeUtils.get_age_hours(timestamp) / 24
    
    @staticmethod
    def is_older_than(timestamp: float, hours: int) -> bool:
        """Check if timestamp is older than N hours
        
        Args:
            timestamp: Unix timestamp
            hours: Number of hours
            
        Returns:
            True if older
        """
        return TimeUtils.get_age_hours(timestamp) > hours


__all__ = ["TimeUtils"]
