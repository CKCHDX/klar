"""kse_pagerank.py - PageRank Algorithm

Factor 2: PageRank - Link-Based Ranking
- Measures link popularity and authority
- Weight: 20% of final score
- Based on citation flow and backlinks
"""

import logging
from typing import Dict, List
from collections import defaultdict

from kse.core import get_logger

logger = get_logger('ranking')


class PageRank:
    """PageRank algorithm implementation"""
    
    def __init__(self, damping_factor: float = 0.85, iterations: int = 20):
        """Initialize PageRank
        
        Args:
            damping_factor: Damping factor (default 0.85)
            iterations: Number of iterations
        """
        self.damping_factor = damping_factor
        self.iterations = iterations
        logger.debug("PageRank initialized")
    
    def compute_pagerank(self, 
                        graph: Dict[str, List[str]],
                        num_pages: int) -> Dict[str, float]:
        """Compute PageRank scores
        
        Args:
            graph: URL → [outgoing links] mapping
            num_pages: Total number of pages
            
        Returns:
            URL → PageRank score mapping
        """
        # Initialize ranks
        ranks = {url: 1.0 / num_pages for url in graph}
        
        # Iterate
        for _ in range(self.iterations):
            new_ranks = {}
            for url in graph:
                # Find pages linking to this URL
                rank_sum = 0.0
                for source_url, links in graph.items():
                    if url in links:
                        rank_sum += ranks[source_url] / max(len(links), 1)
                
                # Apply PageRank formula
                new_ranks[url] = (1 - self.damping_factor) / num_pages
                new_ranks[url] += self.damping_factor * rank_sum
            
            ranks = new_ranks
        
        # Normalize to 0-1
        max_rank = max(ranks.values()) if ranks else 1.0
        normalized = {url: rank / max_rank for url, rank in ranks.items()}
        
        return normalized
    
    def score_document(self, url: str, pagerank_scores: Dict[str, float]) -> float:
        """Score document by PageRank
        
        Args:
            url: Document URL
            pagerank_scores: URL → PageRank mapping
            
        Returns:
            Score (0-1)
        """
        return pagerank_scores.get(url, 0.0)


__all__ = ["PageRank"]
