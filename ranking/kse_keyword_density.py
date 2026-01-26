"""kse_keyword_density.py - Keyword Density Scoring

Factor 5: Keyword Density
- Measures importance of keywords in document
- Weight: 10% of final score
- Higher density (but not keyword stuffing) scores higher
"""

import logging
from typing import Dict, List

from kse.core import get_logger

logger = get_logger('ranking')


class KeywordDensity:
    """Keyword density scoring"""
    
    def __init__(self):
        """Initialize keyword density scorer"""
        logger.debug("KeywordDensity initialized")
    
    def calculate_density(self, 
                         text: str,
                         keyword: str) -> float:
        """Calculate keyword density
        
        Args:
            text: Document text
            keyword: Keyword to measure
            
        Returns:
            Density score (0-1)
        """
        if not text or not keyword:
            return 0.0
        
        # Count keyword occurrences (case-insensitive)
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Count occurrences
        occurrences = text_lower.count(keyword_lower)
        
        # Calculate density
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        density = occurrences / word_count
        
        # Ideal density: 1-2% (0.01-0.02)
        # Score highest at 1.5%, decay outside optimal range
        ideal = 0.015
        if density <= ideal:
            return min(density / ideal, 1.0)
        else:
            # Penalize over-optimization
            return max(1.0 - (density - ideal) * 10, 0.0)
    
    def score_document(self,
                      document: Dict,
                      keywords: List[str]) -> float:
        """Score document by keyword density
        
        Args:
            document: Document data with text
            keywords: List of keywords
            
        Returns:
            Score (0-1)
        """
        if not keywords:
            return 0.5
        
        text = document.get('content', '')
        
        # Average density for all keywords
        densities = []
        for keyword in keywords:
            density = self.calculate_density(text, keyword)
            densities.append(density)
        
        avg_density = sum(densities) / len(densities)
        return min(avg_density, 1.0)


__all__ = ["KeywordDensity"]
