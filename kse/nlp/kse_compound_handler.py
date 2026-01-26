"""kse_compound_handler.py - Swedish Compound Word Handling"""

import logging
from typing import List

from kse.core import get_logger

logger = get_logger('nlp')


class CompoundHandler:
    """Handle Swedish compound words"""
    
    # Common compound connectors in Swedish
    CONNECTORS = {'s', 'e'}
    
    def __init__(self):
        logger.debug("CompoundHandler initialized")
    
    def split_compound(self, word: str) -> List[str]:
        """Split compound word"""
        word_lower = word.lower()
        
        # Try to find connector
        for connector in self.CONNECTORS:
            parts = word_lower.split(connector)
            if len(parts) > 1:
                return parts
        
        return [word]
    
    def is_compound(self, word: str) -> bool:
        """Check if word is compound"""
        parts = self.split_compound(word)
        return len(parts) > 1


__all__ = ["CompoundHandler"]
