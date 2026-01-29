"""
KSE HTML Extractor - HTML parsing and content extraction
"""
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from kse.core.kse_exceptions import CrawlerError
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "crawler.log")


class HTMLExtractor:
    """Extract content and links from HTML pages"""
    
    def __init__(self):
        """Initialize HTML extractor"""
        self.parser = "lxml"  # Use lxml parser for speed
    
    def extract_content(self, html: str, base_url: str) -> Dict[str, any]:
        """
        Extract content from HTML
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
        
        Returns:
            Dictionary with extracted content
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract metadata
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            keywords = self._extract_keywords(soup)
            
            # Extract main content
            text_content = self._extract_text(soup)
            
            # Extract links
            links = self._extract_links(soup, base_url)
            
            # Extract metadata
            lang = soup.html.get('lang', 'sv') if soup.html else 'sv'
            
            result = {
                'title': title,
                'description': description,
                'keywords': keywords,
                'content': text_content,
                'links': links,
                'language': lang,
                'url': base_url
            }
            
            logger.debug(f"Extracted content from {base_url}: {len(text_content)} chars, {len(links)} links")
            return result
        
        except Exception as e:
            logger.error(f"Failed to extract content from {base_url}: {e}")
            raise CrawlerError(f"HTML extraction failed: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try first paragraph
        p = soup.find('p')
        if p:
            text = p.get_text().strip()
            return text[:200] + '...' if len(text) > 200 else text
        
        return ""
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords['content'].split(',')])
        
        return keywords
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=['content', 'main-content', 'article', 'post']) or
            soup.body or
            soup
        )
        
        if main_content:
            # Get text and clean it
            text = main_content.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text
        
        return ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize all links"""
        links = []
        seen = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Resolve relative URLs
            try:
                absolute_url = urljoin(base_url, href)
                
                # Parse and normalize
                parsed = urlparse(absolute_url)
                
                # Reconstruct without fragment
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    normalized += f"?{parsed.query}"
                
                # Add if not seen
                if normalized not in seen and self._is_valid_link(normalized):
                    links.append(normalized)
                    seen.add(normalized)
            
            except Exception as e:
                logger.debug(f"Failed to process link {href}: {e}")
                continue
        
        return links
    
    def _is_valid_link(self, url: str) -> bool:
        """Check if link is valid for crawling"""
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Must be http or https
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Skip common file types we don't want to crawl
            excluded_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.tar', '.gz', '.rar', '.7z',
                '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
                '.mp3', '.mp4', '.avi', '.mov', '.wmv',
                '.css', '.js', '.xml', '.json'
            ]
            
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in excluded_extensions):
                return False
            
            return True
        
        except Exception:
            return False
    
    def extract_metadata(self, html: str) -> Dict[str, str]:
        """
        Extract only metadata without full content
        
        Args:
            html: HTML content
        
        Returns:
            Dictionary with metadata
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            
            return {
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'keywords': self._extract_keywords(soup),
            }
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {}
