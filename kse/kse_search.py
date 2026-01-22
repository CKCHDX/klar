"""
Core Search Engine
Orchestrates:
- Swedish NLP processing
- Index querying
- Result ranking
- Cache management
- Response formatting
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import time

from .kse_nlp import SwedishNLP
from .kse_index import InvertedIndex
from .kse_ranking import RankingEngine
from .kse_cache import CacheManager


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result."""
    title: str
    url: str
    snippet: str
    score: float
    domain_trust: float
    result_type: str  # 'web', 'news', 'local', 'answer'


@dataclass
class SearchResponse:
    """Complete search response."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    intent: Dict[str, float]
    suggestion: Optional[str] = None


class SearchEngine:
    """
    Production-grade Swedish search engine.
    Combines NLP, indexing, and ranking for optimal results.
    """

    def __init__(self, index: InvertedIndex, ranking_engine: RankingEngine):
        """
        Initialize search engine.
        
        Args:
            index: Inverted index
            ranking_engine: Ranking algorithm engine
        """
        self.nlp = SwedishNLP()
        self.index = index
        self.ranking = ranking_engine
        self.cache = CacheManager()
        self.search_count = 0

    def search(self, query: str, limit: int = 10) -> SearchResponse:
        """
        Execute a Swedish search query.
        
        Args:
            query: User's search query
            limit: Maximum results to return (default 10)
            
        Returns:
            SearchResponse with results
            
        Example:
            >>> engine = SearchEngine(index, ranking)
            >>> response = engine.search("restauranger i stockholm")
            >>> for result in response.results:
            ...     print(result.title)
        """
        start_time = time.time()
        
        # Check cache first
        cached = self.cache.get(query)
        if cached:
            logger.debug(f"Cache hit for query: {query}")
            return cached
        
        # Process query through NLP
        tokens = self.nlp.tokenize(query)
        lemmas = [self.nlp.lemmatize(token) for token in tokens]
        intent = self.nlp.detect_intent(query)
        entities = self.nlp.extract_entities(query)
        
        # Remove stopwords
        lemmas = [l for l in lemmas if l not in self.nlp.stopwords]
        
        # Search index
        index_results = self.index.search(lemmas)
        
        # Rank results
        ranked_results = self.ranking.rank(
            index_results,
            query=query,
            entities=entities,
            intent=intent
        )
        
        # Format results
        search_results = []
        for page_id, url, score in ranked_results[:limit]:
            # Get page details (from database in production)
            title, snippet = self._get_page_details(page_id, url)
            domain_trust = self._get_domain_trust(url)
            
            result = SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                score=score,
                domain_trust=domain_trust,
                result_type=self._determine_result_type(intent)
            )
            search_results.append(result)
        
        # Build response
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        response = SearchResponse(
            query=query,
            results=search_results,
            total_results=len(ranked_results),
            search_time_ms=search_time,
            intent=intent
        )
        
        # Cache the response
        self.cache.set(query, response)
        
        self.search_count += 1
        logger.info(f"Search #{self.search_count}: '{query}' returned {len(search_results)} results in {search_time:.1f}ms")
        
        return response

    def search_suggestions(self, prefix: str) -> List[str]:
        """
        Get search suggestions as user types.
        Returns popular completions for prefix.
        
        Args:
            prefix: Partial query
            
        Returns:
            List of suggested complete queries
        """
        # In production, use suggestion index
        # For now, simple implementation
        if len(prefix) < 3:
            return []
        
        # Get popular queries starting with prefix
        suggestions = self.cache.get_suggestions(prefix)
        return suggestions[:5]  # Top 5 suggestions

    def spell_check(self, query: str) -> Optional[str]:
        """
        Check and correct Swedish spelling.
        
        Args:
            query: Query to check
            
        Returns:
            Corrected query, or None if no corrections
        """
        # In production, use Swedish spell checker
        # For now, return as-is
        return None

    # Private methods
    
    def _get_page_details(self, page_id: int, url: str) -> tuple:
        """
        Get page title and snippet from database.
        
        Args:
            page_id: Page identifier
            url: Page URL
            
        Returns:
            (title, snippet) tuple
        """
        # In production, query PostgreSQL
        title = f"Page {page_id}"
        snippet = "Page snippet here..."
        return title, snippet

    def _get_domain_trust(self, url: str) -> float:
        """
        Get domain trust score (0.0 - 1.0).
        Higher for government, news sites, etc.
        
        Args:
            url: Page URL
            
        Returns:
            Trust score (0.0 - 1.0)
        """
        domain = url.split('/')[2]
        
        # Government sites: very high trust
        if '.gov' in domain or '.se' in domain.lower():
            if 'regeringskansliet' in domain or 'riksdag' in domain:
                return 0.95
        
        # News sites: high trust
        if any(news in domain for news in ['sverigesradio', 'aftonbladet', 'dn', 'gp']):
            return 0.90
        
        # Blogs: lower trust
        if 'blog' in domain:
            return 0.60
        
        # Default: medium trust
        return 0.70

    def _determine_result_type(self, intent: Dict[str, float]) -> str:
        """
        Determine type of results based on intent.
        
        Args:
            intent: Intent classification
            
        Returns:
            Result type string
        """
        if 'news_search' in intent and intent['news_search'] > 0.7:
            return 'news'
        elif 'local_search' in intent and intent['local_search'] > 0.7:
            return 'local'
        elif 'calculation' in intent and intent['calculation'] > 0.7:
            return 'answer'
        else:
            return 'web'


if __name__ == "__main__":
    # Test search engine
    from .kse_ranking import RankingEngine
    
    index = InvertedIndex()
    ranking = RankingEngine()
    engine = SearchEngine(index, ranking)
    
    # Test search
    response = engine.search("restauranger i stockholm")
    print(f"Query: {response.query}")
    print(f"Results: {len(response.results)}")
    print(f"Time: {response.search_time_ms:.1f}ms")
