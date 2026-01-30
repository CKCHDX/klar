"""
HTTP Client for fetching web content
"""
import requests
from urllib.parse import urlparse, urljoin


class HTTPClient:
    """Handles HTTP/HTTPS requests for web content"""
    
    DEFAULT_TIMEOUT = 10  # Default timeout in seconds
    
    def __init__(self, timeout=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/1.0 (Custom Render Engine)'
        })
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        
    def fetch(self, url, binary=False):
        """
        Fetch content from a URL
        
        Args:
            url: The URL to fetch
            binary: If True, return binary content; if False, return text (default: False)
            
        Returns:
            dict: Response data with 'content', 'status_code', 'headers', 'url', 'content_type'
        """
        try:
            # Ensure URL has a scheme
            if not urlparse(url).scheme:
                url = 'http://' + url
                
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            # Get content based on type requested
            content = response.content if binary else response.text
            content_type = response.headers.get('Content-Type', 'text/html')
            
            return {
                'content': content,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'url': response.url,
                'content_type': content_type,
                'success': True,
                'error': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'content': None,
                'status_code': None,
                'headers': {},
                'url': url,
                'content_type': None,
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
    
    def close(self):
        """Close the HTTP session and release resources"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.close()
        return False
