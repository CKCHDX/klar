"""
Keyword Density - Factor 5: Keyword density and positioning analysis
Analyzes keyword usage patterns and positions in documents
"""

import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


class KeywordDensity:
    """Keyword density and positioning analyzer"""
    
    def __init__(self):
        """Initialize keyword density analyzer"""
        logger.info("KeywordDensity initialized")
    
    def calculate_density_score(
        self,
        document: Dict[str, Any],
        query_terms: List[str]
    ) -> float:
        """
        Calculate keyword density score
        
        Args:
            document: Document with content
            query_terms: Query terms to analyze
        
        Returns:
            Density score (0.0-1.0)
        """
        if not query_terms:
            return 0.0
        
        title = document.get('title', '').lower()
        description = document.get('description', '').lower()
        content = document.get('content', '').lower()
        
        # Calculate position scores
        title_score = self._calculate_position_score(title, query_terms, weight=2.0)
        desc_score = self._calculate_position_score(description, query_terms, weight=1.5)
        content_score = self._calculate_content_density(content, query_terms)
        
        # Combine scores
        final_score = (title_score + desc_score + content_score) / 4.5
        
        return min(1.0, final_score)
    
    def _calculate_position_score(self, text: str, terms: List[str], weight: float = 1.0) -> float:
        """Calculate score based on term positions"""
        if not text:
            return 0.0
        
        score = 0.0
        for term in terms:
            if term in text:
                # Early occurrence bonus
                position = text.find(term)
                position_factor = 1.0 - (position / max(len(text), 1))
                score += position_factor * weight
        
        return score / len(terms) if terms else 0.0
    
    def _calculate_content_density(self, content: str, terms: List[str]) -> float:
        """Calculate keyword density in content"""
        if not content:
            return 0.0
        
        words = content.split()
        if not words:
            return 0.0
        
        total_matches = sum(content.count(term) for term in terms)
        density = total_matches / len(words)
        
        # Optimal density is around 2-5%
        if 0.02 <= density <= 0.05:
            return 1.0
        elif density > 0.05:
            # Penalize keyword stuffing
            return max(0.3, 1.0 - (density - 0.05) * 2)
        else:
            # Scale up from 0 to 2%
            return density / 0.02
