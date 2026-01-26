"""kse_log_monitor.py - Log Monitoring & Analysis

Monitors log files for issues:
- Error tracking
- Warning aggregation
- Log statistics
- Alert conditions
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
import re

from kse.core import get_logger

logger = get_logger('monitoring')


class LogMonitor:
    """Monitor application logs"""
    
    def __init__(self, log_file: str = None):
        """Initialize log monitor
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.log_cache = []
        self.error_count = 0
        self.warning_count = 0
        logger.debug("LogMonitor initialized")
    
    def read_recent_logs(self, lines: int = 100) -> List[str]:
        """Read recent log lines
        
        Args:
            lines: Number of lines to read
            
        Returns:
            List of log lines
        """
        try:
            if not self.log_file:
                return []
            
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except Exception as e:
            logger.warning(f"Failed to read logs: {e}")
            return []
    
    def get_error_summary(self, hours: int = 1) -> Dict:
        """Get error summary for time period
        
        Args:
            hours: Time period in hours
            
        Returns:
            Error statistics
        """
        logs = self.read_recent_logs(500)
        
        errors = []
        for line in logs:
            if 'ERROR' in line:
                errors.append(line)
        
        return {
            'total_errors': len(errors),
            'recent_errors': errors[-10:],
            'error_types': self._categorize_errors(errors),
        }
    
    def get_warning_summary(self, hours: int = 1) -> Dict:
        """Get warning summary for time period
        
        Args:
            hours: Time period in hours
            
        Returns:
            Warning statistics
        """
        logs = self.read_recent_logs(500)
        
        warnings = []
        for line in logs:
            if 'WARNING' in line:
                warnings.append(line)
        
        return {
            'total_warnings': len(warnings),
            'recent_warnings': warnings[-10:],
        }
    
    def get_log_statistics(self) -> Dict:
        """Get log file statistics
        
        Returns:
            Statistics dictionary
        """
        logs = self.read_recent_logs(1000)
        
        stats = {
            'total_lines': len(logs),
            'errors': len([l for l in logs if 'ERROR' in l]),
            'warnings': len([l for l in logs if 'WARNING' in l]),
            'info': len([l for l in logs if 'INFO' in l]),
            'debug': len([l for l in logs if 'DEBUG' in l]),
        }
        
        return stats
    
    def _categorize_errors(self, errors: List[str]) -> Dict[str, int]:
        """Categorize errors by type
        
        Args:
            errors: List of error lines
            
        Returns:
            Error type counts
        """
        categories = {}
        
        for error in errors:
            # Extract error type
            if 'Timeout' in error:
                cat = 'Timeout'
            elif 'Connection' in error:
                cat = 'Connection'
            elif 'Rate limit' in error:
                cat = 'RateLimit'
            else:
                cat = 'Other'
            
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories


__all__ = ["LogMonitor"]
