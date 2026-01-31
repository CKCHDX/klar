"""
KSE NLP Core - Main NLP coordinator for Swedish language processing
"""
from typing import List
from kse.nlp.kse_tokenizer import SwedishTokenizer
from kse.nlp.kse_lemmatizer import SwedishLemmatizer
from kse.nlp.kse_stopwords import SwedishStopwords
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class NLPCore:
    """Main NLP coordinator for Swedish text processing"""
    
    def __init__(self, enable_lemmatization: bool = True, enable_stopword_removal: bool = True):
        """
        Initialize NLP core
        
        Args:
            enable_lemmatization: Enable lemmatization
            enable_stopword_removal: Enable stopword removal
        """
        self.tokenizer = SwedishTokenizer()
        self.lemmatizer = SwedishLemmatizer() if enable_lemmatization else None
        self.stopwords = SwedishStopwords() if enable_stopword_removal else None
        
        self.enable_lemmatization = enable_lemmatization
        self.enable_stopword_removal = enable_stopword_removal
        
        logger.info(f"NLP Core initialized (lemmatization: {enable_lemmatization}, "
                   f"stopword removal: {enable_stopword_removal})")
    
    def process_text(self, text: str) -> List[str]:
        """
        Process text through full NLP pipeline
        
        Args:
            text: Text to process
        
        Returns:
            List of processed tokens
        """
        if not text:
            return []
        
        # Tokenize
        tokens = self.tokenizer.tokenize(text, lowercase=True, remove_numbers=True)
        
        # Remove stopwords
        if self.enable_stopword_removal and self.stopwords:
            tokens = self.stopwords.remove_stopwords(tokens)
        
        # Lemmatize
        if self.enable_lemmatization and self.lemmatizer:
            tokens = self.lemmatizer.lemmatize_tokens(tokens)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tokens = []
        for token in tokens:
            if token not in seen and len(token) > 1:  # Filter very short tokens
                seen.add(token)
                unique_tokens.append(token)
        
        return unique_tokens
    
    def process_query(self, query: str) -> List[str]:
        """
        Process search query
        
        Args:
            query: Search query
        
        Returns:
            List of processed query tokens
        """
        if not query:
            return []
        
        # Tokenize (keep numbers for queries)
        tokens = self.tokenizer.tokenize(query, lowercase=True, remove_numbers=False)
        
        # Remove stopwords
        if self.enable_stopword_removal and self.stopwords:
            tokens = self.stopwords.remove_stopwords(tokens)
        
        # Lemmatize
        if self.enable_lemmatization and self.lemmatizer:
            tokens = self.lemmatizer.lemmatize_tokens(tokens)
        
        # Filter short tokens but keep meaningful ones
        tokens = [t for t in tokens if len(t) > 1]
        
        return tokens
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords
        
        Returns:
            List of keywords
        """
        tokens = self.process_text(text)
        
        # Count frequency
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in keywords[:max_keywords]]
    
    def tokenize_only(self, text: str) -> List[str]:
        """
        Only tokenize without further processing
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of tokens
        """
        return self.tokenizer.tokenize(text, lowercase=True, remove_numbers=True)
    
    def lemmatize_word(self, word: str) -> str:
        """
        Lemmatize a single word
        
        Args:
            word: Word to lemmatize
        
        Returns:
            Lemmatized word
        """
        if self.lemmatizer:
            return self.lemmatizer.lemmatize(word)
        return word.lower()
