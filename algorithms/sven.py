"""
SVEN - Swedish Natural Language Processing & Query Expansion
Handle Swedish language specifics and expand queries
"""

import re
from typing import List, Set


class SVEN:
    """Swedish Natural Language Processing and query expansion"""
    
    def __init__(self):
        # Swedish synonyms and variations
        self.swedish_synonyms = {
            'väder': ['vädret', 'temperatur', 'väderprognos', 'klimat', 'väderrapport'],
            'jobb': ['arbete', 'anstallning', 'anställning', 'lediga tjänster', 'jobböpning'],
            'hälsa': ['sjukvard', 'sjukvård', 'medicin', 'läkarvård', 'sjukdom'],
            'mat': ['matlagning', 'recept', 'mat', 'dryck', 'matblogg', 'mat-och-dryck'],
            'resa': ['resor', 'resmal', 'resmål', 'turism', 'semesterresa'],
            'nyhet': ['nyheter', 'senaste', 'breaking news', 'händelse', 'nyhetsuppdatering'],
            'sport': ['sportnyheter', 'sportevent', 'match', 'tävling', 'idrottsnyheter'],
        }
        
        # Swedish stop words to remove
        self.stop_words = {
            'och', 'eller', 'men', 'för', 'till', 'från', 'i', 'på', 'av', 'som',
            'är', 'var', 'varit', 'han', 'hon', 'den', 'denna', 'det', 'denna',
            'en', 'ett', 'två', 'tre', 'fyra', 'fem', 'sex', 'sju', 'åtta', 'nio'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize Swedish text (lowercase, remove accents, trim)"""
        # Lowercase
        text = text.lower().strip()
        
        # Keep Swedish characters but standardize
        return text
    
    def expand_query(self, query: str) -> Set[str]:
        """
        Expand query with Swedish synonyms and variations
        Returns: Set of expanded query variations
        """
        normalized = self.normalize_text(query)
        expansions = {normalized}
        
        # Check each word in query
        words = normalized.split()
        for word in words:
            if word in self.swedish_synonyms:
                # Add all synonyms
                for synonym in self.swedish_synonyms[word]:
                    expanded = normalized.replace(word, synonym, 1)
                    expansions.add(expanded)
        
        return expansions
    
    def remove_stop_words(self, text: str) -> str:
        """Remove Swedish stop words"""
        words = text.lower().split()
        filtered = [w for w in words if w not in self.stop_words]
        return ' '.join(filtered)
    
    def handle_special_chars(self, text: str) -> str:
        """Handle Swedish special characters (å, ä, ö)"""
        # These are kept as-is for Swedish compatibility
        # But we can add alternative spellings
        alternatives = {
            'å': ['a'],
            'ä': ['a', 'ae'],
            'ö': ['o', 'oe']
        }
        return text
    
    def detect_intent(self, query: str) -> str:
        """
        Detect query intent from Swedish keywords
        Returns: Category (news, weather, jobs, health, etc)
        """
        query_lower = self.normalize_text(query)
        
        intent_map = {
            'weather': ['väder', 'temperatur', 'snö', 'regn', 'vind', 'solsken'],
            'news': ['nyhet', 'senaste', 'breaking', 'olycka', 'dödat', 'händelse'],
            'jobs': ['jobb', 'anställning', 'lediga', 'arbete', 'rekrytering'],
            'health': ['sjukdom', 'symptom', 'läkare', 'medicin', 'hälsa', 'smärta'],
            'food': ['mat', 'recept', 'matlagning', 'restaurang', 'dryck'],
            'sports': ['sport', 'fotboll', 'hockey', 'match', 'tävling', 'resultat'],
            'travel': ['resa', 'hotell', 'flyg', 'destination', 'turist', 'semester'],
            'entertainment': ['film', 'musik', 'serie', 'kultur', 'show', 'konsert'],
        }
        
        for intent, keywords in intent_map.items():
            if any(kw in query_lower for kw in keywords):
                return intent
        
        return 'general'
    
    def handle_typos(self, word: str) -> List[str]:
        """
        Generate likely corrections for misspelled words
        Returns: List of possible corrections
        """
        corrections = [word]
        
        # Common Swedish typos
        typo_map = {
            'vader': ['väder'],
            'halsa': ['hälsa'],
            'jobb': ['jobb'],
            'anstallning': ['anställning'],
            'smarta': ['smärta'],
        }
        
        if word in typo_map:
            corrections.extend(typo_map[word])
        
        return corrections
    
    def process_query(self, query: str) -> dict:
        """
        Complete query processing pipeline
        Returns: Dict with normalized query, expansions, intent, etc
        """
        normalized = self.normalize_text(query)
        
        return {
            'original': query,
            'normalized': normalized,
            'clean': self.remove_stop_words(normalized),
            'expansions': list(self.expand_query(normalized)),
            'intent': self.detect_intent(normalized),
            'language': 'sv'
        }
