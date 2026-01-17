"""
DOSSNA - Dynamic On-Sight Search/Navigation Algorithm
Core search orchestration algorithm
"""
from typing import List, Dict
import time

class DOSSNA:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        print("[DOSSNA] Initialized dynamic search algorithm")
    
    def search_online(self, query: str, expanded_terms: List[str], 
                     crawler, indexer) -> List[Dict]:
        """
        Online search with real-time crawling
        """
        results = []
        
        # Check cache first
        cache_key = f"online:{query}"
        if cache_key in self.cache:
            cached_time, cached_results = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_results
        
        # Crawl and index new content
        print(f"[DOSSNA] Crawling for: {query}")
        crawled_pages = crawler.crawl_for_query(query, limit=50)
        
        # Index crawled content
        for page in crawled_pages:
            indexer.index_page(page)
        
        # Search indexed content
        results = indexer.search(query, expanded_terms)
        
        # Cache results
        self.cache[cache_key] = (time.time(), results)
        
        return results
    
    def search_offline(self, query: str, expanded_terms: List[str], 
                      indexer) -> List[Dict]:
        """
        Offline search using local index
        """
        print(f"[DOSSNA] Offline search for: {query}")
        
        # Search local index only
        results = indexer.search(query, expanded_terms)
        
        return results
    
    def clear_cache(self):
        """Clear search cache"""
        self.cache.clear()
        print("[DOSSNA] Cache cleared")