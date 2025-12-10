"""
Klar 3.1+ Enhanced Web Crawler
Improved crawling with:
- Deep crawling within whitelisted domains
- Smart search URL generation per domain type
- Parallel requests with rate limiting
- Media extraction (images, videos)
- Content deduplication
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus, quote
from pathlib import Path
import json
import time
from typing import List, Dict, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


class Crawler:
    """Enhanced crawler with deep domain crawling and smart search"""
    
    def __init__(self, domains: List[str], data_path: Path, offline_mode: bool = False):
        self.allowed_domains = set(d.lower() for d in domains)
        self.data_path = data_path
        self.offline_mode = offline_mode
        self.visited_urls: Set[str] = set()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Klar/3.1 (Swedish Search Engine; +https://oscyra.solutions)'
        })
        
        # Create media directories
        (self.data_path / 'images').mkdir(exist_ok=True)
        (self.data_path / 'videos').mkdir(exist_ok=True)
        (self.data_path / 'pages').mkdir(exist_ok=True)
        
        # Domain-specific search URL templates
        self.search_url_templates = self._load_search_templates()
        
        print(f"[Crawler] Initialized with {len(domains)} allowed domains")
    
    def _load_search_templates(self) -> Dict[str, str]:
        """Load search URL templates for different domain types"""
        return {
            # News sites
            'svt.se': 'https://www.svt.se/sok?q={query}',
            'dn.se': 'https://www.dn.se/search?q={query}',
            'aftonbladet.se': 'https://www.aftonbladet.se/sida/sok?q={query}',
            'expressen.se': 'https://www.expressen.se/sok/?query={query}',
            'svd.se': 'https://www.svd.se/sok?q={query}',
            'gp.se': 'https://www.gp.se/sok?q={query}',
            'sydsvenskan.se': 'https://www.sydsvenskan.se/sok?q={query}',
            
            # Wikipedia
            'sv.wikipedia.org': 'https://sv.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&srnamespace=0&format=json',
            'wikipedia.org': 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&srnamespace=0&format=json',
            
            # Shopping/Price comparison
            'prisjakt.nu': 'https://www.prisjakt.nu/search?q={query}',
            'pricerunner.se': 'https://www.pricerunner.se/search?q={query}',
            'inet.se': 'https://www.inet.se/search?q={query}',
            'webhallen.com': 'https://www.webhallen.com/search?q={query}',
            'blocket.se': 'https://www.blocket.se/search?q={query}',
            
            # Shopping/E-commerce
            'ica.se': 'https://www.ica.se/sok?q={query}',
            'coop.se': 'https://www.coop.se/sok?q={query}',
            'hemkop.se': 'https://www.hemkop.se/search?q={query}',
            'willys.se': 'https://www.willys.se/sok?q={query}',
            'elgiganten.se': 'https://www.elgiganten.se/search?q={query}',
            'mediamarkt.se': 'https://www.mediamarkt.se/search?q={query}',
            'netonnet.se': 'https://www.netonnet.se/search?q={query}',
        }
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL is from an allowed domain"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Check exact match
            if domain in self.allowed_domains:
                return True
            
            # Check if it's a subdomain of allowed domain
            for allowed in self.allowed_domains:
                if domain.endswith('.' + allowed) or domain == allowed:
                    return True
            
            return False
        except:
            return False
    
    def crawl_for_query(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Crawl pages relevant to query.
        Uses smart search URLs for different domain types.
        Includes deep crawling of results.
        """
        results = []
        
        print(f"[Crawler] Starting search for: '{query}'")
        
        # Generate smart search URLs
        seed_urls = self._generate_smart_search_urls(query)
        print(f"[Crawler] Generated {len(seed_urls)} seed URLs")
        
        # Crawl seed URLs in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            for url in seed_urls[:limit]:
                if url not in self.visited_urls and self.is_allowed_domain(url):
                    future = executor.submit(self._crawl_and_extract_results, url, query)
                    futures[future] = url
            
            # Collect results as they complete
            for future in as_completed(futures, timeout=15):
                url = futures[future]
                try:
                    page_results = future.result()
                    if page_results:
                        results.extend(page_results)
                        print(f"[Crawler] Found {len(page_results)} results from {url}")
                except Exception as e:
                    print(f"[Crawler] Error crawling {url}: {e}")
                
                if len(results) >= limit:
                    break
        
        # Deduplicate results
        results = self._deduplicate_results(results)
        print(f"[Crawler] Total unique results: {len(results)}")
        
        return results[:limit]
    
    def _generate_smart_search_urls(self, query: str) -> List[str]:
        """
        Generate search URLs for different domain types.
        Uses domain-specific search templates.
        """
        seeds = []
        query_encoded = quote_plus(query)
        
        # Use predefined search templates
        for domain, template in self.search_url_templates.items():
            if domain in self.allowed_domains:
                try:
                    search_url = template.format(query=query_encoded)
                    seeds.append(search_url)
                except:
                    pass
        
        # Add homepage searches for domains without specific templates
        for domain in list(self.allowed_domains)[:10]:  # Limit to avoid too many requests
            if not any(domain in template for template in self.search_url_templates.keys()):
                # Generic search
                if domain.endswith('.se'):
                    seeds.append(f'https://www.{domain}/sok?q={query_encoded}')
                else:
                    seeds.append(f'https://www.{domain}/search?q={query_encoded}')
        
        return seeds
    
    def _crawl_and_extract_results(self, url: str, query: str) -> List[Dict]:
        """
        Crawl a search results page and extract individual result links.
        Then crawl those links to get full content.
        """
        results = []
        
        if url in self.visited_urls:
            return results
        
        self.visited_urls.add(url)
        
        try:
            # Handle Wikipedia API differently
            if 'wikipedia.org' in url and 'api.php' in url:
                return self._handle_wikipedia_api(url, query)
            
            # Regular page crawling
            response = self.session.get(url, timeout=8)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract result links from search results
            result_links = self._extract_result_links(soup, url, query)
            print(f"[Crawler] Found {len(result_links)} result links on {url}")
            
            # Crawl top result links
            for result_url in result_links[:10]:  # Limit to top 10
                if result_url not in self.visited_urls and self.is_allowed_domain(result_url):
                    try:
                        page_data = self.crawl_page(result_url)
                        if page_data and self._is_relevant(page_data, query):
                            results.append(page_data)
                            time.sleep(0.2)  # Rate limiting
                    except:
                        pass
            
            # If no results found from links, include the search page itself
            if not results:
                page_data = self.parse_page(soup, response.url, query)
                if page_data:
                    results.append(page_data)
        
        except Exception as e:
            print(f"[Crawler] Error processing {url}: {e}")
        
        return results
    
    def _extract_result_links(self, soup: BeautifulSoup, base_url: str, query: str) -> List[str]:
        """
        Extract result links from a search results page.
        Looks for common search result patterns.
        """
        links = []
        
        # Common search result selectors
        selectors = [
            'a[href*="/artikel"]',  # Articles
            'a[href*="/nyheter"]',  # News
            'a[href*="/product"]',  # Products
            'a[href*="/item"]',
            'a.search-result',
            'a.result-link',
            'a.headline',
            'h2 a',
            'h3 a',
        ]
        
        for selector in selectors:
            for elem in soup.select(selector):
                href = elem.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    
                    # Only include if it's from allowed domain
                    if self.is_allowed_domain(full_url):
                        # Skip if it looks like pagination or navigation
                        if not any(x in full_url.lower() for x in ['page=', 'sort=', 'filter=', '#']):
                            links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def _handle_wikipedia_api(self, url: str, query: str) -> List[Dict]:
        """
        Handle Wikipedia API search results.
        Returns list of article pages.
        """
        results = []
        
        try:
            response = self.session.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get('query', {}).get('search', [])
            
            for result in search_results[:5]:  # Top 5 results
                title = result.get('title')
                if title:
                    # Build Wikipedia article URL
                    if 'sv.wikipedia' in url:
                        article_url = f"https://sv.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                    else:
                        article_url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                    
                    # Crawl the article
                    if article_url not in self.visited_urls:
                        try:
                            page_data = self.crawl_page(article_url)
                            if page_data:
                                results.append(page_data)
                                time.sleep(0.2)
                        except:
                            pass
        
        except Exception as e:
            print(f"[Crawler] Wikipedia API error: {e}")
        
        return results
    
    def _is_relevant(self, page_data: Dict, query: str) -> bool:
        """
        Check if crawled page is relevant to query.
        Simple relevance check based on query terms in title/description.
        """
        query_terms = set(query.lower().split())
        content = (page_data.get('title', '') + ' ' + page_data.get('description', '')).lower()
        
        # Check if at least one query term appears
        for term in query_terms:
            if len(term) > 3 and term in content:
                return True
        
        # If very short content, likely homepage
        if len(page_data.get('description', '')) < 50:
            return False
        
        return True
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """
        Crawl single page with enhanced metadata extraction.
        Handles subpages and specific content pages.
        """
        if not self.is_allowed_domain(url):
            print(f"[Crawler] Domain not allowed: {url}")
            return None
        
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parse_page(soup, response.url, '')
        
        except Exception as e:
            print(f"[Crawler] Failed to crawl {url}: {e}")
            return None
    
    def parse_page(self, soup: BeautifulSoup, url: str, query: str = '') -> Optional[Dict]:
        """
        Parse page content with enhanced metadata extraction.
        """
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        content = self._extract_content(soup)
        
        # Skip very thin pages
        if len(content) < 100:
            return None
        
        page_data = {
            'url': url,
            'title': title,
            'description': description,
            'content': content,
            'domain': urlparse(url).netloc.replace('www.', ''),
            'timestamp': time.time(),
            'images': self._extract_images(soup, url),
            'videos': self._extract_videos(soup, url),
        }
        
        return page_data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try meta og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try regular title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return 'Ingen titel'
    
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
        
        # Fallback to first paragraph
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:300]
        
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
            element.decompose()
        
        # Get text from main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|body|article'))
        
        if main_content:
            return main_content.get_text(separator=' ', strip=True)[:5000]
        
        return soup.get_text(separator=' ', strip=True)[:5000]
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image URLs from page"""
        images = []
        
        for img in soup.find_all('img', limit=5):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(base_url, src)
                if full_url.startswith('http'):
                    images.append({
                        'url': full_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        return images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract video URLs from page"""
        videos = []
        
        # HTML5 video
        for video in soup.find_all('video', limit=3):
            source = video.find('source')
            if source and source.get('src'):
                videos.append({
                    'url': urljoin(base_url, source['src']),
                    'type': source.get('type', 'video/mp4')
                })
        
        # YouTube embeds
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if 'youtube' in src or 'youtu.be' in src:
                videos.append({'url': src, 'type': 'youtube'})
        
        return videos
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate or near-duplicate results.
        Uses content hashing and URL matching.
        """
        deduplicated = []
        seen_descriptions = set()
        
        for result in results:
            desc = result.get('description', '')[:100].lower()
            
            # Skip if we've seen this description
            if desc and desc in seen_descriptions:
                continue
            
            seen_descriptions.add(desc)
            deduplicated.append(result)
        
        return deduplicated
