"""
Keyword Extraction

Extracts important keywords from text using frequency and contextual analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import Counter
import math

from kse.nlp.kse_nlp_tokenizer import Tokenizer, Token, TokenType
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


@dataclass
class KeywordFrequency:
    """Keyword with frequency data."""
    keyword: str
    frequency: int
    positions: List[int] = field(default_factory=list)
    
    @property
    def is_frequent(self) -> bool:
        """Check if keyword appears frequently (3+ times)."""
        return self.frequency >= 3


@dataclass
class Keyword:
    """Extracted keyword with scores."""
    text: str
    frequency: int
    tfidf_score: float = 0.0
    position_score: float = 0.0
    context_score: float = 0.0
    combined_score: float = 0.0
    is_phrase: bool = False
    
    def __lt__(self, other):
        """Sort by combined score (descending)."""
        return self.combined_score > other.combined_score


class KeywordExtractor:
    """
    Keyword extraction engine.
    
    Features:
    - Frequency-based extraction
    - Position-based scoring (title, heading, first 100 words)
    - Phrase extraction (2-grams, 3-grams)
    - Combined scoring
    """
    
    # Position boost factors
    TITLE_BOOST = 3.0
    HEADING_BOOST = 2.5
    EARLY_TEXT_BOOST = 1.5
    
    def __init__(
        self,
        tokenizer: Optional[Tokenizer] = None,
        min_frequency: int = 2,
        max_keywords: int = 50,
    ):
        """
        Initialize keyword extractor.
        
        Args:
            tokenizer: Custom tokenizer (uses default if None)
            min_frequency: Minimum frequency to extract keyword
            max_keywords: Maximum keywords to return
        """
        self.tokenizer = tokenizer or Tokenizer()
        self.min_frequency = min_frequency
        self.max_keywords = max_keywords
    
    def extract(
        self,
        text: str,
        title: str = "",
        description: str = "",
        include_phrases: bool = True,
    ) -> List[Keyword]:
        """
        Extract keywords from text.
        
        Args:
            text: Main content text
            title: Page title (boosted scoring)
            description: Meta description (boosted scoring)
            include_phrases: Extract 2-gram phrases
        
        Returns:
            List of Keyword objects sorted by score
        """
        keywords = {}
        
        # Process title (highest boost)
        if title:
            title_keywords = self.tokenizer.tokenize(title)
            for token in title_keywords:
                key = token.text.lower()
                if key not in keywords:
                    keywords[key] = Keyword(
                        text=key,
                        frequency=0,
                        position_score=0.0,
                        is_phrase=False
                    )
                keywords[key].frequency += 1
                keywords[key].position_score += self.TITLE_BOOST
        
        # Process description (medium boost)
        if description:
            desc_keywords = self.tokenizer.tokenize(description)
            for token in desc_keywords:
                key = token.text.lower()
                if key not in keywords:
                    keywords[key] = Keyword(
                        text=key,
                        frequency=0,
                        position_score=0.0,
                        is_phrase=False
                    )
                keywords[key].frequency += 1
                keywords[key].position_score += self.HEADING_BOOST
        
        # Process main text
        text_cleaned = self.tokenizer.clean_text(text)
        text_keywords = self.tokenizer.tokenize(text_cleaned)
        
        # Track early text (first 100 words)
        early_text_count = 0
        
        for token in text_keywords:
            key = token.text.lower()
            
            if key not in keywords:
                keywords[key] = Keyword(
                    text=key,
                    frequency=0,
                    position_score=0.0,
                    is_phrase=False
                )
            
            keywords[key].frequency += 1
            
            # Boost early appearance
            if early_text_count < 100:
                keywords[key].position_score += self.EARLY_TEXT_BOOST
                early_text_count += 1
        
        # Extract phrases if requested
        phrase_keywords = {}
        if include_phrases and len(text_keywords) > 2:
            # 2-grams
            bigrams = self.tokenizer.tokenize_phrases(text_cleaned, phrase_length=2)
            for token in bigrams:
                key = token.text.lower()
                if key not in phrase_keywords:
                    phrase_keywords[key] = Keyword(
                        text=key,
                        frequency=1,
                        is_phrase=True
                    )
                else:
                    phrase_keywords[key].frequency += 1
            
            # 3-grams (less frequent)
            trigrams = self.tokenizer.tokenize_phrases(text_cleaned, phrase_length=3)
            for token in trigrams:
                key = token.text.lower()
                if key not in phrase_keywords:
                    phrase_keywords[key] = Keyword(
                        text=key,
                        frequency=1,
                        is_phrase=True
                    )
                else:
                    phrase_keywords[key].frequency += 1
            
            keywords.update(phrase_keywords)
        
        # Filter by minimum frequency
        filtered = {
            k: v for k, v in keywords.items()
            if v.frequency >= self.min_frequency
        }
        
        # Calculate combined scores
        for keyword in filtered.values():
            # Frequency score (0-1)
            max_freq = max(kw.frequency for kw in filtered.values())
            freq_score = keyword.frequency / max_freq if max_freq > 0 else 0
            
            # Position score (normalize)
            max_pos = max(
                (kw.position_score for kw in filtered.values()),
                default=1
            )
            pos_score = keyword.position_score / max_pos if max_pos > 0 else 0
            
            # Combined: weighted sum
            keyword.combined_score = (0.6 * freq_score) + (0.4 * pos_score)
        
        # Sort by combined score and return top N
        sorted_keywords = sorted(filtered.values())
        return sorted_keywords[:self.max_keywords]
    
    def extract_from_document(
        self,
        text: str,
        title: str = "",
        description: str = "",
        headings: List[str] = None,
    ) -> Tuple[List[Keyword], Dict[str, int]]:
        """
        Extract keywords from full document with multiple fields.
        
        Args:
            text: Main content
            title: Page title
            description: Meta description
            headings: List of headings/subheadings
        
        Returns:
            Tuple of (keywords, keyword_stats)
        """
        # Combine headings into description
        if headings:
            description = description + " " + " ".join(headings)
        
        # Extract keywords
        keywords = self.extract(
            text=text,
            title=title,
            description=description,
            include_phrases=True
        )
        
        # Generate statistics
        stats = {
            'total_keywords': len(keywords),
            'single_words': sum(1 for k in keywords if not k.is_phrase),
            'phrases': sum(1 for k in keywords if k.is_phrase),
            'avg_frequency': sum(k.frequency for k in keywords) / len(keywords) if keywords else 0,
            'avg_score': sum(k.combined_score for k in keywords) / len(keywords) if keywords else 0,
        }
        
        return keywords, stats
    
    def get_top_keywords(
        self,
        keywords: List[Keyword],
        count: int = 10,
    ) -> List[Keyword]:
        """
        Get top N keywords.
        
        Args:
            keywords: List of keywords
            count: Number of top keywords
        
        Returns:
            Top N keywords
        """
        return sorted(keywords, key=lambda k: k.combined_score, reverse=True)[:count]
    
    def keywords_to_dict(self, keywords: List[Keyword]) -> List[Dict]:
        """
        Convert keywords to dictionary format for storage.
        
        Args:
            keywords: List of keywords
        
        Returns:
            List of dictionaries
        """
        return [
            {
                'term': k.text,
                'frequency': k.frequency,
                'tfidf_score': k.tfidf_score,
                'combined_score': k.combined_score,
                'is_phrase': k.is_phrase,
            }
            for k in keywords
        ]
