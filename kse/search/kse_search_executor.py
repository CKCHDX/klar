"""
KSE Search Executor - Execute search operations
"""
from typing import List, Dict
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "search.log")


class SearchExecutor:
    """Execute search operations against the index"""
    
    def __init__(self, indexer: IndexerPipeline):
        """
        Initialize search executor
        
        Args:
            indexer: Indexer pipeline instance
        """
        self.indexer = indexer
    
    def execute_search(
        self,
        query_terms: List[str],
        max_results: int = 10
    ) -> List[Dict]:
        """
        Execute search
        
        Args:
            query_terms: Preprocessed query terms
            max_results: Maximum number of results
        
        Returns:
            List of search results
        """
        if not query_terms:
            return []
        
        logger.info(f"Executing search for terms: {query_terms}")
        
        # Search using indexer
        results = self.indexer.search(' '.join(query_terms), max_results)
        
        logger.info(f"Search returned {len(results)} results")
        
        return results
    
    def execute_phrase_search(
        self,
        phrase: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Execute phrase search (words must appear together)
        
        Args:
            phrase: Search phrase
            max_results: Maximum number of results
        
        Returns:
            List of search results
        """
        # For now, use regular search
        # Full phrase search would require position-aware searching
        query_terms = self.indexer.nlp.process_query(phrase)
        return self.execute_search(query_terms, max_results)
    
    def get_suggestions(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """
        Get search suggestions (autocomplete)
        
        Args:
            partial_query: Partial query
            max_suggestions: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        # Basic implementation: return empty for now
        # Full implementation would use term frequency and common queries
        return []
