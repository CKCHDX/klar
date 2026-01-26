"""
kse_url_processor.py - URL Normalization and Processing

Handles URL normalization, validation, and standardization
for consistent crawling and deduplication.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import re
from typing import Optional, Tuple, List
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from pathlib import Path

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class KSEURLException(KSEException):
    """URL processing exception"""
    pass


class URLProcessor:
    """
    URL normalization and validation.
    
    Handles:
    - URL normalization
    - Domain extraction
    - Path canonicalization
    - Query parameter handling
    - URL validation
    """
    
    # URL regex patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # Protocol
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*'  # Subdomains
        r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'  # Domain
        r'(?::\d+)?'  # Optional port
        r'(?:/[^\s]*)?$',  # Optional path
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize URL processor"""
        logger.debug("URLProcessor initialized")
    
    def normalize(self, url: str) -> str:
        """
        Normalize URL for consistency.
        
        Handles:
        - Lowercase scheme and domain
        - Remove default ports
        - Remove fragment
        - Sort query parameters
        - Remove trailing slash from root
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            
            # Lowercase scheme and domain
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            
            # Remove default ports
            if scheme == 'http' and netloc.endswith(':80'):
                netloc = netloc[:-3]
            elif scheme == 'https' and netloc.endswith(':443'):
                netloc = netloc[:-4]
            
            # Normalize path
            path = parsed.path or '/'
            if not path.startswith('/'):
                path = '/' + path
            
            # Sort query parameters
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=True)
                sorted_params = sorted(params.items())
                query = urlencode(sorted_params, doseq=True)
            else:
                query = ''
            
            # Remove fragment
            fragment = ''
            
            # Reconstruct
            normalized = urlunparse((scheme, netloc, path, '', query, fragment))
            
            # Remove trailing slash from root
            if normalized.endswith('/?'):
                normalized = normalized[:-2]
            elif normalized.endswith('/') and path == '/':
                normalized = normalized[:-1]
            
            logger.debug(f"URL normalized: {url} -> {normalized}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            raise KSEURLException(f"Failed to normalize URL: {url}") from e
    
    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL to process
            
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            logger.debug(f"Domain extracted: {url} -> {domain}")
            return domain
            
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {e}")
            raise KSEURLException(f"Failed to extract domain: {url}") from e
    
    def extract_path(self, url: str) -> str:
        """
        Extract path from URL.
        
        Args:
            url: URL to process
            
        Returns:
            Path component
        """
        try:
            parsed = urlparse(url)
            path = parsed.path or '/'
            
            if parsed.query:
                path += '?' + parsed.query
            
            return path
            
        except Exception as e:
            logger.error(f"Error extracting path from {url}: {e}")
            raise KSEURLException(f"Failed to extract path: {url}") from e
    
    def is_valid(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Check minimum length
        if len(url) < 10:
            return False
        
        # Check pattern
        if not self.URL_PATTERN.match(url):
            return False
        
        # Check for valid scheme
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False
            if not parsed.netloc:
                return False
            return True
        except Exception:
            return False
    
    def is_crawlable(self, url: str) -> bool:
        """
        Check if URL should be crawled.
        
        Args:
            url: URL to check
            
        Returns:
            True if crawlable
        """
        if not self.is_valid(url):
            return False
        
        # Lowercase for comparison
        url_lower = url.lower()
        
        # Exclude file types
        excluded_extensions = (
            '.pdf', '.zip', '.tar', '.gz', '.rar',
            '.exe', '.dmg', '.deb', '.rpm',
            '.jpg', '.jpeg', '.png', '.gif', '.webp',
            '.mp3', '.mp4', '.avi', '.mov', '.mkv',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        )
        
        for ext in excluded_extensions:
            if url_lower.endswith(ext):
                logger.debug(f"URL excluded (file type): {url}")
                return False
        
        return True
    
    def are_same(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are the same after normalization.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same
        """
        try:
            norm1 = self.normalize(url1)
            norm2 = self.normalize(url2)
            return norm1 == norm2
        except Exception:
            return url1 == url2
    
    def get_hash(self, url: str) -> str:
        """
        Get hash of normalized URL for deduplication.
        
        Args:
            url: URL to hash
            
        Returns:
            Hash string
        """
        import hashlib
        
        try:
            normalized = self.normalize(url)
            return hashlib.md5(normalized.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing URL {url}: {e}")
            raise KSEURLException(f"Failed to hash URL: {url}") from e
    
    def resolve_relative(self, base_url: str, relative_url: str) -> str:
        """
        Resolve relative URL against base URL.
        
        Args:
            base_url: Base URL
            relative_url: Relative URL
            
        Returns:
            Absolute URL
        """
        try:
            from urllib.parse import urljoin
            
            absolute = urljoin(base_url, relative_url)
            return self.normalize(absolute)
            
        except Exception as e:
            logger.error(f"Error resolving relative URL {relative_url}: {e}")
            raise KSEURLException(f"Failed to resolve relative URL: {relative_url}") from e


__all__ = ["URLProcessor", "KSEURLException"]
