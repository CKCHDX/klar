"""kse_regional_relevance.py - Regional Relevance Scoring

Factor 7: Regional Relevance
- Measures relevance to Swedish/Nordic region
- Weight: 5% of final score
- Swedish domain (.se) scores higher
"""

import logging
from typing import Dict
from urllib.parse import urlparse

from kse.core import get_logger

logger = get_logger('ranking')


class RegionalRelevance:
    """Regional relevance scoring"""
    
    def __init__(self):
        """Initialize regional relevance scorer"""
        self.priority_tlds = {
            '.se': 1.0,      # Swedish domain
            '.ax': 0.95,     # Åland
            '.no': 0.90,     # Norwegian
            '.dk': 0.90,     # Danish
            '.fi': 0.85,     # Finnish
            '.uk': 0.80,     # UK English
            '.com': 0.70,    # Generic (English likely)
            '.org': 0.70,    # Generic
        }
        logger.debug("RegionalRelevance initialized")
    
    def score_document(self, url: str) -> float:
        """Score document by regional relevance
        
        Args:
            url: Document URL
            
        Returns:
            Regional relevance score (0-1)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check TLD
            for tld, score in self.priority_tlds.items():
                if domain.endswith(tld):
                    return score
            
            # Default for unknown TLDs
            return 0.5
        except:
            return 0.0
    
    def batch_score(self, urls: list) -> Dict[str, float]:
        """Score multiple URLs
        
        Args:
            urls: List of URLs
            
        Returns:
            URL → score mapping
        """
        return {url: self.score_document(url) for url in urls}


__all__ = ["RegionalRelevance"]
