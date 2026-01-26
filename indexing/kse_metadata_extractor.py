"""kse_metadata_extractor.py - Metadata Extraction

Extracts and manages page metadata:
- Title, description, URL
- Domain information
- Timestamps
- Metadata indexing
"""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse
import re

from kse.core import get_logger

logger = get_logger('indexing')


class MetadataExtractor:
    """Extract metadata from pages"""
    
    def __init__(self):
        """Initialize metadata extractor"""
        logger.debug("MetadataExtractor initialized")
    
    def extract(self, page: Dict) -> Dict:
        """Extract metadata from page
        
        Args:
            page: Page data
            
        Returns:
            Extracted metadata
        """
        url = page.get('url', '')
        
        return {
            'url': url,
            'title': self._extract_title(page),
            'description': self._extract_description(page),
            'domain': self._extract_domain(url),
            'language': page.get('language', 'sv'),
            'timestamp': page.get('timestamp'),
            'content_length': len(page.get('content', '')),
            'headings': self._extract_headings(page),
        }
    
    def _extract_title(self, page: Dict) -> str:
        """Extract page title"""
        title = page.get('title', '')
        if title:
            return title[:200]  # Limit length
        return ''
    
    def _extract_description(self, page: Dict) -> str:
        """Extract page description"""
        description = page.get('description', '')
        if description:
            return description[:500]  # Limit length
        return ''
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www.
            domain = domain.replace('www.', '')
            return domain
        except:
            return ''
    
    def _extract_headings(self, page: Dict) -> list:
        """Extract headings from page"""
        content = page.get('content', '')
        # Simple heading extraction
        headings = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', content)
        return headings[:10]  # Return first 10 headings
    
    def create_metadata_index(self, pages: Dict[str, Dict]) -> Dict:
        """Create metadata index for all pages
        
        Args:
            pages: URL → page data mapping
            
        Returns:
            URL → metadata mapping
        """
        metadata_index = {}
        for url, page in pages.items():
            metadata_index[url] = self.extract(page)
        return metadata_index


__all__ = ["MetadataExtractor"]
