"""
String Utilities - String manipulation and processing utilities
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Input text
    
    Returns:
        Text with normalized whitespace
    """
    return ' '.join(text.split())


def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to append if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        text: HTML text
    
    Returns:
        Plain text
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem storage
    
    Args:
        filename: Input filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized[:255]  # Limit length


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: URL string
    
    Returns:
        Domain or None
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.warning(f"Failed to extract domain from {url}: {e}")
        return None


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug
    
    Args:
        text: Input text
    
    Returns:
        Slugified text
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def highlight_terms(text: str, terms: List[str], tag: str = 'mark') -> str:
    """
    Highlight search terms in text
    
    Args:
        text: Input text
        terms: Terms to highlight
        tag: HTML tag to use for highlighting
    
    Returns:
        Text with highlighted terms
    """
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(f'<{tag}>\\g<0></{tag}>', text)
    
    return text
