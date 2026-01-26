"""
kse_nlp_core.py - Swedish NLP Core Coordinator

Main NLP orchestrator coordinating tokenization, lemmatization,
entity extraction, and other Swedish text processing tasks.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Tuple

from kse.core import get_logger, KSEException, LANGUAGE

logger = get_logger('nlp')


class KSENLPException(KSEException):
    """NLP exception"""
    pass


class NLPCore:
    """
    Swedish NLP core coordinator.
    
    Orchestrates:
    - Tokenization
    - Lemmatization
    - Entity extraction
    - Sentiment analysis
    - Language detection
    """
    
    def __init__(self):
        """Initialize NLP core"""
        self.language = LANGUAGE
        
        # Import lazy to avoid dependency issues
        self._tokenizer = None
        self._lemmatizer = None
        self._entity_extractor = None
        
        logger.info(f"NLPCore initialized for language: {self.language}")
    
    def process_text(self, text: str) -> Dict:
        """
        Full text processing pipeline.
        
        Args:
            text: Text to process
            
        Returns:
            Dictionary with processing results
        """
        try:
            from .kse_tokenizer import Tokenizer
            from .kse_lemmatizer import Lemmatizer
            from .kse_entity_extractor import EntityExtractor
            from .kse_sentiment_analyzer import SentimentAnalyzer
            
            tokenizer = Tokenizer()
            lemmatizer = Lemmatizer()
            entity_extractor = EntityExtractor()
            sentiment = SentimentAnalyzer()
            
            # Tokenization
            tokens = tokenizer.tokenize(text)
            
            # Lemmatization
            lemmas = lemmatizer.lemmatize(tokens)
            
            # Entity extraction
            entities = entity_extractor.extract(text)
            
            # Sentiment
            sentiment_score = sentiment.analyze(text)
            
            result = {
                'original_text': text,
                'tokens': tokens,
                'lemmas': lemmas,
                'entities': entities,
                'sentiment': sentiment_score,
            }
            
            logger.debug(f"Text processed: {len(tokens)} tokens, {len(entities)} entities")
            return result
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise KSENLPException(f"Failed to process text") from e
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        from .kse_tokenizer import Tokenizer
        tokenizer = Tokenizer()
        return tokenizer.tokenize(text)
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens"""
        from .kse_lemmatizer import Lemmatizer
        lemmatizer = Lemmatizer()
        return lemmatizer.lemmatize(tokens)
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities"""
        from .kse_entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        return extractor.extract(text)
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment"""
        from .kse_sentiment_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        return analyzer.analyze(text)
    
    def detect_language(self, text: str) -> str:
        """Detect language"""
        from .kse_language_detector import LanguageDetector
        detector = LanguageDetector()
        return detector.detect(text)


__all__ = ["NLPCore", "KSENLPException"]
