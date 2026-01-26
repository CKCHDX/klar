"""kse_link_extractor.py - Link Discovery and Validation"""

import logging
import re
from typing import List, Set
from urllib.parse import urlparse, urljoin

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class LinkExtractor:
    """Extract and validate links"""
    
    # Exclusions
    EXCLUDED_SCHEMES = {'javascript', 'mailto', 'ftp', 'telnet', 'file'}
    EXCLUDED_EXTENSIONS = {'.pdf', '.zip', '.exe', '.dmg', '.jpg', '.png', '.gif'}
    
    def __init__(self):
        logger.debug("LinkExtractor initialized")
    
    def extract_links(self, html: bytes, base_url: str) -> Set[str]:
        """Extract valid links"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            links = set()
            
            for tag in soup.find_all(['a', 'link', 'script']):
                href = tag.get('href') or tag.get('src')
                if href:
                    absolute_url = urljoin(base_url, href)
                    if self._is_valid_link(absolute_url):
                        links.add(absolute_url)
            
            logger.debug(f"Extracted {len(links)} valid links")
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return set()
    
    def _is_valid_link(self, url: str) -> bool:
        """Validate link"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme.lower() in self.EXCLUDED_SCHEMES:
                return False
            
            # Check file extension
            if any(url.lower().endswith(ext) for ext in self.EXCLUDED_EXTENSIONS):
                return False
            
            # Check domain
            if not parsed.netloc:
                return False
            
            return True
            
        except Exception:
            return False


__all__ = ["LinkExtractor"]
