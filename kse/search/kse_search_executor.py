"""
Search Executor

Executes search queries against indexed data.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from kse.search.kse_search_query import SearchQuery, QueryParser
from kse.search.kse_search_ranking import Ranker, RankingStrategy, RankingScore
from kse.database import Repository
from kse.core import KSELogger, KSEException

logger = KSELogger.get_logger(__name__)


@dataclass
class SearchResult:
    """Individual search result."""
    page_id: int
    url: str
    title: str
    description: str
    domain: str
    score: float
    keywords: List[str] = field(default_factory=list)
    snippet: Optional[str] = None
    relevance: float = 0.0


@dataclass
class ResultSet:
    """Complete search result set."""
    query: str
    total_results: int
    returned_results: int
    results: List[SearchResult] = field(default_factory=list)
    execution_time_ms: float = 0.0
    ranking_strategy: str = "hybrid"
    offset: int = 0
    limit: int = 10
    
    @property
    def has_more(self) -> bool:
        """Check if more results available."""
        return (self.offset + self.limit) < self.total_results


class SearchExecutor:
    """
    Search query execution engine.
    
    Features:
    - Query parsing and validation
    - Multi-term search
    - Result ranking
    - Pagination
    - Filtering
    """
    
    def __init__(
        self,
        db_repository: Repository,
        query_parser: Optional[QueryParser] = None,
        ranker: Optional[Ranker] = None,
    ):
        """
        Initialize search executor.
        
        Args:
            db_repository: Database repository
            query_parser: Custom query parser
            ranker: Custom ranker
        """
        self.db = db_repository
        self.parser = query_parser or QueryParser()
        self.ranker = ranker or Ranker()
    
    def search(
        self,
        query_string: str,
        limit: int = 10,
        offset: int = 0,
        strategy: str = "hybrid",
    ) -> ResultSet:
        """
        Execute search query.
        
        Args:
            query_string: Search query
            limit: Results per page
            offset: Result offset for pagination
            strategy: Ranking strategy (relevance, popularity, recency, hybrid)
        
        Returns:
            ResultSet with ranked results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Searching: {query_string}")
            
            # Parse query
            parsed_query = self.parser.parse(query_string)
            
            if not self.parser.validate_query(parsed_query):
                logger.warning(f"Invalid query: {query_string}")
                return ResultSet(
                    query=query_string,
                    total_results=0,
                    returned_results=0,
                )
            
            # Execute search
            raw_results = self._execute_search(parsed_query)
            
            if not raw_results:
                return ResultSet(
                    query=query_string,
                    total_results=0,
                    returned_results=0,
                )
            
            # Rank results
            try:
                ranking_enum = RankingStrategy[strategy.upper()]
            except KeyError:
                ranking_enum = RankingStrategy.HYBRID
            
            ranked = self.ranker.rank(raw_results, ranking_enum)
            
            # Apply pagination
            total_count = len(ranked)
            paginated = ranked[offset:offset + limit]
            
            # Convert to result objects
            results = []
            for score in paginated:
                # Get page details
                page = self.db.get_page(score.page_id)
                if page:
                    result = SearchResult(
                        page_id=score.page_id,
                        url=score.url,
                        title=page.get('title', 'Untitled'),
                        description=page.get('description', ''),
                        domain=page.get('domain', ''),
                        score=score.final_score,
                        relevance=score.relevance_score,
                    )
                    results.append(result)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result_set = ResultSet(
                query=query_string,
                total_results=total_count,
                returned_results=len(results),
                results=results,
                execution_time_ms=execution_time,
                ranking_strategy=strategy,
                offset=offset,
                limit=limit,
            )
            
            logger.info(
                f"Search complete: {total_count} total, "
                f"{len(results)} returned, "
                f"{execution_time:.2f}ms"
            )
            
            return result_set
        
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return ResultSet(
                query=query_string,
                total_results=0,
                returned_results=0,
            )
    
    def _execute_search(self, parsed_query: SearchQuery) -> List[Dict]:
        """
        Execute parsed search query against database.
        
        Args:
            parsed_query: Parsed SearchQuery object
        
        Returns:
            List of matching results
        """
        results = []
        
        try:
            # Search for each term
            all_results = {}
            
            # Search single terms
            for term in parsed_query.terms:
                term_results = self.db.search_by_keyword(
                    query=term,
                    limit=100,
                )
                
                for result in term_results:
                    page_id = result.get('page_id')
                    if page_id not in all_results:
                        all_results[page_id] = result
                    else:
                        # Boost score if multiple terms match
                        all_results[page_id]['tfidf_score'] += result.get('tfidf_score', 0) * 0.5
            
            # Search phrases (exact match)
            for phrase in parsed_query.phrases:
                phrase_results = self.db.search_by_keyword(
                    query=phrase,
                    limit=100,
                )
                
                for result in phrase_results:
                    page_id = result.get('page_id')
                    if page_id not in all_results:
                        all_results[page_id] = result
                    else:
                        # Boost score for phrase matches
                        all_results[page_id]['tfidf_score'] += result.get('tfidf_score', 0) * 0.8
            
            # Apply exclusions
            if parsed_query.exclude_terms:
                for term in parsed_query.exclude_terms:
                    exclude_results = self.db.search_by_keyword(
                        query=term,
                        limit=1000,
                    )
                    
                    for result in exclude_results:
                        page_id = result.get('page_id')
                        all_results.pop(page_id, None)  # Remove from results
            
            # Apply domain filter
            if parsed_query.domain_filter:
                filtered = {}
                for page_id, result in all_results.items():
                    url = result.get('url', '')
                    if parsed_query.domain_filter in url:
                        filtered[page_id] = result
                all_results = filtered
            
            # Apply date filters
            if parsed_query.date_from or parsed_query.date_to:
                filtered = {}
                for page_id, result in all_results.items():
                    created_at = result.get('created_at')
                    
                    # Basic date comparison (would need proper datetime parsing)
                    if parsed_query.date_from:
                        if created_at >= parsed_query.date_from:
                            filtered[page_id] = result
                    elif parsed_query.date_to:
                        if created_at <= parsed_query.date_to:
                            filtered[page_id] = result
                    else:
                        filtered[page_id] = result
                
                all_results = filtered
            
            results = list(all_results.values())
        
        except Exception as e:
            logger.error(f"Search execution error: {e}", exc_info=True)
        
        return results
    
    def get_suggestions(self, query_string: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions for query.
        
        Args:
            query_string: Partial query
            limit: Number of suggestions
        
        Returns:
            List of suggested queries
        """
        try:
            # Get popular terms matching prefix
            suggestions = self.db.get_term_suggestions(
                prefix=query_string,
                limit=limit,
            )
            
            return suggestions or [query_string]
        
        except Exception as e:
            logger.warning(f"Error getting suggestions: {e}")
            return [query_string]
    
    def get_related_searches(self, page_id: int, limit: int = 5) -> List[str]:
        """
        Get related searches for a page.
        
        Args:
            page_id: Page ID
            limit: Number of related searches
        
        Returns:
            List of related search queries
        """
        try:
            # Get top keywords for page
            keywords = self.db.get_page_keywords(
                page_id=page_id,
                limit=limit,
            )
            
            return [kw.get('term', '') for kw in keywords if kw.get('term')]
        
        except Exception as e:
            logger.warning(f"Error getting related searches: {e}")
            return []
