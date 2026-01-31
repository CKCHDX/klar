"""
KSE Query Preprocessor - Preprocess search queries
"""
from typing import List, Dict
from kse.nlp.kse_nlp_core import NLPCore
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "search.log")


class QueryPreprocessor:
    """Preprocess and normalize search queries"""
    
    def __init__(self, nlp_core: NLPCore):
        """
        Initialize query preprocessor
        
        Args:
            nlp_core: NLP core instance
        """
        self.nlp = nlp_core
    
    def preprocess(self, query: str) -> Dict:
        """
        Preprocess search query
        
        Args:
            query: Raw search query
        
        Returns:
            Dictionary with preprocessed query data
        """
        if not query or not query.strip():
            return {
                'original_query': query,
                'processed_terms': [],
                'is_valid': False
            }
        
        # Clean query
        query = query.strip()
        
        # Process with NLP
        terms = self.nlp.process_query(query)
        
        # Check if valid
        is_valid = len(terms) > 0
        
        result = {
            'original_query': query,
            'processed_terms': terms,
            'is_valid': is_valid,
            'term_count': len(terms)
        }
        
        logger.debug(f"Preprocessed query: '{query}' -> {terms}")
        
        return result
    
    def extract_phrases(self, query: str) -> List[str]:
        """
        Extract phrases from query (words in quotes)
        
        Args:
            query: Search query
        
        Returns:
            List of phrases
        """
        import re
        phrases = re.findall(r'"([^"]+)"', query)
        return [p.strip() for p in phrases if p.strip()]
    
    def expand_query(self, terms: List[str]) -> List[str]:
        """
        Expand query with synonyms (basic implementation)
        
        Args:
            terms: Query terms
        
        Returns:
            Expanded terms
        """
        # Basic Swedish synonyms
        synonyms = {
            'universitet': ['högskola', 'lärosät'],
            'forskning': ['studie', 'vetenskp'],
            'utbildning': ['kurs', 'program'],
            'student': ['studerande', 'elev'],
        }
        
        expanded = list(terms)
        for term in terms:
            if term in synonyms:
                expanded.extend(synonyms[term])
        
        return list(set(expanded))  # Remove duplicates
