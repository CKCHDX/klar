"""kse_ranking_stats.py - Ranking Statistics and Monitoring

Tracks and reports ranking metrics:
- Average scores
- Score distribution
- Factor contributions
- Performance metrics
"""

import logging
from typing import Dict, List, Tuple

from kse.core import get_logger

logger = get_logger('ranking')


class RankingStatistics:
    """Track ranking statistics"""
    
    def __init__(self):
        """Initialize statistics tracker"""
        self.stats = {
            'total_ranked': 0,
            'avg_score': 0.0,
            'min_score': 100.0,
            'max_score': 0.0,
        }
        logger.debug("RankingStatistics initialized")
    
    def calculate_statistics(self, 
                            ranked_results: List[Tuple[str, float]]) -> Dict:
        """Calculate ranking statistics
        
        Args:
            ranked_results: List of (url, score) tuples
            
        Returns:
            Statistics dictionary
        """
        if not ranked_results:
            return self.stats
        
        scores = [score for _, score in ranked_results]
        
        self.stats['total_ranked'] = len(ranked_results)
        self.stats['avg_score'] = sum(scores) / len(scores)
        self.stats['min_score'] = min(scores)
        self.stats['max_score'] = max(scores)
        
        # Calculate score distribution
        self.stats['distribution'] = {
            'excellent': len([s for s in scores if s >= 90]),
            'good': len([s for s in scores if 70 <= s < 90]),
            'fair': len([s for s in scores if 50 <= s < 70]),
            'poor': len([s for s in scores if s < 50]),
        }
        
        return self.stats
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return self.stats.copy()
    
    def get_summary(self) -> str:
        """Get formatted statistics summary"""
        s = self.stats
        return f"""
Ranking Statistics:
├─ Total Results: {s['total_ranked']}
├─ Average Score: {s['avg_score']:.2f}
├─ Score Range: {s['min_score']:.2f} - {s['max_score']:.2f}
├─ Excellent (90+): {s.get('distribution', {}).get('excellent', 0)}
├─ Good (70-89): {s.get('distribution', {}).get('good', 0)}
├─ Fair (50-69): {s.get('distribution', {}).get('fair', 0)}
└─ Poor (<50): {s.get('distribution', {}).get('poor', 0)}
""".strip()


__all__ = ["RankingStatistics"]
