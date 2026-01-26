"""kse_query_parser.py - Query Parsing and Expansion

Parses search queries and expands with related terms:
- Query tokenization
- Stopword removal
- Query expansion
- Synonym handling
"""

import logging
from typing import Dict, List

from kse.core import get_logger
from kse.nlp import NLPCore, StopwordManager

logger = get_logger('search')


class QueryParser:
    """Parse and expand search queries"""
    
    def __init__(self):
        """Initialize query parser"""
        self.nlp = NLPCore()
        self.stopwords = StopwordManager()
        
        # Synonym mappings for Swedish
        self.synonyms = {
            'universitet': ['högskola', 'utbildning'],
            'svenska': ['swedish', 'sverige'],
            'söka': ['search', 'find'],
            'information': ['data', 'innehål'],
        }
        
        logger.debug("QueryParser initialized")
    
    def parse(self, query: str) -> Dict:
        """Parse search query
        
        Args:
            query: Raw query string
            
        Returns:
            Parsed query data
        """
        # Normalize
        normalized = query.lower().strip()
        
        # Tokenize
        tokens = self.nlp.tokenize(normalized)
        
        # Remove stopwords
        terms = self.stopwords.remove_stopwords(tokens)
        
        return {
            'raw': query,
            'normalized': normalized,
            'terms': terms,
            'term_count': len(terms),
        }
    
    def expand_query(self, query: str, max_expansions: int = 5) -> List[str]:
        """Expand query with synonyms
        
        Args:
            query: Query string
            max_expansions: Maximum expansions to return
            
        Returns:
            List of expanded query terms
        """
        parsed = self.parse(query)
        expansions = [query]
        
        # Add synonyms
        for term in parsed['terms']:
            if term in self.synonyms:
                for synonym in self.synonyms[term][:max_expansions - len(expansions) + 1]:
                    expanded = query.replace(term, synonym)
                    expansions.append(expanded)
                    if len(expansions) >= max_expansions:
                        break
        
        return expansions[:max_expansions]
    
    def get_operators(self, query: str) -> Dict:
        """Extract search operators
        
        Args:
            query: Query string
            
        Returns:
            Dictionary of operators
        """
        operators = {
            'exact': False,
            'exclude': [],
            'domain': None,
        }
        
        # Check for exact match (quoted)
        if '"' in query:
            operators['exact'] = True
        
        # Check for exclusions (-)
        import re
        excludes = re.findall(r'-(\w+)', query)
        operators['exclude'] = excludes
        
        # Check for domain filter (site:)
        domain_match = re.search(r'site:(\S+)', query)
        if domain_match:
            operators['domain'] = domain_match.group(1)
        
        return operators


__all__ = ["QueryParser"]
