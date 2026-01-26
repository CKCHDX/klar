"""kse_crawler_monitor.py - Crawler Performance Monitoring

Monitors crawler health and performance:
- Crawl speed
- Success rate
- Error tracking
- Domain health
"""

import logging
from typing import Dict
import time

from kse.core import get_logger

logger = get_logger('monitoring')


class CrawlerMonitor:
    """Monitor crawler performance"""
    
    def __init__(self):
        """Initialize crawler monitor"""
        self.start_time = time.time()
        self.stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'total_bytes': 0,
            'errors': {},
        }
        logger.debug("CrawlerMonitor initialized")
    
    def record_page_crawl(self, 
                         url: str,
                         success: bool,
                         bytes_downloaded: int = 0,
                         error: str = None) -> None:
        """Record page crawl
        
        Args:
            url: URL crawled
            success: Whether crawl succeeded
            bytes_downloaded: Bytes downloaded
            error: Error message if failed
        """
        if success:
            self.stats['pages_crawled'] += 1
            self.stats['total_bytes'] += bytes_downloaded
        else:
            self.stats['pages_failed'] += 1
            if error:
                error_type = error.split(':')[0]
                self.stats['errors'][error_type] = self.stats['errors'].get(error_type, 0) + 1
    
    def get_crawl_speed(self) -> float:
        """Get pages per second
        
        Returns:
            Pages per second
        """
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        
        total = self.stats['pages_crawled'] + self.stats['pages_failed']
        return total / elapsed
    
    def get_success_rate(self) -> float:
        """Get success rate percentage
        
        Returns:
            Success rate (0-100)
        """
        total = self.stats['pages_crawled'] + self.stats['pages_failed']
        if total == 0:
            return 0
        
        return (self.stats['pages_crawled'] / total) * 100
    
    def get_download_speed(self) -> float:
        """Get download speed (MB/s)
        
        Returns:
            MB per second
        """
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        
        mb_downloaded = self.stats['total_bytes'] / (1024 * 1024)
        return mb_downloaded / elapsed
    
    def get_crawler_health(self) -> Dict:
        """Get overall crawler health
        
        Returns:
            Health status
        """
        health = 'healthy'
        if self.get_success_rate() < 80:
            health = 'warning'
        if self.get_success_rate() < 50:
            health = 'critical'
        
        return {
            'status': health,
            'pages_crawled': self.stats['pages_crawled'],
            'pages_failed': self.stats['pages_failed'],
            'success_rate': round(self.get_success_rate(), 2),
            'pages_per_second': round(self.get_crawl_speed(), 2),
            'mb_per_second': round(self.get_download_speed(), 2),
            'top_errors': self._get_top_errors(),
        }
    
    def _get_top_errors(self) -> Dict[str, int]:
        """Get top error types"""
        sorted_errors = sorted(
            self.stats['errors'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_errors[:5])


__all__ = ["CrawlerMonitor"]
