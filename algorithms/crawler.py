"""
Klar 3.1+ Crawler Module
Web crawler with domain security and smart search
Supports deep crawling within whitelisted domains
"""

import requests
import time
import json
from urllib.parse import urlparse, urljoin, quote_plus
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class Crawler:
    """
    Secure web crawler with domain verification and smart search.
    Uses whitelisted domains from domains.json.
    Supports deep crawling of search results within trusted domains.
    """
    
    def __init__(self, domains_config="domains.json"):
        """Initialize crawler with domain configuration"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/3.1 (Swedish Search Engine; +https://oscyra.solutions)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Load trusted domains
        try:
            with open(domains_config, 'r', encoding='utf-8') as f:
                domains_list = json.load(f)
                self.trusted_domains = set(d.lower() for d in domains_list if isinstance(d, str))
        except Exception as e:
            print(f"[Crawler] Warning: Could not load domains config: {e}")
            self.trusted_domains = set()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 0.5  # 0.5 second between requests per domain
        
        # Crawl settings
        self.timeout = 10
        self.max_retries = 2
        self.visited_urls = set()
    
    def is_domain_trusted(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        SECURITY CHECK: Verify domain is in trusted list
        
        Returns: (is_trusted: bool, domain: str, error_message: str)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Check if domain is trusted
            if domain in self.trusted_domains:
                return True, domain, None
            
            # Check if it's a subdomain of a trusted domain
            for trusted in self.trusted_domains:
                if domain.endswith('.' + trusted):
                    return True, domain, None
            
            # Domain not trusted
            return False, domain, f"Domain '{domain}' is not in trusted list"
        
        except Exception as e:
            return False, None, f"URL validation error: {str(e)}"
    
    def _rate_limit(self, domain: str):
        """Enforce rate limiting per domain"""
        now = time.time()
        
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def fetch(self, url: str, verify_domain=True) -> Dict:
        """
        Fetch and parse a URL
        
        Args:
            url: URL to fetch
            verify_domain: If True, verify domain is trusted before fetching
        
        Returns:
            {
                'url': str,
                'title': str,
                'content': str,
                'description': str,
                'html': str,
                'success': bool,
                'error': str if not success
            }
        """
        result = {
            'url': url,
            'title': None,
            'content': None,
            'description': None,
            'html': None,
            'success': False,
            'error': None,
        }
        
        # Avoid fetching same URL twice
        if url in self.visited_urls:
            return result
        
        self.visited_urls.add(url)
        
        # SECURITY: Verify domain first
        if verify_domain:
            is_trusted, domain, error = self.is_domain_trusted(url)
            if not is_trusted:
                result['error'] = error or "Domain not trusted"
                return result
        else:
            parsed = urlparse(url)
            domain = parsed.netloc
        
        # Rate limiting
        self._rate_limit(domain)
        
        # Fetch with retries
        for attempt in range(self.max_retries):
            try:
                print(f"[Crawler] Fetching: {url}")
                
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=True
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Store HTML
                result['html'] = response.text
                
                # Extract title
                title_tag = soup.find('title')
                result['title'] = title_tag.string if title_tag else None
                
                # Extract description (meta description)
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    result['description'] = meta_desc['content'].strip()
                
                # Extract main content
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
                    tag.decompose()
                
                # Get text content
                text_content = soup.get_text(separator=' ', strip=True)
                text_content = ' '.join(text_content.split())
                
                result['content'] = text_content[:5000]  # Limit to 5000 chars
                result['success'] = True
                
                print(f"[Crawler] ✓ Success: {url}")
                return result
            
            except requests.RequestException as e:
                result['error'] = str(e)
                print(f"[Crawler] Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(1 ** attempt)
        
        return result
    
    def fetch_multiple(self, urls: List[str], verify_domain=True) -> List[Dict]:
        """
        Fetch multiple URLs
        
        Args:
            urls: List of URLs to fetch
            verify_domain: If True, verify all domains before fetching
        
        Returns:
            List of fetch results
        """
        results = []
        
        for url in urls:
            result = self.fetch(url, verify_domain=verify_domain)
            if result['success']:
                results.append(result)
            
            # Small delay between requests
            time.sleep(0.2)
        
        return results
    
    def search_domain(self, domain: str, query: str, search_path: str = '/sok') -> List[str]:
        """
        Search within a domain for query-related results.
        
        Args:
            domain: Domain to search (e.g., 'svt.se')
            query: Search query
            search_path: Path to search endpoint (e.g., '/sok', '/search')
        
        Returns:
            List of result URLs found
        """
        if not domain in self.trusted_domains:
            print(f"[Crawler] Domain not trusted: {domain}")
            return []
        
        search_url = f"https://www.{domain}{search_path}?q={quote_plus(query)}"
        print(f"[Crawler] Searching: {search_url}")
        
        result = self.fetch(search_url, verify_domain=True)
        
        if not result['success']:
            return []
        
        # Extract links from search results
        soup = BeautifulSoup(result['html'], 'html.parser')
        links = []
        
        # Find all links that look like article/result links
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Build full URL
            full_url = urljoin(search_url, href)
            
            # Only include URLs from same domain
            if domain in full_url.lower():
                # Skip pagination and parameters
                if '?page=' not in full_url and '#' not in full_url:
                    links.append(full_url)
        
        return list(set(links))[:20]  # Return top 20 unique links
    
    def get_subpage_urls(self, base_url: str, patterns: List[str] = None) -> List[str]:
        """
        Get subpage URLs based on patterns
        
        Args:
            base_url: Base domain URL
            patterns: List of path patterns (e.g., ['/nyheter', '/väder'])
        
        Returns:
            List of full URLs
        """
        if patterns is None:
            patterns = []
        
        urls = [base_url]
        
        for pattern in patterns:
            full_url = urljoin(base_url, pattern)
            urls.append(full_url)
        
        return urls
    
    def validate_url(self, url: str) -> bool:
        """Basic URL validation"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent comparison"""
        url = url.lower().strip()
        url = url.replace('https://', 'http://')  # Normalize protocol
        url = url.rstrip('/')
        return url
    
    def clear_visited(self):
        """Clear visited URL cache"""
        self.visited_urls.clear()


class SecurityValidator:
    """Validate content for security issues"""
    
    BLOCKED_PATTERNS = [
        '<iframe',
        'onclick=',
        'onerror=',
        'javascript:',
        '<script',
        'eval(',
    ]
    
    @staticmethod
    def is_content_safe(html: str) -> bool:
        """Check if HTML content is safe"""
        html_lower = html.lower()
        
        for pattern in SecurityValidator.BLOCKED_PATTERNS:
            if pattern in html_lower:
                return False
        
        return True
    
    @staticmethod
    def sanitize_content(text: str) -> str:
        """Remove potentially dangerous content"""
        import re
        
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers
        text = re.sub(r'\s+on\w+\s*=', ' ', text)
        
        return text
