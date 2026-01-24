"""
Swedish Text Tokenizer

Breaks text into tokens (words, phrases) for NLP processing.
"""

from dataclasses import dataclass
from typing import List, Set, Optional
from enum import Enum
import re

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class TokenType(Enum):
    """Token classification."""
    WORD = "word"
    PHRASE = "phrase"
    NUMBER = "number"
    SPECIAL = "special"
    UNKNOWN = "unknown"


@dataclass
class Token:
    """Represents a tokenized word."""
    text: str
    token_type: TokenType
    position: int
    length: int
    frequency: int = 1
    
    def __hash__(self):
        return hash(self.text.lower())
    
    def __eq__(self, other):
        if isinstance(other, Token):
            return self.text.lower() == other.text.lower()
        return self.text.lower() == str(other).lower()


class Tokenizer:
    """
    Swedish text tokenizer.
    
    Features:
    - Case-insensitive tokenization
    - Swedish stopword filtering
    - Compound word handling
    - Number and special character handling
    """
    
    # Swedish stopwords (common, low-value words)
    SWEDISH_STOPWORDS = {
        'och', 'det', 'att', 'en', 'i', 'jag', 'hon', 'som', 'han', 'på',
        'de', 'med', 'han', 'då', 'sin', 'var', 'mig', 'zich', 'över',
        'än', 'dig', 'kan', 'sina', 'här', 'ha', 'mot', 'alla', 'under',
        'någon', 'eller', 'allt', 'mycket', 'sedan', 'ju', 'denna', 'själv',
        'detta', 'åt', 'utan', 'varit', 'hur', 'ingen', 'mitt', 'ni', 'bli',
        'blev', 'oss', 'din', 'dessa', 'några', 'deras', 'blir', 'mina',
        'vilken', 'er', 'sådan', 'vår', 'blivit', 'dess', 'inom', 'mellan',
        'sådant', 'varför', 'varje', 'vilka', 'ditt', 'vem', 'vilket', 'sitta',
        'detta', 'vart', 'dina', 'vars', 'vårt', 'våra', 'ert', 'era', 'vilkas',
        'är', 'av', 'till', 'för', 'från', 'när', 'om', 'om', 'genom', 'efter'
    }
    
    # Min/max token length
    MIN_TOKEN_LENGTH = 2
    MAX_TOKEN_LENGTH = 50
    
    def __init__(
        self,
        min_token_length: int = MIN_TOKEN_LENGTH,
        max_token_length: int = MAX_TOKEN_LENGTH,
        remove_stopwords: bool = True,
    ):
        """
        Initialize tokenizer.
        
        Args:
            min_token_length: Minimum token length
            max_token_length: Maximum token length
            remove_stopwords: Remove Swedish stopwords
        """
        self.min_token_length = min_token_length
        self.max_token_length = max_token_length
        self.remove_stopwords = remove_stopwords
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
        
        Returns:
            List of Token objects
        """
        if not text or not isinstance(text, str):
            return []
        
        tokens = []
        position = 0
        
        # Split by whitespace and punctuation
        # Pattern matches words (including Swedish chars: åäö)
        word_pattern = r'[a-zåäö0-9]+'
        
        for match in re.finditer(word_pattern, text.lower()):
            word = match.group()
            start_pos = match.start()
            
            # Length validation
            if len(word) < self.min_token_length or len(word) > self.max_token_length:
                continue
            
            # Stopword filtering
            if self.remove_stopwords and word in self.SWEDISH_STOPWORDS:
                continue
            
            # Determine token type
            token_type = self._classify_token(word)
            
            token = Token(
                text=word,
                token_type=token_type,
                position=start_pos,
                length=len(word)
            )
            
            tokens.append(token)
        
        return tokens
    
    def tokenize_phrases(self, text: str, phrase_length: int = 2) -> List[Token]:
        """
        Extract n-grams (phrases) from text.
        
        Args:
            text: Input text
            phrase_length: Number of words in phrase (default 2-gram)
        
        Returns:
            List of phrase tokens
        """
        if phrase_length < 2 or phrase_length > 5:
            raise ValueError("Phrase length must be between 2 and 5")
        
        # First tokenize normally
        tokens = self.tokenize(text)
        
        if len(tokens) < phrase_length:
            return []
        
        phrases = []
        
        # Create n-grams
        for i in range(len(tokens) - phrase_length + 1):
            phrase_tokens = tokens[i:i + phrase_length]
            phrase_text = ' '.join([t.text for t in phrase_tokens])
            
            # Create phrase token
            phrase = Token(
                text=phrase_text,
                token_type=TokenType.PHRASE,
                position=phrase_tokens[0].position,
                length=phrase_tokens[-1].position + phrase_tokens[-1].length
            )
            
            phrases.append(phrase)
        
        return phrases
    
    def get_unique_tokens(self, tokens: List[Token]) -> Set[Token]:
        """
        Get unique tokens from list.
        
        Args:
            tokens: List of tokens
        
        Returns:
            Set of unique tokens
        """
        return set(tokens)
    
    def get_token_frequencies(self, tokens: List[Token]) -> dict:
        """
        Calculate frequency of each token.
        
        Args:
            tokens: List of tokens
        
        Returns:
            Dictionary: token.text -> frequency
        """
        frequencies = {}
        
        for token in tokens:
            key = token.text.lower()
            frequencies[key] = frequencies.get(key, 0) + 1
        
        return frequencies
    
    def _classify_token(self, word: str) -> TokenType:
        """
        Classify token type.
        
        Args:
            word: Token to classify
        
        Returns:
            TokenType classification
        """
        # Check if number
        if word.isdigit():
            return TokenType.NUMBER
        
        # Check if contains numbers
        if any(c.isdigit() for c in word):
            return TokenType.SPECIAL
        
        # Check if contains special characters
        if not all(c.isalpha() or c in 'åäö' for c in word):
            return TokenType.SPECIAL
        
        # Regular word
        return TokenType.WORD
    
    def clean_text(self, text: str) -> str:
        """
        Clean text for tokenization.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text
    
    def get_stopwords(self) -> Set[str]:
        """
        Get Swedish stopwords set.
        
        Returns:
            Set of stopwords
        """
        return self.SWEDISH_STOPWORDS.copy()
    
    def add_stopword(self, word: str) -> None:
        """
        Add custom stopword.
        
        Args:
            word: Stopword to add
        """
        self.SWEDISH_STOPWORDS.add(word.lower())
    
    def remove_stopword(self, word: str) -> None:
        """
        Remove stopword.
        
        Args:
            word: Stopword to remove
        """
        self.SWEDISH_STOPWORDS.discard(word.lower())
