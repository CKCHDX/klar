"""kse_link_structure.py - Link Structure Analysis

Factor 6: Link Structure
- Analyzes internal and external links
- Weight: 10% of final score
- Good structure with quality links scores higher
"""

import logging
from typing import Dict, List

from kse.core import get_logger

logger = get_logger('ranking')


class LinkStructure:
    """Link structure analysis"""
    
    def __init__(self):
        """Initialize link structure analyzer"""
        logger.debug("LinkStructure initialized")
    
    def score_document(self,
                      url: str,
                      document: Dict) -> float:
        """Score document by link structure
        
        Args:
            url: Document URL
            document: Document data with links
            
        Returns:
            Score (0-1)
        """
        # Count internal and external links
        internal_links = len(document.get('internal_links', []))
        external_links = len(document.get('external_links', []))
        backlinks = len(document.get('backlinks', []))
        
        # Score components
        # Internal links: 0-0.3
        internal_score = min(internal_links / 20.0, 0.3)
        
        # External links: 0-0.3
        external_score = min(external_links / 10.0, 0.3)
        
        # Backlinks: 0-0.4
        backlink_score = min(backlinks / 50.0, 0.4)
        
        return internal_score + external_score + backlink_score


__all__ = ["LinkStructure"]
