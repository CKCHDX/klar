"""kse_lemmatizer.py - Swedish Lemmatization"""

import logging
from typing import List, Dict

from kse.core import get_logger

logger = get_logger('nlp')


class Lemmatizer:
    """Swedish lemmatization"""
    
    # Swedish lemma rules (simplified)
    RULES = {
        'a': 'a', 'e': 'e', 'o': 'o', 'u': 'u',
        'ar': '', 'er': '', 'or': '',
        'ad': '', 'ed': '', 'od': '',
    }
    
    def __init__(self):
        logger.debug("Lemmatizer initialized")
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens"""
        return [self._lemmatize_word(token) for token in tokens]
    
    def _lemmatize_word(self, word: str) -> str:
        """Lemmatize single word"""
        word_lower = word.lower()
        
        # Try to find lemma
        for suffix, replacement in self.RULES.items():
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix):
                return word_lower[:-len(suffix)] + replacement
        
        return word_lower


__all__ = ["Lemmatizer"]
