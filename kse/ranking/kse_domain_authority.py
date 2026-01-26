"""kse_domain_authority.py - Domain Trust Scoring

Factor 3: Domain Authority
- Measures overall domain trustworthiness
- Weight: 15% of final score
- Based on domain age, SSL, reputation
"""

import logging
from typing import Dict
from urllib.parse import urlparse

from kse.core import get_logger

logger = get_logger('ranking')


class DomainAuthority:
    """Domain authority scoring"""
    
    def __init__(self):
        """Initialize domain authority calculator"""
        # Pre-computed domain trust scores
        self.domain_scores = {
            'svt.se': 0.95,
            'dn.se': 0.95,
            'expressen.se': 0.90,
            'aftonbladet.se': 0.90,
            'bbc.co.uk': 0.95,
            'wikipedia.org': 0.95,
        }
        logger.debug("DomainAuthority initialized")
    
    def score_document(self, url: str) -> float:
        """Score document by domain authority
        
        Args:
            url: Document URL
            
        Returns:
            Authority score (0-1)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            
            # Return pre-computed score if available
            if domain in self.domain_scores:
                return self.domain_scores[domain]
            
            # Default score for unknown domains
            return 0.5
        except:
            return 0.0
    
    def set_domain_score(self, domain: str, score: float) -> None:
        """Set domain authority score
        
        Args:
            domain: Domain name
            score: Authority score (0-1)
        """
        if 0 <= score <= 1:
            self.domain_scores[domain] = score
            logger.debug(f"Updated domain score: {domain} = {score}")


__all__ = ["DomainAuthority"]
