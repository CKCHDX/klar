"""kse_query_expander.py - Query Expansion and Synonyms"""

import logging
from typing import List, Set

from kse.core import get_logger

logger = get_logger('nlp')


class QueryExpander:
    """Query expansion and synonym handling"""
    
    # Swedish synonyms dictionary
    SYNONYMS = {
        'bil': ['automobil', 'fordon', 'personbil'],
        'hus': ['bostad', 'hem', 'fastighet'],
        'person': ['människa', 'individ', 'individer'],
        'arbete': ['jobb', 'syssla', 'yrke'],
    }
    
    def __init__(self):
        logger.debug("QueryExpander initialized")
    
    def expand(self, query: str) -> List[str]:
        """Expand query with synonyms"""
        tokens = query.lower().split()
        expanded = set(tokens)
        
        for token in tokens:
            if token in self.SYNONYMS:
                expanded.update(self.SYNONYMS[token])
        
        return list(expanded)
    
    def get_synonyms(self, word: str) -> Set[str]:
        """Get synonyms for word"""
        word_lower = word.lower()
        return set(self.SYNONYMS.get(word_lower, []))


__all__ = ["QueryExpander"]
