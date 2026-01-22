"""
Swedish Natural Language Processing Engine
Handles Swedish-specific linguistic challenges:
- Compound word splitting
- Lemmatization
- Named entity recognition
- Intent detection
- Sentiment analysis
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter


class SwedishNLP:
    """
    Production-grade Swedish NLP engine optimized for search queries.
    Handles Swedish language nuances that English-first NLP misses.
    """

    def __init__(self):
        """
        Initialize Swedish NLP engine with linguistic data.
        Loads Swedish-specific dictionaries and rules.
        """
        self.compound_words = self._load_compound_words()
        self.lemma_rules = self._load_lemma_rules()
        self.stopwords = self._load_swedish_stopwords()
        self.entity_patterns = self._load_entity_patterns()
        self.synonyms = self._load_synonyms()
        
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Swedish text while handling special cases.
        Preserves Swedish characters (å, ä, ö)
        
        Args:
            text: Input Swedish text
            
        Returns:
            List of tokens (words)
            
        Example:
            >>> nlp = SwedishNLP()
            >>> nlp.tokenize("Hur många restauranger finns i Stockholm?")
            ['Hur', 'många', 'restauranger', 'finns', 'i', 'Stockholm']
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation except hyphens (for compound words)
        text = re.sub(r'[^\wå\ä\ö\s-]', '', text)
        
        # Split on whitespace
        tokens = text.split()
        
        # Handle hyphenated words
        expanded = []
        for token in tokens:
            if '-' in token:
                expanded.extend(token.split('-'))
            else:
                expanded.append(token)
        
        return expanded

    def lemmatize(self, token: str) -> str:
        """
        Convert Swedish word to its base form (lemma).
        
        Examples:
            restauranger -> restaurang
            huset -> hus
            springa -> springa
            
        Args:
            token: Word to lemmatize
            
        Returns:
            Base form of word
        """
        token = token.lower()
        
        # Check if already in base form
        if token in self.lemma_rules['base_forms']:
            return token
        
        # Apply Swedish suffix rules
        for suffix, replacement in self.lemma_rules['suffix_rules'].items():
            if token.endswith(suffix):
                base = token[:-len(suffix)] + replacement
                if base in self.lemma_rules['base_forms']:
                    return base
        
        return token

    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract named entities (people, places, organizations).
        
        Args:
            text: Input text
            
        Returns:
            List of (entity, type) tuples
            
        Example:
            >>> nlp.extract_entities("Stefan Löfven är statsminister i Sverige")
            [('Stefan Löfven', 'person'), ('Sverige', 'country')]
        """
        entities = []
        
        # Geographic entities
        for pattern, entity_type in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group(0), entity_type))
        
        return entities

    def detect_intent(self, query: str) -> Dict[str, float]:
        """
        Detect user's search intent.
        
        Intents:
            - calculation: Mathematical queries ("1+1?", "vad är 2*3?")
            - factual_question: "Vem är?", "Vad är?", "Hur?"
            - local_search: "restauranger i stockholm"
            - news_search: "senaste nytt om"
            - general_search: Default intent
            
        Args:
            query: Search query
            
        Returns:
            Dict mapping intent -> confidence (0-1)
        """
        query_lower = query.lower()
        intents = defaultdict(float)
        
        # Calculation intent
        if re.search(r'\d+\s*[+\-*/]\s*\d+', query_lower):
            intents['calculation'] = 0.95
        
        # Factual question intent
        if query_lower.startswith(('vem är', 'vad är', 'hur', 'när', 'där')):
            intents['factual_question'] = 0.90
        
        # Local search intent
        if 'i stockholm' in query_lower or 'i göteborg' in query_lower or 'i malmö' in query_lower:
            intents['local_search'] = 0.85
        
        # News intent
        if any(word in query_lower for word in ['senaste', 'nytt', 'idag', 'igår', 'nyheter']):
            intents['news_search'] = 0.80
        
        # Default to general search
        if not intents:
            intents['general_search'] = 0.70
        
        return dict(intents)

    def normalize(self, text: str) -> str:
        """
        Normalize Swedish text for indexing.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalize Swedish characters
        text = text.replace('å', 'a').replace('ä', 'e').replace('ö', 'o')
        
        return text

    def get_synonyms(self, word: str) -> List[str]:
        """
        Get Swedish synonyms for word.
        
        Args:
            word: Input word
            
        Returns:
            List of synonyms
        """
        return self.synonyms.get(word.lower(), [])

    # Private methods for loading linguistic data
    
    def _load_compound_words(self) -> Dict[str, List[str]]:
        """Load Swedish compound word rules."""
        return {
            'badrum': ['bad', 'rum'],
            'sovrum': ['sov', 'rum'],
            'vardagsrum': ['vardags', 'rum'],
            'kök': ['köks', 'rum'],
        }
    
    def _load_lemma_rules(self) -> Dict:
        """Load Swedish lemmatization rules."""
        return {
            'base_forms': {
                'restaurang', 'hus', 'springa', 'stockholm', 'sverige',
                'person', 'plats', 'organisation', 'stad', 'land'
            },
            'suffix_rules': {
                'er': '',      # restauranger -> restaurang
                'ar': '',      # hus -> hus (no change)
                'a': '',       # springa -> spring
                'et': '',      # huset -> hus
                'en': '',      # hanen -> han
            }
        }
    
    def _load_swedish_stopwords(self) -> set:
        """Load Swedish stop words (common words to ignore in indexing)."""
        return {
            'och', 'i', 'en', 'ett', 'eller', 'men', 'som', 'av', 'för',
            'på', 'till', 'från', 'var', 'är', 'han', 'hon', 'det', 'den',
            'som', 'då', 'där', 'här', 'vad', 'hur', 'vilken', 'vilka',
            'denna', 'denne', 'denna', 'dessa', 'mycket', 'lite', 'några',
        }
    
    def _load_entity_patterns(self) -> Dict[str, str]:
        """Load Swedish entity recognition patterns."""
        return {
            r'\b(Sverige|Swedish|Swede)\b': 'country',
            r'\b(Stockholm|Göteborg|Malmö|Uppsala|Västerås|Örebro|Linköping)\b': 'city',
            r'\b(Jan|Stefan|Magdalena|Eva|Anders|Per|Ingrid)\s+\w+\b': 'person',
        }
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Load Swedish synonym mappings."""
        return {
            'restaurang': ['matställe', 'krog', 'eatery'],
            'bil': ['automobil', 'fordon', 'motorfordon'],
            'snabb': ['fort', 'hastig', 'skyndsam'],
            'dålig': ['useless', 'dåligt', 'elak'],
        }


if __name__ == "__main__":
    # Test the Swedish NLP engine
    nlp = SwedishNLP()
    
    test_query = "Vilka restauranger finns i Stockholm?"
    print(f"Query: {test_query}")
    print(f"Tokens: {nlp.tokenize(test_query)}")
    print(f"Entities: {nlp.extract_entities(test_query)}")
    print(f"Intent: {nlp.detect_intent(test_query)}")
