"""kse_search_analytics.py - Search Analytics and Tracking

Tracks search analytics:
- Query statistics
- Search performance
- Popular queries
- User metrics
"""

import logging
from typing import Dict, List
from collections import defaultdict

from kse.core import get_logger

logger = get_logger('search')


class SearchAnalytics:
    """Track search analytics"""
    
    def __init__(self):
        """Initialize analytics tracker"""
        self.stats = {
            'total_searches': 0,
            'unique_queries': 0,
            'avg_results': 0,
            'avg_execution_time': 0,
            'popular_queries': [],
        }
        
        self.query_history = defaultdict(int)
        self.execution_times = []
        
        logger.debug("SearchAnalytics initialized")
    
    def track_search(self, 
                    query: str,
                    result_count: int,
                    execution_time: float) -> None:
        """Track search event
        
        Args:
            query: Search query
            result_count: Number of results
            execution_time: Execution time in seconds
        """
        self.stats['total_searches'] += 1
        self.query_history[query] += 1
        self.execution_times.append(execution_time)
        
        # Update statistics
        self.stats['unique_queries'] = len(self.query_history)
        self.stats['avg_execution_time'] = sum(self.execution_times) / len(self.execution_times)
        
        logger.debug(f"Tracked search: {query} ({result_count} results, {execution_time:.3f}s)")
    
    def get_popular_queries(self, limit: int = 10) -> List[tuple]:
        """Get most popular queries
        
        Args:
            limit: Number of queries to return
            
        Returns:
            List of (query, count) tuples
        """
        sorted_queries = sorted(
            self.query_history.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_queries[:limit]
    
    def get_statistics(self) -> Dict:
        """Get analytics statistics"""
        return {
            'total_searches': self.stats['total_searches'],
            'unique_queries': self.stats['unique_queries'],
            'avg_execution_time': round(self.stats['avg_execution_time'], 3),
            'popular_queries': self.get_popular_queries(5),
        }
    
    def get_summary(self) -> str:
        """Get formatted summary"""
        stats = self.get_statistics()
        
        popular = "\n".join([
            f"  {i+1}. {query}: {count} searches"
            for i, (query, count) in enumerate(stats['popular_queries'])
        ])
        
        return f"""
Search Analytics:
├─ Total Searches: {stats['total_searches']}
├─ Unique Queries: {stats['unique_queries']}
├─ Avg Execution Time: {stats['avg_execution_time']}s
└─ Popular Queries:
{popular}
""".strip()


__all__ = ["SearchAnalytics"]
