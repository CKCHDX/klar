"""
Ranking Statistics - Ranking statistics and diagnostics
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class RankingStats:
    """Ranking statistics and diagnostics"""
    
    def __init__(self):
        self.stats = defaultdict(list)
        logger.info("RankingStats initialized")
    
    def record_ranking(self, query: str, results: List[Dict[str, Any]]) -> None:
        """Record ranking statistics"""
        self.stats['queries'].append(query)
        self.stats['result_counts'].append(len(results))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ranking statistics"""
        return {
            'total_queries': len(self.stats['queries']),
            'avg_results': sum(self.stats['result_counts']) / max(len(self.stats['result_counts']), 1)
        }
