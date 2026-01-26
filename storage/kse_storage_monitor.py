"""
kse_storage_monitor.py - Storage Usage Monitoring

Monitors storage usage, tracks metrics, and provides alerts
when storage space runs low or quotas exceeded.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from kse.core import (
    get_logger,
    INDEX_DIR,
    CACHE_DIR,
    CRAWL_STATE_DIR,
    SNAPSHOTS_DIR,
    LOGS_DIR,
    DATA_DIR,
)

logger = get_logger('storage')


class StorageMonitor:
    """Monitors and reports storage usage"""
    
    def __init__(self):
        """Initialize storage monitor"""
        logger.debug("StorageMonitor initialized")
    
    def get_directory_size(self, path: Path) -> int:
        """
        Calculate total size of directory.
        
        Args:
            path: Directory path
            
        Returns:
            Size in bytes
        """
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception as e:
            logger.warning(f"Error calculating size for {path}: {e}")
        return total
    
    def get_storage_usage(self) -> Dict[str, int]:
        """
        Get storage usage for all directories.
        
        Returns:
            Dictionary with directory sizes
        """
        usage = {
            'timestamp': datetime.now().isoformat(),
            'index': self.get_directory_size(INDEX_DIR),
            'cache': self.get_directory_size(CACHE_DIR),
            'crawl_state': self.get_directory_size(CRAWL_STATE_DIR),
            'snapshots': self.get_directory_size(SNAPSHOTS_DIR),
            'logs': self.get_directory_size(LOGS_DIR),
        }
        
        usage['total'] = sum(v for k, v in usage.items() if k != 'timestamp')
        return usage
    
    def get_disk_space(self) -> Dict[str, int]:
        """
        Get available disk space.
        
        Returns:
            Dictionary with disk space info:
            - total: Total disk space
            - used: Used space
            - free: Available space
            - percent_used: Usage percentage
        """
        try:
            stat = shutil.disk_usage(DATA_DIR)
            return {
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'percent_used': (stat.used / stat.total) * 100,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get disk space: {e}")
            return {}
    
    def get_storage_report(self) -> Dict:
        """
        Get comprehensive storage report.
        
        Returns:
            Storage report with usage and disk space
        """
        usage = self.get_storage_usage()
        disk = self.get_disk_space()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'usage': usage,
            'disk': disk,
            'warnings': [],
        }
        
        # Check for warnings
        if usage['total'] > 1024 * 1024 * 1024:  # >1GB
            report['warnings'].append(
                f"Storage usage high: {usage['total'] / (1024*1024*1024):.1f}GB"
            )
        
        if disk and disk['percent_used'] > 90:
            report['warnings'].append(
                f"Disk space critical: {disk['percent_used']:.1f}% used"
            )
        elif disk and disk['percent_used'] > 80:
            report['warnings'].append(
                f"Disk space warning: {disk['percent_used']:.1f}% used"
            )
        
        return report
    
    def is_storage_healthy(self) -> bool:
        """
        Check if storage is healthy.
        
        Returns:
            True if storage is OK
        """
        report = self.get_storage_report()
        return len(report['warnings']) == 0


__all__ = ["StorageMonitor"]
