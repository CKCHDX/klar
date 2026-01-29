"""
Metadata Extractor for Klar 4.0
Extracts metadata from HTML pages (title, description, keywords, Open Graph, Twitter cards)
Enables Google-like search by indexing metadata tags
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
import re
from urllib.parse import urlparse


class MetadataExtractor:
    """Extract and process metadata from HTML pages"""
    
    def __init__(self):
        # Metadata fields to extract
        self.meta_fields = [
            'title',
            'description',
            'keywords',
            'og:title',
            'og:description',
            'og:type',
            'og:site_name',
            'twitter:title',
            'twitter:description',
            'twitter:card',
            'article:tag',
            'article:section',
            'article:published_time',
            'article:author'
        ]
        
    def extract_metadata(self, html: str, url: str) -> Dict[str, any]:
        """
        Extract all metadata from HTML page
        
        Args:
            html: HTML content
            url: Page URL
            
        Returns:
            Dictionary with extracted metadata
        """
        if not html:
            return self._empty_metadata(url)
            
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            'url': url,
            'domain': self._extract_domain(url),
            'path': self._extract_path(url),
            'title': self._extract_title(soup),
            'description': self._extract_description(soup),
            'keywords': self._extract_keywords(soup),
            'og_tags': self._extract_og_tags(soup),
            'twitter_tags': self._extract_twitter_tags(soup),
            'article_tags': self._extract_article_tags(soup),
            'headings': self._extract_headings(soup),
            'text_content': self._extract_text_content(soup),
            'links': self._extract_links(soup, url),
            'images': self._extract_images(soup, url)
        }
        
        return metadata
    
    def _empty_metadata(self, url: str) -> Dict:
        """Return empty metadata structure"""
        return {
            'url': url,
            'domain': self._extract_domain(url),
            'path': self._extract_path(url),
            'title': '',
            'description': '',
            'keywords': [],
            'og_tags': {},
            'twitter_tags': {},
            'article_tags': {},
            'headings': {'h1': [], 'h2': [], 'h3': []},
            'text_content': '',
            'links': [],
            'images': []
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''
    
    def _extract_path(self, url: str) -> str:
        """Extract path from URL"""
        try:
            parsed = urlparse(url)
            return parsed.path
        except:
            return ''
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try <title> tag first
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Fallback to h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc.get('content').strip()
        
        return ''
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords_str = meta_keywords.get('content')
            # Split by comma and clean
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            return keywords
        return []
    
    def _extract_og_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph tags"""
        og_tags = {}
        og_meta_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        
        for tag in og_meta_tags:
            property_name = tag.get('property', '')
            content = tag.get('content', '')
            if property_name and content:
                og_tags[property_name] = content.strip()
        
        return og_tags
    
    def _extract_twitter_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card tags"""
        twitter_tags = {}
        twitter_meta_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        
        for tag in twitter_meta_tags:
            name = tag.get('name', '')
            content = tag.get('content', '')
            if name and content:
                twitter_tags[name] = content.strip()
        
        return twitter_tags
    
    def _extract_article_tags(self, soup: BeautifulSoup) -> Dict[str, any]:
        """Extract article-specific tags"""
        article_tags = {}
        article_meta_tags = soup.find_all('meta', property=re.compile(r'^article:'))
        
        for tag in article_meta_tags:
            property_name = tag.get('property', '')
            content = tag.get('content', '')
            if property_name and content:
                # Handle multiple tags (like article:tag)
                if property_name == 'article:tag':
                    if 'article:tag' not in article_tags:
                        article_tags['article:tag'] = []
                    article_tags['article:tag'].append(content.strip())
                else:
                    article_tags[property_name] = content.strip()
        
        return article_tags
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract headings (h1, h2, h3)"""
        headings = {
            'h1': [],
            'h2': [],
            'h3': []
        }
        
        for level in ['h1', 'h2', 'h3']:
            tags = soup.find_all(level)
            headings[level] = [tag.get_text().strip() for tag in tags if tag.get_text().strip()]
        
        return headings
    
    def _extract_text_content(self, soup: BeautifulSoup, max_length: int = 5000) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract internal links"""
        links = []
        base_domain = self._extract_domain(base_url)
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Skip empty links
            if not href or href.startswith('#'):
                continue
            
            # Check if internal link
            if href.startswith('/') or base_domain in href:
                links.append({
                    'href': href,
                    'text': text
                })
        
        # Limit to 100 links
        return links[:100]
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images with alt text"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src:
                images.append({
                    'src': src,
                    'alt': alt
                })
        
        # Limit to 20 images
        return images[:20]
    
    def build_search_index(self, metadata: Dict) -> str:
        """
        Build searchable text index from metadata
        Combines all searchable fields with weights
        
        Returns:
            Single string for full-text search
        """
        parts = []
        
        # Title (highest weight - repeat 3x)
        if metadata.get('title'):
            parts.extend([metadata['title']] * 3)
        
        # Description (repeat 2x)
        if metadata.get('description'):
            parts.extend([metadata['description']] * 2)
        
        # Keywords (repeat 2x)
        if metadata.get('keywords'):
            parts.extend(metadata['keywords'] * 2)
        
        # OG tags
        og_tags = metadata.get('og_tags', {})
        if og_tags.get('og:title'):
            parts.append(og_tags['og:title'])
        if og_tags.get('og:description'):
            parts.append(og_tags['og:description'])
        
        # Article tags
        article_tags = metadata.get('article_tags', {})
        if article_tags.get('article:tag'):
            parts.extend(article_tags['article:tag'])
        if article_tags.get('article:section'):
            parts.append(article_tags['article:section'])
        
        # Headings
        headings = metadata.get('headings', {})
        parts.extend(headings.get('h1', []))
        parts.extend(headings.get('h2', []))
        
        # Text content (truncated)
        if metadata.get('text_content'):
            parts.append(metadata['text_content'][:1000])
        
        # Combine all parts
        return ' '.join(parts)
    
    def extract_subpage_structure(self, metadata: Dict) -> Dict[str, any]:
        """
        Extract subpage structure information
        Useful for discovering related pages on same domain
        
        Returns:
            Structure information about the page
        """
        domain = metadata.get('domain', '')
        path = metadata.get('path', '')
        
        # Parse path into sections
        path_parts = [p for p in path.split('/') if p]
        
        structure = {
            'domain': domain,
            'path': path,
            'path_depth': len(path_parts),
            'path_parts': path_parts,
            'section': path_parts[0] if path_parts else None,
            'subsection': path_parts[1] if len(path_parts) > 1 else None,
            'is_homepage': len(path_parts) == 0,
            'internal_links': metadata.get('links', []),
            'related_sections': self._extract_related_sections(metadata)
        }
        
        return structure
    
    def _extract_related_sections(self, metadata: Dict) -> Set[str]:
        """Extract related sections from links"""
        sections = set()
        
        for link in metadata.get('links', []):
            href = link.get('href', '')
            if href.startswith('/'):
                # Extract first part of path
                parts = [p for p in href.split('/') if p]
                if parts:
                    sections.add(parts[0])
        
        return list(sections)
