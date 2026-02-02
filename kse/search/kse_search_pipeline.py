"""
KSE Search Pipeline - Main search orchestrator with advanced ranking and caching
"""
from typing import List, Dict, Optional
from kse.search.kse_query_preprocessor import QueryPreprocessor
from kse.search.kse_result_processor import ResultProcessor
from kse.search.kse_search_executor import SearchExecutor
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.nlp.kse_nlp_core import NLPCore
from kse.nlp.kse_query_processor import QueryProcessor
from kse.ranking.kse_ranking_core import RankingCore
from kse.ranking.kse_diversity_ranker import DiversityRanker
from kse.cache.kse_cache_manager import CacheManager
from kse.core.kse_logger import get_logger
import time

logger = get_logger(__name__, "search.log")


class SearchPipeline:
    """Main search orchestrator with ranking and caching"""
    
    def __init__(
        self,
        indexer: IndexerPipeline,
        nlp_core: Optional[NLPCore] = None,
        enable_cache: bool = True,
        enable_ranking: bool = True
    ):
        """
        Initialize search pipeline
        
        Args:
            indexer: Indexer pipeline instance
            nlp_core: NLP core instance (uses indexer's NLP if None)
            enable_cache: Enable search result caching
            enable_ranking: Enable advanced ranking
        """
        self.indexer = indexer
        self.nlp = nlp_core or indexer.nlp
        self.enable_cache = enable_cache
        self.enable_ranking = enable_ranking
        
        # Initialize components
        self.query_preprocessor = QueryPreprocessor(self.nlp)
        self.query_processor = QueryProcessor()  # Enhanced query processor
        self.result_processor = ResultProcessor()
        self.search_executor = SearchExecutor(indexer)
        
        # Initialize ranking system
        if self.enable_ranking:
            self.ranking_core = RankingCore()
            self.diversity_ranker = DiversityRanker(max_per_domain=3)
            logger.info("Advanced ranking enabled")
        
        # Initialize cache
        if self.enable_cache:
            self.cache_manager = CacheManager(max_size_mb=100, default_ttl=3600)
            logger.info("Search cache enabled")
        
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
        Execute search query with advanced ranking and caching
        
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
        
        # Enhanced query processing for natural language
        enhanced_query = self.query_processor.process_query(query)
        logger.debug(f"Enhanced query: {enhanced_query['expanded_terms']}")
        
        # Check cache if enabled
        if self.enable_cache:
            cache_key = f"{query}_{max_results}_{diversify}"
            cached_result = self.cache_manager.get('search', cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: '{query}'")
                cached_result['from_cache'] = True
                return cached_result
        
        # Preprocess query (traditional method)
        preprocessed = self.query_preprocessor.preprocess(query)
        
        # Combine traditional terms with enhanced expanded terms
        search_terms = list(set(preprocessed.get('processed_terms', []) + 
                                enhanced_query.get('expanded_terms', [])))
        
        if not search_terms:
            logger.warning(f"Invalid query: '{query}'")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'search_time': time.time() - start_time,
                'error': 'Invalid query'
            }
        
        logger.info(f"Search terms: {search_terms}")
        
        # Execute search with expanded terms
        results = self.search_executor.execute_search(
            search_terms,
            max_results * 3  # Get more results for ranking
        )
        
        # Process results
        if results:
            # Deduplicate
            results = self.result_processor.deduplicate_results(results)
            
            # Apply advanced ranking if enabled
            if self.enable_ranking:
                results = self.ranking_core.rank_results(
                    results,
                    preprocessed['processed_terms'],
                    original_query=query,
                    query_intent=enhanced_query.get('intent')
                )
                logger.debug(f"Applied advanced ranking to {len(results)} results")
            
            # Diversify if requested
            if diversify:
                if self.enable_ranking:
                    # Use advanced diversity ranker
                    results = self.diversity_ranker.diversify_results(results)
                else:
                    # Use basic diversity
                    results = self.result_processor.diversify_results(
                        results,
                        max_per_domain
                    )
            
            # Limit to max_results
            results = results[:max_results]
            
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
            'timestamp': time.time(),
            'from_cache': False,
            'ranking_enabled': self.enable_ranking,
            'cache_enabled': self.enable_cache
        }
        
        # Cache result if enabled
        if self.enable_cache:
            cache_key = f"{query}_{max_results}_{diversify}"
            self.cache_manager.set('search', cache_key, response)
        
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
            stats = {
                'total_searches': 0,
                'average_search_time': 0,
                'average_results': 0
            }
        else:
            total_time = sum(s['search_time'] for s in self.search_history)
            total_results = sum(s['results_count'] for s in self.search_history)
            
            stats = {
                'total_searches': len(self.search_history),
                'average_search_time': round(total_time / len(self.search_history), 3),
                'average_results': round(total_results / len(self.search_history), 2)
            }
        
        # Add cache statistics if enabled
        if self.enable_cache:
            stats['cache'] = self.cache_manager.get_statistics()
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear search cache"""
        if self.enable_cache:
            self.cache_manager.clear('search')
            logger.info("Search cache cleared")
    
    def get_ranking_weights(self) -> Dict:
        """Get current ranking weights"""
        if self.enable_ranking:
            weights = self.ranking_core.get_weights()
            return {
                'tf_idf': weights.tf_idf,
                'pagerank': weights.pagerank,
                'domain_authority': weights.domain_authority,
                'recency': weights.recency,
                'keyword_density': weights.keyword_density,
                'link_structure': weights.link_structure,
                'regional_relevance': weights.regional_relevance
            }
        return {}

