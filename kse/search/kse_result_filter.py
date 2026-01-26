"""kse_result_filter.py - Result Filtering and Diversification

Filters and diversifies search results:
- Domain deduplication
- Spam detection
- Result diversity
- Quality scoring
"""

import logging
from typing import Dict, List, Tuple
from urllib.parse import urlparse

from kse.core import get_logger

logger = get_logger('search')


class ResultFilter:
    """Filter and diversify search results"""
    
    def __init__(self):
        """Initialize result filter"""
        self.spam_domains = [
            'spam.example.com',
            'fake-results.com',
        ]
        logger.debug("ResultFilter initialized")
    
    def deduplicate(self, results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Remove duplicate domains from results
        
        Args:
            results: List of (url, score) tuples
            
        Returns:
            Deduplicated results (max 1 per domain)
        """
        seen_domains = set()
        deduped = []
        
        for url, score in results:
            domain = self._extract_domain(url)
            if domain not in seen_domains:
                seen_domains.add(domain)
                deduped.append((url, score))
        
        return deduped
    
    def remove_spam(self, results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Remove known spam domains
        
        Args:
            results: List of (url, score) tuples
            
        Returns:
            Filtered results
        """
        filtered = []
        
        for url, score in results:
            domain = self._extract_domain(url)
            if domain not in self.spam_domains:
                filtered.append((url, score))
        
        return filtered
    
    def diversify(self, 
                 results: List[Tuple[str, float]],
                 max_per_domain: int = 2) -> List[Tuple[str, float]]:
        """Limit results per domain for diversity
        
        Args:
            results: List of (url, score) tuples
            max_per_domain: Max results from same domain
            
        Returns:
            Diversified results
        """
        domain_count = {}
        diversified = []
        
        for url, score in results:
            domain = self._extract_domain(url)
            count = domain_count.get(domain, 0)
            
            if count < max_per_domain:
                diversified.append((url, score))
                domain_count[domain] = count + 1
        
        return diversified
    
    def apply_filters(self, 
                     results: List[Tuple[str, float]],
                     deduplicate: bool = True,
                     remove_spam: bool = True,
                     diversify: bool = True) -> List[Tuple[str, float]]:
        """Apply all filters
        
        Args:
            results: Input results
            deduplicate: Remove duplicates
            remove_spam: Remove spam
            diversify: Diversify results
            
        Returns:
            Filtered results
        """
        if deduplicate:
            results = self.deduplicate(results)
        
        if remove_spam:
            results = self.remove_spam(results)
        
        if diversify:
            results = self.diversify(results)
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return url


__all__ = ["ResultFilter"]
