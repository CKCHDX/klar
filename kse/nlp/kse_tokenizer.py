"""
KSE Tokenizer - Swedish tokenization and normalization
"""
import re
from typing import List
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class SwedishTokenizer:
    """Tokenize and normalize Swedish text"""
    
    def __init__(self):
        """Initialize tokenizer"""
        # Swedish alphabet includes å, ä, ö
        self.word_pattern = re.compile(r'\b[a-zåäöA-ZÅÄÖ]+\b')
        self.number_pattern = re.compile(r'\d+')
    
    def tokenize(self, text: str, lowercase: bool = True, remove_numbers: bool = True) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Text to tokenize
            lowercase: Convert to lowercase
            remove_numbers: Remove numeric tokens
        
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Find all words
        tokens = self.word_pattern.findall(text)
        
        # Lowercase
        if lowercase:
            tokens = [t.lower() for t in tokens]
        
        # Remove numbers
        if remove_numbers:
            tokens = [t for t in tokens if not self.number_pattern.fullmatch(t)]
        
        # Remove empty tokens
        tokens = [t for t in tokens if t]
        
        return tokens
    
    def normalize_word(self, word: str) -> str:
        """
        Normalize a single word
        
        Args:
            word: Word to normalize
        
        Returns:
            Normalized word
        """
        # Convert to lowercase
        word = word.lower()
        
        # Remove any remaining non-alphabetic characters
        word = re.sub(r'[^a-zåäö]', '', word)
        
        return word
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
        
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def tokenize_query(self, query: str) -> List[str]:
        """
        Tokenize search query
        
        Args:
            query: Search query
        
        Returns:
            List of query tokens
        """
        # For queries, keep more tokens including numbers
        tokens = self.tokenize(query, lowercase=True, remove_numbers=False)
        return tokens
    
    def get_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """
        Generate n-grams from tokens
        
        Args:
            tokens: List of tokens
            n: N-gram size
        
        Returns:
            List of n-grams
        """
        if len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
