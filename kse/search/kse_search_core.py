"""kse_search_core.py - Main Search Engine

Coordinates the complete search pipeline:
- Query parsing and processing
- Document retrieval from index
- Result ranking
- Response formatting
"""

import logging
from typing import Dict, List, Tuple
import time

from kse.core import get_logger, KSEException
from kse.cache import CacheManager

logger = get_logger('search')


class KSESearchException(KSEException):
    """Search-specific exceptions"""
    pass


class SearchCore:
    """Main search engine core"""
    
    def __init__(self, 
                 index_manager,
                 ranking_core,
                 cache_manager: CacheManager):
        """Initialize search core
        
        Args:
            index_manager: Index from Phase 6
            ranking_core: Ranking from Phase 7
            cache_manager: Cache for results
        """
        self.index = index_manager
        self.ranking = ranking_core
        self.cache = cache_manager
        
        logger.info("SearchCore initialized")
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """Execute search query
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            Search results dictionary
        """
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = f"search:{query}:{limit}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for query: {query}")
                return cached
            
            # Parse query
            parsed_query = self._parse_query(query)
            
            # Retrieve documents from index
            documents = self.index.search(parsed_query['terms'])
            
            if not documents:
                logger.info(f"No results for query: {query}")
                result = {
                    'query': query,
                    'total_results': 0,
                    'results': [],
                    'execution_time': time.time() - start_time,
                }
            else:
                # Rank results
                ranked = self.ranking.rank_results(
                    query=query,
                    documents=documents,
                    scoring_data=self._get_scoring_data(documents)
                )
                
                # Limit results
                ranked = ranked[:limit]
                
                # Format results
                results = self._format_results(ranked)
                
                result = {
                    'query': query,
                    'total_results': len(ranked),
                    'results': results,
                    'execution_time': time.time() - start_time,
                }
            
            # Cache result
            self.cache.set(cache_key, result)
            
            logger.info(f"Search completed: {query} ({result['execution_time']:.3f}s)")
            return result
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise KSESearchException(f"Search error: {e}")
    
    def _parse_query(self, query: str) -> Dict:
        """Parse search query
        
        Args:
            query: Raw query string
            
        Returns:
            Parsed query data
        """
        # Basic parsing - split into terms
        terms = query.lower().strip().split()
        
        return {
            'raw': query,
            'terms': terms,
            'term_count': len(terms),
        }
    
    def _get_scoring_data(self, documents: List[Dict]) -> Dict:
        """Get scoring data for documents
        
        Args:
            documents: List of documents
            
        Returns:
            Scoring data dictionary
        """
        # Prepare scoring data for ranking
        scoring_data = {
            'tfidf': {},
            'pagerank': {},
            'authority': {},
            'recency': {},
            'density': {},
            'structure': {},
            'regional': {},
        }
        
        # Initialize with default scores
        for doc in documents:
            url = doc.get('url')
            scoring_data['tfidf'][url] = doc.get('tfidf_score', 0.5)
            scoring_data['pagerank'][url] = doc.get('pagerank_score', 0.5)
            scoring_data['authority'][url] = doc.get('authority_score', 0.5)
            scoring_data['recency'][url] = doc.get('recency_score', 0.5)
            scoring_data['density'][url] = doc.get('density_score', 0.5)
            scoring_data['structure'][url] = doc.get('structure_score', 0.5)
            scoring_data['regional'][url] = doc.get('regional_score', 0.5)
        
        return scoring_data
    
    def _format_results(self, ranked: List[Tuple[str, float]]) -> List[Dict]:
        """Format search results
        
        Args:
            ranked: Ranked results (url, score)
            
        Returns:
            Formatted result list
        """
        results = []
        for idx, (url, score) in enumerate(ranked, 1):
            result = {
                'rank': idx,
                'url': url,
                'score': round(score, 2),
                'title': url.split('/')[-1],  # Simple title extraction
            }
            results.append(result)
        return results


__all__ = ["SearchCore", "KSESearchException"]
