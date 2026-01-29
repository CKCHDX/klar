"""
Date Utilities - Date and time manipulation utilities
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string to datetime
    
    Args:
        timestamp_str: Timestamp string
    
    Returns:
        Datetime object or None
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Failed to parse timestamp: {timestamp_str}")
    return None


def format_timestamp(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object
        format_str: Format string
    
    Returns:
        Formatted timestamp string
    """
    return dt.strftime(format_str)


def get_age_days(dt: datetime) -> int:
    """
    Get age in days from datetime
    
    Args:
        dt: Datetime object
    
    Returns:
        Age in days
    """
    return (datetime.now() - dt).days


def is_within_range(
    dt: datetime,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None
) -> bool:
    """
    Check if datetime is within range
    
    Args:
        dt: Datetime to check
        start: Start of range (inclusive)
        end: End of range (inclusive)
    
    Returns:
        True if within range
    """
    if start and dt < start:
        return False
    if end and dt > end:
        return False
    return True


def add_days(dt: datetime, days: int) -> datetime:
    """
    Add days to datetime
    
    Args:
        dt: Base datetime
        days: Number of days to add
    
    Returns:
        New datetime
    """
    return dt + timedelta(days=days)


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time string
    
    Args:
        dt: Datetime object
    
    Returns:
        Relative time string (e.g., "2 hours ago")
    """
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} år sedan" if years > 1 else "1 år sedan"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} månader sedan" if months > 1 else "1 månad sedan"
    elif diff.days > 0:
        return f"{diff.days} dagar sedan" if diff.days > 1 else "1 dag sedan"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} timmar sedan" if hours > 1 else "1 timme sedan"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minuter sedan" if minutes > 1 else "1 minut sedan"
    else:
        return "just nu"
