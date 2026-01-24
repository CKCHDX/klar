"""
Core Web Crawler

Main crawling engine orchestrating fetch, parse, and storage.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import time

from kse.crawler.kse_crawler_fetcher import Fetcher, FetchStatus
from kse.crawler.kse_crawler_parser import Parser, ParsedPage
from kse.crawler.kse_crawler_scheduler import CrawlScheduler, CrawlJob
from kse.crawler.kse_crawler_limiter import RateLimiter, RobotsTxtChecker
from kse.core import KSELogger, KSEException
from kse.database import Repository

logger = KSELogger.get_logger(__name__)


class CrawlResult(Enum):
    """Result of crawling a domain."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    BLOCKED_BY_ROBOTS = "blocked_by_robots"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"


@dataclass
class CrawlerConfig:
    """Crawler configuration."""
    user_agent: str = "KSE-Bot/1.0 (+https://klar.se/bot)"
    timeout_seconds: float = 30.0
    max_content_size_mb: float = 50.0
    default_delay_seconds: float = 1.0
    max_pages_per_domain: int = 1000
    respect_robots_txt: bool = True
    follow_redirects: bool = True
    max_retries: int = 3
    backoff_factor: float = 0.5


class Crawler:
    """
    Web crawler for Swedish domains.
    
    Features:
    - Respectful crawling with rate limiting
    - Robots.txt compliance
    - Error handling and retries
    - Change detection
    """
    
    def __init__(
        self,
        db_repository: Repository,
        config: Optional[CrawlerConfig] = None
    ):
        """
        Initialize crawler.
        
        Args:
            db_repository: Database repository
            config: Crawler configuration
        """
        self.db = db_repository
        self.config = config or CrawlerConfig()
        
        # Initialize components
        self.fetcher = Fetcher(
            user_agent=self.config.user_agent,
            timeout_seconds=self.config.timeout_seconds,
            max_content_size_mb=self.config.max_content_size_mb,
            max_retries=self.config.max_retries,
            backoff_factor=self.config.backoff_factor
        )
        self.parser = Parser()
        self.scheduler = CrawlScheduler()
        self.rate_limiter = RateLimiter(
            default_delay_seconds=self.config.default_delay_seconds
        )
        self.robots_checker = RobotsTxtChecker(
            user_agent=self.config.user_agent
        )
        
        self._crawl_stats = {
            'domains_crawled': 0,
            'pages_crawled': 0,
            'pages_failed': 0,
            'total_time_ms': 0,
            'errors': [],
        }
    
    def schedule_domain_crawl(
        self,
        domain_id: int,
        domain_name: str,
        domain_url: str,
        priority: int = 0
    ) -> bool:
        """Schedule a domain for crawling.
        
        Args:
            domain_id: Domain ID from database
            domain_name: Domain name
            domain_url: Domain URL
            priority: Priority level
        
        Returns:
            True if scheduled successfully
        """
        job = self.scheduler.add_job(
            domain_id=domain_id,
            domain_name=domain_name,
            domain_url=domain_url,
            priority=priority
        )
        
        return job is not None
    
    def _handle_robots_txt(self, domain_url: str) -> Optional[float]:
        """Handle robots.txt checking and rate limiting.
        
        Args:
            domain_url: Domain URL
        
        Returns:
            Custom delay from robots.txt, or None
        """
        if not self.config.respect_robots_txt:
            return None
        
        # Fetch robots.txt
        self.robots_checker.fetch_robots_txt(domain_url)
        
        # Get custom crawl-delay
        delay = self.robots_checker.get_crawl_delay(domain_url)
        if delay:
            self.rate_limiter.set_domain_delay(domain_url, delay)
            logger.debug(f"Set rate limit for {domain_url}: {delay}s (from robots.txt)")
        
        return delay
    
    def crawl_domain(
        self,
        domain_id: int,
        domain_url: str,
        max_pages: Optional[int] = None
    ) -> Dict:
        """Crawl a single domain.
        
        Args:
            domain_id: Domain ID
            domain_url: Domain URL
            max_pages: Maximum pages to crawl (None for config default)
        
        Returns:
            Dictionary with crawl statistics
        """
        start_time = time.time()
        max_pages = max_pages or self.config.max_pages_per_domain
        
        result = {
            'domain_id': domain_id,
            'domain_url': domain_url,
            'pages_crawled': 0,
            'pages_failed': 0,
            'status': CrawlResult.SUCCESS,
            'errors': [],
            'start_time': start_time,
            'end_time': None,
            'duration_seconds': 0,
        }
        
        try:
            logger.info(f"Starting crawl of {domain_url}")
            
            # Check robots.txt
            self._handle_robots_txt(domain_url)
            
            # Rate limiting
            from urllib.parse import urlparse
            parsed = urlparse(domain_url if domain_url.startswith('http') else f'https://{domain_url}')
            domain_key = parsed.netloc or domain_url
            
            self.rate_limiter.wait_if_needed(domain_key)
            self.rate_limiter.record_request(domain_key)
            
            # Fetch homepage
            fetch_url = domain_url if domain_url.startswith('http') else f'https://{domain_url}'
            fetch_result = self.fetcher.fetch(fetch_url)
            
            if not fetch_result.is_success:
                result['status'] = CrawlResult.FAILED
                result['errors'].append(fetch_result.error_message or 'Unknown error')
                logger.warning(f"Failed to crawl {domain_url}: {fetch_result.error_message}")
                return result
            
            # Parse homepage
            page = self.parser.parse(
                fetch_url,
                fetch_result.content,
                fetch_result.encoding
            )
            
            # Store in database
            try:
                page_id = self.db.add_page(
                    domain_id=domain_id,
                    url=page.url,
                    title=page.title,
                    description=page.description,
                    content_text=page.text_content,
                    status_code=fetch_result.status_code,
                    content_type=fetch_result.content_type,
                    language=page.language or 'sv',
                    inbound_links=0,
                    outbound_links=len(page.outbound_links),
                )
                result['pages_crawled'] += 1
                logger.debug(f"Stored page: {page.url}")
            except Exception as e:
                result['pages_failed'] += 1
                result['errors'].append(f"Database error: {e}")
                logger.error(f"Failed to store page {page.url}: {e}")
            
            # Set status
            if result['pages_crawled'] == 0 and result['pages_failed'] > 0:
                result['status'] = CrawlResult.FAILED
            elif result['pages_failed'] > 0:
                result['status'] = CrawlResult.PARTIAL_SUCCESS
            
            logger.info(f"Completed crawl of {domain_url}: {result['pages_crawled']} pages")
        
        except Exception as e:
            result['status'] = CrawlResult.FAILED
            result['errors'].append(str(e))
            logger.error(f"Crawl error for {domain_url}: {e}", exc_info=True)
        
        finally:
            result['end_time'] = time.time()
            result['duration_seconds'] = result['end_time'] - result['start_time']
            
            # Update stats
            self._crawl_stats['domains_crawled'] += 1
            self._crawl_stats['pages_crawled'] += result['pages_crawled']
            self._crawl_stats['pages_failed'] += result['pages_failed']
            self._crawl_stats['total_time_ms'] += result['duration_seconds'] * 1000
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get crawl statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            **self._crawl_stats,
            'queue_stats': self.scheduler.get_queue_stats(),
        }
    
    def close(self) -> None:
        """Close crawler resources."""
        self.fetcher.close()
        logger.info("Crawler closed")
