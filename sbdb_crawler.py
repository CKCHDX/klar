"""
Klar SBDB Crawler - Domain Crawling & Change Detection
Handles fetching content from Swedish domains with change detection
"""

import requests
import hashlib
import logging
import json
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
from queue import Queue

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Default Swedish domains to crawl
SWEDISH_DOMAINS_CURATED = [
    'sverigesradio.se',
    'svt.se',
    'dn.se',
    'aftonbladet.se',
    'expressen.se',
    'bbc.com',  # English, good content
    'wikipedia.se',
    'scb.se',  # Statistics Sweden
    'government.se',
    'riksdag.se',
    'gmail.com',
    'linkedin.com',
]


class DomainCrawler:
    """
    Crawls Swedish domains and extracts content
    """
    
    def __init__(self, data_dir: str = "klar_sbdb_data", timeout: int = 10):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar-SBDB/1.0 (+https://oscyra.solutions/)'
        })
        
        self.crawl_log = []
        self.domain_hashes = {}  # domain → hash of content
        self._load_domain_hashes()
        
        logger.info(f"DomainCrawler initialized with data_dir={data_dir}")
    
    def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, url: str, html: str, same_domain_only: bool = True) -> List[str]:
        """
        Extract all links from HTML
        
        Args:
            url: Base URL (for relative links)
            html: HTML content
            same_domain_only: Only return links on same domain
            
        Returns:
            List of URLs
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            base_domain = urlparse(url).netloc
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                absolute_url = urljoin(url, href)
                
                # Filter: same domain only
                if same_domain_only:
                    link_domain = urlparse(absolute_url).netloc
                    if link_domain != base_domain:
                        continue
                
                # Filter: valid http/https
                if absolute_url.startswith(('http://', 'https://')):
                    links.append(absolute_url)
            
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []
    
    def extract_text(self, html: str) -> Tuple[str, str]:
        """
        Extract title and main text from HTML
        
        Args:
            html: HTML content
            
        Returns:
            Tuple of (title, text)
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "Untitled"
            
            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            # Priority: article > main > div.content > body
            content = None
            for selector in ['article', 'main', "div[class*='content']"]:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup.find('body')
            
            if content:
                text = content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return title_text, text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return "", ""
    
    def crawl_domain(self, domain: str, max_pages: int = 100) -> List[Dict]:
        """
        Crawl a domain and return all pages
        
        Args:
            domain: Domain to crawl (e.g., 'sverigesradio.se')
            max_pages: Maximum pages to crawl
            
        Returns:
            List of page data dictionaries
        """
        pages = []
        visited_urls = set()
        to_visit = Queue()
        
        # Start with domain homepage
        start_url = f"https://{domain}/"
        to_visit.put(start_url)
        
        logger.info(f"Starting crawl of {domain}")
        
        while not to_visit.empty() and len(visited_urls) < max_pages:
            url = to_visit.get()
            
            # Skip if already visited
            if url in visited_urls:
                continue
            
            visited_urls.add(url)
            
            # Fetch content
            html = self.fetch_url(url)
            if not html:
                continue
            
            # Extract title and text
            title, text = self.extract_text(html)
            
            # Add to results
            pages.append({
                'url': url,
                'title': title,
                'text': text,
                'domain': domain,
                'crawl_time': time.time()
            })
            
            # Extract links for further crawling
            links = self.extract_links(url, html, same_domain_only=True)
            for link in links:
                if link not in visited_urls and len(visited_urls) < max_pages:
                    to_visit.put(link)
            
            # Progress logging
            if len(pages) % 10 == 0:
                logger.info(f"Crawled {len(pages)} pages from {domain}")
        
        logger.info(f"Completed crawl of {domain}: {len(pages)} pages")
        return pages
    
    def detect_changes(self, domain: str) -> bool:
        """
        Detect if a domain has changed since last crawl
        Uses content hash comparison
        
        Args:
            domain: Domain to check
            
        Returns:
            True if domain has changed
        """
        try:
            html = self.fetch_url(f"https://{domain}/")
            if not html:
                return False
            
            # Calculate hash
            current_hash = hashlib.sha256(html.encode()).hexdigest()
            previous_hash = self.domain_hashes.get(domain)
            
            # Check if changed
            if previous_hash is None:
                # First crawl
                self.domain_hashes[domain] = current_hash
                return True
            
            if current_hash != previous_hash:
                logger.info(f"Change detected in {domain}")
                self.domain_hashes[domain] = current_hash
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error detecting changes for {domain}: {e}")
            return False
    
    def _load_domain_hashes(self) -> None:
        """
        Load domain content hashes from disk
        """
        hash_file = self.data_dir / "domain_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    self.domain_hashes = json.load(f)
                logger.info(f"Loaded {len(self.domain_hashes)} domain hashes")
            except Exception as e:
                logger.error(f"Error loading domain hashes: {e}")
    
    def save_domain_hashes(self) -> None:
        """
        Save domain content hashes to disk
        """
        hash_file = self.data_dir / "domain_hashes.json"
        try:
            with open(hash_file, 'w') as f:
                json.dump(self.domain_hashes, f, indent=2)
            logger.info(f"Saved {len(self.domain_hashes)} domain hashes")
        except Exception as e:
            logger.error(f"Error saving domain hashes: {e}")


class ChangeDetector:
    """
    Background service that monitors domains for changes
    """
    
    def __init__(self, crawler: DomainCrawler, check_interval: int = 86400):
        self.crawler = crawler
        self.check_interval = check_interval  # Default 24 hours
        self.running = False
        self.thread = None
        self.recrawl_queue = []
    
    def start(self) -> None:
        """
        Start change detection background thread
        """
        if self.running:
            logger.warning("ChangeDetector already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("ChangeDetector started")
    
    def stop(self) -> None:
        """
        Stop change detection
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("ChangeDetector stopped")
    
    def _monitor_loop(self) -> None:
        """
        Main monitoring loop (runs in background thread)
        """
        while self.running:
            try:
                # Check all domains
                domains_to_check = list(self.crawler.domain_hashes.keys())
                
                for domain in domains_to_check:
                    if self.crawler.detect_changes(domain):
                        # Domain has changed, add to recrawl queue
                        self.recrawl_queue.append({
                            'domain': domain,
                            'detected_time': time.time()
                        })
                        logger.info(f"Added {domain} to recrawl queue")
                
                # Save updated hashes
                self.crawler.save_domain_hashes()
                
                # Wait for next check
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)  # Wait 60 seconds before retry
    
    def get_recrawl_queue(self) -> List[Dict]:
        """
        Get domains that need recrawling
        
        Returns:
            List of domains to recrawl
        """
        return self.recrawl_queue.copy()
    
    def clear_recrawl_queue(self) -> None:
        """
        Clear recrawl queue after processing
        """
        self.recrawl_queue = []


if __name__ == "__main__":
    # Test crawler
    crawler = DomainCrawler()
    
    # Test fetching
    html = crawler.fetch_url("https://www.example.com")
    if html:
        print(f"Fetched {len(html)} bytes from example.com")
        
        # Extract text
        title, text = crawler.extract_text(html)
        print(f"Title: {title}")
        print(f"Text preview: {text[:200]}...")
        
        # Extract links
        links = crawler.extract_links("https://www.example.com", html, same_domain_only=True)
        print(f"Found {len(links)} links")
    
    # Test change detection
    has_changed = crawler.detect_changes("example.com")
    print(f"\nChange detected in example.com: {has_changed}")
    
    # Test ChangeDetector
    detector = ChangeDetector(crawler, check_interval=60)
    # detector.start()  # Would run in background
    # ...
    # detector.stop()
