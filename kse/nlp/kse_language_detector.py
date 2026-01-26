"""kse_language_detector.py - Language Detection"""

import logging

from kse.core import get_logger

logger = get_logger('nlp')


class LanguageDetector:
    """Detect text language"""
    
    # Language markers
    MARKERS = {
        'sv': {'och', 'det', 'är', 'på', 'för', 'från'},
        'en': {'the', 'and', 'is', 'in', 'for', 'from'},
        'de': {'der', 'und', 'ist', 'in', 'für', 'von'},
    }
    
    def __init__(self):
        logger.debug("LanguageDetector initialized")
    
    def detect(self, text: str) -> str:
        """Detect language"""
        words = set(text.lower().split())
        
        scores = {}
        for lang, markers in self.MARKERS.items():
            score = sum(1 for m in markers if m in words)
            scores[lang] = score
        
        if not scores or max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)


__all__ = ["LanguageDetector"]
