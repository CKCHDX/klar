"""
KSE URL Frontier

Manages URL crawl queue with politeness, prioritization, and deduplication.
"""

from typing import Optional, Set, List, Dict
from urllib.parse import urlparse
from collections import deque, defaultdict
import time
import logging

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class URLFrontier:
    """Manages crawl queue with per-domain politeness and prioritization."""
    
    def __init__(
        self,
        per_domain_delay: float = 1.0,
        max_queue_size: int = 100000,
    ):
        """
        Initialize URL frontier.
        
        Args:
            per_domain_delay: Seconds between requests to same domain (politeness)
            max_queue_size: Maximum URLs in queue
        """
        self.per_domain_delay = per_domain_delay
        self.max_queue_size = max_queue_size
        
        # Main queue: (priority, url)
        self.queue = deque()
        
        # Visited URLs (deduplication)
        self.visited: Set[str] = set()
        
        # URLs in queue (for fast lookup)
        self.queued: Set[str] = set()
        
        # Last crawl time per domain
        self.domain_last_crawled: Dict[str, float] = defaultdict(float)
        
        # URLs per domain (for statistics)
        self.domain_urls: Dict[str, int] = defaultdict(int)
        
        self.stats = {
            'total_added': 0,
            'total_visited': 0,
            'total_dequeued': 0,
        }
    
    def _get_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain (netloc)
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for deduplication.
        
        Args:
            url: URL string
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            # Rebuild without fragment
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized += f"?{parsed.query}"
            return normalized.lower()
        except Exception:
            return url.lower()
    
    def add_url(
        self,
        url: str,
        priority: int = 5,
    ) -> bool:
        """
        Add URL to frontier.
        
        Args:
            url: URL to add
            priority: Priority (1-10, higher = sooner)
            
        Returns:
            True if added, False if duplicate or queue full
        """
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # Normalize for deduplication
        normalized = self._normalize_url(url)
        
        # Check if already visited or queued
        if normalized in self.visited or normalized in self.queued:
            return False
        
        # Check queue size
        if len(self.queue) >= self.max_queue_size:
            logger.warning(f"URL frontier queue full ({self.max_queue_size})")
            return False
        
        # Add to queue
        domain = self._get_domain(url)
        priority = max(1, min(10, priority))  # Clamp 1-10
        
        self.queue.append((priority, url))
        self.queued.add(normalized)
        self.domain_urls[domain] += 1
        self.stats['total_added'] += 1
        
        return True
    
    def add_urls(self, urls: List[str], priority: int = 5) -> int:
        """
        Add multiple URLs.
        
        Args:
            urls: List of URLs
            priority: Priority for all URLs
            
        Returns:
            Number of URLs added
        """
        added = 0
        for url in urls:
            if self.add_url(url, priority):
                added += 1
        
        logger.info(f"Added {added}/{len(urls)} URLs to frontier")
        return added
    
    def get_next_url(self) -> Optional[str]:
        """
        Get next URL to crawl, respecting per-domain politeness.
        
        Returns:
            URL to crawl or None if queue empty or must wait
        """
        if not self.queue:
            return None
        
        current_time = time.time()
        
        # Try to find a URL respecting per-domain delay
        for _ in range(len(self.queue)):
            priority, url = self.queue.popleft()
            domain = self._get_domain(url)
            
            # Check if enough time passed since last crawl of this domain
            last_crawled = self.domain_last_crawled.get(domain, 0)
            time_since_crawl = current_time - last_crawled
            
            if time_since_crawl >= self.per_domain_delay:
                # Can crawl this URL
                normalized = self._normalize_url(url)
                self.queued.discard(normalized)
                self.domain_last_crawled[domain] = current_time
                self.stats['total_dequeued'] += 1
                
                logger.debug(f"Dequeuing: {url} (domain: {domain}, priority: {priority})")
                return url
            else:
                # Re-queue with adjusted priority
                wait_time = self.per_domain_delay - time_since_crawl
                new_priority = max(1, priority - 1)  # Lower priority after waiting
                self.queue.append((new_priority, url))
        
        # All URLs require waiting
        return None
    
    def mark_visited(self, url: str) -> None:
        """
        Mark URL as visited (successfully crawled).
        
        Args:
            url: URL that was crawled
        """
        normalized = self._normalize_url(url)
        self.visited.add(normalized)
        self.queued.discard(normalized)
        self.stats['total_visited'] += 1
    
    def mark_failed(self, url: str) -> None:
        """
        Mark URL as failed (will be retried later).
        
        Args:
            url: URL that failed
        """
        normalized = self._normalize_url(url)
        self.queued.discard(normalized)
        # Don't add to visited, allow retry
    
    def has_url_to_crawl(self) -> bool:
        """
        Check if frontier has URLs ready to crawl.
        
        Returns:
            True if URL available without waiting
        """
        return self.get_next_url() is not None
    
    def get_queue_size(self) -> int:
        """
        Get current queue size.
        
        Returns:
            Number of URLs in queue
        """
        return len(self.queue)
    
    def get_visited_count(self) -> int:
        """
        Get number of visited URLs.
        
        Returns:
            Count of visited URLs
        """
        return len(self.visited)
    
    def get_stats(self) -> Dict:
        """
        Get frontier statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'queue_size': self.get_queue_size(),
            'visited_count': self.get_visited_count(),
            'queued_count': len(self.queued),
            'domain_count': len(self.domain_urls),
            'total_added': self.stats['total_added'],
            'total_visited': self.stats['total_visited'],
            'total_dequeued': self.stats['total_dequeued'],
            'per_domain_delay': self.per_domain_delay,
        }
    
    def get_domain_stats(self) -> Dict[str, Dict]:
        """
        Get statistics per domain.
        
        Returns:
            Dictionary {domain: stats}
        """
        stats = {}
        for domain, count in self.domain_urls.items():
            last_crawled = self.domain_last_crawled.get(domain, 0)
            stats[domain] = {
                'urls_queued': count,
                'last_crawled': last_crawled,
                'time_since_crawl': time.time() - last_crawled,
            }
        
        return stats
    
    def clear(self) -> None:
        """
        Clear frontier (for testing).
        """
        self.queue.clear()
        self.visited.clear()
        self.queued.clear()
        self.domain_last_crawled.clear()
        self.domain_urls.clear()
        logger.warning("URL frontier cleared")
