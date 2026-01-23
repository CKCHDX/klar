"""
Klar 3.1+ Enhanced Web Crawler
Improved crawling with:
- Deep crawling within whitelisted domains  
- Smart search URL generation per domain type
- Parallel requests with rate limiting (adaptive)
- Media extraction (images, videos)
- Content deduplication
- Exponential backoff for 429 errors
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus, quote
from pathlib import Path
import json
import time
from typing import List, Dict, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


class Crawler:
    """Enhanced crawler with deep domain crawling and smart search"""
    
    def __init__(self, domains: List[str], data_path: Path, offline_mode: bool = False):
        self.allowed_domains = set(d.lower() for d in domains)
        self.data_path = data_path
        self.offline_mode = offline_mode
        self.visited_urls: Set[str] = set()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/3.1 (Swedish Search Engine; +https://oscyra.solutions)'
        })
        
        # Rate limiting configuration - FIXED
        self.base_delay = 1.0  # Base delay between requests (seconds)
        self.rate_limit_delay = 2.0  # Additional delay for rate-limited domains
        self.backoff_multiplier = 1.5  # Exponential backoff multiplier
        self.domain_delays: Dict[str, float] = {}  # Per-domain backoff tracking
        
        # Create storage directories
        (self.data_path / 'images').mkdir(exist_ok=True)
        (self.data_path / 'videos').mkdir(exist_ok=True)
        (self.data_path / 'pages').mkdir(exist_ok=True)
        
        self.search_url_templates = self._load_search_templates()
        
        print(f"[Crawler] ✅ Initialized with {len(domains)} allowed domains")
        print(f"[Crawler] ⏱️ Rate limiting: base_delay={self.base_delay}s")
    
    def _load_search_templates(self) -> Dict[str, str]:
        """Load search URL templates for different domain types"""
        return {
            'svt.se': 'https://www.svt.se/sok?q={query}',
            'dn.se': 'https://www.dn.se/search?q={query}',
            'aftonbladet.se': 'https://www.aftonbladet.se/sida/sok?q={query}',
            'expressen.se': 'https://www.expressen.se/sok/?query={query}',
        }
    
    def _get_delay_for_domain(self, domain: str) -> float:
        """Get adaptive delay for domain (with exponential backoff for 429s)"""
        return self.domain_delays.get(domain, self.base_delay)
    
    def _apply_domain_backoff(self, domain: str):
        """Increase delay for domain after receiving 429 rate limit"""
        current_delay = self.domain_delays.get(domain, self.base_delay)
        new_delay = min(current_delay * self.backoff_multiplier, 5.0)  # Cap at 5s
        self.domain_delays[domain] = new_delay
        print(f"[Crawler] 🔄 Rate limited: {domain} → delay now {new_delay:.1f}s")
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL is from an allowed domain"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            for allowed in self.allowed_domains:
                if domain == allowed or domain.endswith('.' + allowed):
                    return True
            return False
        except:
            return False
    
    def crawl_for_query(self, query: str, limit: int = 50) -> List[Dict]:
        """Crawl pages for query with proper rate limiting"""
        results = []
        
        print(f"[Crawler] 🔍 Searching: '{query}'")
        
        seed_urls = self._generate_search_urls(query)
        print(f"[Crawler] 📋 Generated {len(seed_urls)} seed URLs")
        
        # REDUCED to 2 workers to avoid overwhelming servers
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            for url in seed_urls[:limit]:
                if url not in self.visited_urls and self.is_allowed_domain(url):
                    future = executor.submit(self._crawl_and_extract_results, url, query)
                    futures[future] = url
            
            for future in as_completed(futures, timeout=30):
                try:
                    page_results = future.result()
                    if page_results:
                        results.extend(page_results)
                        print(f"[Crawler] ✓ Found {len(page_results)} results")
                except Exception as e:
                    print(f"[Crawler] ✗ Error: {e}")
                
                if len(results) >= limit:
                    break
        
        results = self._deduplicate_results(results)
        print(f"[Crawler] 📊 Total unique results: {len(results)}")
        
        return results[:limit]
    
    def _generate_search_urls(self, query: str) -> List[str]:
        """Generate search URLs from templates"""
        seeds = []
        query_encoded = quote_plus(query)
        
        for domain, template in self.search_url_templates.items():
            if domain in self.allowed_domains:
                try:
                    search_url = template.format(query=query_encoded)
                    seeds.append(search_url)
                except:
                    pass
        
        return seeds
    
    def _crawl_and_extract_results(self, url: str, query: str) -> List[Dict]:
        """Crawl page with rate limiting"""
        results = []
        
        if url in self.visited_urls:
            return results
        
        self.visited_urls.add(url)
        
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            delay = self._get_delay_for_domain(domain)
            
            # APPLY DELAY BEFORE REQUEST
            time.sleep(delay)
            
            response = self.session.get(url, timeout=10)
            
            # Handle 429 rate limiting
            if response.status_code == 429:
                self._apply_domain_backoff(domain)
                return results
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_data = self.parse_page(soup, response.url, query)
            
            if page_data:
                results.append(page_data)
        
        except requests.exceptions.RequestException as e:
            if '429' in str(e):
                domain = urlparse(url).netloc.lower().replace('www.', '')
                self._apply_domain_backoff(domain)
            print(f"[Crawler] ⚠️ {url}: {e}")
        
        return results
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """Crawl single page with rate limiting"""
        if not self.is_allowed_domain(url) or url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            delay = self._get_delay_for_domain(domain)
            
            # APPLY DELAY BEFORE REQUEST
            time.sleep(delay)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 429:
                self._apply_domain_backoff(domain)
                return None
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parse_page(soup, response.url)
        
        except Exception as e:
            if '429' in str(e):
                domain = urlparse(url).netloc.lower().replace('www.', '')
                self._apply_domain_backoff(domain)
            return None
    
    def parse_page(self, soup: BeautifulSoup, url: str, query: str = '') -> Optional[Dict]:
        """Parse page content"""
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        content = self._extract_content(soup)
        
        if len(content) < 100:
            return None
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'content': content,
            'domain': urlparse(url).netloc.replace('www.', ''),
            'timestamp': time.time(),
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return 'Ingen titel'
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:300]
        
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        main_content = soup.find('main') or soup.find('article')
        
        if main_content:
            return main_content.get_text(separator=' ', strip=True)[:5000]
        
        return soup.get_text(separator=' ', strip=True)[:5000]
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results"""
        deduplicated = []
        seen_descriptions = set()
        
        for result in results:
            desc = result.get('description', '')[:100].lower()
            
            if desc and desc in seen_descriptions:
                continue
            
            seen_descriptions.add(desc)
            deduplicated.append(result)
        
        return deduplicated
