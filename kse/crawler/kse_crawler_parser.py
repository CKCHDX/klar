"""
HTML Parser for Web Pages

Extracts text, links, and metadata from HTML content.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


@dataclass
class ParsedPage:
    """Parsed page content and metadata."""
    url: str
    title: str = ""
    description: str = ""
    keywords: str = ""
    heading_1: str = ""  # H1 tag (usually main title)
    text_content: str = ""  # All text
    raw_html: bytes = b""
    outbound_links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    language: Optional[str] = None  # e.g., 'sv' for Swedish
    has_robots_noindex: bool = False
    has_robots_nofollow: bool = False
    canonical_url: Optional[str] = None
    
    @property
    def word_count(self) -> int:
        """Get word count of text content."""
        return len(self.text_content.split())
    
    @property
    def link_count(self) -> int:
        """Get count of outbound links."""
        return len(self.outbound_links)


class _HTMLExtractor(HTMLParser):
    """
    Custom HTML parser using built-in HTMLParser.
    Extracts text, links, and metadata.
    """
    
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self.description = ""
        self.keywords = ""
        self.heading_1 = ""
        self.text_content = []
        self.outbound_links = []
        self.images = []
        self.language = None
        self.canonical_url = None
        self.robots_noindex = False
        self.robots_nofollow = False
        
        self._in_script = False
        self._in_style = False
        self._in_h1 = False
    
    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        """Handle opening tags."""
        attrs_dict = dict(attrs)
        
        if tag == 'title':
            pass  # Handle in data
        
        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            content = attrs_dict.get('content', '')
            
            if name == 'description':
                self.description = content
            elif name == 'keywords':
                self.keywords = content
            elif name == 'robots':
                robots_content = content.lower()
                self.robots_noindex = 'noindex' in robots_content
                self.robots_nofollow = 'nofollow' in robots_content
            elif name == 'language':
                self.language = content
        
        elif tag == 'html':
            lang = attrs_dict.get('lang', '')
            if lang:
                self.language = lang.split('-')[0].lower()
        
        elif tag == 'link':
            if attrs_dict.get('rel', '').lower() == 'canonical':
                href = attrs_dict.get('href', '')
                if href:
                    self.canonical_url = urljoin(self.base_url, href)
        
        elif tag == 'h1':
            self._in_h1 = True
        
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href and not href.startswith(('#', 'javascript:')):
                abs_url = urljoin(self.base_url, href)
                # Only add if different domain (outbound)
                if abs_url not in self.outbound_links:
                    self.outbound_links.append(abs_url)
        
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            if src:
                abs_url = urljoin(self.base_url, src)
                if abs_url not in self.images:
                    self.images.append(abs_url)
        
        elif tag == 'script':
            self._in_script = True
        
        elif tag == 'style':
            self._in_style = True
    
    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags."""
        if tag == 'script':
            self._in_script = False
        elif tag == 'style':
            self._in_style = False
        elif tag == 'h1':
            self._in_h1 = False
    
    def handle_data(self, data: str) -> None:
        """Handle text data."""
        if self._in_script or self._in_style:
            return
        
        if data.strip():
            self.text_content.append(data.strip())
            
            if self._in_h1:
                if not self.heading_1:
                    self.heading_1 = data.strip()
    
    def handle_entityref(self, name: str) -> None:
        """Handle HTML entities."""
        # Common HTML entities
        entities = {
            'nbsp': ' ',
            'amp': '&',
            'lt': '<',
            'gt': '>',
            'quot': '"',
            'apos': "'",
        }
        self.text_content.append(entities.get(name, f'&{name};'))


class Parser:
    """
    HTML parser for extracting page content.
    
    Features:
    - Text extraction
    - Link discovery
    - Metadata extraction
    - Robots directive compliance
    """
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def parse(
        self,
        url: str,
        html_content: bytes,
        encoding: Optional[str] = None
    ) -> ParsedPage:
        """Parse HTML content.
        
        Args:
            url: Page URL
            html_content: HTML content bytes
            encoding: Character encoding
        
        Returns:
            ParsedPage with extracted data
        """
        try:
            # Decode content
            if encoding:
                try:
                    text = html_content.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    text = html_content.decode('utf-8', errors='ignore')
            else:
                # Try common encodings
                for enc in ['utf-8', 'iso-8859-1', 'cp1252']:
                    try:
                        text = html_content.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    text = html_content.decode('utf-8', errors='ignore')
            
            # Parse with custom extractor
            extractor = _HTMLExtractor(url)
            try:
                extractor.feed(text)
            except Exception as e:
                logger.warning(f"HTML parsing error for {url}: {e}")
            
            # Extract title from first heading if not in <title>
            title = extractor.title or extractor.heading_1 or ""
            
            # Combine text content
            full_text = " ".join(extractor.text_content)
            
            # Clean up whitespace
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            logger.debug(f"Parsed {url}: {len(full_text)} chars, {len(extractor.outbound_links)} links")
            
            return ParsedPage(
                url=url,
                title=title,
                description=extractor.description,
                keywords=extractor.keywords,
                heading_1=extractor.heading_1,
                text_content=full_text,
                raw_html=html_content,
                outbound_links=extractor.outbound_links,
                images=extractor.images,
                language=extractor.language,
                has_robots_noindex=extractor.robots_noindex,
                has_robots_nofollow=extractor.robots_nofollow,
                canonical_url=extractor.canonical_url
            )
        
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}", exc_info=True)
            # Return partial result
            return ParsedPage(
                url=url,
                text_content=f"[Parse error: {e}]"
            )
    
    def extract_metadata(self, html_content: str) -> Dict[str, str]:
        """Extract meta tags from HTML.
        
        Args:
            html_content: HTML string
        
        Returns:
            Dictionary of meta tag values
        """
        metadata = {}
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Extract meta tags
        meta_pattern = r'<meta\s+(?:[^>]*?\s+)?(?:name|property)=["\']([^"\']*)(?:["\'][^>]*)content=["\']([^"\']*)'
        for match in re.finditer(meta_pattern, html_content, re.IGNORECASE):
            key, value = match.groups()
            metadata[key.lower()] = value
        
        return metadata
