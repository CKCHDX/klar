"""kse_snippet_generator.py - Search Result Snippet Generation

Generates search result snippets:
- Text extraction
- Query highlighting
- Snippet truncation
"""

import logging
from typing import Dict

from kse.core import get_logger

logger = get_logger('search')


class SnippetGenerator:
    """Generate search result snippets"""
    
    def __init__(self, snippet_length: int = 150):
        """Initialize snippet generator
        
        Args:
            snippet_length: Target snippet length in characters
        """
        self.snippet_length = snippet_length
        logger.debug("SnippetGenerator initialized")
    
    def generate(self, 
                document: Dict,
                query_terms: list) -> str:
        """Generate snippet for document
        
        Args:
            document: Document data with content
            query_terms: Query terms to highlight
            
        Returns:
            Generated snippet
        """
        content = document.get('content', '')
        title = document.get('title', '')
        
        if not content:
            return title[:self.snippet_length]
        
        # Find best section containing query terms
        snippet = self._find_best_section(content, query_terms)
        
        # Truncate to length
        if len(snippet) > self.snippet_length:
            snippet = snippet[:self.snippet_length] + "..."
        
        return snippet
    
    def _find_best_section(self, text: str, query_terms: list) -> str:
        """Find best section of text containing query terms
        
        Args:
            text: Full text
            query_terms: Query terms
            
        Returns:
            Best section
        """
        if not query_terms:
            return text[:self.snippet_length]
        
        # Find position of first query term
        min_pos = len(text)
        for term in query_terms:
            pos = text.lower().find(term.lower())
            if pos >= 0 and pos < min_pos:
                min_pos = pos
        
        # Extract section around term
        if min_pos < len(text):
            start = max(0, min_pos - 50)
            end = min(len(text), min_pos + self.snippet_length)
            return text[start:end]
        
        return text[:self.snippet_length]
    
    def highlight_query_terms(self, snippet: str, query_terms: list) -> str:
        """Highlight query terms in snippet
        
        Args:
            snippet: Snippet text
            query_terms: Query terms
            
        Returns:
            Snippet with highlighted terms
        """
        highlighted = snippet
        
        for term in query_terms:
            # Simple highlighting with markers
            pattern = term.lower()
            highlighted_term = f"[{term}]"
            highlighted = highlighted.lower().replace(pattern, highlighted_term)
        
        return highlighted


__all__ = ["SnippetGenerator"]
