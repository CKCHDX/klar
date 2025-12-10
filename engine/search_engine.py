"""
Enhanced search with phrase matching, subpage discovery, demographic optimization
and SVEN (Swedish Enhanced Vocabulary and Entity Normalization)
Wikipedia is prioritized for factual/encyclopedia queries with DIRECT article URLs
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus, quote
import json
from pathlib import Path
import time
from typing import List, Dict, Set, Tuple, Optional

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import sys
import os

# Import SVEN from algorithms folder
from algorithms.sven import SVEN

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
        
        # Initialize SVEN for enhanced search
        self.sven = SVEN()
        print("[Klar] SVEN initialized - Swedish Enhanced Vocabulary active")
        
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
                self.domains = self._get_default_domains()
        else:
            print(f"[ERROR] domains.json not found at: {domains_file}")
            self.domains = self._get_default_domains()
        
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        total_keywords = sum(len(v.get('keywords', [])) for v in self.keyword_db.get('mappings', {}).values())
        print(f"[Klar] Search engine initialized")
        print(f"[Klar] Domains: {len(self.domains)}")
        print(f"[Klar] Keywords: {total_keywords}")
        print(f"[Klar] Categories: {len(self.domain_categories)}")
        print(f"[Klar] Wikipedia prioritization: ENABLED (direct article search)")

    def _get_default_domains(self) -> dict:
        """Fallback default domains if file loading fails"""
        return {
            "sv.wikipedia.org": {"name": "Wikipedia (Svenska)", "category": "encyclopedia"},
            "wikipedia.org": {"name": "Wikipedia", "category": "encyclopedia"},
            "svt.se": {"name": "SVT", "category": "news"},
            "dn.se": {"name": "Dagens Nyheter", "category": "news"},
            "aftonbladet.se": {"name": "Aftonbladet", "category": "news"},
            "1177.se": {"name": "1177 Vårdguiden", "category": "health"},
            "hemnet.se": {"name": "Hemnet", "category": "realestate"},
            "ica.se": {"name": "ICA", "category": "shopping"},
            "arbetsformedlingen.se": {"name": "Arbetsförmedlingen", "category": "jobs"},
            "folkhalsomyndigheten.se": {"name": "Folkhälsomyndigheten", "category": "health"},
            "google.com": {"name": "Google", "category": "search"},
        }
    
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
        
        for mapping_name, mapping_data in self.keyword_db.get('mappings', {}).items():
            category = mapping_data.get('category', 'general')
            domains = mapping_data.get('priority_domains', [])
            
            if category not in categories:
                categories[category] = []
            
            categories[category].extend(domains)
        
        for category in categories:
            categories[category] = list(set(categories[category]))
        
        return categories
    
    def _extract_wikipedia_topic(self, query: str) -> Optional[str]:
        """
        Extract the topic from a query for direct Wikipedia article lookup
        Examples:
        "vem ar Elon Musk" -> "Elon Musk"
        "vad ar AI" -> "AI"
        "Stockholm" -> "Stockholm"
        """
        query = query.strip()
        query_lower = query.lower()
        
        # Remove question words
        question_words = ['vem ar', 'vad ar', 'var ar', 'nar ar', 'hur manga',
                         'who is', 'what is', 'where is', 'when is', 'how many']
        
        topic = query
        for qword in question_words:
            if query_lower.startswith(qword.lower()):
                topic = query[len(qword):].strip()
                break
        
        topic = topic.strip("?.,!").strip()
        return topic if topic else None
    
    def _get_wikipedia_article_url(self, topic: str, lang: str = 'sv') -> Optional[str]:
        """
        Find direct Wikipedia article URL using Wikipedia API
        lang: 'sv' for Swedish, 'en' for English
        Returns: Direct Wikipedia article URL or None
        
        Example: "Elon Musk" -> "https://sv.wikipedia.org/wiki/Elon_Musk"
        """
        try:
            # Build Wikipedia API URL
            if lang == 'sv':
                api_url = "https://sv.wikipedia.org/w/api.php"
                wiki_base = "https://sv.wikipedia.org/wiki/"
            else:
                api_url = "https://en.wikipedia.org/w/api.php"
                wiki_base = "https://en.wikipedia.org/wiki/"
            
            # Search for the article
            params = {
                'action': 'query',
                'format': 'json',
                'titles': topic,
                'redirects': True,  # Follow redirects
            }
            
            response = self.session.get(api_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            # Find the article (may be redirected)
            for page_id, page_data in pages.items():
                # Check if article exists (page_id != -1)
                if page_id != '-1':
                    title = page_data.get('title')
                    if title:
                        # Build direct article URL
                        article_url = wiki_base + quote(title.replace(' ', '_'), safe='/')
                        print(f"[Wikipedia] Found: {title}")
                        print(f"[Wikipedia] URL: {article_url}")
                        return article_url
            
            print(f"[Wikipedia] Article not found: {topic}")
            return None
        
        except Exception as e:
            print(f"[Wikipedia] Error searching: {e}")
            return None
    
    def _is_factual_query(self, query: str) -> bool:
        """
        Detect if query is asking for facts/definitions
        Examples: 'vem ar', 'what is', 'vad ar', 'hur manga'
        """
        factual_patterns = [
            r'^(vem|who)\s+(ar|is)',           # Who is
            r'^(vad|what)\s+(ar|is)',          # What is
            r'^(hur|how)\s+(manga|much|old)', # How many/much/old
            r'^(var|where)\s+(ar|is)',         # Where is
            r'^(nar|when)',                     # When
            r'definition',
            r'forklara',                        # Explain
            r'biography',
            r'biografi',
            r'meaning',
            r'betydelse',
        ]
        
        query_lower = query.lower().strip()
        for pattern in factual_patterns:
            if re.search(pattern, query_lower):
                print(f"[Wikipedia] Factual query detected: '{query}'")
                return True
        
        return False
    
    def _is_encyclopedia_topic(self, query: str) -> bool:
        """
        Detect if query is about a person, place, concept, or event
        that would have a Wikipedia article
        """
        encyclopedia_patterns = [
            r'\b(Stockholm|Sverige|Sverige|Goteborg|Malmo)\b',
            r'\b(Einstein|Darwin|Newton|Marie Curie)\b',
            r'\b(Elon Musk|Greta Thunberg|Zlatan|Tesla|SpaceX)\b',
            r'\b(World War|Cold War|French Revolution)\b',
            r'\b(Climate|Evolution|Quantum|DNA)\b',
            r'\b(Python|JavaScript|Computer|Internet)\b',
        ]
        
        query_lower = query.lower()
        for pattern in encyclopedia_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        # Check if it's a single word or proper noun (likely encyclopedia topic)
        words = query.strip().split()
        if len(words) <= 3:
            # Check if first word is capitalized (proper noun)
            if words[0] and words[0][0].isupper():
                return True
        
        return False
    
    def detect_query_intent(self, query: str) -> Tuple[List[str], List[str]]:
        """Detect query intent with Wikipedia direct article search"""
        query_lower = query.lower()
        detected_categories = []
        priority_domains = []
        
        # NEW: Check if this is a factual/encyclopedia query
        is_factual = self._is_factual_query(query)
        is_encyclopedia = self._is_encyclopedia_topic(query)
        
        if is_factual or is_encyclopedia:
            # PRIORITIZE WIKIPEDIA with DIRECT ARTICLE SEARCH
            topic = self._extract_wikipedia_topic(query)
            if topic:
                # Try to find the direct article URL
                sv_article = self._get_wikipedia_article_url(topic, lang='sv')
                if sv_article:
                    priority_domains.append(sv_article)
                else:
                    # Fallback to homepage if article not found
                    priority_domains.append('https://sv.wikipedia.org')
                
                # Also add English Wikipedia as backup
                en_article = self._get_wikipedia_article_url(topic, lang='en')
                if en_article:
                    priority_domains.append(en_article)
                else:
                    priority_domains.append('https://en.wikipedia.org')
                
                print(f"[Wikipedia] Direct article search complete for: '{topic}'")
            else:
                priority_domains.append('https://sv.wikipedia.org')
                priority_domains.append('https://en.wikipedia.org')
        
        # NEW: Use SVEN to expand query with semantic understanding
        sven_hints = self.sven.generate_search_hints(query)
        expanded_terms = sven_hints['expanded_terms']
        
        print(f"[SVEN] Expanded '{query}' to {len(expanded_terms)} terms")
        
        # Check expanded terms against keyword database
        for expanded_term in expanded_terms:
            expanded_lower = expanded_term.lower()
            
            # Check direct domain mappings
            direct_mappings = self.keyword_db.get('direct_domain_mappings', {})
            for keyword, domains in direct_mappings.items():
                if expanded_lower in keyword.lower() or keyword.lower() in expanded_lower:
                    priority_domains.extend(domains)
            
            # Check keyword mappings
            for mapping_name, mapping_data in self.keyword_db.get('mappings', {}).items():
                keywords = mapping_data.get('keywords', [])
                category = mapping_data.get('category', 'general')
                domains = mapping_data.get('priority_domains', [])
                
                for keyword in keywords:
                    if expanded_lower in keyword.lower() or keyword.lower() in expanded_lower:
                        if category not in detected_categories:
                            detected_categories.append(category)
                        priority_domains.extend(domains)
                        break
        
        priority_domains = list(dict.fromkeys(priority_domains))
        
        return detected_categories, priority_domains
    
    def get_relevant_domains(self, query: str, demographic: str = "general") -> List[str]:
        """Get relevant domains with Wikipedia direct article priority"""
        if '.' in query and ' ' not in query and len(query.split('.')) >= 2:
            domain = query.lower().replace('www.', '')
            if domain in self.domains:
                return [domain]
            # Return as-is if it looks like a domain even if not in list
            return [domain]
        
        categories, priority_domains = self.detect_query_intent(query)
        relevant_domains = []
        
        # Add priority domains (Wikipedia articles come first)
        relevant_domains.extend(priority_domains)
        
        for category in categories:
            if category in self.domain_categories:
                relevant_domains.extend(self.domain_categories[category])
        
        if not relevant_domains:
            # NEW: Default domains based on demographic
            defaults = {
                'seniors_65plus': ['sv.wikipedia.org', '1177.se', 'svt.se', 'folkhalsomyndigheten.se'],
                'women_general': ['sv.wikipedia.org', 'hemnet.se', 'ica.se', 'svt.se'],
                'men_general': ['sv.wikipedia.org', 'webhallen.com', 'inet.se', 'svt.se'],
                'teens_10to20': ['sv.wikipedia.org', '1177.se', 'svt.se', 'dn.se'],
                'young_adults_20to40': ['sv.wikipedia.org', 'dn.se', 'aftonbladet.se', 'arbetsformedlingen.se'],
                'general': ['sv.wikipedia.org', 'svt.se', 'dn.se', 'aftonbladet.se']
            }
            relevant_domains = defaults.get(demographic, defaults['general'])
        
        seen = set()
        result = []
        for domain in relevant_domains:
            # Handle both full URLs and domain names
            if domain.startswith('http'):
                result.append(domain)  # Direct URL
            elif domain not in seen and domain in self.domains:
                seen.add(domain)
                result.append(domain)
            elif domain not in seen:
                # Add even if not in domains list (fallback)
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
        """Main search with direct Wikipedia article links"""
        print(f"\n[Search] Query: {query}")
        print(f"[Search] Demographic: {demographic}")
        
        # Get SVEN hints for enhanced searching
        sven_hints = self.sven.generate_search_hints(query)
        print(f"[SVEN] Normalized: {sven_hints['normalized_query']}")
        print(f"[SVEN] Expanded terms: {len(sven_hints['expanded_terms'])}")
        if sven_hints['entities']:
            print(f"[SVEN] Entities: {sven_hints['entities']}")
        
        relevant_domains = self.get_relevant_domains(query, demographic)
        categories, priority_domains = self.detect_query_intent(query)
        
        print(f"[Search] Detected: {', '.join(categories) if categories else 'general'}")
        print(f"[Search] Searching {len(relevant_domains)} domains")
        print(f"[Search] Domains: {relevant_domains}")
        
        results = []
        
        # For phrases, we need to search more intelligently
        is_phrase = len(query.split()) > 1
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_domain = {}
            
            for domain in relevant_domains:
                try:
                    # Handle direct Wikipedia URLs
                    if domain.startswith('http'):
                        future = executor.submit(self.fetch_and_parse, domain, query, sven_hints)
                    elif is_phrase:
                        # For phrases, try deeper search
                        future = executor.submit(self.search_domain_deeply, domain, query, sven_hints)
                    else:
                        # Single word - construct proper URL
                        url = f"https://www.{domain}" if not domain.startswith(('wikipedia', 'sv.', 'en.')) else f"https://{domain}"
                        future = executor.submit(self.fetch_and_parse, url, query, sven_hints)
                    
                    future_to_domain[future] = domain
                except Exception as e:
                    print(f"  ✗ {domain}: {e}")
            
            for future in as_completed(future_to_domain, timeout=15):
                domain = future_to_domain[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                        print(f"  ✓ {domain}")
                except Exception as e:
                    print(f"  ✗ {domain}: {str(e)[:50]}")
        
        # Rank results
        ranked_results = self.rank_results(results, query, priority_domains, demographic, sven_hints)
        
        # Get demographic hints for result limiting
        hints = self.get_demographic_hints(demographic)
        result_count = hints['result_count']
        
        # Ensure we have results
        if not ranked_results:
            print(f"[Search] WARNING: No results found, creating default results")
            ranked_results = self.create_default_results(query, relevant_domains)
        
        return {
            'query': query,
            'results': ranked_results[:result_count],
            'total': len(ranked_results),
            'categories_used': categories,
            'is_phrase_search': is_phrase,
            'demographic': demographic,
            'demographic_hints': hints,
            'sven_expanded': len(sven_hints['expanded_terms']),
            'wikipedia_prioritized': any('wikipedia' in str(d).lower() for d in priority_domains)
        }
    
    def create_default_results(self, query: str, domains: List[str]) -> List[Dict]:
        """Create default results when search fails"""
        results = []
        for domain in domains[:5]:
            # Extract clean domain name
            clean_domain = domain.replace('www.', '').replace('https://', '').split('/')[0]
            results.append({
                'url': f"https://{clean_domain}" if clean_domain.startswith(('wikipedia', 'sv.')) else f"https://www.{clean_domain}",
                'title': f"Sök '{query}' på {clean_domain}",
                'description': f"Hitta information om '{query}' på {clean_domain}",
                'domain': clean_domain,
                'relevance': 0.5,
                'images': [],
                'verified': False
            })
        return results
    
    def search_domain_deeply(self, domain: str, query: str, sven_hints: Dict) -> List[Dict]:
        """
        Deep search within a domain to find specific subpages
        Uses SVEN expanded terms for improved matching
        """
        results = []
        expanded_terms = sven_hints.get('expanded_terms', [])
        
        try:
            # Start with homepage
            if domain.startswith('sv.wikipedia') or domain.startswith('wikipedia') or domain.startswith('en.'):
                base_url = f"https://{domain}"
            else:
                base_url = f"https://www.{domain}"
            
            response = self.session.get(base_url, timeout=(3, 8))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract internal links
            links = self.extract_internal_links(soup, base_url, domain)
            
            # Filter links that might be relevant to query or expanded terms
            relevant_links = self.filter_relevant_links(links, query, expanded_terms)
            
            # Fetch top 3 most relevant subpages
            for link in relevant_links[:3]:
                try:
                    result = self.fetch_and_parse(link, query, sven_hints)
                    if result and result['relevance'] > 0.3:
                        results.append(result)
                except:
                    pass
            
            # Also include homepage if relevant
            homepage_result = self.parse_page(soup, base_url, query, sven_hints)
            if homepage_result and homepage_result['relevance'] > 0.1:
                results.append(homepage_result)
        
        except Exception as e:
            print(f"[DeepSearch] Error for {domain}: {e}")
        
        return results
    
    def extract_internal_links(self, soup: BeautifulSoup, base_url: str, domain: str) -> List[str]:
        """Extract internal links from page"""
        links = []
        
        try:
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(base_url, href)
                
                # Only internal links
                if domain in urlparse(full_url).netloc:
                    links.append(full_url)
        except:
            pass
        
        return list(set(links))[:50]  # Limit to 50 links
    
    def filter_relevant_links(self, links: List[str], query: str, expanded_terms: List[str]) -> List[str]:
        """Filter links using both original query and SVEN expanded terms"""
        all_terms = set([query.lower()] + [t.lower() for t in expanded_terms])
        scored_links = []
        
        for link in links:
            url_lower = link.lower()
            score = 0
            
            # Check if any term appears in URL
            for term in all_terms:
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
    
    def fetch_and_parse(self, url: str, query: str, sven_hints: Dict = None) -> Dict:
        """Fetch and parse single page"""
        try:
            response = self.session.get(url, timeout=(3, 8), allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parse_page(soup, response.url, query, sven_hints)
            
        except requests.exceptions.Timeout:
            print(f"[Fetch] Timeout: {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[Fetch] Connection error: {url}")
            return None
        except Exception as e:
            print(f"[Fetch] Error: {url} - {str(e)[:50]}")
            return None
    
    def parse_page(self, soup: BeautifulSoup, url: str, query: str, sven_hints: Dict = None) -> Dict:
        """Parse page content with SVEN enhancement"""
        title = self.extract_title(soup)
        description = self.extract_description(soup)
        content = self.extract_content(soup)
        images = self.extract_images(soup, url)
        
        relevance = self.calculate_relevance(query, title, description, content, url, sven_hints)
        
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
        
        return "Ingen beskrivning tillganglig"
    
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
        try:
            for img in soup.find_all('img', limit=5):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url.startswith('http'):
                        images.append(full_url)
        except:
            pass
        return images
    
    def calculate_relevance(self, query: str, title: str, description: str,
                           content: str, url: str, sven_hints: Dict = None) -> float:
        """Calculate relevance with SVEN expansion and phrase matching"""
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Use SVEN expanded terms for better matching
        if sven_hints:
            expanded_terms = sven_hints.get('expanded_terms', [])
            all_match_terms = query_terms | set(t.lower() for t in expanded_terms)
        else:
            all_match_terms = query_terms
        
        score = 0.0
        
        # Exact phrase match (highest priority)
        if query_lower in title.lower():
            score += 3.0
        if query_lower in description.lower():
            score += 2.0
        if query_lower in content.lower()[:1000]:
            score += 1.5
        
        # Check expanded terms
        for expanded_term in (sven_hints.get('expanded_terms', []) if sven_hints else []):
            expanded_lower = expanded_term.lower()
            if expanded_lower in title.lower():
                score += 1.5
            if expanded_lower in description.lower():
                score += 0.8
        
        # URL contains query terms
        url_lower = url.lower()
        for term in all_match_terms:
            if term in url_lower:
                score += 0.8
        
        # Individual term matching
        title_terms = set(title.lower().split())
        if query_terms:
            title_overlap = len(all_match_terms & title_terms)
            score += (title_overlap / max(1, len(all_match_terms))) * 1.5
        
        desc_terms = set(description.lower().split())
        if query_terms:
            desc_overlap = len(all_match_terms & desc_terms)
            score += (desc_overlap / max(1, len(all_match_terms))) * 0.8
        
        # Proximity bonus (terms close together in content)
        if len(query_terms) > 1:
            proximity_score = self.calculate_proximity(all_match_terms, content)
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
    
    def rank_results(self, results: List[Dict], query: str, priority_domains: List[str], demographic: str = "general", sven_hints: Dict = None) -> List[Dict]:
        """Rank results with Wikipedia boost, demographic and contextual optimization"""
        authority = {
            'sv.wikipedia.org': 1.0,
            'wikipedia.org': 1.0,
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
            
            # MASSIVE BOOST for Wikipedia on factual queries
            wikipedia_boost = 0.0
            if 'wikipedia' in domain.lower() and self._is_factual_query(query):
                wikipedia_boost = 0.4  # 40% boost for Wikipedia on factual queries
            elif 'wikipedia' in domain.lower():
                wikipedia_boost = 0.2  # 20% boost for Wikipedia on any query
            
            priority_boost = 0.5 if any(domain in str(pd).lower() for pd in priority_domains) else 0.0
            
            # NEW: Use SVEN contextual weight for improved ranking
            contextual_boost = 0.0
            if sven_hints:
                contextual_weight = self.sven.get_contextual_weight(query, domain)
                contextual_boost = (contextual_weight - 0.5) * 0.2  # Normalized impact
            
            # Demographic-aware weighting
            demographic_boost = 0.0
            if demographic == 'seniors_65plus' and domain in ['1177.se', 'folkhalsomyndigheten.se', 'svt.se']:
                demographic_boost = 0.3
            elif demographic == 'teens_10to20' and domain in ['1177.se', 'dn.se']:
                demographic_boost = 0.2
            elif demographic == 'young_adults_20to40' and domain in ['arbetsformedlingen.se', 'hemnet.se']:
                demographic_boost = 0.2
            
            # Heavily favor relevance with contextual enhancement AND Wikipedia boost
            result['final_score'] = (
                (result['relevance'] * 0.60) +  
                (auth_score * 0.12) + 
                (priority_boost * 0.08) +
                (demographic_boost * 0.07) +
                (contextual_boost * 0.03) +
                (wikipedia_boost * 0.10)  
            )
        
        return sorted(results, key=lambda x: x['final_score'], reverse=True)
