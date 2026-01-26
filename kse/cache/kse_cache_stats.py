"""
kse_cache_stats.py - Cache Statistics and Monitoring

Collects and reports cache performance statistics,
hit/miss rates, eviction tracking, and monitoring data.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from kse.core import get_logger

logger = get_logger('cache')


class CacheStatistics:
    """
    Cache statistics collector and reporter.
    
    Tracks:
    - Hit/miss rates
    - Eviction counts
    - Expiration tracking
    - Performance metrics
    """
    
    def __init__(self):
        """Initialize cache statistics"""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'sets': 0,
            'deletes': 0,
            'clears': 0,
            'created_at': datetime.now(),
        }
        
        # Track requests over time
        self._time_windows: Dict[str, List[int]] = {
            'hourly': [],    # requests per hour
            'daily': [],     # requests per day
        }
        
        logger.debug("CacheStatistics initialized")
    
    def record_hit(self) -> None:
        """Record cache hit"""
        self._stats['hits'] += 1
    
    def record_miss(self) -> None:
        """Record cache miss"""
        self._stats['misses'] += 1
    
    def record_eviction(self) -> None:
        """Record cache eviction"""
        self._stats['evictions'] += 1
    
    def record_expiration(self) -> None:
        """Record cache expiration"""
        self._stats['expirations'] += 1
    
    def record_set(self) -> None:
        """Record cache set"""
        self._stats['sets'] += 1
    
    def record_delete(self) -> None:
        """Record cache delete"""
        self._stats['deletes'] += 1
    
    def record_clear(self) -> None:
        """Record cache clear"""
        self._stats['clears'] += 1
    
    def get_hit_rate(self) -> float:
        """
        Calculate cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        total = self._stats['hits'] + self._stats['misses']
        if total == 0:
            return 0.0
        return (self._stats['hits'] / total) * 100
    
    def get_miss_rate(self) -> float:
        """
        Calculate cache miss rate.
        
        Returns:
            Miss rate as percentage (0-100)
        """
        return 100.0 - self.get_hit_rate()
    
    def get_eviction_rate(self) -> float:
        """
        Calculate eviction rate per total operations.
        
        Returns:
            Eviction rate as percentage
        """
        total = (self._stats['hits'] + self._stats['misses'] +
                self._stats['evictions'])
        if total == 0:
            return 0.0
        return (self._stats['evictions'] / total) * 100
    
    def get_uptime(self) -> timedelta:
        """
        Get cache uptime since creation.
        
        Returns:
            Uptime as timedelta
        """
        return datetime.now() - self._stats['created_at']
    
    def get_total_requests(self) -> int:
        """
        Get total cache requests.
        
        Returns:
            Total hits + misses
        """
        return self._stats['hits'] + self._stats['misses']
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get statistics summary.
        
        Returns:
            Dictionary with all statistics
        """
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': self.get_hit_rate(),
            'miss_rate': self.get_miss_rate(),
            'total_requests': self.get_total_requests(),
            'evictions': self._stats['evictions'],
            'eviction_rate': self.get_eviction_rate(),
            'expirations': self._stats['expirations'],
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'clears': self._stats['clears'],
            'uptime_seconds': self.get_uptime().total_seconds(),
            'created_at': self._stats['created_at'].isoformat(),
        }
    
    def get_detailed_report(self) -> str:
        """
        Get detailed statistics report as formatted string.
        
        Returns:
            Formatted report
        """
        summary = self.get_summary()
        uptime = self.get_uptime()
        
        report = f"""
╔══════════════════════════════════════════════════════╗
║           CACHE STATISTICS REPORT                   ║
╚══════════════════════════════════════════════════════╝

Performance Metrics:
  Hit Rate:             {summary['hit_rate']:.2f}%
  Miss Rate:            {summary['miss_rate']:.2f}%
  Total Requests:       {summary['total_requests']}
  Hit Count:            {summary['hits']}
  Miss Count:           {summary['misses']}

Eviction & Cleanup:
  Evictions:            {summary['evictions']}
  Eviction Rate:        {summary['eviction_rate']:.2f}%
  Expirations:          {summary['expirations']}

Operations:
  Sets:                 {summary['sets']}
  Deletes:              {summary['deletes']}
  Clears:               {summary['clears']}

Uptime:
  Created:              {summary['created_at']}
  Uptime:               {uptime}
  Uptime (seconds):     {summary['uptime_seconds']:.0f}
"""
        return report
    
    def reset(self) -> None:
        """Reset all statistics"""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'sets': 0,
            'deletes': 0,
            'clears': 0,
            'created_at': datetime.now(),
        }
        logger.info("Cache statistics reset")


class CachePerformanceMonitor:
    """
    Monitor cache performance over time.
    
    Tracks performance trends and anomalies.
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self._samples: List[Dict[str, Any]] = []
        self._interval_seconds = 60
        
        logger.debug("CachePerformanceMonitor initialized")
    
    def sample(self, stats: CacheStatistics) -> None:
        """
        Record a performance sample.
        
        Args:
            stats: CacheStatistics instance
        """
        sample = {
            'timestamp': datetime.now().isoformat(),
            'hit_rate': stats.get_hit_rate(),
            'miss_rate': stats.get_miss_rate(),
            'eviction_rate': stats.get_eviction_rate(),
            'total_requests': stats.get_total_requests(),
        }
        
        self._samples.append(sample)
        
        # Keep only last 100 samples
        if len(self._samples) > 100:
            self._samples = self._samples[-100:]
    
    def get_average_hit_rate(self) -> float:
        """
        Get average hit rate from samples.
        
        Returns:
            Average hit rate percentage
        """
        if not self._samples:
            return 0.0
        
        total = sum(s['hit_rate'] for s in self._samples)
        return total / len(self._samples)
    
    def get_trend(self) -> str:
        """
        Analyze performance trend.
        
        Returns:
            'improving', 'declining', or 'stable'
        """
        if len(self._samples) < 2:
            return 'stable'
        
        recent = self._samples[-10:] if len(self._samples) >= 10 else self._samples
        
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        avg_first = sum(s['hit_rate'] for s in first_half) / len(first_half)
        avg_second = sum(s['hit_rate'] for s in second_half) / len(second_half)
        
        if avg_second > avg_first + 1:
            return 'improving'
        elif avg_second < avg_first - 1:
            return 'declining'
        else:
            return 'stable'
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get performance monitoring report.
        
        Returns:
            Report dictionary
        """
        return {
            'sample_count': len(self._samples),
            'average_hit_rate': self.get_average_hit_rate(),
            'trend': self.get_trend(),
            'recent_samples': self._samples[-5:] if self._samples else [],
        }


__all__ = ["CacheStatistics", "CachePerformanceMonitor"]
