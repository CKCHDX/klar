"""
HTML Content Parser
Extract and parse HTML content with category detection
"""

from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import re


class Parser:
    """Parse HTML content and extract relevant information"""
    
    def __init__(self):
        self.category_indicators = {
            'news': ['breaking', 'nyhet', 'senaste', 'aktuell', 'händelse'],
            'weather': ['väder', 'temperatur', 'prognos', 'grad', 'vind'],
            'health': ['hälsa', 'sjukdom', 'symptom', 'medicin', 'behandling'],
            'jobs': ['jobb', 'anställning', 'lediga', 'arbete', 'tjänst'],
            'sports': ['sport', 'fotboll', 'hockey', 'match', 'resultat'],
            'food': ['mat', 'recept', 'matlagning', 'ingrediens', 'dryck'],
            'travel': ['resa', 'hotell', 'flyg', 'destination', 'resemål'],
        }
    
    def parse(self, html: str) -> Dict:
        """
        Parse HTML content and extract key information
        Returns: Dict with title, content, snippets, date, etc
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract meta description
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract snippets
            snippets = self.extract_snippets(content)
            
            # Extract date
            date = self._extract_date(soup)
            
            # Detect category
            category = self._detect_category(content + ' ' + (title or ''))
            
            return {
                'title': title,
                'description': description,
                'content': content,
                'snippets': snippets,
                'date': date,
                'category': category,
                'word_count': len(content.split())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_main_content(self, soup) -> str:
        """Extract main content from HTML"""
        # Try to find main content areas
        main_areas = soup.find_all(['main', 'article', 'div'])
        
        content_text = ''
        for area in main_areas:
            # Skip navigation, header, footer
            if area.name in ['nav', 'header', 'footer']:
                continue
            
            # Get text from area
            text = area.get_text()
            if len(text) > len(content_text):
                content_text = text
        
        # If nothing found, use body
        if not content_text:
            body = soup.find('body')
            content_text = body.get_text() if body else ''
        
        # Clean up whitespace
        content_text = ' '.join(content_text.split())
        return content_text[:2000]  # First 2000 chars
    
    def extract_snippets(self, content: str, num_snippets: int = 3) -> List[str]:
        """
        Extract 2-3 sentence snippets from content
        Returns: List of snippets
        """
        # Split by sentence (simple approach)
        sentences = re.split(r'[.!?]+', content)
        snippets = []
        
        for sentence in sentences[:num_snippets]:
            cleaned = sentence.strip()
            if len(cleaned) > 20:  # Only snippets with substance
                snippets.append(cleaned + '.')
        
        return snippets
    
    def _extract_date(self, soup) -> Optional[str]:
        """
        Extract publication date from HTML
        Returns: Date string or None
        """
        # Try common date attributes
        date_selectors = [
            soup.find('time'),
            soup.find('meta', attrs={'property': 'article:published_time'}),
            soup.find('meta', attrs={'name': 'publish_date'}),
        ]
        
        for selector in date_selectors:
            if selector:
                if selector.name == 'time':
                    return selector.get('datetime')
                else:
                    return selector.get('content')
        
        return None
    
    def _detect_category(self, text: str) -> Optional[str]:
        """
        Detect content category from text
        Returns: Category name or None
        """
        text_lower = text.lower()
        
        for category, indicators in self.category_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if matches >= 2:  # At least 2 matches
                return category
        
        return None
    
    def extract_links(self, html: str, limit: int = 10) -> List[Dict]:
        """
        Extract links from HTML
        Returns: List of links with text and href
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', limit=limit):
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and text:
                    links.append({
                        'text': text,
                        'href': href
                    })
            
            return links
        except:
            return []
    
    def extract_images(self, html: str, limit: int = 5) -> List[Dict]:
        """
        Extract images from HTML
        Returns: List of images with src and alt text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            for img in soup.find_all('img', limit=limit):
                src = img.get('src')
                alt = img.get('alt', '')
                
                if src:
                    images.append({
                        'src': src,
                        'alt': alt
                    })
            
            return images
        except:
            return []
