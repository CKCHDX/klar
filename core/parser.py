"""
HTML parser with enhanced metadata extraction
"""
from bs4 import BeautifulSoup
from typing import Dict

class Parser:
    def __init__(self):
        pass
    
    def parse_html(self, html: str, url: str) -> Dict:
        """Parse HTML and extract structured data"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'url': url,
            'title': self._get_title(soup),
            'description': self._get_description(soup),
            'content': self._get_content(soup),
            'meta': self._get_meta_tags(soup)
        }
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        title = soup.find('title')
        return title.get_text() if title else ''
    
    def _get_description(self, soup: BeautifulSoup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'] if meta and meta.get('content') else ''
    
    def _get_content(self, soup: BeautifulSoup) -> str:
        for element in soup(['script', 'style']):
            element.decompose()
        return soup.get_text(separator=' ', strip=True)
    
    def _get_meta_tags(self, soup: BeautifulSoup) -> Dict:
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        return meta_tags