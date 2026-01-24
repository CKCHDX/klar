"""
Search Module

Stage 4: Search Pipeline - Query parsing, ranking, and execution
"""

from .kse_search_query import (
    QueryType,
    SearchQuery,
    QueryParser,
)

from .kse_search_ranking import (
    RankingStrategy,
    RankingScore,
    Ranker,
)

from .kse_search_executor import (
    SearchResult,
    ResultSet,
    SearchExecutor,
)

from .kse_search_cache import (
    CacheEntry,
    SearchCache,
)

__all__ = [
    # Query types and classes
    'QueryType',
    'SearchQuery',
    'QueryParser',
    
    # Ranking
    'RankingStrategy',
    'RankingScore',
    'Ranker',
    
    # Execution
    'SearchResult',
    'ResultSet',
    'SearchExecutor',
    
    # Caching
    'CacheEntry',
    'SearchCache',
]

__version__ = '4.0.0'
__stage__ = 'Stage 4: Search Pipeline'
