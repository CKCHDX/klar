"""
KSE Web Crawler Module

Provides HTTP crawling, HTML parsing, link extraction, and content processing
for the Klar Search Engine.
"""

from .kse_crawler import KSECrawler, CrawlResult
from .kse_crawler_manager import KSECrawlerManager
from .kse_url_frontier import URLFrontier
from .kse_parser import HTMLParser, extract_links, extract_text

__version__ = "1.0.0"
__all__ = [
    "KSECrawler",
    "CrawlResult",
    "KSECrawlerManager",
    "URLFrontier",
    "HTMLParser",
    "extract_links",
    "extract_text",
]
