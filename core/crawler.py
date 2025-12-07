"""
Enhanced web crawler with video and image support
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import json
import time
from typing import List, Dict, Set
import mimetypes

class Crawler:
    def __init__(self, domains: List[str], data_path: Path, offline_mode: bool):
        self.allowed_domains = domains
        self.data_path = data_path
        self.offline_mode = offline_mode
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/3.0 (Swedish Search Engine; +https://klar.se/bot)'
        })
        
        # Create media directories
        (self.data_path / 'images').mkdir(exist_ok=True)
        (self.data_path / 'videos').mkdir(exist_ok=True)
        (self.data_path / 'pages').mkdir(exist_ok=True)
        
        print(f"[Crawler] Initialized with {len(domains)} allowed domains")
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL is from allowed domain"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for allowed in self.allowed_domains:
            if allowed in domain:
                return True
        return False
    
    def crawl_for_query(self, query: str, limit: int = 50) -> List[Dict]:
        """Crawl pages relevant to query"""
        results = []
        
        # Start with seed URLs from allowed domains
        seed_urls = self._generate_seed_urls(query)
        
        for url in seed_urls[:limit]:
            if url in self.visited_urls:
                continue
            
            try:
                page_data = self.crawl_page(url)
                if page_data:
                    results.append(page_data)
                    
                    if self.offline_mode:
                        self._save_page_offline(page_data)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"[Crawler] Error crawling {url}: {e}")
        
        return results
    
    def crawl_page(self, url: str) -> Dict:
        """Crawl single page with enhanced metadata extraction"""
        if not self.is_allowed_domain(url):
            return None
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract comprehensive metadata
            page_data = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'content': self._extract_content(soup),
                'images': self._extract_images(soup, url),
                'videos': self._extract_videos(soup, url),
                'meta_tags': self._extract_meta_tags(soup),
                'links': self._extract_links(soup, url),
                'timestamp': time.time()
            }
            
            return page_data
            
        except Exception as e:
            print(f"[Crawler] Failed to crawl {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try meta og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        # Try regular title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        # Fallback to first paragraph
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text().strip()[:200]
        
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text from main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            return main_content.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all images with metadata"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            full_url = urljoin(base_url, src)
            
            images.append({
                'url': full_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        return images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all videos with metadata"""
        videos = []
        
        # HTML5 video tags
        for video in soup.find_all('video'):
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    videos.append({
                        'url': urljoin(base_url, src),
                        'type': source.get('type', 'video/mp4'),
                        'poster': video.get('poster', '')
                    })
        
        # YouTube embeds
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if 'youtube.com' in src or 'youtu.be' in src:
                videos.append({
                    'url': src,
                    'type': 'youtube',
                    'title': iframe.get('title', '')
                })
        
        return videos
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict:
        """Extract all meta tags"""
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                meta_tags[name] = content
        
        return meta_tags
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all outgoing links"""
        links = []
        
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            if self.is_allowed_domain(full_url):
                links.append(full_url)
        
        return list(set(links))
    
    def _generate_seed_urls(self, query: str) -> List[str]:
        """Generate seed URLs for query"""
        seeds = []
        
        # Add major Swedish news sites
        news_sites = ['svt.se', 'dn.se', 'aftonbladet.se', 'expressen.se']
        for site in news_sites:
            seeds.append(f"https://{site}/sok?q={query}")
        
        # Add domain homepages
        for domain in self.allowed_domains[:20]:
            if domain.endswith('.se') or domain.endswith('.com'):
                seeds.append(f"https://{domain}")
        
        return seeds
    
    def _save_page_offline(self, page_data: Dict):
        """Save page data for offline use"""
        filename = self.data_path / 'pages' / f"{hash(page_data['url'])}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)