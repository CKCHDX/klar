"""
kse/crawler/__init__.py - Web Crawler Public API

Components:
  - CrawlerCore: Main orchestrator
  - URLProcessor: URL normalization
  - URLQueue: Smart queue management
  - HTTPClient: HTTP requests with retries
  - HTMLExtractor: HTML parsing
  - RobotsParser: robots.txt compliance
  - LinkExtractor: Link discovery
  - PaginationHandler: Pagination detection
  - ChangeDetector: Content change detection
  - CrawlScheduler: Crawl scheduling
  - CrawlerStatistics: Statistics tracking
  - CrawlerResilience: Error recovery

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_crawler_core import CrawlerCore, CrawlerStatus, KSECrawlerException
from .kse_url_processor import URLProcessor, KSEURLException
from .kse_url_queue import URLQueue, QueueStrategy
from .kse_http_client import HTTPClient, KSEHTTPException
from .kse_html_extractor import HTMLExtractor, KSEHTMLException
from .kse_robots_parser import RobotsParser
from .kse_link_extractor import LinkExtractor
from .kse_pagination_handler import PaginationHandler
from .kse_change_detection import ChangeDetector
from .kse_crawler_scheduler import CrawlScheduler
from .kse_crawler_stats import CrawlerStatistics
from .kse_crawler_resilience import CrawlerResilience

__all__ = [
    # Core
    "CrawlerCore",
    "CrawlerStatus",
    
    # URL Management
    "URLProcessor",
    "URLQueue",
    "QueueStrategy",
    
    # HTTP & Parsing
    "HTTPClient",
    "HTMLExtractor",
    "RobotsParser",
    
    # Link Management
    "LinkExtractor",
    "PaginationHandler",
    
    # Monitoring
    "ChangeDetector",
    "CrawlScheduler",
    "CrawlerStatistics",
    "CrawlerResilience",
    
    # Exceptions
    "KSECrawlerException",
    "KSEURLException",
    "KSEHTTPException",
    "KSEHTMLException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Crawler Layer

1. Basic crawler:
    from kse.crawler import CrawlerCore
    
    crawler = CrawlerCore(max_depth=3, max_pages_per_domain=10000)
    crawler.start()
    crawler.add_domain('example.com')
    stats = crawler.get_stats()

2. URL processing:
    from kse.crawler import URLProcessor
    
    processor = URLProcessor()
    normalized = processor.normalize('https://EXAMPLE.COM:443/path?b=2&a=1')
    domain = processor.extract_domain(normalized)

3. URL queue:
    from kse.crawler import URLQueue
    
    queue = URLQueue(strategy='priority')
    queue.add('https://example.com', 'example.com', priority=10)
    url, domain, priority = queue.get()

4. HTTP requests:
    from kse.crawler import HTTPClient
    
    client = HTTPClient(timeout=10, max_retries=3)
    content, status, headers = client.get('https://example.com')

5. HTML parsing:
    from kse.crawler import HTMLExtractor
    
    extractor = HTMLExtractor()
    text = extractor.extract_text(content)
    metadata = extractor.extract_metadata(content, url)
    links = extractor.extract_links(content, url)

ARCHITECTURE:

kse/crawler/
├── kse_crawler_core.py         Main orchestrator
├── kse_url_processor.py        URL normalization
├── kse_url_queue.py            Queue management
├── kse_http_client.py          HTTP requests
├── kse_html_extractor.py       HTML parsing
├── kse_robots_parser.py        robots.txt
├── kse_link_extractor.py       Link discovery
├── kse_pagination_handler.py   Pagination
├── kse_change_detection.py     Change detection
├── kse_crawler_scheduler.py    Scheduling
├── kse_crawler_stats.py        Statistics
├── kse_crawler_resilience.py   Error recovery
└── __init__.py                 Public API

INTEGRATION:

- Phase 3 (cache): Uses cache for URL deduplication
- Phase 5 (nlp): Will process crawled content
- Phase 6 (indexing): Will index crawled pages
"""
