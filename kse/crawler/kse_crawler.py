"""
KSE Core Web Crawler

Fetches URLs, handles errors, and returns crawl results.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import hashlib
import logging

from kse.core import KSELogger
from .kse_parser import HTMLParser

logger = KSELogger.get_logger(__name__)


@dataclass
class CrawlResult:
    """Result of a single crawl operation."""
    url: str
    success: bool
    status_code: Optional[int]
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
    content_hash: Optional[str]
    language: Optional[str]
    links: list
    duration_ms: float
    error_message: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: int = 0


class KSECrawler:
    """Core web crawler for KSE."""
    
    def __init__(
        self,
        user_agent: str = None,
        timeout: int = 10,
        max_retries: int = 3,
        max_content_size: int = 5_000_000,  # 5MB
    ):
        """
        Initialize crawler.
        
        Args:
            user_agent: User agent string
            timeout: Request timeout in seconds
            max_retries: Max retries on failure
            max_content_size: Maximum page size to download
        """
        self.user_agent = user_agent or self._get_default_user_agent()
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_content_size = max_content_size
        
        # Setup requests session with retries
        self.session = self._setup_session()
    
    def _get_default_user_agent(self) -> str:
        """
        Get default user agent.
        
        Returns:
            User agent string
        """
        return (
            "Mozilla/5.0 (compatible; KlarSearchEngine/1.0; "
            "+https://klar.oscyra.solutions)"
        )
    
    def _setup_session(self) -> requests.Session:
        """
        Setup requests session with retry strategy.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Retry strategy
        retry = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=['GET', 'HEAD'],
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
        })
        
        return session
    
    def crawl(self, url: str) -> CrawlResult:
        """
        Crawl a single URL.
        
        Args:
            url: URL to crawl
            
        Returns:
            CrawlResult with page data
        """
        start_time = time.time()
        
        result = CrawlResult(
            url=url,
            success=False,
            status_code=None,
            title=None,
            description=None,
            content=None,
            content_hash=None,
            language=None,
            links=[],
            duration_ms=0,
            error_message=None,
            content_type=None,
            size_bytes=0,
        )
        
        try:
            logger.info(f"Crawling: {url}")
            
            # Fetch URL
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True,
            )
            
            result.status_code = response.status_code
            result.content_type = response.headers.get('Content-Type', '')
            
            # Check if HTML
            if 'text/html' not in result.content_type.lower():
                result.error_message = f"Not HTML: {result.content_type}"
                logger.warning(result.error_message)
                return result
            
            # Limit content size
            if int(response.headers.get('Content-Length', 0)) > self.max_content_size:
                result.error_message = "Content too large"
                logger.warning(f"{url}: Content too large")
                return result
            
            # Read content
            content = response.content[:self.max_content_size]
            result.size_bytes = len(content)
            
            # Decode HTML
            try:
                html = content.decode('utf-8', errors='ignore')
            except Exception as e:
                result.error_message = f"Decode error: {e}"
                logger.warning(result.error_message)
                return result
            
            result.content = html
            
            # Hash content
            result.content_hash = hashlib.sha256(content).hexdigest()
            
            # Parse HTML
            parser = HTMLParser(html, url)
            
            result.title = parser.get_title()
            result.description = parser.get_description()
            result.language = parser.get_language() or 'sv'
            
            # Extract links
            links = parser.get_links()
            result.links = links
            
            # Mark success
            if result.status_code == 200:
                result.success = True
                logger.info(
                    f"✅ Crawled: {url} ({result.size_bytes} bytes, "
                    f"{len(links)} links)"
                )
            else:
                result.error_message = f"Status {result.status_code}"
                logger.warning(f"Non-200 status: {result.status_code}")
        
        except requests.exceptions.Timeout:
            result.error_message = "Timeout"
            logger.warning(f"Timeout: {url}")
        
        except requests.exceptions.ConnectionError as e:
            result.error_message = "Connection error"
            logger.warning(f"Connection error: {e}")
        
        except requests.exceptions.RequestException as e:
            result.error_message = str(e)[:100]
            logger.warning(f"Request error: {e}")
        
        except Exception as e:
            result.error_message = str(e)[:100]
            logger.error(f"Unexpected error crawling {url}: {e}")
        
        finally:
            result.duration_ms = (time.time() - start_time) * 1000
        
        return result
    
    def crawl_batch(self, urls: list, delay: float = 1.0) -> list:
        """
        Crawl multiple URLs with delay between requests.
        
        Args:
            urls: List of URLs to crawl
            delay: Delay between requests in seconds
            
        Returns:
            List of CrawlResult objects
        """
        results = []
        
        for i, url in enumerate(urls):
            result = self.crawl(url)
            results.append(result)
            
            # Delay between requests (except last)
            if i < len(urls) - 1:
                time.sleep(delay)
        
        return results
    
    def close(self) -> None:
        """
        Close session (cleanup).
        """
        self.session.close()
        logger.info("Crawler session closed")
