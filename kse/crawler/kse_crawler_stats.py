"""kse_crawler_stats.py - Crawling Statistics and Reporting"""

import logging
from typing import Dict, Any
from datetime import datetime

from kse.core import get_logger

logger = get_logger('crawler')


class CrawlerStatistics:
    """Track crawling statistics"""
    
    def __init__(self):
        self._stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'bytes_downloaded': 0,
            'errors': 0,
            'start_time': datetime.now(),
        }
        logger.debug("CrawlerStatistics initialized")
    
    def record_page(self, size: int, success: bool = True) -> None:
        """Record page crawl"""
        if success:
            self._stats['pages_crawled'] += 1
        else:
            self._stats['pages_failed'] += 1
        self._stats['bytes_downloaded'] += size
    
    def record_error(self) -> None:
        """Record error"""
        self._stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        total = self._stats['pages_crawled'] + self._stats['pages_failed']
        success_rate = 0 if total == 0 else (self._stats['pages_crawled'] / total) * 100
        
        return {
            'pages_crawled': self._stats['pages_crawled'],
            'pages_failed': self._stats['pages_failed'],
            'success_rate': success_rate,
            'bytes_downloaded': self._stats['bytes_downloaded'],
            'errors': self._stats['errors'],
        }


__all__ = ["CrawlerStatistics"]
