"""
HTTP Client for fetching web content
"""
import requests
from urllib.parse import urlparse, urljoin


class HTTPClient:
    """Handles HTTP/HTTPS requests for web content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/1.0 (Custom Render Engine)'
        })
        
    def fetch(self, url):
        """
        Fetch content from a URL
        
        Args:
            url: The URL to fetch
            
        Returns:
            dict: Response data with 'content', 'status_code', 'headers', 'url'
        """
        try:
            # Ensure URL has a scheme
            if not urlparse(url).scheme:
                url = 'http://' + url
                
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            return {
                'content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'url': response.url,
                'success': True,
                'error': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'content': None,
                'status_code': None,
                'headers': {},
                'url': url,
                'success': False,
                'error': str(e)
            }
    
    def resolve_url(self, base_url, relative_url):
        """
        Resolve a relative URL against a base URL
        
        Args:
            base_url: Base URL
            relative_url: Relative URL or absolute URL
            
        Returns:
            str: Absolute URL
        """
        return urljoin(base_url, relative_url)
