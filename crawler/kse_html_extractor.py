"""
kse_html_extractor.py - HTML Parsing and Content Extraction

Parses HTML and extracts text content, metadata, and links.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Set
import re

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class KSEHTMLException(KSEException):
    """HTML extraction exception"""
    pass


class HTMLExtractor:
    """HTML parsing and content extraction"""
    
    # Meta tags to extract
    META_TAGS = ['title', 'description', 'keywords', 'author']
    
    def __init__(self):
        """Initialize HTML extractor"""
        logger.debug("HTMLExtractor initialized")
    
    def extract_text(self, html: bytes) -> str:
        """Extract plain text from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            logger.debug(f"Extracted {len(text)} chars from HTML")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise KSEHTMLException(f"Failed to extract text") from e
    
    def extract_metadata(self, html: bytes, url: str = "") -> Dict[str, str]:
        """Extract metadata from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            metadata = {'url': url, 'title': '', 'description': '', 'language': ''}
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Meta tags
            for tag_name in self.META_TAGS:
                tag = soup.find('meta', attrs={'name': tag_name})
                if tag and tag.get('content'):
                    metadata[tag_name] = tag['content']
            
            # Language
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                metadata['language'] = html_tag['lang']
            
            logger.debug(f"Extracted metadata: {len(metadata)} fields")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            raise KSEHTMLException(f"Failed to extract metadata") from e
    
    def extract_links(self, html: bytes, base_url: str = "") -> List[str]:
        """Extract all links from HTML"""
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin
            
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link_tag in soup.find_all('a', href=True):
                href = link_tag.get('href', '').strip()
                if href and not href.startswith('#'):
                    # Convert relative to absolute
                    if base_url:
                        href = urljoin(base_url, href)
                    links.append(href)
            
            logger.debug(f"Extracted {len(links)} links from HTML")
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            raise KSEHTMLException(f"Failed to extract links") from e


__all__ = ["HTMLExtractor", "KSEHTMLException"]
