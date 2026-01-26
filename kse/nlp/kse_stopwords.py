"""kse_stopwords.py - Swedish Stopword Management"""

import logging
from typing import Set

from kse.core import get_logger

logger = get_logger('nlp')


class StopwordManager:
    """Manage Swedish stopwords"""
    
    # Swedish stopwords
    SWEDISH_STOPWORDS = {
        'och', 'det', 'att', 'en', 'i', 'på', 'de', 'han', 'av', 'för',
        'är', 'med', 'han', 'hon', 'då', 'så', 'till', 'från', 'har', 'hade',
        'som', 'den', 'denna', 'vilken', 'var', 'vad', 'hur', 'än', 'då', 'se',
        'om', 'eller', 'andra', 'några', 'mycket', 'bara', 'när', 'väl', 'där',
        'ut', 'här', 'nej', 'ja', 'aldrig', 'ofta', 'ej', 'icke', 'innan', 'efter',
    }
    
    def __init__(self):
        logger.debug("StopwordManager initialized")
    
    def is_stopword(self, word: str) -> bool:
        """Check if word is stopword"""
        return word.lower() in self.SWEDISH_STOPWORDS
    
    def remove_stopwords(self, tokens: list) -> list:
        """Remove stopwords from token list"""
        return [t for t in tokens if not self.is_stopword(t)]
    
    def get_stopwords(self) -> Set[str]:
        """Get all stopwords"""
        return self.SWEDISH_STOPWORDS.copy()


__all__ = ["StopwordManager"]
