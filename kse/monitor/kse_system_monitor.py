"""kse_system_monitor.py - System Health Monitoring

Monitors system health and performance:
- CPU usage
- Memory usage
- Disk space
- Process health
"""

import logging
from typing import Dict
import psutil
import os

from kse.core import get_logger

logger = get_logger('monitoring')


class SystemMonitor:
    """Monitor system health"""
    
    def __init__(self):
        """Initialize system monitor"""
        logger.debug("SystemMonitor initialized")
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage
        
        Returns:
            CPU usage (0-100)
        """
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage
        
        Returns:
            Memory stats (used, total, percent)
        """
        try:
            mem = psutil.virtual_memory()
            return {
                'used_mb': mem.used / (1024 * 1024),
                'total_mb': mem.total / (1024 * 1024),
                'percent': mem.percent,
            }
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return {'used_mb': 0, 'total_mb': 0, 'percent': 0}
    
    def get_disk_usage(self, path: str = '/') -> Dict[str, float]:
        """Get disk usage
        
        Args:
            path: Path to check
            
        Returns:
            Disk stats (used, total, percent)
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                'used_gb': disk.used / (1024 * 1024 * 1024),
                'total_gb': disk.total / (1024 * 1024 * 1024),
                'percent': disk.percent,
            }
        except Exception as e:
            logger.warning(f"Failed to get disk usage: {e}")
            return {'used_gb': 0, 'total_gb': 0, 'percent': 0}
    
    def get_system_health(self) -> Dict:
        """Get overall system health
        
        Returns:
            Health status dictionary
        """
        cpu = self.get_cpu_usage()
        mem = self.get_memory_usage()
        disk = self.get_disk_usage()
        
        # Determine health status
        health = 'healthy'
        if cpu > 80 or mem['percent'] > 80 or disk['percent'] > 80:
            health = 'warning'
        if cpu > 95 or mem['percent'] > 95 or disk['percent'] > 95:
            health = 'critical'
        
        return {
            'status': health,
            'cpu_usage': round(cpu, 2),
            'memory': mem,
            'disk': disk,
        }


__all__ = ["SystemMonitor"]
