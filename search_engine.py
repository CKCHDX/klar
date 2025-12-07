"""
KLAR 3.0 - Enhanced Search Engine with Domain Validation & URL Support
Fixes: Intent detection specificity ordering, URL domain whitelist, precision improvements
"""

import json
import requests
from urllib.parse import urlparse, urljoin
from core.crawler import Crawler
from core.indexer import BM25Index
from algorithms.dossna import DOSSNA
from algorithms.thor import THOR
from algorithms.sven import SVEN


class SearchEngine:
    def __init__(self, keywords_db_path="keywords_db.json", domains_path="domains.json"):
        """Initialize search engine with enhanced domain validation"""
        self.keyword_db = self._load_json(keywords_db_path)
        self.domains_data = self._load_json(domains_path)
        self.crawler = Crawler()
        self.bm25 = BM25Index()
        self.dossna = DOSSNA()
        self.thor = THOR()
        self.sven = SVEN()
        
        # Build domain whitelist for validation
        self.trusted_domains = set()
        self.domain_configs = {}
        self._build_domain_whitelist()

    def _load_json(self, path):
        """Load JSON file with error handling"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: {path} not found")
            return {}

    def _build_domain_whitelist(self):
        """Build whitelist of trusted domains from domains.json"""
        for domain_group in self.domains_data.get('domains', []):
            for domain in domain_group.get('domains', []):
                domain_clean = domain.lower().replace('www.', '')
                self.trusted_domains.add(domain_clean)
                self.domain_configs[domain_clean] = {
                    'category': domain_group.get('category'),
                    'subpages': domain_group.get('subpages', []),
                    'search_endpoint': domain_group.get('search_endpoint', f'https://{domain}/search?q='),
                    'priority': domain_group.get('priority', 5)
                }

    def is_valid_domain(self, url: str) -> tuple:
        """
        CRITICAL: Validate URL domain against whitelist
        Returns: (is_valid, domain_name, error_message)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Check exact match
            if domain in self.trusted_domains:
                return True, domain, None
            
            # Check if it's a subdomain of trusted domain
            for trusted in self.trusted_domains:
                if domain.endswith('.' + trusted) or domain == trusted:
                    return True, trusted, None
            
            # Domain not found in whitelist
            return False, domain, (
                f"❌ Domain '{domain}' is not in our database.\n\n"
                f"We only search trusted Swedish domains for security.\n\n"
                f"Would you like to:\n"
                f"1. Request this domain (help@klar.se)\n"
                f"2. Search our database instead"
            )
        except Exception as e:
            return False, None, f"Invalid URL format: {str(e)}"

    def detect_query_intent(self, query: str) -> tuple:
        """
        IMPROVED: Detect query intent using category specificity priority
        CRITICAL FIX: Searches in priority order, STOPS at first match
        
        Returns: (detected_categories, priority_domains)
        """
        query_lower = query.lower()
        
        # Define category specificity (most specific FIRST)
        category_specificity = [
            "news_breaking",            # 1st: Breaking news (time-sensitive)
            "health_symptoms",          # 2nd: Specific health symptoms
            "health_diseases",          # 3rd: Specific diseases
            "health_services",          # 4th: Health services
            "weather",                  # 5th: Weather (specific domain)
            "food_recipes",             # 6th: Food recipes (specific)
            "shopping_food",            # 7th: Food shopping
            "shopping_systembolaget",   # 8th: Alcohol specific
            "news_world",               # 9th: World news
            "news_politics",            # 10th: Political news
            "jobs",                     # 11th: Job search
            "education",                # 12th: Education
            "sports",                   # 13th: Sports
            "travel",                   # 14th: Travel
            "government",               # 15th: Government services
            "entertainment_movies",     # 16th: Movies
            "entertainment_music",      # 17th: Music
            "shopping_general",         # 18th: General shopping (least specific)
        ]
        
        detected_categories = []
        priority_domains = []
        found_match = False
        
        # Check categories in order of specificity
        for category_name in category_specificity:
            for mapping_name, mapping_data in self.keyword_db.get('mappings', {}).items():
                if mapping_data.get('category') != category_name:
                    continue
                
                keywords = mapping_data.get('keywords', [])
                
                # Check if ANY keyword matches
                for keyword in keywords:
                    if keyword in query_lower:
                        detected_categories.append(category_name)
                        priority_domains.extend(
                            mapping_data.get('priority_domains', [])
                        )
                        found_match = True
                        break
            
            # CRITICAL: Stop after first strong match
            if found_match:
                break
        
        # Remove duplicates while preserving order
        priority_domains = list(dict.fromkeys(priority_domains))
        
        # Fallback to general news if no match
        if not detected_categories:
            detected_categories = ["news"]
            for mapping_name, mapping_data in self.keyword_db.get('mappings', {}).items():
                if mapping_data.get('category') == 'news':
                    priority_domains = mapping_data.get('priority_domains', [])
                    break
        
        return detected_categories, priority_domains

    def search(self, query: str, direct_url: bool = False) -> dict:
        """
        Main search method with URL support & domain validation
        
        Args:
            query: Search query or direct URL
            direct_url: If True, treat query as URL and validate domain
        
        Returns:
            dict: Search results with metadata
        """
        results = {
            'query': query,
            'results': [],
            'categories': [],
            'domains_used': [],
            'total_results': 0,
            'execution_time': 0,
            'error': None
        }
        
        # Handle direct URL search
        if direct_url or query.startswith('http'):
            is_valid, domain, error_msg = self.is_valid_domain(query)
            
            if not is_valid:
                results['error'] = error_msg
                return results
            
            # Fetch directly from URL
            content = self.crawler.fetch(query)
            if content:
                results['results'] = [{'url': query, 'content': content[:500]}]
                results['domains_used'] = [domain]
            else:
                results['error'] = f"Failed to fetch content from {domain}"
            
            return results
        
        # Regular keyword search
        categories, priority_domains = self.detect_query_intent(query)
        results['categories'] = categories
        
        print(f"\n[Search] Query: {query}")
        print(f"[Search] Detected: {categories[0] if categories else 'general'}")
        print(f"[Search] Priority domains: {priority_domains[:3]}")
        
        # Expand query using SVEN
        expanded_queries = self.sven.expand_query(query)
        all_queries = [query] + expanded_queries
        
        # Search through priority domains
        search_results = []
        for domain in priority_domains[:5]:  # Limit to top 5 domains
            domain_config = self.domain_configs.get(domain, {})
            
            # Try search endpoint first
            search_url = domain_config.get('search_endpoint', '').format(query=query)
            if search_url.startswith('http'):
                content = self.crawler.fetch(search_url)
                if content:
                    search_results.append({
                        'domain': domain,
                        'url': search_url,
                        'content': content[:1000],
                        'priority': domain_config.get('priority', 5)
                    })
        
        # Rank results using THOR
        if search_results:
            ranked = self.thor.rank_results(search_results, query)
            results['results'] = ranked[:10]
            results['domains_used'] = list(set([r.get('domain') for r in ranked]))
            results['total_results'] = len(ranked)
        
        return results

    def search_with_subpages(self, query: str, category: str = None) -> dict:
        """
        ENHANCED: Search with subpage & subdomain precision
        Automatically crawls subpages from priority domains
        """
        if category:
            categories = [category]
        else:
            categories, _ = self.detect_query_intent(query)
        
        results = {
            'query': query,
            'category': categories[0] if categories else 'general',
            'results': [],
            'subpages': [],
            'total': 0
        }
        
        # Find domains by category
        domains_by_category = {}
        for mapping_name, mapping_data in self.keyword_db.get('mappings', {}).items():
            cat = mapping_data.get('category')
            if cat in categories:
                for domain in mapping_data.get('priority_domains', []):
                    if domain not in domains_by_category:
                        domains_by_category[domain] = mapping_data
        
        # Search each domain with subpage patterns
        for domain, mapping_data in domains_by_category.items():
            domain_config = self.domain_configs.get(domain, {})
            subpages = domain_config.get('subpages', [])
            
            for subpage in subpages[:3]:  # Limit subpages
                search_url = f"https://{domain}{subpage}?q={query}"
                content = self.crawler.fetch(search_url)
                
                if content:
                    results['subpages'].append({
                        'domain': domain,
                        'subpage': subpage,
                        'url': search_url,
                        'snippet': content[:300]
                    })
        
        results['total'] = len(results['subpages'])
        return results
