"""
KSE Tokenizer

Swedish text tokenization and stemming for search indexing.
"""

from typing import List, Set
import re
import logging

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


# Swedish stop words (common words to exclude from indexing)
SWEDISH_STOPWORDS = {
    'och', 'det', 'att', 'en', 'i', 'som', 'på', 'de', 'är', 'det', 'den',
    'som', 'ett', 'för', 'var', 'varit', 'varit', 'varit', 'varit', 'varit',
    'med', 'från', 'av', 'till', 'om', 'eller', 'än', 'då', 'nu', 'varit',
    'kan', 'ska', 'skulle', 'kan', 'kunna', 'många', 'var', 'vid', 'väl',
    'just', 'redan', 'sina', 'sina', 'sina', 'sina', 'sina', 'sina', 'sina',
    'hans', 'hennes', 'dess', 'deras', 'den', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'detta', 'dessa', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
    'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna', 'denna',
}


def stem_swedish(word: str) -> str:
    """
    Simple Swedish stemmer using suffix removal.
    
    Args:
        word: Word to stem
        
    Returns:
        Stemmed word
    """
    word = word.lower()
    
    if len(word) <= 3:
        return word
    
    # Common Swedish suffixes (ordered by length, longest first)
    suffixes = [
        # Noun plurals and cases
        ('heterna', 'het'),  # Plural definite
        ('heten', 'het'),    # Singular definite
        ('erna', 'er'),      # Plural definite
        ('en', ''),          # Singular definite
        ('ar', ''),          # Plural indefinite
        ('er', ''),          # Plural
        ('a', ''),           # Plural
        
        # Adjective forms
        ('ast', ''),         # Superlative
        ('are', 'ar'),       # Comparative
        
        # Verb forms
        ('ade', ''),         # Past tense
        ('ar', ''),          # Present tense
        ('as', ''),          # Passive
        
        # Diminutives and augmentatives
        ('ig', ''),          # Diminutive
        ('lig', ''),         # Adjective suffix
    ]
    
    for suffix, replacement in suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) > 2:
            word = word[:-len(suffix)] + replacement
            break
    
    return word


class Tokenizer:
    """Tokenizes and processes Swedish text for indexing."""
    
    def __init__(self, remove_stopwords: bool = True, use_stemming: bool = True):
        """
        Initialize tokenizer.
        
        Args:
            remove_stopwords: Remove common stop words
            use_stemming: Apply stemming to words
        """
        self.remove_stopwords = remove_stopwords
        self.use_stemming = use_stemming
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Split on non-alphanumeric (keep Swedish characters å, ä, ö)
        # Unicode pattern for Swedish text
        tokens = re.findall(r'[\w\-åäöæøé]+', text, re.UNICODE)
        
        # Filter by length (minimum 2 characters, maximum 50)
        tokens = [t for t in tokens if 2 <= len(t) <= 50]
        
        # Remove stopwords
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in SWEDISH_STOPWORDS]
        
        # Apply stemming
        if self.use_stemming:
            tokens = [stem_swedish(t) for t in tokens]
        
        # Remove duplicates (preserve order)
        seen = set()
        unique_tokens = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                unique_tokens.append(t)
        
        return unique_tokens
    
    def tokenize_with_positions(self, text: str) -> List[tuple]:
        """
        Tokenize text and return with positions.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of (token, position) tuples
        """
        if not text:
            return []
        
        text_lower = text.lower()
        tokens = []
        position = 0
        
        for match in re.finditer(r'[\w\-åäöæøé]+', text_lower, re.UNICODE):
            token = match.group(0)
            
            if 2 <= len(token) <= 50:
                if self.remove_stopwords and token in SWEDISH_STOPWORDS:
                    continue
                
                stemmed = stem_swedish(token) if self.use_stemming else token
                tokens.append((stemmed, position))
                position += 1
        
        return tokens
    
    def get_term_frequency(self, tokens: List[str]) -> dict:
        """
        Calculate term frequency in token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary {term: frequency}
        """
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        return freq
    
    @staticmethod
    def remove_html_tags(html: str) -> str:
        """
        Remove HTML tags from text.
        
        Args:
            html: HTML string
            
        Returns:
            Text without tags
        """
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text for processing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')
        
        return text
