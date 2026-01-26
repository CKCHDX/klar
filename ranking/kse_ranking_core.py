"""kse_ranking_core.py - Main Ranking Orchestrator

Coordinates the complete ranking pipeline:
- Combines multiple ranking factors
- Computes final scores
- Returns ranked results
- Manages ranking cache
"""

import logging
from typing import Dict, List, Tuple
import time

from kse.core import get_logger, KSEException
from kse.cache import CacheManager

logger = get_logger('ranking')


class KSERankingException(KSEException):
    """Ranking-specific exceptions"""
    pass


class RankingCore:
    """Main ranking orchestrator"""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize ranking core
        
        Args:
            cache_manager: Cache for ranking results
        """
        self.cache = cache_manager
        
        # Ranking factors and their weights
        self.weights = {
            'tfidf': 0.25,           # Relevance
            'pagerank': 0.20,        # Link popularity
            'authority': 0.15,       # Domain trust
            'recency': 0.15,         # Content freshness
            'density': 0.10,         # Keyword density
            'structure': 0.10,       # Link structure
            'regional': 0.05,        # Regional relevance
        }
        
        logger.info("RankingCore initialized")
    
    def rank_results(self, 
                     query: str,
                     documents: List[Dict],
                     scoring_data: Dict) -> List[Tuple[str, float]]:
        """Rank documents by relevance
        
        Args:
            query: Search query
            documents: List of document data
            scoring_data: Pre-computed scores
            
        Returns:
            Sorted list of (url, score) tuples
        """
        try:
            # Check cache first
            cache_key = f"ranking:{query}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for query: {query}")
                return cached
            
            # Compute scores for each document
            scores = []
            for doc in documents:
                url = doc.get('url')
                final_score = self._compute_score(url, doc, scoring_data)
                scores.append((url, final_score))
            
            # Sort by score (descending)
            ranked = sorted(scores, key=lambda x: x[1], reverse=True)
            
            # Cache result
            self.cache.set(cache_key, ranked)
            
            logger.debug(f"Ranked {len(ranked)} documents")
            return ranked
        
        except Exception as e:
            logger.error(f"Ranking failed: {e}")
            raise KSERankingException(f"Ranking error: {e}")
    
    def _compute_score(self, 
                      url: str,
                      document: Dict,
                      scoring_data: Dict) -> float:
        """Compute final score for document
        
        Args:
            url: Document URL
            document: Document data
            scoring_data: Pre-computed scores
            
        Returns:
            Final score (0-100)
        """
        score = 0.0
        
        # TF-IDF score (25%)
        tfidf = scoring_data.get('tfidf', {}).get(url, 0.0)
        score += tfidf * self.weights['tfidf'] * 100
        
        # PageRank score (20%)
        pagerank = scoring_data.get('pagerank', {}).get(url, 0.5)
        score += pagerank * self.weights['pagerank'] * 100
        
        # Authority score (15%)
        authority = scoring_data.get('authority', {}).get(url, 0.5)
        score += authority * self.weights['authority'] * 100
        
        # Recency score (15%)
        recency = scoring_data.get('recency', {}).get(url, 0.5)
        score += recency * self.weights['recency'] * 100
        
        # Density score (10%)
        density = scoring_data.get('density', {}).get(url, 0.5)
        score += density * self.weights['density'] * 100
        
        # Structure score (10%)
        structure = scoring_data.get('structure', {}).get(url, 0.5)
        score += structure * self.weights['structure'] * 100
        
        # Regional score (5%)
        regional = scoring_data.get('regional', {}).get(url, 0.5)
        score += regional * self.weights['regional'] * 100
        
        return min(100.0, score)  # Cap at 100
    
    def get_weights(self) -> Dict[str, float]:
        """Get current ranking weights"""
        return self.weights.copy()
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """Set ranking weights
        
        Args:
            weights: New weight configuration
        """
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            self.weights = {k: v/total for k, v in weights.items()}
            logger.info("Ranking weights updated")


__all__ = ["RankingCore", "KSERankingException"]
