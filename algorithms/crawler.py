"""
KLAR 3.0 - UPDATED crawler.py
Web crawler with domain security and verification
"""

import requests
import time
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime


class Crawler:
    """
    Secure web crawler with domain verification
    Only crawls trusted domains from domains.json
    """
    
    def __init__(self, domains_config="domains.json"):
        """Initialize crawler with domain configuration"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/3.0 (Swedish Search Engine; +https://oscyra.solutions)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Load trusted domains
        try:
            with open(domains_config, 'r', encoding='utf-8') as f:
                self.domains_config = json.load(f)
                self.trusted_domains = self._build_trusted_domains()
        except Exception as e:
            print(f"❌ Warning: Could not load domains config: {e}")
            self.domains_config = {}
            self.trusted_domains = set()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # 1 second between requests per domain
        
        # Crawl settings
        self.timeout = 10
        self.max_retries = 3
    
    def _build_trusted_domains(self):
        """Build set of all trusted domains from config"""
        trusted = set()
        
        for category, domains_list in self.domains_config.items():
            if isinstance(domains_list, list):
                for domain_entry in domains_list:
                    if isinstance(domain_entry, str):
                        trusted.add(domain_entry.lower())
                    elif isinstance(domain_entry, dict):
                        domain = domain_entry.get('domain', '').lower()
                        if domain:
                            trusted.add(domain)
                        # Add subdomains
                        for subdomain in domain_entry.get('subdomains', []):
                            trusted.add(f"{subdomain}.{domain}")
        
        return trusted
    
    def is_domain_trusted(self, url: str) -> tuple:
        """
        SECURITY CHECK: Verify domain is in trusted list
        
        Returns: (is_trusted: bool, domain: str, error_message: str)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Check if domain is trusted
            for trusted in self.trusted_domains:
                if domain.endswith(trusted) or domain == trusted:
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
    
    def fetch(self, url: str, verify_domain=True) -> dict:
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
                'html': str,
                'metadata': dict,
                'success': bool,
                'error': str if not success
            }
        """
        result = {
            'url': url,
            'title': None,
            'content': None,
            'html': None,
            'metadata': {},
            'success': False,
            'error': None,
        }
        
        # SECURITY: Verify domain first
        if verify_domain:
            is_trusted, domain, error = self.is_domain_trusted(url)
            if not is_trusted:
                result['error'] = error or f"Domain not trusted"
                return result
        else:
            parsed = urlparse(url)
            domain = parsed.netloc
        
        # Rate limiting
        self._rate_limit(domain)
        
        # Fetch with retries
        for attempt in range(self.max_retries):
            try:
                print(f"[Crawler] Fetching: {url} (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=True
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract metadata
                result['html'] = response.text
                result['metadata'] = {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'last_modified': response.headers.get('last-modified', ''),
                    'fetch_time': datetime.now().isoformat(),
                }
                
                # Extract title
                title_tag = soup.find('title')
                result['title'] = title_tag.string if title_tag else None
                
                # Extract main content
                # Remove script and style tags
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                # Get text content
                text_content = soup.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text_content = ' '.join(text_content.split())
                
                result['content'] = text_content[:5000]  # Limit to 5000 chars
                result['success'] = True
                
                print(f"[Crawler] ✅ Success: {url}")
                return result
            
            except requests.RequestException as e:
                result['error'] = str(e)
                print(f"[Crawler] ⚠️ Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return result
    
    def fetch_multiple(self, urls: list, verify_domain=True) -> list:
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
            time.sleep(0.5)
        
        return results
    
    def get_subpage_urls(self, base_url: str, patterns: list = None) -> list:
        """
        Get subpage URLs based on patterns
        
        Args:
            base_url: Base domain URL
            patterns: List of path patterns (e.g., ['/nyheter', '/väder', '/sport'])
        
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


# ============================================================================
# SECURITY UTILITIES
# ============================================================================

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
        # This is basic - in production use a library like bleach
        import re
        
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers
        text = re.sub(r'\s+on\w+\s*=', ' ', text)
        
        return text
