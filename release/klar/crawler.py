import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
import random
import time

class EnhancedSwedishCrawler:
    """
    Enhanced crawler that works for ALL Swedish domains, not just news
    Fixes the issue where only news sites work
    """
    
    def __init__(self, domain_metadata, max_pages=50, concurrent_limit=5):
        self.domain_metadata = domain_metadata
        self.max_pages = max_pages
        self.concurrent_limit = concurrent_limit
        self.cache = {}
        
        # Enhanced URL patterns for different domain types
        self.domain_url_patterns = {
            # News sites
            'news': {
                'domains': ['svt.se', 'dn.se', 'aftonbladet.se', 'expressen.se', 'svd.se', 'gp.se'],
                'paths': ['/nyheter', '/senaste', '/aktuellt', '/artikel', '/news', '/', '/sport', '/kultur']
            },
            
            # Government sites  
            'government': {
                'domains': ['skatteverket.se', 'regeringen.se', 'polisen.se', 'forsakringskassan.se', 'arbetsformedlingen.se'],
                'paths': ['/', '/privat', '/foretag', '/tjanster', '/information', '/kontakt', '/om-oss']
            },
            
            # Commerce sites
            'commerce': {
                'domains': ['blocket.se', 'tradera.com', 'ica.se', 'coop.se', 'prisjakt.nu'],
                'paths': ['/', '/kategorier', '/produkter', '/erbjudanden', '/butiker', '/om-oss']
            },
            
            # Education sites
            'education': {
                'domains': ['kth.se', 'uu.se', 'lu.se', 'su.se', 'liu.se', 'hh.se'],
                'paths': ['/', '/utbildning', '/program', '/kurser', '/forskning', '/om-oss', '/kontakt']
            },
            
            # Municipality sites
            'municipal': {
                'domains': ['stockholm.se', 'goteborg.se', 'malmo.se'],
                'paths': ['/', '/invånare', '/foretag', '/besokare', '/kommun', '/tjanster']
            },
            
            # Sports sites
            'sports': {
                'domains': ['svenskfotboll.se', 'hockeysverige.se', 'bandy.se'],
                'paths': ['/', '/nyheter', '/resultat', '/tabeller', '/matcher']
            }
        }
        
        # Headers to appear more like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def generate_domain_urls(self, domain, keywords):
        """Generate comprehensive URLs for a specific domain"""
        urls = []
        
        # Determine domain type
        domain_type = self._classify_domain(domain)
        
        # Base URL
        urls.append(f"https://{domain}")
        
        # Add type-specific paths
        if domain_type in self.domain_url_patterns:
            paths = self.domain_url_patterns[domain_type]['paths']
            for path in paths[:8]:  # Limit to prevent too many URLs
                urls.append(f"https://{domain}{path}")
        
        # Add keyword-based URLs (for better content discovery)
        for keyword in keywords[:3]:  # Top 3 keywords only
            # Try common Swedish URL patterns
            keyword_clean = keyword.replace(' ', '-').lower()
            potential_paths = [
                f"/{keyword_clean}",
                f"/kategori/{keyword_clean}",
                f"/om/{keyword_clean}", 
                f"/information/{keyword_clean}"
            ]
            
            for path in potential_paths[:2]:  # Limit per keyword
                urls.append(f"https://{domain}{path}")
        
        return list(set(urls))  # Remove duplicates
    
    def _classify_domain(self, domain):
        """Classify domain type for appropriate crawling strategy"""
        for domain_type, config in self.domain_url_patterns.items():
            if domain in config['domains']:
                return domain_type
        
        # Default classification based on domain patterns
        if 'kommun' in domain or any(city in domain for city in ['stockholm', 'goteborg', 'malmo']):
            return 'municipal'
        elif any(word in domain for word in ['skatt', 'polis', 'regering', 'myndighet']):
            return 'government'
        elif any(word in domain for word in ['handel', 'shop', 'butik']):
            return 'commerce'
        elif any(word in domain for word in ['universitet', 'hogskola', 'kth', 'uu']):
            return 'education'
        else:
            return 'news'  # Default fallback
    
    async def fetch_single_url(self, url):
        """Fetch a single URL with enhanced error handling"""
        if url in self.cache:
            return self.cache[url]
        
        try:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'text/html' in content_type:
                            text = await response.text()
                            
                            # Basic Swedish content check
                            if self.is_swedish_content(text):
                                self.cache[url] = text
                                return text
                    
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        
        return None
    
    def is_swedish_content(self, text):
        """Enhanced Swedish content detection"""
        if not text or len(text) < 100:
            return False
        
        text_lower = text.lower()
        
        # Swedish character check
        swedish_chars = len([c for c in text_lower if c in 'åäö'])
        char_ratio = swedish_chars / len(text) if text else 0
        
        # Swedish word indicators (expanded list)
        swedish_words = [
            'och', 'att', 'för', 'på', 'är', 'som', 'av', 'till', 'den', 'det',
            'svenska', 'sverige', 'kronor', 'myndighet', 'kommun', 'tjänster',
            'information', 'kontakt', 'hem', 'nyheter', 'senaste', 'mer'
        ]
        
        word_matches = sum(1 for word in swedish_words if word in text_lower)
        
        # Content is Swedish if it has enough indicators
        return char_ratio > 0.001 or word_matches >= 3
    
    def score_url_relevance(self, url, query_keywords=None):
        """Score URL relevance for better prioritization"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        score = 0
        
        # Domain trust score
        if domain in self.domain_metadata:
            score += 10
        
        # HTTPS bonus
        if parsed.scheme == 'https':
            score += 2
        
        # Path relevance
        high_value_paths = ['/', '/nyheter', '/tjanster', '/information', '/om-oss', '/kontakt']
        if any(path.startswith(hvp) for hvp in high_value_paths):
            score += 5
        
        # Keyword relevance (if provided)
        if query_keywords:
            for keyword in query_keywords:
                if keyword.lower() in url.lower():
                    score += 3
        
        # Avoid low-value URLs
        avoid_patterns = ['cookie', 'gdpr', 'login', 'admin', 'api', 'rss', 'feed']
        if any(pattern in url.lower() for pattern in avoid_patterns):
            score -= 5
        
        return max(score, 0)
    
    async def find_seeds(self, query: str):
        """Enhanced seed finding for better domain coverage"""
        query_tokens = [t.lower().strip() for t in query.split() if t.strip()]
        seeds = []
        
        # Score domains based on query relevance
        domain_scores = {}
        
        for domain, keywords in self.domain_metadata.items():
            score = 0
            
            # Check domain name match
            if any(token in domain.lower() for token in query_tokens):
                score += 10
            
            # Check keyword matches (expanded matching)
            for keyword in keywords:
                keyword_lower = keyword.lower()
                for token in query_tokens:
                    if token in keyword_lower or keyword_lower in token:
                        score += 3
                    # Partial matches for compound words
                    if len(token) > 4 and any(token[i:i+4] in keyword_lower for i in range(len(token)-3)):
                        score += 1
            
            domain_scores[domain] = score
        
        # Sort domains by relevance and select top ones
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take top domains or fallback to default list
        selected_domains = []
        for domain, score in sorted_domains:
            if score > 0:
                selected_domains.append(domain)
            if len(selected_domains) >= 8:  # Limit to avoid too many
                break
        
        # If no relevant domains found, use default Swedish domains
        if not selected_domains:
            selected_domains = [
                'svt.se', 'dn.se', 'skatteverket.se', 'blocket.se', 
                'stockholm.se', 'kth.se', 'ica.se'
            ]
        
        # Convert to URLs
        for domain in selected_domains:
            seeds.extend(self.generate_domain_urls(domain, query_tokens))
        
        print(f"Generated {len(seeds)} seed URLs from {len(selected_domains)} domains")
        return seeds[:20]  # Limit total seeds
    
    async def crawl(self, seeds):
        """Enhanced crawling with better success rates"""
        pages = {}
        
        # Prioritize seeds by relevance
        prioritized_seeds = []
        for seed in seeds:
            score = self.score_url_relevance(seed)
            prioritized_seeds.append((seed, score))
        
        prioritized_seeds.sort(key=lambda x: x[1], reverse=True)
        
        # Crawl with controlled concurrency
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        
        async def fetch_with_semaphore(url):
            async with semaphore:
                # Random delay to be respectful
                await asyncio.sleep(random.uniform(0.5, 1.5))
                return await self.fetch_single_url(url)
        
        # Process priority URLs first
        tasks = []
        urls_to_process = [url for url, score in prioritized_seeds[:self.max_pages]]
        
        for url in urls_to_process:
            task = asyncio.create_task(fetch_with_semaphore(url))
            tasks.append((url, task))
        
        # Collect results
        for url, task in tasks:
            try:
                html = await task
                if html and len(html) > 500:  # Minimum content threshold
                    pages[url] = html
                    
                    # Stop if we have enough good content
                    if len(pages) >= self.max_pages // 2:
                        break
                        
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
        print(f"Successfully crawled {len(pages)} pages")
        return pages
    
    def is_allowed_domain(self, url):
        """Check if domain is in our allowed list"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            
            # Must be in our domain list and be a .se domain (or approved .com/.fi)
            is_listed = domain in self.domain_metadata
            is_swedish_tld = (
                domain.endswith('.se') or 
                domain.endswith('.nu') or
                domain in ['tradera.com', 'visitsweden.com', 'svenska.yle.fi']
            )
            
            return is_listed and is_swedish_tld
            
        except Exception:
            return False