"""
DOSSNA - Dynamic Orchestration Search Strategy Navigation Architecture
Search orchestration with enhanced subpage & subdomain precision
"""

import re
from typing import List, Dict, Tuple
from urllib.parse import urlparse, urljoin


class DOSSNA:
    """Search orchestration engine for multi-domain strategy"""
    
    def __init__(self):
        self.subpage_patterns = {
            'news': ['/nyheter', '/senaste', '/inrikes', '/sverige', '/breaking'],
            'weather': ['/vader', '/väder', '/prognos', '/temperatur', '/snö'],
            'health': ['/halsa', '/hälsa', '/sjukdomar', '/symptom', '/medicin'],
            'jobs': ['/jobs', '/lediga-jobb', '/anstallningar', '/karriar', '/rekrytering'],
            'sports': ['/sport', '/fotboll', '/hockey', '/resultat', '/tabell'],
            'food': ['/mat', '/recept', '/matrecept', '/mat-och-dryck', '/smaksaker'],
            'travel': ['/resa', '/resor', '/flygbokningar', '/hotell', '/turist'],
            'government': ['/politik', '/regering', '/lag', '/skatt', '/pass'],
            'shopping': ['/shop', '/shopping', '/priser', '/produkter', '/kop'],
            'entertainment': ['/kultur', '/film', '/musik', '/tv', '/recensioner']
        }
    
    def generate_search_urls(self, domain: str, query: str, category: str = None) -> List[str]:
        """
        Generate search URLs with subpage patterns
        Returns: List of URLs to search
        """
        urls = []
        parsed = urlparse(domain if domain.startswith('http') else f'https://{domain}')
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Base domain search
        urls.append(f"{base_url}/search?q={query}")
        urls.append(f"{base_url}?q={query}")
        
        # Add subpage patterns if category specified
        if category and category in self.subpage_patterns:
            for subpage in self.subpage_patterns[category][:3]:
                urls.append(f"{base_url}{subpage}?q={query}")
                urls.append(f"{base_url}{subpage}/search?q={query}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def extract_category_keywords(self, query: str) -> str:
        """
        Extract implied category from query keywords
        """
        category_keywords = {
            'news': ['nyhet', 'senaste', 'breaking', 'olycka', 'dödad'],
            'weather': ['väder', 'vind', 'temperatur', 'snö', 'regn'],
            'jobs': ['jobb', 'anställ', 'karriär', 'lediga', 'arbete'],
            'health': ['sjukdom', 'symptom', 'läkare', 'medicin', 'hälsa'],
            'sports': ['sport', 'fotboll', 'hockey', 'match', 'spel'],
            'food': ['mat', 'recept', 'dryck', 'restaurang', 'pizza'],
            'travel': ['resa', 'hotell', 'flyg', 'destination', 'turist'],
            'entertainment': ['film', 'musik', 'serie', 'kultur', 'recensioner']
        }
        
        query_lower = query.lower()
        for category, keywords in category_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return category
        
        return None
    
    def prioritize_domains(self, domains: List[str], query: str) -> List[Tuple[str, float]]:
        """
        Prioritize domains based on category match and relevance
        Returns: List of (domain, score) tuples
        """
        category = self.extract_category_keywords(query)
        scored_domains = []
        
        for idx, domain in enumerate(domains):
            score = 1.0
            
            # Authority score (earlier domains higher)
            authority_score = 1.0 / (idx + 1) * 0.5
            score += authority_score
            
            # Category relevance
            if category and category in domain.lower():
                score += 1.0
            
            scored_domains.append((domain, score))
        
        return sorted(scored_domains, key=lambda x: x[1], reverse=True)
    
    def orchestrate_search(self, query: str, domains: List[str], category: str = None) -> Dict:
        """
        Create comprehensive search strategy
        Returns: Dict with search strategy details
        """
        strategy = {
            'query': query,
            'category': category or self.extract_category_keywords(query),
            'primary_domains': [],
            'search_urls': [],
            'estimated_precision': 0.0
        }
        
        # Prioritize domains
        prioritized = self.prioritize_domains(domains, query)
        strategy['primary_domains'] = [d for d, _ in prioritized[:5]]
        
        # Generate search URLs
        all_urls = []
        for domain in strategy['primary_domains']:
            urls = self.generate_search_urls(domain, query, strategy['category'])
            all_urls.extend(urls[:3])
        
        strategy['search_urls'] = all_urls[:10]
        
        # Estimate precision
        if strategy['category']:
            strategy['estimated_precision'] = 0.85
        else:
            strategy['estimated_precision'] = 0.70
        
        return strategy
