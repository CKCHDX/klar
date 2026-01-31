"""
Health Checker - System health checks and diagnostics
"""

import logging
from typing import Dict, Any
import psutil
from pathlib import Path

logger = logging.getLogger(__name__)


class HealthChecker:
    """System health checking"""
    
    def __init__(self):
        """Initialize health checker"""
        logger.info("HealthChecker initialized")
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check
        
        Returns:
            Health status dictionary
        """
        checks = {
            'cpu': self._check_cpu(),
            'memory': self._check_memory(),
            'disk': self._check_disk(),
            'index': self._check_index()
        }
        
        # Determine overall health
        healthy = all(check.get('status') == 'ok' for check in checks.values())
        
        return {
            'healthy': healthy,
            'checks': checks,
            'timestamp': psutil.boot_time()
        }
    
    def _check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        status = 'ok' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
        
        return {
            'status': status,
            'usage_percent': cpu_percent,
            'cores': psutil.cpu_count()
        }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        status = 'ok' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
        
        return {
            'status': status,
            'usage_percent': memory.percent,
            'available_mb': memory.available / (1024 * 1024)
        }
    
    def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage"""
        disk = psutil.disk_usage('/')
        status = 'ok' if disk.percent < 80 else 'warning' if disk.percent < 95 else 'critical'
        
        return {
            'status': status,
            'usage_percent': disk.percent,
            'free_gb': disk.free / (1024 * 1024 * 1024)
        }
    
    def _check_index(self) -> Dict[str, Any]:
        """Check index availability"""
        index_path = Path('data/storage/index')
        exists = index_path.exists()
        
        return {
            'status': 'ok' if exists else 'warning',
            'exists': exists,
            'path': str(index_path)
        }
    
    def check_component(self, component_name: str) -> Dict[str, Any]:
        """Check specific component"""
        checks = {
            'cpu': self._check_cpu,
            'memory': self._check_memory,
            'disk': self._check_disk,
            'index': self._check_index
        }
        
        check_func = checks.get(component_name)
        if check_func:
            return check_func()
        
        return {'status': 'unknown', 'message': f'Unknown component: {component_name}'}
