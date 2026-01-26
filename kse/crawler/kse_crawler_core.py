"""
kse_crawler_core.py - Main Web Crawler Orchestrator

Orchestrates the entire web crawling process including:
- URL queue management
- Crawl scheduling
- Domain-specific crawl state
- Error handling and recovery

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from kse.core import get_logger, KSEException, CRAWL_STATE_DIR
from kse.storage import DataSerializer
from kse.cache import CacheManager

logger = get_logger('crawler')


class CrawlerStatus(Enum):
    """Crawler operational status"""
    IDLE = 'idle'
    RUNNING = 'running'
    PAUSED = 'paused'
    STOPPED = 'stopped'
    ERROR = 'error'


class KSECrawlerException(KSEException):
    """Base crawler exception"""
    pass


class CrawlerCore:
    """
    Main web crawler orchestrator.
    
    Coordinates all crawling operations including:
    - URL queue management
    - Domain crawl scheduling
    - Crawl state persistence
    - Statistics tracking
    """
    
    def __init__(
        self,
        max_depth: int = 3,
        max_pages_per_domain: int = 10000,
        cache_manager: Optional[CacheManager] = None,
    ):
        """
        Initialize crawler core.
        
        Args:
            max_depth: Maximum crawl depth per domain
            max_pages_per_domain: Max pages to crawl per domain
            cache_manager: Optional cache for URL deduplication
        """
        if max_depth <= 0:
            raise KSECrawlerException(f"max_depth must be positive, got {max_depth}")
        
        if max_pages_per_domain <= 0:
            raise KSECrawlerException(
                f"max_pages_per_domain must be positive, got {max_pages_per_domain}"
            )
        
        self.max_depth = max_depth
        self.max_pages_per_domain = max_pages_per_domain
        self.cache = cache_manager or CacheManager(max_size=50000)
        
        # Crawler state
        self.status = CrawlerStatus.IDLE
        self.created_at = datetime.now()
        self.last_crawled = None
        
        # Crawl statistics
        self._stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'total_bytes_downloaded': 0,
            'errors_encountered': 0,
            'urls_queued': 0,
        }
        
        # Domain crawl states
        self._domain_states: Dict[str, Dict] = {}
        
        # URL cache for deduplication
        self._url_cache: Set[str] = set()
        
        logger.info(
            f"CrawlerCore initialized: max_depth={max_depth}, "
            f"max_pages={max_pages_per_domain}"
        )
    
    def start(self) -> None:
        """Start crawler"""
        if self.status == CrawlerStatus.RUNNING:
            logger.warning("Crawler already running")
            return
        
        self.status = CrawlerStatus.RUNNING
        logger.info("Crawler started")
    
    def pause(self) -> None:
        """Pause crawler"""
        if self.status != CrawlerStatus.RUNNING:
            logger.warning("Crawler not running")
            return
        
        self.status = CrawlerStatus.PAUSED
        logger.info("Crawler paused")
    
    def resume(self) -> None:
        """Resume crawler"""
        if self.status != CrawlerStatus.PAUSED:
            logger.warning("Crawler not paused")
            return
        
        self.status = CrawlerStatus.RUNNING
        logger.info("Crawler resumed")
    
    def stop(self) -> None:
        """Stop crawler"""
        self.status = CrawlerStatus.STOPPED
        self.last_crawled = datetime.now()
        logger.info("Crawler stopped")
    
    def add_domain(
        self,
        domain: str,
        priority: int = 1,
        enabled: bool = True,
    ) -> None:
        """
        Add domain to crawl queue.
        
        Args:
            domain: Domain to crawl
            priority: Crawl priority (1-10)
            enabled: Whether to crawl this domain
        """
        if domain in self._domain_states:
            logger.debug(f"Domain already exists: {domain}")
            return
        
        self._domain_states[domain] = {
            'domain': domain,
            'priority': priority,
            'enabled': enabled,
            'created_at': datetime.now().isoformat(),
            'last_crawled': None,
            'pages_crawled': 0,
            'errors': 0,
            'status': 'pending',
        }
        
        logger.info(f"Domain added: {domain} (priority={priority})")
    
    def mark_page_crawled(
        self,
        url: str,
        domain: str,
        status_code: int,
        bytes_downloaded: int = 0,
        success: bool = True,
    ) -> None:
        """
        Mark page as crawled.
        
        Args:
            url: Page URL
            domain: Domain
            status_code: HTTP status code
            bytes_downloaded: Bytes downloaded
            success: Whether crawl was successful
        """
        # Add to URL cache
        self.cache.set(url, {'crawled': True, 'timestamp': datetime.now().isoformat()})
        self._url_cache.add(url)
        
        # Update statistics
        if success:
            self._stats['pages_crawled'] += 1
        else:
            self._stats['pages_failed'] += 1
        
        self._stats['total_bytes_downloaded'] += bytes_downloaded
        
        # Update domain state
        if domain in self._domain_states:
            state = self._domain_states[domain]
            state['pages_crawled'] += 1
            state['last_crawled'] = datetime.now().isoformat()
            
            if not success:
                state['errors'] += 1
        
        logger.debug(f"Page crawled: {url} (status={status_code})")
    
    def get_status(self) -> Dict:
        """
        Get crawler status.
        
        Returns:
            Status dictionary
        """
        return {
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_crawled': self.last_crawled.isoformat() if self.last_crawled else None,
            'uptime_seconds': (datetime.now() - self.created_at).total_seconds(),
            'stats': self._stats.copy(),
            'domains_total': len(self._domain_states),
            'urls_cached': len(self._url_cache),
        }
    
    def get_domain_status(self, domain: str) -> Optional[Dict]:
        """
        Get status for specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain status or None if not found
        """
        return self._domain_states.get(domain)
    
    def get_all_domains(self) -> List[Dict]:
        """
        Get all domain states.
        
        Returns:
            List of domain states
        """
        return list(self._domain_states.values())
    
    def is_url_cached(self, url: str) -> bool:
        """
        Check if URL has been crawled.
        
        Args:
            url: URL to check
            
        Returns:
            True if cached
        """
        return self.cache.exists(url) or url in self._url_cache
    
    def get_stats(self) -> Dict:
        """
        Get crawler statistics.
        
        Returns:
            Statistics dictionary
        """
        total_pages = self._stats['pages_crawled'] + self._stats['pages_failed']
        success_rate = 0.0
        if total_pages > 0:
            success_rate = (self._stats['pages_crawled'] / total_pages) * 100
        
        avg_bytes_per_page = 0
        if self._stats['pages_crawled'] > 0:
            avg_bytes_per_page = (
                self._stats['total_bytes_downloaded'] / self._stats['pages_crawled']
            )
        
        return {
            'pages_crawled': self._stats['pages_crawled'],
            'pages_failed': self._stats['pages_failed'],
            'total_pages': total_pages,
            'success_rate': success_rate,
            'total_bytes_downloaded': self._stats['total_bytes_downloaded'],
            'avg_bytes_per_page': avg_bytes_per_page,
            'errors': self._stats['errors_encountered'],
            'urls_cached': len(self._url_cache),
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        self._stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'total_bytes_downloaded': 0,
            'errors_encountered': 0,
            'urls_queued': 0,
        }
        logger.info("Crawler statistics reset")


__all__ = ["CrawlerCore", "CrawlerStatus", "KSECrawlerException"]
