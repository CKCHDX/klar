"""
KLAR 3.0 Search Engine - WORKING VERSION
Fixed to work with your existing code structure
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
        """Detect query intent - supports phrases"""
        query_lower = query.lower()
        detected_categories = []
        priority_domains = []
        
        # Check direct domain mappings
        direct_mappings = self.keyword_db.get('direct_domain_mappings', {})
        for keyword, domains in direct_mappings.items():
            if keyword in query_lower:
                priority_domains.extend(domains)
        
        # Check keyword mappings (supports phrases)
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
    
    def get_relevant_domains(self, query: str) -> List[str]:
        """Get relevant domains for query"""
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
            relevant_domains = ['svt.se', 'dn.se', 'aftonbladet.se']
        
        seen = set()
        result = []
        for domain in relevant_domains:
            if domain not in seen and domain in self.domains:
                seen.add(domain)
                result.append(domain)
        
        return result[:12]
    
    def search(self, query: str) -> Dict:
        """Main search with phrase support"""
        print(f"\n[Search] Query: {query}")
        relevant_domains = self.get_relevant_domains(query)
        categories, priority_domains = self.detect_query_intent(query)
        
        print(f"[Search] Detected: {', '.join(categories) if categories else 'general'}")
        print(f"[Search] Searching {len(relevant_domains)} domains")
        
        results = []
        
        # TODO: Implement actual search crawling
        # For now return basic structure
        return {
            'query': query,
            'categories': categories,
            'domains': relevant_domains,
            'results': results,
            'total': len(results)
        }
    
    def get_statistics(self) -> Dict:
        """Get search engine statistics"""
        return {
            'domains': len(self.domains),
            'categories': len(self.domain_categories),
            'keywords': sum(len(v.get('keywords', [])) for v in self.keyword_db.get('mappings', {}).values())
        }


if __name__ == "__main__":
    # Test the search engine
    engine = SearchEngine()
    
    # Test intent detection
    test_queries = [
        "väder stockholm",
        "smärta i nacken",
        "lediga jobb python",
        "man dödad idag",
        "fotboll allsvenskan"
    ]
    
    print("\n🧪 Testing Intent Detection:")
    print("=" * 60)
    
    for query in test_queries:
        categories, domains = engine.detect_query_intent(query)
        print(f"Query: '{query}'")
        print(f"  → Category: {categories[0] if categories else 'unknown'}")
        print(f"  → Domains: {domains[:3]}")
        print()
