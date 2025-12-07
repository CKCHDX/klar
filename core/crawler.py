"""
Web Crawler with Subdomain & Subpage Support
Crawl trusted domains with category-specific subpages
"""

import requests
from typing import Optional, List, Dict
from urllib.parse import urlparse
import time


class Crawler:
    """Web crawler with subdomain and subpage support"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': 'Klar-Browser/3.0 (Swedish Search Engine; +https://klar.se)'
        }
        self.session = requests.Session()
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL with retry logic
        Returns: First 5000 characters of content or None on failure
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    headers=self.headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text[:5000]
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"Fetch error for {url}: {e}")
                return None
        
        return None
    
    def fetch_with_subpages(self, domain: str, query: str, subpages: List[str]) -> List[Dict]:
        """
        Fetch from multiple subpage variations
        Returns: List of results with URL and content
        """
        results = []
        base_url = f"https://{domain}" if not domain.startswith('http') else domain
        
        for subpage in subpages:
            # Try multiple URL formats
            urls_to_try = [
                f"{base_url}{subpage}?q={query}",
                f"{base_url}{subpage}/search?q={query}",
                f"{base_url}{subpage}",
            ]
            
            for url in urls_to_try:
                content = self.fetch(url)
                if content:
                    results.append({
                        'url': url,
                        'content': content,
                        'domain': domain,
                        'subpage': subpage
                    })
                    break  # Found content, move to next subpage
        
        return results
    
    def fetch_with_subdomains(self, base_domain: str, query: str, subdomains: List[str]) -> List[Dict]:
        """
        Fetch from subdomain variations
        Returns: List of results from different subdomains
        """
        results = []
        
        for subdomain in subdomains:
            url = f"https://{subdomain}.{base_domain}/search?q={query}"
            content = self.fetch(url)
            
            if content:
                results.append({
                    'url': url,
                    'content': content,
                    'domain': base_domain,
                    'subdomain': subdomain
                })
        
        return results
    
    def fetch_multi_source(self, domain: str, query: str, subpages: List[str] = None,
                          subdomains: List[str] = None) -> List[Dict]:
        """
        Fetch from both subpages and subdomains
        Returns: Combined results from all sources
        """
        results = []
        
        if subpages:
            results.extend(self.fetch_with_subpages(domain, query, subpages))
        
        if subdomains:
            base_domain = domain.replace('https://', '').replace('http://', '')
            results.extend(self.fetch_with_subdomains(base_domain, query, subdomains))
        
        # Remove duplicates by URL
        unique_results = {}
        for result in results:
            url = result['url']
            if url not in unique_results:
                unique_results[url] = result
        
        return list(unique_results.values())
    
    def check_robots_txt(self, domain: str, path: str = '/') -> bool:
        """
        Check if path is allowed in robots.txt
        Returns: True if allowed, False if disallowed or error
        """
        try:
            robots_url = f"https://{domain}/robots.txt"
            response = self.session.get(robots_url, timeout=5, headers=self.headers)
            
            if response.status_code == 200:
                # Simple check for Disallow
                if f"Disallow: {path}" in response.text:
                    return False
            
            return True
        except:
            # If we can't fetch robots.txt, assume allowed
            return True
    
    def batch_fetch(self, urls: List[str]) -> List[Dict]:
        """
        Fetch multiple URLs
        Returns: List of results
        """
        results = []
        for url in urls:
            content = self.fetch(url)
            if content:
                results.append({
                    'url': url,
                    'content': content
                })
        
        return results
    
    def close(self):
        """Close session"""
        self.session.close()
