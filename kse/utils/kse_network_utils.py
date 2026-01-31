"""
Network Utilities - Network and URL handling utilities
"""

import logging
from typing import Optional
from urllib.parse import urlparse, urljoin, parse_qs

logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL string
    
    Returns:
        True if valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL (remove fragments, sort query params)
    
    Args:
        url: Input URL
    
    Returns:
        Normalized URL
    """
    try:
        parsed = urlparse(url)
        
        # Rebuild URL without fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Add query if present
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        return normalized.lower()
    except Exception as e:
        logger.warning(f"Failed to normalize URL {url}: {e}")
        return url


def get_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: URL string
    
    Returns:
        Domain or None
    """
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return None


def get_base_url(url: str) -> Optional[str]:
    """
    Get base URL (scheme + domain)
    
    Args:
        url: URL string
    
    Returns:
        Base URL or None
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None


def join_url(base: str, relative: str) -> str:
    """
    Join base and relative URLs
    
    Args:
        base: Base URL
        relative: Relative URL
    
    Returns:
        Joined URL
    """
    return urljoin(base, relative)


def get_query_params(url: str) -> dict:
    """
    Extract query parameters from URL
    
    Args:
        url: URL string
    
    Returns:
        Dictionary of query parameters
    """
    try:
        parsed = urlparse(url)
        return parse_qs(parsed.query)
    except Exception:
        return {}
