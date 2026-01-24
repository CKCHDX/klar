"""
KSE Web Crawler Module

Comprehensive web crawling engine for Swedish domains.
Includes fetching, parsing, deduplication, and scheduling.
"""

from kse.crawler.kse_crawler_core import (
    Crawler,
    CrawlerConfig,
    CrawlResult,
)
from kse.crawler.kse_crawler_fetcher import (
    Fetcher,
    FetchResult,
    FetchStatus,
)
from kse.crawler.kse_crawler_parser import (
    Parser,
    ParsedPage,
)
from kse.crawler.kse_crawler_scheduler import (
    CrawlScheduler,
    CrawlJob,
)
from kse.crawler.kse_crawler_limiter import (
    RateLimiter,
    RobotsTxtChecker,
)

__all__ = [
    # Core crawler
    "Crawler",
    "CrawlerConfig",
    "CrawlResult",
    # Fetching
    "Fetcher",
    "FetchResult",
    "FetchStatus",
    # Parsing
    "Parser",
    "ParsedPage",
    # Scheduling
    "CrawlScheduler",
    "CrawlJob",
    # Rate limiting
    "RateLimiter",
    "RobotsTxtChecker",
]
