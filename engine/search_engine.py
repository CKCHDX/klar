"""
Enhanced search with phrase matching, subpage discovery, and demographic optimization
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import json
from pathlib import Path
import time
from typing import List, Dict, Set, Tuple

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource - works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class SearchEngine:
    def __init__(self):
        self.data_path = Path("klar_data")
        self.data_path.mkdir(exist_ok=True)
        
        # Load domains using resource path for PyInstaller
        domains_file = get_resource_path("domains.json")
        print(f"[DEBUG] Looking for domains.json at: {domains_file}")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r', encoding='utf-8') as f:
                    self.domains = json.load(f)
                print(f"[DEBUG] Loaded {len(self.domains)} domains")
            except Exception as e:
                print(f"[ERROR] Failed to load domains.json: {e}")
                self.domains = []
        else:
            print(f"[ERROR] domains.json not found at: {domains_file}")
            self.domains = []
        
        # Load keyword database using resource path
        keywords_file = get_resource_path("keywords_db.json")
        print(f"[DEBUG] Looking for keywords_db.json at: {keywords_file}")
        
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    self.keyword_db = json.load(f)
                print(f"[DEBUG] Loaded keyword database")
            except Exception as e:
                print(f"[ERROR] Failed to load keywords_db.json: {e}")
                self.keyword_db = {'version': '1.0', 'mappings': {}, 'direct_domain_mappings': {}}
        else:
            print(f"[ERROR] keywords_db.json not found at: {keywords_file}")
            self.keyword_db = {'version': '1.0', 'mappings': {}, 'direct_domain_mappings': {}}
        
        # Categorize domains
        self.domain_categories = self._categorize_domains()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        total_keywords = sum(len(v.get('keywords', [])) for v in self.keyword_db.get('mappings', {}).values())
        print(f"[Klar] Search engine initialized")
        print(f"[Klar] Domains: {len(self.domains)}")
        print(f"[Klar] Keywords: {total_keywords}")
        print(f"[Klar] Categories: {len(self.domain_categories)}")

    
    def _load_keyword_database(self) -> Dict:
        """Load keyword database from JSON"""
        keywords_file = Path("keywords_db.json")
        
        if keywords_file.exists():
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("[Warning] keywords_db.json not found")
            return {'version': '1.0', 'mappings': {}, 'direct_domain_mappings': {}}
    
    def _categorize_domains(self) -> Dict[str, List[str]]:
        """Categorize domains"""
        categories = {}
        
        for mapping_name, mapping_data in self.keyword_db['mappings'].items():
            category = mapping_data.get('category', 'general')
            domains = mapping_data.get('priority_domains', [])
            
            if category not in categories:
                categories[category] = []
            
            categories[category].extend(domains)
        
        for category in categories:
            categories[category] = list(set(categories[category]))
        
        return categories
    
    def detect_query_intent(self, query: str) -> Tuple[List[str], List[str]]:
        """Detect query intent - now supports phrases"""
        query_lower = query.lower()
        detected_categories = []
        priority_domains = []
        
        # Check direct domain mappings
        direct_mappings = self.keyword_db.get('direct_domain_mappings', {})
        for keyword, domains in direct_mappings.items():
            if keyword in query_lower:
                priority_domains.extend(domains)
        
        # Check keyword mappings (now matches phrases)
        for mapping_name, mapping_data in self.keyword_db['mappings'].items():
            keywords = mapping_data.get('keywords', [])
            category = mapping_data.get('category', 'general')
            domains = mapping_data.get('priority_domains', [])
            
            # Check if any keyword matches
            for keyword in keywords:
                # Support partial word matching for phrases
                if keyword in query_lower or any(word in query_lower for word in keyword.split()):
                    if category not in detected_categories:
                        detected_categories.append(category)
                    priority_domains.extend(domains)
                    break
        
        priority_domains = list(dict.fromkeys(priority_domains))
        
        return detected_categories, priority_domains
    
    def get_relevant_domains(self, query: str, demographic: str = "general") -> List[str]:
        """Get relevant domains with demographic optimization"""
        if '.' in query and ' ' not in query:
            domain = query.lower().replace('www.', '')
            if domain in self.domains:
                return [domain]
        
        categories, priority_domains = self.detect_query_intent(query)
        relevant_domains = []
        relevant_domains.extend(priority_domains)
        
        for category in categories:
            if category in self.domain_categories:
                relevant_domains.extend(self.domain_categories[category])
        
        if not relevant_domains:
            # NEW: Default domains based on demographic
            defaults = {
                'seniors_65plus': ['1177.se', 'svt.se', 'folkhalsomyndigheten.se'],
                'women_general': ['hemnet.se', 'ica.se', 'svt.se'],
                'men_general': ['webhallen.com', 'inet.se', 'svt.se'],
                'teens_10to20': ['1177.se', 'svt.se', 'dn.se'],
                'young_adults_20to40': ['dn.se', 'aftonbladet.se', 'arbetsformedlingen.se'],
                'general': ['svt.se', 'dn.se', 'aftonbladet.se']
            }
            relevant_domains = defaults.get(demographic, defaults['general'])
        
        seen = set()
        result = []
        for domain in relevant_domains:
            if domain not in seen and domain in self.domains:
                seen.add(domain)
                result.append(domain)
        
        return result[:12]
    
    def get_demographic_hints(self, demographic: str) -> Dict:
        """Get result optimization hints for demographic"""
        hints = {
            'seniors_65plus': {
                'result_count': 5,
                'min_snippet_length': 200,
                'avoid_technical_jargon': True,
                'prioritize_safe_domains': True,
                'include_instructions': True,
                'language_style': 'simplified'
            },
            'women_general': {
                'result_count': 10,
                'min_snippet_length': 100,
                'include_reviews': True,
                'include_prices': True,
                'language_style': 'normal'
            },
            'men_general': {
                'result_count': 10,
                'min_snippet_length': 100,
                'include_technical_specs': True,
                'include_comparisons': True,
                'language_style': 'normal'
            },
            'teens_10to20': {
                'result_count': 10,
                'min_snippet_length': 100,
                'prioritize_safe_domains': True,
                'avoid_inappropriate_content': True,
                'educational_focus': True,
                'mental_health_resources': True,
                'language_style': 'casual'
            },
            'young_adults_20to40': {
                'result_count': 10,
                'min_snippet_length': 100,
                'include_latest_news': True,
                'language_style': 'professional'
            },
            'general': {
                'result_count': 10,
                'min_snippet_length': 100,
                'language_style': 'normal'
            }
        }
        
        return hints.get(demographic, hints['general'])
    
    def search(self, query: str, demographic: str = "general") -> Dict:
        """Main search with phrase support, subpage discovery, and demographic optimization"""
        print(f"\n[Search] Query: {query}")
        print(f"[Search] Demographic: {demographic}")
        
        relevant_domains = self.get_relevant_domains(query, demographic)
        categories, priority_domains = self.detect_query_intent(query)
        
        print(f"[Search] Detected: {', '.join(categories) if categories else 'general'}")
        print(f"[Search] Searching {len(relevant_domains)} domains")
        
        results = []
        
        # For phrases, we need to search more intelligently
        is_phrase = len(query.split()) > 1
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_domain = {}
            
            for domain in relevant_domains:
                # For phrases, try to find specific subpages
                if is_phrase:
                    future = executor.submit(self.search_domain_deeply, domain, query)
                else:
                    url = f"https://www.{domain}"
                    future = executor.submit(self.fetch_and_parse, url, query)
                
                future_to_domain[future] = domain
            
            for future in as_completed(future_to_domain, timeout=10):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    if result:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                        print(f"  ✓ {domain}")
                except:
                    print(f"  ✗ {domain}")
        
        # Rank results
        ranked_results = self.rank_results(results, query, priority_domains, demographic)
        
        # Get demographic hints for result limiting
        hints = self.get_demographic_hints(demographic)
        result_count = hints['result_count']
        
        return {
            'query': query,
            'results': ranked_results[:result_count],
            'total': len(ranked_results),
            'categories_used': categories,
            'is_phrase_search': is_phrase,
            'demographic': demographic,
            'demographic_hints': hints
        }
    
    def search_domain_deeply(self, domain: str, query: str) -> List[Dict]:
        """
        Deep search within a domain to find specific subpages
        This is especially useful for phrases like "smärta i nacken"
        """
        results = []
        
        try:
            # Start with homepage
            base_url = f"https://www.{domain}"
            response = self.session.get(base_url, timeout=(2, 5))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract internal links
            links = self.extract_internal_links(soup, base_url, domain)
            
            # Filter links that might be relevant to query
            relevant_links = self.filter_relevant_links(links, query)
            
            # Fetch top 3 most relevant subpages
            for link in relevant_links[:3]:
                try:
                    result = self.fetch_and_parse(link, query)
                    if result and result['relevance'] > 0.3:
                        results.append(result)
                except:
                    pass
            
            # Also include homepage if relevant
            homepage_result = self.parse_page(soup, base_url, query)
            if homepage_result and homepage_result['relevance'] > 0.1:
                results.append(homepage_result)
        
        except:
            pass
        
        return results
    
    def extract_internal_links(self, soup: BeautifulSoup, base_url: str, domain: str) -> List[str]:
        """Extract internal links from page"""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # Only internal links
            if domain in urlparse(full_url).netloc:
                links.append(full_url)
        
        return list(set(links))[:50]  # Limit to 50 links
    
    def filter_relevant_links(self, links: List[str], query: str) -> List[str]:
        """Filter links that might contain query terms"""
        query_terms = set(query.lower().split())
        scored_links = []
        
        for link in links:
            url_lower = link.lower()
            score = 0
            
            # Check if query terms appear in URL
            for term in query_terms:
                if term in url_lower:
                    score += 2
            
            # Prefer paths over parameters
            if '?' not in link:
                score += 1
            
            # Prefer shorter paths (usually more specific)
            path_depth = url_lower.count('/')
            if 3 <= path_depth <= 5:
                score += 1
            
            if score > 0:
                scored_links.append((score, link))
        
        # Sort by score
        scored_links.sort(reverse=True, key=lambda x: x[0])
        
        return [link for score, link in scored_links]
    
    def fetch_and_parse(self, url: str, query: str) -> Dict:
        """Fetch and parse single page"""
        try:
            response = self.session.get(url, timeout=(2, 5), allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parse_page(soup, response.url, query)
            
        except:
            return None
    
    def parse_page(self, soup: BeautifulSoup, url: str, query: str) -> Dict:
        """Parse page content"""
        title = self.extract_title(soup)
        description = self.extract_description(soup)
        content = self.extract_content(soup)
        images = self.extract_images(soup, url)
        
        relevance = self.calculate_relevance(query, title, description, content, url)
        
        if relevance > 0.05:
            return {
                'url': url,
                'title': title,
                'description': description,
                'domain': urlparse(url).netloc.replace('www.', ''),
                'relevance': relevance,
                'images': images,
                'verified': True
            }
        
        return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Ingen titel"
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:250] + "..."
        
        return "Ingen beskrivning tillgänglig"
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """Extract content"""
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        main = soup.find('main') or soup.find('article') or soup.find('body')
        if main:
            return main.get_text(separator=' ', strip=True)[:3000]
        
        return soup.get_text(separator=' ', strip=True)[:3000]
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract images"""
        images = []
        for img in soup.find_all('img', limit=5):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(base_url, src)
                if full_url.startswith('http'):
                    images.append(full_url)
        return images
    
    def calculate_relevance(self, query: str, title: str, description: str,
                           content: str, url: str) -> float:
        """Calculate relevance with phrase matching"""
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        score = 0.0
        
        # Exact phrase match (highest priority)
        if query_lower in title.lower():
            score += 3.0
        if query_lower in description.lower():
            score += 2.0
        if query_lower in content.lower()[:1000]:
            score += 1.5
        
        # URL contains query terms
        url_lower = url.lower()
        for term in query_terms:
            if term in url_lower:
                score += 0.8
        
        # Individual term matching
        title_terms = set(title.lower().split())
        if query_terms:
            title_overlap = len(query_terms & title_terms)
            score += (title_overlap / len(query_terms)) * 1.5
        
        desc_terms = set(description.lower().split())
        if query_terms:
            desc_overlap = len(query_terms & desc_terms)
            score += (desc_overlap / len(query_terms)) * 0.8
        
        # Proximity bonus (terms close together in content)
        if len(query_terms) > 1:
            proximity_score = self.calculate_proximity(query_terms, content)
            score += proximity_score
        
        return min(score, 5.0)
    
    def calculate_proximity(self, query_terms: Set[str], content: str) -> float:
        """Calculate how close query terms are to each other in content"""
        content_lower = content.lower()
        positions = {}
        
        for term in query_terms:
            positions[term] = [m.start() for m in re.finditer(re.escape(term), content_lower)]
        
        if not all(positions.values()):
            return 0.0
        
        # Find minimum distance between all terms
        min_distance = float('inf')
        
        for i, term1 in enumerate(query_terms):
            for term2 in list(query_terms)[i+1:]:
                for pos1 in positions[term1][:5]:  # Check first 5 occurrences
                    for pos2 in positions[term2][:5]:
                        distance = abs(pos1 - pos2)
                        min_distance = min(min_distance, distance)
        
        # Convert distance to score (closer = higher score)
        if min_distance < 50:
            return 1.0
        elif min_distance < 200:
            return 0.5
        elif min_distance < 500:
            return 0.2
        
        return 0.0
    
    def rank_results(self, results: List[Dict], query: str, priority_domains: List[str], demographic: str = "general") -> List[Dict]:
        """Rank results with demographic optimization"""
        authority = {
            '1177.se': 1.0,
            'folkhalsomyndigheten.se': 0.98,
            'spotify.com': 1.0,
            'ikea.com': 1.0,
            'smhi.se': 0.95,
            'skatteverket.se': 0.95,
            'polisen.se': 0.95,
        }
        
        for result in results:
            domain = result['domain']
            
            auth_score = 0.5
            for key, value in authority.items():
                if key in domain:
                    auth_score = value
                    break
            
            priority_boost = 0.5 if domain in priority_domains else 0.0
            
            # NEW: Demographic-aware weighting
            demographic_boost = 0.0
            if demographic == 'seniors_65plus' and domain in ['1177.se', 'folkhalsomyndigheten.se', 'svt.se']:
                demographic_boost = 0.3
            elif demographic == 'teens_10to20' and domain in ['1177.se', 'dn.se']:
                demographic_boost = 0.2
            elif demographic == 'young_adults_20to40' and domain in ['arbetsformedlingen.se', 'hemnet.se']:
                demographic_boost = 0.2
            
            # Heavily favor relevance
            result['final_score'] = (
                (result['relevance'] * 0.70) + 
                (auth_score * 0.12) + 
                (priority_boost * 0.10) +
                (demographic_boost * 0.08)
            )
        
        return sorted(results, key=lambda x: x['final_score'], reverse=True)
