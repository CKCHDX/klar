"""kse_index_monitor.py - Index Health Monitoring

Monitors index health and statistics:
- Index size
- Document count
- Query performance
- Index freshness
"""

import logging
from typing import Dict
import time

from kse.core import get_logger

logger = get_logger('monitoring')


class IndexMonitor:
    """Monitor index health"""
    
    def __init__(self):
        """Initialize index monitor"""
        self.stats = {
            'total_documents': 0,
            'index_size_mb': 0,
            'avg_query_time_ms': 0,
            'total_queries': 0,
            'last_update': None,
        }
        logger.debug("IndexMonitor initialized")
    
    def update_index_stats(self,
                          doc_count: int,
                          index_size_bytes: int,
                          last_update: float = None) -> None:
        """Update index statistics
        
        Args:
            doc_count: Number of documents
            index_size_bytes: Index size in bytes
            last_update: Last update timestamp
        """
        self.stats['total_documents'] = doc_count
        self.stats['index_size_mb'] = index_size_bytes / (1024 * 1024)
        self.stats['last_update'] = last_update or time.time()
        
        logger.debug(f"Index updated: {doc_count} docs, {self.stats['index_size_mb']:.2f}MB")
    
    def record_query(self, query_time_ms: float) -> None:
        """Record query execution time
        
        Args:
            query_time_ms: Query time in milliseconds
        """
        total_time = self.stats['avg_query_time_ms'] * self.stats['total_queries']
        self.stats['total_queries'] += 1
        total_time += query_time_ms
        self.stats['avg_query_time_ms'] = total_time / self.stats['total_queries']
    
    def get_index_age(self) -> float:
        """Get index age in hours
        
        Returns:
            Hours since last update
        """
        if not self.stats['last_update']:
            return 0
        
        age_seconds = time.time() - self.stats['last_update']
        return age_seconds / 3600
    
    def get_index_health(self) -> Dict:
        """Get overall index health
        
        Returns:
            Health status
        """
        age = self.get_index_age()
        health = 'healthy'
        
        if age > 24:  # Over 24 hours old
            health = 'stale'
        if age > 72:  # Over 72 hours old
            health = 'outdated'
        
        if self.stats['avg_query_time_ms'] > 100:
            health = 'slow'
        
        return {
            'status': health,
            'total_documents': self.stats['total_documents'],
            'index_size_mb': round(self.stats['index_size_mb'], 2),
            'index_age_hours': round(age, 2),
            'avg_query_time_ms': round(self.stats['avg_query_time_ms'], 2),
            'total_queries': self.stats['total_queries'],
        }
    
    def get_index_stats(self) -> Dict:
        """Get detailed index statistics
        
        Returns:
            Detailed stats
        """
        return {
            'documents': self.stats['total_documents'],
            'size_mb': round(self.stats['index_size_mb'], 2),
            'size_gb': round(self.stats['index_size_mb'] / 1024, 2),
            'bytes_per_doc': int(self.stats['index_size_mb'] * 1024 * 1024 / max(1, self.stats['total_documents'])),
            'queries_processed': self.stats['total_queries'],
            'avg_query_time_ms': round(self.stats['avg_query_time_ms'], 2),
            'freshness_hours': round(self.get_index_age(), 2),
        }


__all__ = ["IndexMonitor"]
