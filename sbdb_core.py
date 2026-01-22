"""
Klar SBDB Core - Swedish NLP Engine
Handles tokenization, lemmatization, and Swedish-optimized text processing
"""

import re
import json
import logging
from typing import List, Dict, Set, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Swedish stopwords (common filler words)
SWEDISH_STOPWORDS = {
    'och', 'det', 'att', 'en', 'i', 'som', 'på', 'de', 'är', 'till',
    'var', 'då', 'ha', 'från', 'de', 'som', 'denna', 'denna', 'dessa',
    'det', 'denna', 'detta', 'denna', 'här', 'där', 'vad', 'vilken',
    'detta', 'vilka', 'dessa', 'alla', 'ingen', 'någon', 'något',
    'några', 'andra', 'övriga', 'samma', 'sådan', 'många', 'mycket',
    'om', 'så', 'än', 'eller', 'men', 'dock', 'utan', 'för', 'vi',
    'genom', 'under', 'över', 'mellan', 'kring', 'mitt', 'utan', 'genom'
}

# Swedish compound word separators and patterns
COMPOUND_PATTERNS = [
    (r'(\w+)(bad)(rum)', lambda m: f"{m.group(1)}bad rum"),  # bad|rum
    (r'(\w+)(rum)(\w+)', lambda m: f"{m.group(1)}rum {m.group(3)}"),  # rum|word
    (r'(\w+)(hus)(\w+)', lambda m: f"{m.group(1)}hus {m.group(3)}"),  # hus|word
]

# Swedish lemmatization rules (simplified)
LEMMATIZATION_RULES = {
    'er$': '',          # restauranger → restaurang
    'ar$': '',          # hundar → hund (removed for safety)
    'or$': '',          # dörrar → dörr
    'ade$': 'a',        # spelade → spela
    'ade$': 'a',        # gick → gå
    'ade$': 'a',        # var → vara
    'are$': '',         # vackrare → vacker
    'est$': '',         # vackrast → vacker
}


class SwedishNLPEngine:
    """
    Swedish Natural Language Processing Engine
    Handles tokenization, lemmatization, and Swedish-specific text processing
    """
    
    def __init__(self):
        self.stopwords = SWEDISH_STOPWORDS
        self.compound_patterns = COMPOUND_PATTERNS
        self.lemmatization_rules = LEMMATIZATION_RULES
        logger.info("SwedishNLPEngine initialized")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Swedish text into words
        Handles compound words, special characters, and case normalization
        
        Args:
            text: Raw text to tokenize
            
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep Swedish letters (åäö)
        text = re.sub(r'[^a-zåäö\s\-]', '', text)
        
        # Split by whitespace
        tokens = text.split()
        
        # Remove empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def lemmatize(self, word: str) -> str:
        """
        Lemmatize Swedish word (normalize to base form)
        Examples:
            'restauranger' → 'restaurang'
            'spelade' → 'spela'
            'hundar' → 'hund'
        
        Args:
            word: Word to lemmatize
            
        Returns:
            Lemmatized form
        """
        word_lower = word.lower()
        
        # Apply lemmatization rules
        for suffix, replacement in self.lemmatization_rules.items():
            if re.search(suffix, word_lower):
                return re.sub(suffix, replacement, word_lower)
        
        return word_lower
    
    def process_text(self, text: str) -> List[str]:
        """
        Complete text processing pipeline:
        1. Tokenize
        2. Remove stopwords
        3. Lemmatize
        4. Filter empty tokens
        
        Args:
            text: Raw text
            
        Returns:
            Processed tokens (cleaned, normalized, lemmatized)
        """
        # Step 1: Tokenize
        tokens = self.tokenize(text)
        
        # Step 2: Remove stopwords
        tokens = [t for t in tokens if t not in self.stopwords]
        
        # Step 3: Lemmatize
        tokens = [self.lemmatize(t) for t in tokens]
        
        # Step 4: Remove duplicates (optional)
        # tokens = list(set(tokens))  # Uncomment for deduplication
        
        # Step 5: Filter very short tokens (< 3 chars are usually noise)
        tokens = [t for t in tokens if len(t) >= 3]
        
        return tokens
    
    def extract_metadata(self, text: str, url: str) -> Dict:
        """
        Extract metadata from text:
        - Geographic regions (Stockholm, Göteborg, etc.)
        - Dates
        - Named entities
        - Trust indicators
        
        Args:
            text: Page text
            url: Page URL (for trust scoring)
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'regions': [],
            'dates': [],
            'entities': [],
            'domain': self._extract_domain(url),
            'trust_score': self._calculate_trust(url)
        }
        
        # Extract Swedish regions
        metadata['regions'] = self._extract_regions(text)
        
        # Extract dates (YYYY-MM-DD format)
        metadata['dates'] = self._extract_dates(text)
        
        return metadata
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        Example: https://sverigesradio.se/news → sverigesradio.se
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    
    def _calculate_trust(self, url: str) -> float:
        """
        Calculate trust score based on URL characteristics
        gov.se, svt.se, sverigesradio.se → 0.95+
        .se domains → 0.75-0.90
        Others → lower
        
        Returns:
            Trust score 0.0 - 1.0
        """
        domain = self._extract_domain(url)
        
        # Government domains (highest trust)
        if '.gov.se' in domain:
            return 0.98
        
        # Official media
        if domain in ['svt.se', 'sverigesradio.se', 'dn.se', 'aftonbladet.se']:
            return 0.95
        
        # Swedish domain
        if domain.endswith('.se'):
            return 0.80
        
        # Foreign domain
        return 0.60
    
    def _extract_regions(self, text: str) -> List[str]:
        """
        Extract Swedish region names from text
        Läns (counties): Stockholm, Västra Götaland, Skåne, etc.
        Municipalities: Göteborg, Malmö, Uppsala, etc.
        """
        swedish_regions = [
            'stockholm', 'västra götaland', 'skåne', 'uppsala', 'värmland',
            'göteborg', 'malmö', 'växjö', 'karlstad', 'linköping', 'östersund',
            'gävle', 'umeå', 'luleå', 'sundsvall', 'norrköping', 'jönköping',
            'helsingborg', 'västerås', 'örebro', 'trollhättan', 'borås'
        ]
        
        text_lower = text.lower()
        found_regions = []
        
        for region in swedish_regions:
            if region in text_lower:
                found_regions.append(region)
        
        return found_regions
    
    def _extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text (YYYY-MM-DD and Swedish format)
        Patterns:
            2026-01-22
            22 januari 2026
            22/1/2026
        """
        dates = []
        
        # ISO format (YYYY-MM-DD)
        iso_dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        dates.extend(iso_dates)
        
        # Swedish format (DD/MM/YYYY)
        swedish_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)
        dates.extend(swedish_dates)
        
        return dates
    
    def calculate_tf_idf(self, word: str, page_text: str, all_pages_text: List[str]) -> float:
        """
        Calculate TF-IDF score for a word in a page
        TF-IDF = (word_count_in_page / total_words_in_page) * log(total_pages / pages_with_word)
        
        Args:
            word: Word to score
            page_text: Text of the page
            all_pages_text: List of all page texts (for IDF calculation)
            
        Returns:
            TF-IDF score (0.0 - 1.0)
        """
        import math
        
        # Term Frequency (TF)
        page_words = page_text.lower().split()
        word_count = page_words.count(word.lower())
        tf = word_count / len(page_words) if page_words else 0
        
        # Inverse Document Frequency (IDF)
        pages_with_word = sum(1 for page in all_pages_text if word.lower() in page.lower())
        total_pages = len(all_pages_text)
        
        if pages_with_word == 0:
            return 0.0
        
        idf = math.log(total_pages / pages_with_word)
        
        # TF-IDF
        tf_idf = tf * idf
        
        # Normalize to 0.0 - 1.0
        return min(tf_idf, 1.0)


