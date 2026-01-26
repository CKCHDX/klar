"""kse_intent_detector.py - Query Intent Classification"""

import logging
from typing import Tuple

from kse.core import get_logger

logger = get_logger('nlp')


class IntentDetector:
    """Detect query intent"""
    
    INTENT_KEYWORDS = {
        'search': ['sök', 'hitta', 'information', 'vad är'],
        'product': ['köp', 'pris', 'var kan', 'shop'],
        'question': ['hur', 'varför', 'vad', 'vilken'],
        'navigation': ['gå till', 'öppna', 'visa'],
    }
    
    def __init__(self):
        logger.debug("IntentDetector initialized")
    
    def detect(self, query: str) -> Tuple[str, float]:
        """Detect intent and confidence"""
        query_lower = query.lower()
        
        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            scores[intent] = matches
        
        if not scores or max(scores.values()) == 0:
            return 'search', 0.5
        
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent] / len(query.split())
        
        return best_intent, min(confidence, 1.0)


__all__ = ["IntentDetector"]
