"""kse_url_utils.py - URL Handling Utilities

Utilities for URL manipulation:
- URL normalization
- Domain extraction
- URL validation
- URL encoding/decoding
"""

import logging
from typing import Optional
from urllib.parse import urlparse, urljoin
import re

from kse.core import get_logger

logger = get_logger('utils')


class URLUtils:
    """URL handling utilities"""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for consistency
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            # Remove trailing slash unless it's root
            if url.endswith('/') and url.count('/') > 2:
                url = url.rstrip('/')
            
            # Convert to lowercase
            url = url.lower()
            
            # Remove fragment
            url = url.split('#')[0]
            
            # Remove common tracking params
            params_to_remove = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']
            for param in params_to_remove:
                url = re.sub(f'[?&]{param}=[^&]*', '', url)
            
            # Remove trailing ? if no params
            url = url.rstrip('?')
            
            return url
        except Exception as e:
            logger.warning(f"Failed to normalize URL: {e}")
            return url
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL
        
        Args:
            url: URL string
            
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except Exception as e:
            logger.warning(f"Failed to extract domain: {e}")
            return None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_swedish_domain(url: str) -> bool:
        """Check if URL is Swedish domain
        
        Args:
            url: URL to check
            
        Returns:
            True if .se domain
        """
        domain = URLUtils.extract_domain(url)
        if domain:
            return domain.endswith('.se')
        return False
    
    @staticmethod
    def join_url(base: str, relative: str) -> str:
        """Join base and relative URLs
        
        Args:
            base: Base URL
            relative: Relative URL
            
        Returns:
            Joined URL
        """
        try:
            return urljoin(base, relative)
        except Exception as e:
            logger.warning(f"Failed to join URLs: {e}")
            return relative


__all__ = ["URLUtils"]
