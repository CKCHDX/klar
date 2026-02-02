"""
KSE Crawler Core - Main crawler orchestrator for Klar Search Engine
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Set
from pathlib import Path
from kse.core.kse_logger import get_logger
from kse.core.kse_exceptions import CrawlerError, DomainNotAllowedError
from kse.core.kse_constants import CrawlStatus
from kse.crawler.kse_http_client import HTTPClient
from kse.crawler.kse_html_extractor import HTMLExtractor
from kse.crawler.kse_url_processor import URLProcessor
from kse.crawler.kse_robots_parser import RobotsParser
from kse.storage.kse_storage_manager import StorageManager

logger = get_logger(__name__, "crawler.log")


class CrawlerCore:
    """Main web crawler orchestrator"""
    
    def __init__(
        self,
        storage_manager: StorageManager,
        allowed_domains: List[str],
        user_agent: str,
        crawl_delay: float = 1.0,
        timeout: int = 10,
        max_retries: int = 3,
        crawl_depth: int = 50,
        respect_robots: bool = True,
        dynamic_speed: bool = False,
        max_workers: int = 5
    ):
        """
        Initialize crawler
        
        Args:
            storage_manager: Storage manager instance
            allowed_domains: List of allowed domains to crawl
            user_agent: User agent string
            crawl_delay: Delay between requests in seconds
            timeout: Request timeout
            max_retries: Maximum retries per request
            crawl_depth: Maximum pages to crawl per domain
            respect_robots: Whether to respect robots.txt
            dynamic_speed: Whether to dynamically adjust crawl speed from robots.txt
            max_workers: Maximum number of concurrent threads for parallel crawling
        """
        self.storage = storage_manager
        self.allowed_domains = set(allowed_domains)
        self.crawl_delay = crawl_delay
        self.crawl_depth = crawl_depth
        self.respect_robots = respect_robots
        self.dynamic_speed = dynamic_speed
        self.max_workers = max_workers
        
        # Initialize components
        self.http_client = HTTPClient(user_agent, timeout, max_retries)
        self.html_extractor = HTMLExtractor()
        self.url_processor = URLProcessor()
        self.robots_parser = RobotsParser(user_agent)
        
        # Thread-safe crawl state
        self.crawled_pages: List[Dict] = []
        self.domain_status: Dict[str, Dict] = {}
        self._state_lock = threading.Lock()  # Lock for thread-safe state updates
        
        # Load previous state if exists
        self._load_crawl_state()
        
        logger.info(f"Crawler initialized for {len(self.allowed_domains)} domains")
        if dynamic_speed:
            logger.info("Dynamic speed adjustment enabled")
        if max_workers > 1:
            logger.info(f"Multi-threaded crawling enabled with {max_workers} workers")
    
    def _load_crawl_state(self) -> None:
        """Load previous crawl state from storage"""
        try:
            # Load visited URLs
            visited = self.storage.load_crawl_state("visited_urls")
            if visited:
                self.url_processor.load_visited_urls(visited)
            
            # Load domain status
            status = self.storage.load_crawl_state("domain_status")
            if status:
                self.domain_status = status
            
            logger.info(f"Loaded crawl state: {self.url_processor.get_visited_count()} visited URLs")
        except Exception as e:
            logger.warning(f"Failed to load crawl state: {e}")
    
    def _save_crawl_state(self) -> None:
        """Save current crawl state to storage"""
        try:
            # Save visited URLs
            visited_urls = self.url_processor.get_visited_urls()
            self.storage.save_crawl_state(visited_urls, "visited_urls")
            
            # Save domain status
            self.storage.save_crawl_state(self.domain_status, "domain_status")
            
            logger.debug("Crawl state saved")
        except Exception as e:
            logger.error(f"Failed to save crawl state: {e}")
    
    def crawl_domain(
        self,
        domain: str,
        start_url: Optional[str] = None,
        start_urls: Optional[List[str]] = None,
        force_ignore_robots: bool = False
    ) -> Dict:
        """
        Crawl a single domain
        
        Args:
            domain: Domain name to crawl
            start_url: Starting URL (defaults to https://domain)
            start_urls: Optional list of seed URLs to try first
            force_ignore_robots: If True, ignore robots.txt for this domain crawl
        
        Returns:
            Dictionary with crawl statistics
        """
        if domain not in self.allowed_domains:
            raise DomainNotAllowedError(f"Domain not in allowed list: {domain}")
        
        # Normalize domain
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Build seed URL list
        seed_urls: List[str] = []
        if start_urls:
            seed_urls.extend([u for u in start_urls if u])

        # Set default start URL if none provided
        if not start_url:
            start_url = f"https://{domain}"

        # Add common variants if not already present
        if start_url not in seed_urls:
            seed_urls.append(start_url)
        if not start_url.startswith("http://"):
            http_variant = f"http://{domain}"
            if http_variant not in seed_urls:
                seed_urls.append(http_variant)
        # Only add www variant for apex domains (e.g., example.com)
        if domain.count('.') == 1:
            www_variant = f"https://www.{domain}"
            if www_variant not in seed_urls:
                seed_urls.append(www_variant)
        
        logger.info(f"Starting crawl of {domain} from {seed_urls[0]}")
        
        # Get domain-level crawl delay (static for entire domain crawl)
        domain_crawl_delay = self.crawl_delay
        if self.dynamic_speed:
            from urllib.parse import urlparse
            parsed = urlparse(start_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_delay = self.robots_parser.get_crawl_delay(base_url)
            if robots_delay:
                domain_crawl_delay = robots_delay
                logger.info(f"Using robots.txt crawl delay for {domain}: {robots_delay}s")
            else:
                logger.info(f"No robots.txt delay found for {domain}, using default: {domain_crawl_delay}s")
        
        # Initialize domain status
        self.domain_status[domain] = {
            "status": CrawlStatus.IN_PROGRESS.value,
            "pages_crawled": 0,
            "pages_failed": 0,
            "start_time": time.time(),
            "last_crawl": None,
            "crawl_delay": domain_crawl_delay
        }
        
        # URL queue for this domain
        url_queue = seed_urls.copy()
        crawled_count = 0
        failed_count = 0
        
        try:
            while url_queue and crawled_count < self.crawl_depth:
                current_url = url_queue.pop(0)
                
                # Skip if already visited
                if self.url_processor.is_duplicate(current_url):
                    continue
                
                # Check if URL is from this domain
                url_domain = self.url_processor.get_domain(current_url)
                if url_domain and url_domain != domain:
                    continue
                
                # Check robots.txt
                respect_robots = False if force_ignore_robots else self.respect_robots
                if not self.robots_parser.can_fetch(current_url, respect_robots):
                    logger.warning(f"⚠️  SKIPPED: {current_url} - Blocked by robots.txt")
                    failed_count += 1
                    continue
                
                # Crawl the page
                try:
                    logger.info(f"Crawling [{crawled_count + 1}/{self.crawl_depth}]: {current_url}")
                    
                    # Fetch page
                    try:
                        html, status_code, headers = self.http_client.get(current_url)
                    except Exception as fetch_error:
                        logger.error(f"HTTP fetch failed for {current_url}: {fetch_error}")
                        failed_count += 1
                        continue
                    
                    # Extract content
                    try:
                        content = self.html_extractor.extract_content(html, current_url)
                    except Exception as extract_error:
                        logger.error(f"Content extraction failed for {current_url}: {extract_error}")
                        failed_count += 1
                        continue
                    
                    # Store page data (thread-safe)
                    page_data = {
                        'url': current_url,
                        'domain': domain,
                        'title': content['title'],
                        'description': content['description'],
                        'content': content['content'],
                        'keywords': content['keywords'],
                        'links': content['links'],
                        'status_code': status_code,
                        'crawl_time': time.time()
                    }
                    
                    with self._state_lock:
                        self.crawled_pages.append(page_data)
                    
                    # Mark as visited
                    self.url_processor.mark_visited(current_url)
                    crawled_count += 1
                    
                    # Add new links to queue (only from same domain)
                    for link in content['links']:
                        link_domain = self.url_processor.get_domain(link)
                        if link_domain == domain and not self.url_processor.is_duplicate(link):
                            url_queue.append(link)
                    
                    # Save state periodically
                    if crawled_count % 10 == 0:
                        self._save_crawl_state()
                    
                    # Respect domain-level crawl delay
                    time.sleep(domain_crawl_delay)
                
                except Exception as e:
                    logger.error(f"Failed to crawl {current_url}: {e}")
                    failed_count += 1
                    continue
            
            # Update domain status (thread-safe)
            with self._state_lock:
                self.domain_status[domain].update({
                    "status": CrawlStatus.COMPLETED.value,
                    "pages_crawled": crawled_count,
                    "pages_failed": failed_count,
                    "last_crawl": time.time(),
                    "end_time": time.time()
                })
            
            # Save final state
            self._save_crawl_state()
            
            if crawled_count == 0:
                logger.warning(f"⚠️  NO PAGES CRAWLED from {domain}! Total URLs checked: {crawled_count + failed_count}, Failed: {failed_count}")
                if failed_count > 0:
                    logger.warning(f"   Reason: {failed_count} URLs were blocked by robots.txt or failed to fetch")
            else:
                logger.info(f"✓ Completed crawl of {domain}: {crawled_count} pages, {failed_count} failed")
            
            return self.domain_status[domain]
        
        except Exception as e:
            logger.error(f"Crawl failed for {domain}: {e}")
            self.domain_status[domain]["status"] = CrawlStatus.FAILED.value
            self._save_crawl_state()
            raise CrawlerError(f"Failed to crawl {domain}: {e}")
    
    def crawl_all_domains(self, use_threading: bool = True) -> Dict[str, Dict]:
        """
        Crawl all allowed domains with optional multi-threading
        
        Args:
            use_threading: If True and max_workers > 1, crawl domains in parallel
        
        Returns:
            Dictionary of domain crawl results
        """
        logger.info(f"Starting crawl of {len(self.allowed_domains)} domains")
        
        # Use multi-threading if enabled and multiple workers configured
        if use_threading and self.max_workers > 1:
            return self._crawl_all_domains_threaded()
        else:
            return self._crawl_all_domains_sequential()
    
    def _crawl_all_domains_sequential(self) -> Dict[str, Dict]:
        """Crawl all domains sequentially (original behavior)"""
        results = {}
        
        for domain in self.allowed_domains:
            try:
                result = self.crawl_domain(domain)
                results[domain] = result
            except Exception as e:
                logger.error(f"Failed to crawl {domain}: {e}")
                results[domain] = {
                    "status": CrawlStatus.FAILED.value,
                    "error": str(e)
                }
        
        logger.info(f"Completed crawl of all domains")
        return results
    
    def _crawl_all_domains_threaded(self) -> Dict[str, Dict]:
        """Crawl all domains in parallel using thread pool"""
        logger.info(f"Starting parallel crawl with {self.max_workers} workers")
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all domain crawl tasks
            future_to_domain = {
                executor.submit(self.crawl_domain, domain): domain
                for domain in self.allowed_domains
            }
            
            # Process completed tasks
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    results[domain] = result
                    logger.info(f"✓ Completed parallel crawl of {domain}")
                except Exception as e:
                    logger.error(f"Failed to crawl {domain}: {e}")
                    results[domain] = {
                        "status": CrawlStatus.FAILED.value,
                        "error": str(e)
                    }
        
        logger.info(f"Completed parallel crawl of all domains")
        return results
    
    def get_crawled_pages(self) -> List[Dict]:
        """
        Get all crawled pages
        
        Returns:
            List of crawled page data
        """
        return self.crawled_pages.copy()
    
    def get_crawl_stats(self) -> Dict:
        """
        Get crawl statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_pages_crawled": len(self.crawled_pages),
            "total_urls_visited": self.url_processor.get_visited_count(),
            "domains_status": self.domain_status,
            "allowed_domains": len(self.allowed_domains)
        }
    
    def shutdown(self) -> None:
        """Shutdown crawler gracefully"""
        logger.info("Shutting down crawler...")
        self._save_crawl_state()
        self.http_client.close()
        logger.info("Crawler shutdown complete")
