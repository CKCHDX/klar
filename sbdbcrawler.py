#!/usr/bin/env python3
"""
SBDB Crawler - Web Crawler with Change Detection and Incremental Updates
Production-ready crawling with per-domain hash-based change detection
"""

import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DomainCrawler:
    """Crawls Swedish domains with URL filtering and change detection"""
    
    def __init__(self, nlp, config_manager, pages_file: Path, logs_dir: Path):
        self.nlp = nlp
        self.config = config_manager
        self.pages_file = pages_file
        self.logs_dir = logs_dir
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar-SBDB/1.0 (Swedish Search Engine)'
        })
        
        self.crawl_log_file = logs_dir / 'crawllog.json'
        self.error_log_file = logs_dir / 'errorlog.json'
        
        self.pages = []
        self.page_id_counter = 0
        self.crawl_stats = {
            'domains_crawled': 0,
            'pages_downloaded': 0,
            'errors': 0,
            'duplicates': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def load_existing_pages(self):
        """Load already crawled pages from disk"""
        if self.pages_file.exists():
            try:
                self.pages = json.loads(self.pages_file.read_text(encoding='utf-8'))
                self.page_id_counter = len(self.pages)
                logger.info(f"✓ Loaded {len(self.pages)} existing pages")
            except:
                logger.warning("Could not load existing pages, starting fresh")
                self.pages = []
    
    def crawl_domain(self, domain: Dict, max_pages: int = 500, crawl_depth: int = 2) -> Tuple[int, int]:
        """
        Crawl a single domain.
        Returns: (pages_crawled, errors)
        """
        domain_url = domain['url']
        if not domain_url.startswith('http'):
            domain_url = f'https://{domain_url}'
        
        visited = set()
        to_visit = [domain_url]
        pages_crawled = 0
        errors = 0
        
        logger.info(f"↻ Crawling {domain['url']}...")
        
        while to_visit and pages_crawled < max_pages:
            current_url = to_visit.pop(0)
            
            # Skip if already visited
            if current_url in visited:
                continue
            visited.add(current_url)
            
            # Filter URLs: only crawl same domain
            if not self._is_valid_url(current_url, domain['url']):
                continue
            
            try:
                # Fetch page
                response = self.session.get(current_url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    errors += 1
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Check for duplicates
                page_hash = hashlib.md5(response.content).hexdigest()
                if self._is_duplicate(page_hash):
                    self.crawl_stats['duplicates'] += 1
                    continue
                
                # Extract content
                page_data = self._extract_page_data(current_url, soup, domain, page_hash)
                
                # Store page
                self.pages.append(page_data)
                pages_crawled += 1
                
                # Extract links for further crawling
                if len(visited) < max_pages:
                    for link in soup.find_all('a', href=True):
                        href = urljoin(current_url, link['href'])
                        # Remove fragments
                        href = href.split('#')[0]
                        if href not in visited and self._is_valid_url(href, domain['url']):
                            to_visit.append(href)
                
                logger.debug(f"  ✓ Crawled {current_url}")
            
            except requests.Timeout:
                logger.warning(f"  ✗ Timeout: {current_url}")
                errors += 1
            except Exception as e:
                logger.warning(f"  ✗ Error: {current_url} - {str(e)[:50]}")
                errors += 1
            
            time.sleep(0.5)  # Be respectful to servers
        
        logger.info(f"  ✓ Domain crawl complete: {pages_crawled} pages, {errors} errors")
        return pages_crawled, errors
    
    def _extract_page_data(self, url: str, soup: BeautifulSoup, domain: Dict, page_hash: str) -> Dict:
        """
        Extract structured data from a page.
        """
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else url.split('/')[-1]
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract main text
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())  # Normalize whitespace
        
        # Process text through NLP
        tokens, entities = self.nlp.process_text(text)
        
        # Create page data
        page_data = {
            'page_id': self.page_id_counter,
            'url': url,
            'title': title,
            'description': description,
            'text': text[:5000],  # Store first 5000 chars
            'tokens': tokens,
            'entities': entities,
            'domain': domain['url'],
            'trust_score': domain.get('trust_score', 0.5),
            'region': domain.get('region', 'Unknown'),
            'category': domain.get('category', 'Other'),
            'crawl_date': datetime.now().isoformat(),
            'page_hash': page_hash,
            'language': 'sv',
        }
        
        self.page_id_counter += 1
        self.crawl_stats['pages_downloaded'] += 1
        
        return page_data
    
    def _is_valid_url(self, url: str, domain_base: str) -> bool:
        """
        Validate that URL belongs to the target domain.
        Implements 'smart' crawl strategy: only .se domains.
        """
        try:
            parsed = urlparse(url)
            domain_netloc = domain_base.replace('https://', '').replace('http://', '')
            
            # Must be a .se domain or match domain
            if not parsed.netloc.endswith('.se') and parsed.netloc != domain_netloc:
                return False
            
            # Skip common non-content URLs
            skip_patterns = ['.pdf', '.jpg', '.png', '.mp3', '.mp4', '/logout', '/admin']
            if any(pattern in parsed.path for pattern in skip_patterns):
                return False
            
            return True
        except:
            return False
    
    def _is_duplicate(self, page_hash: str) -> bool:
        """
        Check if page hash already exists in our database.
        """
        for page in self.pages:
            if page.get('page_hash') == page_hash:
                return True
        return False
    
    def save_pages(self) -> bool:
        """
        Save crawled pages to disk.
        """
        try:
            self.pages_file.write_text(json.dumps(self.pages, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"✓ Saved {len(self.pages)} pages to {self.pages_file}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save pages: {e}")
            return False
    
    def log_crawl_session(self):
        """
        Log the crawl session to crawllog.json.
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.crawl_stats,
        }
        
        logs = []
        if self.crawl_log_file.exists():
            logs = json.loads(self.crawl_log_file.read_text(encoding='utf-8'))
        
        logs.append(log_entry)
        
        self.crawl_log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


class ChangeDetector:
    """Detects changes in domains for incremental crawling"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config = config_manager
    
    def compute_domain_hash(self, domain_url: str) -> str:
        """
        Compute a hash of a domain's content to detect changes.
        Simple implementation: hash of homepage.
        """
        try:
            if not domain_url.startswith('http'):
                domain_url = f'https://{domain_url}'
            
            response = requests.get(domain_url, timeout=10)
            content_hash = hashlib.sha256(response.content).hexdigest()
            return content_hash
        except:
            return None
    
    def check_domain_for_changes(self, domain: Dict) -> bool:
        """
        Check if a domain has changed since last crawl.
        Returns: True if changes detected, False otherwise
        """
        current_hash = self.compute_domain_hash(domain['url'])
        last_hash = domain.get('last_content_hash')
        
        if current_hash is None:
            return False
        
        if last_hash != current_hash:
            # Changes detected
            domain['last_content_hash'] = current_hash
            domain['last_change_detected'] = datetime.now().isoformat()
            return True
        
        return False
    
    def should_recrawl_domain(self, domain: Dict, recrawl_frequency: str = '24h') -> bool:
        """
        Determine if a domain should be recrawled based on recrawl frequency.
        
        Args:
            domain: Domain dictionary
            recrawl_frequency: '24h', '7d', '30d', or 'manual'
        
        Returns:
            True if domain should be recrawled
        """
        if recrawl_frequency == 'manual':
            return False
        
        last_crawl = domain.get('last_crawl')
        if not last_crawl:
            return True  # Never crawled
        
        last_crawl_dt = datetime.fromisoformat(last_crawl)
        now = datetime.now()
        
        if recrawl_frequency == '24h':
            return (now - last_crawl_dt) > timedelta(hours=24)
        elif recrawl_frequency == '7d':
            return (now - last_crawl_dt) > timedelta(days=7)
        elif recrawl_frequency == '30d':
            return (now - last_crawl_dt) > timedelta(days=30)
        
        return False
    
    def get_domains_to_recrawl(self, domains: List[Dict], change_detection_enabled: bool = True) -> List[Dict]:
        """
        Get list of domains that need to be recrawled.
        """
        to_recrawl = []
        
        for domain in domains:
            if not domain.get('selected', False):
                continue
            
            # Check for changes
            if change_detection_enabled:
                if self.check_domain_for_changes(domain):
                    to_recrawl.append(domain)
                    logger.info(f"↫ Changes detected in {domain['url']}")
            else:
                # Use time-based recrawl
                if self.should_recrawl_domain(domain):
                    to_recrawl.append(domain)
        
        return to_recrawl


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    print("SBDB Crawler module loaded")
