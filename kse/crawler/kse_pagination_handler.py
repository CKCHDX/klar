"""kse_pagination_handler.py - Pagination Detection and Navigation"""

import logging
from typing import Optional, List
import re
from urllib.parse import urlparse, urljoin

from kse.core import get_logger

logger = get_logger('crawler')


class PaginationHandler:
    """Detect and handle pagination"""
    
    # Common pagination patterns
    PAGINATION_PATTERNS = [
        r'/page[/?](\d+)',
        r'[?&]page[=](\d+)',
        r'/\d+-\d+/',
        r'[?&]offset[=](\d+)',
        r'[?&]start[=](\d+)',
    ]
    
    def __init__(self):
        logger.debug("PaginationHandler initialized")
    
    def detect_pagination(self, html: bytes, base_url: str) -> List[str]:
        """Detect pagination links"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            pagination_links = []
            
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if not href:
                    continue
                
                text = link.get_text().strip().lower()
                
                # Check link text
                if any(x in text for x in ['next', 'previous', 'page', '→', '←']):
                    absolute = urljoin(base_url, href)
                    pagination_links.append(absolute)
                    continue
                
                # Check URL pattern
                if any(re.search(pattern, href) for pattern in self.PAGINATION_PATTERNS):
                    absolute = urljoin(base_url, href)
                    pagination_links.append(absolute)
            
            logger.debug(f"Found {len(pagination_links)} pagination links")
            return pagination_links
            
        except Exception as e:
            logger.error(f"Error detecting pagination: {e}")
            return []


__all__ = ["PaginationHandler"]
