"""kse_tokenizer.py - Swedish Tokenization"""

import logging
import re
from typing import List

from kse.core import get_logger

logger = get_logger('nlp')


class Tokenizer:
    """Swedish text tokenization"""
    
    # Swedish-specific patterns
    ABBREVIATIONS = {'dr', 'mr', 'mrs', 'st', 'väg', 'nr', 'tel'}
    
    def __init__(self):
        logger.debug("Tokenizer initialized")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Swedish text"""
        try:
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Split into sentences first
            sentences = self._split_sentences(text)
            
            tokens = []
            for sentence in sentences:
                tokens.extend(self._tokenize_sentence(sentence))
            
            logger.debug(f"Tokenized into {len(tokens)} tokens")
            return tokens
            
        except Exception as e:
            logger.error(f"Error tokenizing: {e}")
            return text.split()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle Swedish abbreviations
        for abbr in self.ABBREVIATIONS:
            text = text.replace(f'{abbr}.', f'{abbr}§')
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        # Restore abbreviations
        sentences = [s.replace('§', '.') for s in sentences]
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize_sentence(self, sentence: str) -> List[str]:
        """Tokenize single sentence"""
        # Add space before punctuation
        sentence = re.sub(r'([.,!?;:])', r' \1 ', sentence)
        
        # Split on whitespace
        tokens = sentence.split()
        
        return [t for t in tokens if t]


__all__ = ["Tokenizer"]
