"""
KSE Search Pipeline - Main search orchestrator
"""
from typing import List, Dict, Optional
from kse.search.kse_query_preprocessor import QueryPreprocessor
from kse.search.kse_result_processor import ResultProcessor
from kse.search.kse_search_executor import SearchExecutor
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.nlp.kse_nlp_core import NLPCore
from kse.core.kse_logger import get_logger
import time

logger = get_logger(__name__, "search.log")


class SearchPipeline:
    """Main search orchestrator"""
    
    def __init__(self, indexer: IndexerPipeline, nlp_core: Optional[NLPCore] = None):
        """
        Initialize search pipeline
        
        Args:
            indexer: Indexer pipeline instance
            nlp_core: NLP core instance (uses indexer's NLP if None)
        """
        self.indexer = indexer
        self.nlp = nlp_core or indexer.nlp
        
        # Initialize components
        self.query_preprocessor = QueryPreprocessor(self.nlp)
        self.result_processor = ResultProcessor()
        self.search_executor = SearchExecutor(indexer)
        
        # Search history
        self.search_history: List[Dict] = []
        
        logger.info("Search pipeline initialized")
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        diversify: bool = True,
        max_per_domain: int = 3
    ) -> Dict:
        """
        Execute search query
        
        Args:
            query: Search query
            max_results: Maximum number of results
            diversify: Whether to diversify results by domain
            max_per_domain: Maximum results per domain when diversifying
        
        Returns:
            Dictionary with search results and metadata
        """
        start_time = time.time()
        
        logger.info(f"Search request: '{query}'")
        
        # Preprocess query
        preprocessed = self.query_preprocessor.preprocess(query)
        
        if not preprocessed['is_valid']:
            logger.warning(f"Invalid query: '{query}'")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'search_time': time.time() - start_time,
                'error': 'Invalid query'
            }
        
        # Execute search
        results = self.search_executor.execute_search(
            preprocessed['processed_terms'],
            max_results
        )
        
        # Process results
        if results:
            # Deduplicate
            results = self.result_processor.deduplicate_results(results)
            
            # Diversify if requested
            if diversify:
                results = self.result_processor.diversify_results(
                    results,
                    max_per_domain
                )
            
            # Format results
            results = self.result_processor.format_results(
                results,
                query,
                max_results
            )
        
        search_time = time.time() - start_time
        
        # Create response
        response = {
            'query': query,
            'processed_terms': preprocessed['processed_terms'],
            'results': results,
            'total_results': len(results),
            'search_time': round(search_time, 3),
            'timestamp': time.time()
        }
        
        # Log search
        self._log_search(response)
        
        logger.info(f"Search completed: {len(results)} results in {search_time:.3f}s")
        
        return response
    
    def _log_search(self, search_data: Dict) -> None:
        """Log search to history"""
        self.search_history.append({
            'query': search_data['query'],
            'results_count': search_data['total_results'],
            'search_time': search_data['search_time'],
            'timestamp': search_data['timestamp']
        })
        
        # Keep only last 1000 searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]
    
    def get_search_history(self, limit: int = 100) -> List[Dict]:
        """
        Get search history
        
        Args:
            limit: Maximum number of history items
        
        Returns:
            List of search history items
        """
        return self.search_history[-limit:]
    
    def get_search_statistics(self) -> Dict:
        """
        Get search statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.search_history:
            return {
                'total_searches': 0,
                'average_search_time': 0,
                'average_results': 0
            }
        
        total_time = sum(s['search_time'] for s in self.search_history)
        total_results = sum(s['results_count'] for s in self.search_history)
        
        return {
            'total_searches': len(self.search_history),
            'average_search_time': round(total_time / len(self.search_history), 3),
            'average_results': round(total_results / len(self.search_history), 2)
        }
