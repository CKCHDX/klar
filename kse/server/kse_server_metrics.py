"""kse_server_metrics.py - Server Performance Metrics

Tracks server metrics:
- Request statistics
- Performance metrics
- Health monitoring
"""

import logging
from typing import Dict
import time

from kse.core import get_logger

logger = get_logger('server')


class ServerMetrics:
    """Track server metrics"""
    
    def __init__(self):
        """Initialize metrics tracker"""
        self.start_time = time.time()
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_execution_time': 0,
            'avg_execution_time': 0,
            'uptime_seconds': 0,
        }
        logger.debug("ServerMetrics initialized")
    
    def record_request(self, 
                      success: bool,
                      execution_time: float) -> None:
        """Record request metrics
        
        Args:
            success: Whether request succeeded
            execution_time: Execution time in seconds
        """
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        self.metrics['total_execution_time'] += execution_time
        
        if self.metrics['total_requests'] > 0:
            self.metrics['avg_execution_time'] = (
                self.metrics['total_execution_time'] / 
                self.metrics['total_requests']
            )
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        self.metrics['uptime_seconds'] = int(time.time() - self.start_time)
        
        success_rate = 0
        if self.metrics['total_requests'] > 0:
            success_rate = (
                self.metrics['successful_requests'] / 
                self.metrics['total_requests'] * 100
            )
        
        return {
            **self.metrics,
            'success_rate': round(success_rate, 2),
            'avg_execution_time_ms': round(self.metrics['avg_execution_time'] * 1000, 2),
        }
    
    def get_summary(self) -> str:
        """Get formatted summary"""
        m = self.get_metrics()
        return f"""
Server Metrics:
├─ Uptime: {m['uptime_seconds']}s
├─ Total Requests: {m['total_requests']}
├─ Successful: {m['successful_requests']} ({m['success_rate']}%)
├─ Failed: {m['failed_requests']}
└─ Avg Response Time: {m['avg_execution_time_ms']}ms
""".strip()


__all__ = ["ServerMetrics"]
