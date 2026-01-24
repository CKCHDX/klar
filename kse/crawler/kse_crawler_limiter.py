"""
Rate Limiting & Robots.txt Compliance

Handles per-domain rate limiting and robots.txt parsing.
"""

import time
import urllib.robotparser
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class RateLimiter:
    """
    Per-domain rate limiting.
    
    Ensures respectful crawling with configurable delays.
    """
    
    def __init__(
        self,
        default_delay_seconds: float = 1.0,
        min_delay: float = 0.1,
        max_delay: float = 10.0
    ):
        """
        Initialize rate limiter.
        
        Args:
            default_delay_seconds: Default delay between requests
            min_delay: Minimum allowed delay
            max_delay: Maximum allowed delay
        """
        self.default_delay = default_delay_seconds
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time: Dict[str, float] = {}  # domain -> timestamp
        self._domain_delays: Dict[str, float] = {}      # domain -> custom delay
    
    def set_domain_delay(self, domain: str, delay: float) -> None:
        """Set custom delay for specific domain.
        
        Args:
            domain: Domain name (e.g., 'example.com')
            delay: Delay in seconds
        """
        delay = max(self.min_delay, min(delay, self.max_delay))
        self._domain_delays[domain] = delay
        logger.debug(f"Set delay for {domain}: {delay}s")
    
    def get_delay(self, domain: str) -> float:
        """Get delay for domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Delay in seconds
        """
        return self._domain_delays.get(domain, self.default_delay)
    
    def wait_if_needed(self, domain: str) -> float:
        """Wait if necessary before making request.
        
        Args:
            domain: Domain name
        
        Returns:
            Actual wait time in seconds
        """
        delay = self.get_delay(domain)
        last_request = self._last_request_time.get(domain, 0)
        elapsed = time.time() - last_request
        
        if elapsed < delay:
            wait_time = delay - elapsed
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            return wait_time
        
        return 0.0
    
    def record_request(self, domain: str) -> None:
        """Record that a request was made.
        
        Args:
            domain: Domain name
        """
        self._last_request_time[domain] = time.time()
    
    def reset_domain(self, domain: str) -> None:
        """Reset rate limiter for domain.
        
        Args:
            domain: Domain name
        """
        self._last_request_time.pop(domain, None)
        logger.debug(f"Reset rate limiter for {domain}")


class RobotsTxtChecker:
    """
    Robots.txt parser and compliance checker.
    
    Respects robots.txt directives for crawling.
    """
    
    def __init__(self, user_agent: str = "KSE-Bot/1.0"):
        """
        Initialize robots.txt checker.
        
        Args:
            user_agent: User-Agent for robots.txt matching
        """
        self.user_agent = user_agent
        self._cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self._crawl_delays: Dict[str, float] = {}  # domain -> crawl-delay
    
    def _get_robots_url(self, domain_url: str) -> str:
        """Get robots.txt URL for domain.
        
        Args:
            domain_url: Full domain URL (e.g., 'https://example.com')
        
        Returns:
            URL to robots.txt
        """
        if not domain_url.startswith(('http://', 'https://')):
            domain_url = f'https://{domain_url}'
        
        return urljoin(domain_url, '/robots.txt')
    
    def fetch_robots_txt(self, domain_url: str, timeout: float = 10.0) -> bool:
        """Fetch and parse robots.txt for domain.
        
        Args:
            domain_url: Domain URL
            timeout: Request timeout in seconds
        
        Returns:
            True if robots.txt was fetched, False otherwise
        """
        parsed = urlparse(domain_url if domain_url.startswith('http') else f'https://{domain_url}')
        domain = parsed.netloc or domain_url
        
        if domain in self._cache:
            return True
        
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(self._get_robots_url(domain_url))
            rp.read()  # This will use urllib to fetch
            
            # Extract crawl-delay if available
            if hasattr(rp, 'crawl_delay'):
                for ua in [self.user_agent, '*']:
                    delay = rp.crawl_delay(ua)
                    if delay:
                        self._crawl_delays[domain] = delay
                        break
            
            self._cache[domain] = rp
            logger.debug(f"Fetched robots.txt for {domain}")
            return True
        
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
            return False
    
    def can_fetch(self, domain_url: str, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt.
        
        Args:
            domain_url: Domain URL
            url: Full URL to check
        
        Returns:
            True if URL can be fetched
        """
        parsed = urlparse(domain_url if domain_url.startswith('http') else f'https://{domain_url}')
        domain = parsed.netloc or domain_url
        
        # If robots.txt not fetched, allow by default
        if domain not in self._cache:
            self.fetch_robots_txt(domain_url)
        
        if domain not in self._cache:
            return True
        
        try:
            rp = self._cache[domain]
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow on error
    
    def get_crawl_delay(self, domain_url: str) -> Optional[float]:
        """Get crawl-delay from robots.txt.
        
        Args:
            domain_url: Domain URL
        
        Returns:
            Crawl delay in seconds, or None
        """
        parsed = urlparse(domain_url if domain_url.startswith('http') else f'https://{domain_url}')
        domain = parsed.netloc or domain_url
        
        return self._crawl_delays.get(domain)
    
    def clear_cache(self) -> None:
        """Clear robots.txt cache."""
        self._cache.clear()
        self._crawl_delays.clear()
        logger.debug("Cleared robots.txt cache")
