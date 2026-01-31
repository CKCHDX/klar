"""
KSE URL Processor - URL normalization and deduplication
"""
from typing import Set, Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "crawler.log")


class URLProcessor:
    """Process and normalize URLs for crawling"""
    
    def __init__(self):
        """Initialize URL processor"""
        self.visited_urls: Set[str] = set()
    
    def normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize URL to canonical form
        
        Args:
            url: URL to normalize
        
        Returns:
            Normalized URL or None if invalid
        """
        try:
            # Parse URL
            parsed = urlparse(url.strip())
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return None
            
            # Normalize scheme (lowercase)
            scheme = parsed.scheme.lower()
            if scheme not in ['http', 'https']:
                return None
            
            # Normalize netloc (lowercase, remove www)
            netloc = parsed.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            # Normalize path
            path = parsed.path or '/'
            # Remove trailing slash except for root
            if len(path) > 1 and path.endswith('/'):
                path = path[:-1]
            
            # Normalize query parameters (sort them)
            query = ''
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=True)
                # Sort parameters
                sorted_params = sorted(params.items())
                query = urlencode(sorted_params, doseq=True)
            
            # Reconstruct URL (no fragment)
            normalized = urlunparse((
                scheme,
                netloc,
                path,
                '',  # params (usually empty)
                query,
                ''   # fragment (remove)
            ))
            
            return normalized
        
        except Exception as e:
            logger.debug(f"Failed to normalize URL {url}: {e}")
            return None
    
    def is_duplicate(self, url: str) -> bool:
        """
        Check if URL has already been visited
        
        Args:
            url: URL to check
        
        Returns:
            True if URL is duplicate
        """
        normalized = self.normalize_url(url)
        if not normalized:
            return True
        
        if normalized in self.visited_urls:
            return True
        
        return False
    
    def mark_visited(self, url: str) -> None:
        """
        Mark URL as visited
        
        Args:
            url: URL to mark
        """
        normalized = self.normalize_url(url)
        if normalized:
            self.visited_urls.add(normalized)
    
    def get_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url: URL to parse
        
        Returns:
            Domain name (without www)
        """
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return None
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from same domain
        
        Args:
            url1: First URL
            url2: Second URL
        
        Returns:
            True if same domain
        """
        domain1 = self.get_domain(url1)
        domain2 = self.get_domain(url2)
        return domain1 == domain2 and domain1 is not None
    
    def get_base_url(self, url: str) -> Optional[str]:
        """
        Get base URL (scheme + netloc)
        
        Args:
            url: URL to parse
        
        Returns:
            Base URL
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return None
    
    def clear_visited(self) -> None:
        """Clear visited URLs set"""
        self.visited_urls.clear()
        logger.debug("Cleared visited URLs")
    
    def get_visited_count(self) -> int:
        """
        Get count of visited URLs
        
        Returns:
            Number of visited URLs
        """
        return len(self.visited_urls)
    
    def load_visited_urls(self, urls: Set[str]) -> None:
        """
        Load visited URLs from storage
        
        Args:
            urls: Set of visited URLs
        """
        self.visited_urls = urls
        logger.info(f"Loaded {len(urls)} visited URLs")
    
    def get_visited_urls(self) -> Set[str]:
        """
        Get set of visited URLs
        
        Returns:
            Set of visited URLs
        """
        return self.visited_urls.copy()
