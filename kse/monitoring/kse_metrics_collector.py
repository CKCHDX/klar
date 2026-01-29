"""
Metrics Collector - System metrics collection and aggregation
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import psutil
from collections import deque

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Metrics collection system"""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize metrics collector
        
        Args:
            history_size: Number of historical data points to keep
        """
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        logger.info(f"MetricsCollector initialized (history_size={history_size})")
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect current system metrics
        
        Returns:
            Metrics dictionary
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': self._get_network_io(),
            'process_info': self._get_process_info()
        }
        
        # Add to history
        self.metrics_history.append(metrics)
        
        return metrics
    
    def _get_network_io(self) -> Dict[str, int]:
        """Get network I/O counters"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }
    
    def _get_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        import os
        process = psutil.Process(os.getpid())
        
        return {
            'memory_mb': process.memory_info().rss / (1024 * 1024),
            'cpu_percent': process.cpu_percent(),
            'num_threads': process.num_threads()
        }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get most recent metrics"""
        return self.metrics_history[-1] if self.metrics_history else {}
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get metrics history"""
        return list(self.metrics_history)
