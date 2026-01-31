"""
Regional Relevance - Factor 7: Regional and Swedish-specific relevance
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RegionalRelevance:
    """Regional relevance scoring for Swedish content"""
    
    def __init__(self):
        self.swedish_tlds = ['.se', '.nu']
        self.swedish_keywords = [
            'sverige', 'swedish', 'stockholm', 'göteborg', 'malmö',
            'svensk', 'svenska', 'riksdag', 'kommun'
        ]
        logger.info("RegionalRelevance initialized")
    
    def calculate_regional_score(self, document: Dict[str, Any]) -> float:
        """
        Calculate regional relevance score
        
        Args:
            document: Document with metadata
        
        Returns:
            Regional score (0.0-1.0)
        """
        url = document.get('url', '').lower()
        title = document.get('title', '').lower()
        content = document.get('content', '').lower()
        
        score = 0.5  # Baseline
        
        # Swedish TLD bonus
        if any(tld in url for tld in self.swedish_tlds):
            score += 0.3
        
        # Swedish language indicators
        swedish_matches = sum(1 for kw in self.swedish_keywords if kw in content)
        if swedish_matches > 0:
            score += min(0.2, swedish_matches * 0.05)
        
        return min(1.0, score)
