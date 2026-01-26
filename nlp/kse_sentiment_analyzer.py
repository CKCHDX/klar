"""kse_sentiment_analyzer.py - Sentiment Analysis"""

import logging
from typing import Dict

from kse.core import get_logger

logger = get_logger('nlp')


class SentimentAnalyzer:
    """Swedish sentiment analysis"""
    
    POSITIVE_WORDS = {
        'bra', 'bäst', 'utmärkt', 'fantastisk', 'undebar', 'älskar',
        'häftig', 'rolig', 'skön', 'fin', 'snäll', 'aning'
    }
    
    NEGATIVE_WORDS = {
        'dålig', 'värsta', 'fruktansvärd', 'hemsk', 'hatar',
        'tråkig', 'elak', 'sorglig', 'arg', 'sur'
    }
    
    def __init__(self):
        logger.debug("SentimentAnalyzer initialized")
    
    def analyze(self, text: str) -> float:
        """Analyze sentiment (-1.0 to 1.0)"""
        words = text.lower().split()
        
        positive = sum(1 for w in words if w in self.POSITIVE_WORDS)
        negative = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        
        total = positive + negative
        if total == 0:
            return 0.0
        
        score = (positive - negative) / total
        return max(-1.0, min(1.0, score))
    
    def get_sentiment_label(self, score: float) -> str:
        """Get sentiment label"""
        if score > 0.2:
            return 'positive'
        elif score < -0.2:
            return 'negative'
        return 'neutral'


__all__ = ["SentimentAnalyzer"]
