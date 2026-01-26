"""kse_recency_scorer.py - Content Freshness Scoring

Factor 4: Recency
- Measures how recent/fresh the content is
- Weight: 15% of final score
- Newer content scores higher
"""

import logging
from typing import Dict
from datetime import datetime, timedelta

from kse.core import get_logger

logger = get_logger('ranking')


class RecencyScorer:
    """Content recency scoring"""
    
    def __init__(self):
        """Initialize recency scorer"""
        logger.debug("RecencyScorer initialized")
    
    def score_document(self, url: str, timestamp: float) -> float:
        """Score document by recency
        
        Args:
            url: Document URL
            timestamp: Last update timestamp (seconds since epoch)
            
        Returns:
            Recency score (0-1)
        """
        try:
            # Convert timestamp to date
            doc_date = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            
            # Calculate days since last update
            days_old = (now - doc_date).days
            
            # Scoring: 1.0 if < 7 days, decay after
            if days_old <= 7:
                return 1.0
            elif days_old <= 30:
                return 0.8
            elif days_old <= 90:
                return 0.6
            elif days_old <= 365:
                return 0.4
            else:
                return 0.2
        
        except:
            return 0.5
    
    def batch_score(self, documents: Dict[str, Dict]) -> Dict[str, float]:
        """Score multiple documents by recency
        
        Args:
            documents: URL → document data
            
        Returns:
            URL → score mapping
        """
        scores = {}
        for url, doc in documents.items():
            timestamp = doc.get('timestamp', 0)
            scores[url] = self.score_document(url, timestamp)
        return scores


__all__ = ["RecencyScorer"]
