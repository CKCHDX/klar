"""
Diversity Ranker - Result diversity algorithm
Ensures diverse results from different domains and perspectives
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class DiversityRanker:
    """Result diversification engine"""
    
    def __init__(self, max_per_domain: int = 3):
        """
        Initialize diversity ranker
        
        Args:
            max_per_domain: Maximum results per domain
        """
        self.max_per_domain = max_per_domain
        logger.info(f"DiversityRanker initialized (max_per_domain={max_per_domain})")
    
    def diversify_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply diversification to results
        
        Args:
            results: Ranked search results
        
        Returns:
            Diversified results
        """
        if not results:
            return []
        
        diversified = []
        domain_counts = defaultdict(int)
        
        for result in results:
            domain = self._extract_domain(result.get('url', ''))
            
            if domain_counts[domain] < self.max_per_domain:
                diversified.append(result)
                domain_counts[domain] += 1
        
        logger.info(f"Diversified {len(results)} → {len(diversified)} results")
        return diversified
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return ""