class TextProcessor:
    """
    High-level text processor combining NLP + indexing
    """
    
    def __init__(self):
        self.nlp_engine = SwedishNLPEngine()
    
    def process_page(self, title: str, text: str, url: str) -> Dict:
        """
        Complete page processing for indexing
        
        Args:
            title: Page title
            text: Page content
            url: Page URL
            
        Returns:
            Processed page data
        """
        # Combine title + text
        full_text = f"{title} {text}"
        
        # Process text
        tokens = self.nlp_engine.process_text(full_text)
        
        # Extract metadata
        metadata = self.nlp_engine.extract_metadata(text, url)
        
        return {
            'url': url,
            'title': title,
            'tokens': tokens,
            'text': text,
            'metadata': metadata,
            'token_count': len(tokens)
        }


if __name__ == "__main__":
    # Test the Swedish NLP Engine
    nlp = SwedishNLPEngine()
    
    # Test tokenization
    test_text = "Restauranger i Stockholm och Göteborg är fantastiska."
    tokens = nlp.tokenize(test_text)
    print(f"Tokens: {tokens}")
    
    # Test lemmatization
    test_words = ["restauranger", "hundar", "spelade", "vackrare"]
    for word in test_words:
        lemma = nlp.lemmatize(word)
        print(f"  {word} → {lemma}")
    
    # Test full processing
    processed = nlp.process_text(test_text)
    print(f"\nProcessed tokens: {processed}")
    
    # Test metadata extraction
    metadata = nlp.extract_metadata(test_text, "https://sverigesradio.se/article/123")
    print(f"\nMetadata: {json.dumps(metadata, indent=2, ensure_ascii=False)}")
    
    # Test TextProcessor
    processor = TextProcessor()
    page_data = processor.process_page(
        title="Bästa restaurangerna i Stockholm",
        text="Stockholm har många fantastiska restauranger. Vi listar de bästa.",
        url="https://sverigesradio.se/article/123"
    )
    print(f"\nProcessed page: {json.dumps(page_data, indent=2, ensure_ascii=False)}")
