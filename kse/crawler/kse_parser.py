"""
KSE HTML Parser

Parses HTML content and extracts links, text, metadata.
"""

from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from html.parser import HTMLParser as BaseHTMLParser
from bs4 import BeautifulSoup
import logging

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class HTMLParser:
    """Parse HTML and extract content, links, metadata."""
    
    def __init__(self, html: str, base_url: str):
        """
        Initialize parser.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
        """
        self.html = html
        self.base_url = base_url
        self.soup = None
        self._parse()
    
    def _parse(self) -> None:
        """Parse HTML using BeautifulSoup."""
        try:
            self.soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            logger.warning(f"Failed to parse HTML: {e}")
            self.soup = None
    
    def get_title(self) -> Optional[str]:
        """
        Extract page title.
        
        Returns:
            Title string or None
        """
        if not self.soup:
            return None
        
        try:
            # Try <title> tag first
            title = self.soup.find('title')
            if title:
                return title.get_text(strip=True)
            
            # Try og:title meta tag
            og_title = self.soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title.get('content')
            
            # Try h1
            h1 = self.soup.find('h1')
            if h1:
                return h1.get_text(strip=True)
            
        except Exception as e:
            logger.warning(f"Error extracting title: {e}")
        
        return None
    
    def get_description(self) -> Optional[str]:
        """
        Extract meta description.
        
        Returns:
            Description string or None
        """
        if not self.soup:
            return None
        
        try:
            # Try meta description
            meta_desc = self.soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                return meta_desc.get('content')
            
            # Try og:description
            og_desc = self.soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                return og_desc.get('content')
            
            # Extract first paragraph
            p = self.soup.find('p')
            if p:
                text = p.get_text(strip=True)
                return text[:160] if len(text) > 160 else text
            
        except Exception as e:
            logger.warning(f"Error extracting description: {e}")
        
        return None
    
    def get_text(self, max_length: int = None) -> str:
        """
        Extract visible text content.
        
        Args:
            max_length: Maximum length of text
            
        Returns:
            Text content
        """
        if not self.soup:
            return ""
        
        try:
            # Remove script and style
            for script in self.soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = self.soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Truncate if needed
            if max_length and len(text) > max_length:
                text = text[:max_length]
            
            return text
        except Exception as e:
            logger.warning(f"Error extracting text: {e}")
            return ""
    
    def get_links(self) -> List[Dict[str, str]]:
        """
        Extract all links from page.
        
        Returns:
            List of link dictionaries {url, anchor_text, rel}
        """
        if not self.soup:
            return []
        
        links = []
        try:
            for link in self.soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                # Resolve relative URLs
                try:
                    absolute_url = urljoin(self.base_url, href)
                except Exception:
                    continue
                
                # Skip anchors and javascript
                if absolute_url.startswith('javascript:') or absolute_url.startswith('#'):
                    continue
                
                anchor_text = link.get_text(strip=True)
                rel = link.get('rel', [])
                rel_str = ' '.join(rel) if isinstance(rel, list) else rel
                
                links.append({
                    'url': absolute_url,
                    'anchor_text': anchor_text[:100] if anchor_text else '',
                    'rel': rel_str,
                })
        
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
        
        return links
    
    def get_internal_links(self, domain: str = None) -> List[Dict[str, str]]:
        """
        Get only internal (same-domain) links.
        
        Args:
            domain: Domain to filter by (extracted from base_url if not provided)
            
        Returns:
            List of internal links
        """
        if not domain:
            parsed = urlparse(self.base_url)
            domain = parsed.netloc
        
        internal = []
        for link in self.get_links():
            parsed = urlparse(link['url'])
            if parsed.netloc == domain:
                internal.append(link)
        
        return internal
    
    def get_external_links(self, domain: str = None) -> List[Dict[str, str]]:
        """
        Get only external (different-domain) links.
        
        Args:
            domain: Domain to filter by (extracted from base_url if not provided)
            
        Returns:
            List of external links
        """
        if not domain:
            parsed = urlparse(self.base_url)
            domain = parsed.netloc
        
        external = []
        for link in self.get_links():
            parsed = urlparse(link['url'])
            if parsed.netloc != domain:
                external.append(link)
        
        return external
    
    def get_headers(self) -> Dict[int, List[str]]:
        """
        Extract header hierarchy (h1-h6).
        
        Returns:
            Dictionary {level: [headers]}
        """
        if not self.soup:
            return {}
        
        headers = {}
        try:
            for i in range(1, 7):
                h_tags = self.soup.find_all(f'h{i}')
                if h_tags:
                    headers[i] = [h.get_text(strip=True) for h in h_tags]
        except Exception as e:
            logger.warning(f"Error extracting headers: {e}")
        
        return headers
    
    def get_language(self) -> Optional[str]:
        """
        Detect page language.
        
        Returns:
            Language code (e.g., 'sv', 'en')
        """
        if not self.soup:
            return None
        
        try:
            # Try html lang attribute
            html = self.soup.find('html')
            if html and html.get('lang'):
                lang = html.get('lang')
                return lang.split('-')[0].lower()  # en-US -> en
            
            # Try Content-Language meta
            meta_lang = self.soup.find('meta', attrs={'http-equiv': 'Content-Language'})
            if meta_lang and meta_lang.get('content'):
                return meta_lang.get('content').split('-')[0].lower()
        
        except Exception as e:
            logger.warning(f"Error detecting language: {e}")
        
        return None
    
    def get_charset(self) -> Optional[str]:
        """
        Extract charset.
        
        Returns:
            Charset (e.g., 'utf-8')
        """
        if not self.soup:
            return None
        
        try:
            # Try meta charset
            meta = self.soup.find('meta', attrs={'charset': True})
            if meta:
                return meta.get('charset')
            
            # Try http-equiv
            meta = self.soup.find('meta', attrs={'http-equiv': 'Content-Type'})
            if meta and meta.get('content'):
                content = meta.get('content')
                if 'charset=' in content:
                    return content.split('charset=')[1].split(';')[0]
        
        except Exception as e:
            logger.warning(f"Error extracting charset: {e}")
        
        return 'utf-8'  # Default
    
    def get_canonical_url(self) -> Optional[str]:
        """
        Get canonical URL if specified.
        
        Returns:
            Canonical URL or None
        """
        if not self.soup:
            return None
        
        try:
            canonical = self.soup.find('link', {'rel': 'canonical'})
            if canonical and canonical.get('href'):
                return canonical.get('href')
        except Exception as e:
            logger.warning(f"Error extracting canonical URL: {e}")
        
        return None


def extract_links(html: str, base_url: str) -> List[Dict[str, str]]:
    """
    Extract all links from HTML.
    
    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        
    Returns:
        List of link dictionaries
    """
    parser = HTMLParser(html, base_url)
    return parser.get_links()


def extract_text(html: str, max_length: int = None) -> str:
    """
    Extract text content from HTML.
    
    Args:
        html: HTML content
        max_length: Maximum length of text
        
    Returns:
        Text content
    """
    parser = HTMLParser(html, '')
    return parser.get_text(max_length)
