"""kse_entity_extractor.py - Named Entity Recognition"""

import logging
import re
from typing import List, Dict

from kse.core import get_logger

logger = get_logger('nlp')


class EntityExtractor:
    """Named entity recognition"""
    
    def __init__(self):
        logger.debug("EntityExtractor initialized")
    
    def extract(self, text: str) -> List[Dict]:
        """Extract named entities"""
        entities = []
        
        # Find capitalized words (potential entities)
        for match in re.finditer(r'\b[A-Z][a-zäöå]+\b', text):
            entities.append({
                'text': match.group(),
                'type': 'PERSON',  # Simplified
                'start': match.start(),
                'end': match.end(),
            })
        
        # Find email addresses
        for match in re.finditer(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            entities.append({
                'text': match.group(),
                'type': 'EMAIL',
                'start': match.start(),
                'end': match.end(),
            })
        
        logger.debug(f"Extracted {len(entities)} entities")
        return entities


__all__ = ["EntityExtractor"]
