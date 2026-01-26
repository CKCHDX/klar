"""kse_crawler_scheduler.py - Crawl Scheduling and Recrawling"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from kse.core import get_logger

logger = get_logger('crawler')


class CrawlScheduler:
    """Manage crawl scheduling"""
    
    def __init__(self, recrawl_interval_days: int = 7):
        self.recrawl_interval = timedelta(days=recrawl_interval_days)
        self._last_crawl: Dict[str, datetime] = {}
        logger.debug(f"CrawlScheduler initialized (interval={recrawl_interval_days}d)")
    
    def should_recrawl(self, url: str) -> bool:
        """Check if URL needs recrawling"""
        if url not in self._last_crawl:
            return True
        
        last_crawl = self._last_crawl[url]
        return datetime.now() - last_crawl > self.recrawl_interval
    
    def mark_crawled(self, url: str) -> None:
        """Mark URL as crawled"""
        self._last_crawl[url] = datetime.now()
    
    def get_recrawl_candidates(self, urls: List[str]) -> List[str]:
        """Get URLs needing recrawl"""
        return [u for u in urls if self.should_recrawl(u)]


__all__ = ["CrawlScheduler"]
