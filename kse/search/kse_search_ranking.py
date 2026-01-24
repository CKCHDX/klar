"""
Search Result Ranking

Ranks search results using multiple scoring factors.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import math

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class RankingStrategy(Enum):
    """Ranking algorithm selection."""
    RELEVANCE = "relevance"        # TF-IDF based
    POPULARITY = "popularity"      # Page rank / domain authority
    RECENCY = "recency"            # Newer pages ranked higher
    HYBRID = "hybrid"              # Combination of all


@dataclass
class RankingScore:
    """Ranking score for a result."""
    page_id: int
    url: str
    relevance_score: float = 0.0   # 0-1 TF-IDF
    popularity_score: float = 0.0  # 0-1 PageRank/authority
    recency_score: float = 0.0     # 0-1 Date based
    final_score: float = 0.0       # 0-1 Combined
    
    def __lt__(self, other):
        """Sort by final score (descending)."""
        return self.final_score > other.final_score


class Ranker:
    """
    Search result ranking engine.
    
    Features:
    - TF-IDF relevance scoring
    - Domain authority scoring
    - Recency scoring
    - Combined hybrid ranking
    """
    
    # Ranking weights (sum = 1.0)
    WEIGHTS = {
        'relevance': 0.50,   # TF-IDF relevance
        'popularity': 0.30,  # Domain/page popularity
        'recency': 0.20,     # Page freshness
    }
    
    # Domain authority scores (example data)
    DOMAIN_AUTHORITY = {
        'sv.wikipedia.org': 0.95,
        'governo.se': 0.90,
        'scb.se': 0.90,
        'svt.se': 0.85,
        'dn.se': 0.80,
        'aftonbladet.se': 0.75,
        'expressen.se': 0.75,
        'bbc.com': 0.70,
    }
    
    def __init__(
        self,
        strategy: RankingStrategy = RankingStrategy.HYBRID,
        weights: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize ranker.
        
        Args:
            strategy: Ranking strategy
            weights: Custom scoring weights
        """
        self.strategy = strategy
        self.weights = weights or self.WEIGHTS.copy()
    
    def rank(
        self,
        results: List[Dict],
        strategy: Optional[RankingStrategy] = None,
    ) -> List[RankingScore]:
        """
        Rank search results.
        
        Args:
            results: List of result dicts (page_id, url, tfidf_score, domain, created_at)
            strategy: Override ranking strategy
        
        Returns:
            Sorted list of RankingScore objects
        """
        strategy = strategy or self.strategy
        scores = []
        
        for result in results:
            # Calculate component scores
            relevance = self._calculate_relevance(result)
            popularity = self._calculate_popularity(result)
            recency = self._calculate_recency(result)
            
            # Calculate final score based on strategy
            if strategy == RankingStrategy.RELEVANCE:
                final_score = relevance
            elif strategy == RankingStrategy.POPULARITY:
                final_score = popularity
            elif strategy == RankingStrategy.RECENCY:
                final_score = recency
            else:  # HYBRID
                final_score = (
                    self.weights['relevance'] * relevance +
                    self.weights['popularity'] * popularity +
                    self.weights['recency'] * recency
                )
            
            score = RankingScore(
                page_id=result.get('page_id'),
                url=result.get('url', ''),
                relevance_score=relevance,
                popularity_score=popularity,
                recency_score=recency,
                final_score=final_score,
            )
            
            scores.append(score)
        
        # Sort by final score
        scores.sort()
        
        return scores
    
    def _calculate_relevance(self, result: Dict) -> float:
        """
        Calculate relevance score (TF-IDF based).
        
        Args:
            result: Result dict
        
        Returns:
            Relevance score (0-1)
        """
        # Use stored TF-IDF score
        tfidf = result.get('tfidf_score', 0.0)
        
        # Normalize to 0-1 range
        # Assuming TF-IDF scores are in 0-1 range from Stage 3
        return min(float(tfidf), 1.0)
    
    def _calculate_popularity(self, result: Dict) -> float:
        """
        Calculate popularity/authority score.
        
        Args:
            result: Result dict
        
        Returns:
            Popularity score (0-1)
        """
        url = result.get('url', '')
        domain = result.get('domain', '')
        
        # Extract domain from URL if not provided
        if not domain and url:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
        
        # Look up domain authority
        authority = self.DOMAIN_AUTHORITY.get(domain, 0.5)
        
        # Factor in inbound links if available
        inbound_links = result.get('inbound_links', 0)
        link_score = min(inbound_links / 100.0, 0.5)  # Max 0.5 from links
        
        # Combined
        popularity = authority * 0.7 + link_score * 0.3
        
        return min(popularity, 1.0)
    
    def _calculate_recency(self, result: Dict) -> float:
        """
        Calculate recency/freshness score.
        
        Args:
            result: Result dict
        
        Returns:
            Recency score (0-1)
        """
        from datetime import datetime, timedelta
        
        created_at = result.get('created_at')
        
        if not created_at:
            return 0.5  # Middle score if unknown
        
        try:
            # Parse creation date
            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_dt = created_at
            
            # Calculate age in days
            age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
            
            # Scoring: older = lower score
            # Linear decay: 0 days = 1.0, 365 days = 0.0, older = 0.0
            if age_days <= 0:
                return 1.0
            elif age_days >= 365:
                return 0.1
            else:
                return 1.0 - (age_days / 365.0)
        
        except Exception as e:
            logger.warning(f"Error calculating recency: {e}")
            return 0.5
    
    def boost_result(
        self,
        score: RankingScore,
        boost_factor: float = 1.5,
    ) -> RankingScore:
        """
        Boost a result's score.
        
        Args:
            score: RankingScore object
            boost_factor: Boost multiplier (default 1.5x)
        
        Returns:
            Boosted RankingScore
        """
        score.final_score = min(score.final_score * boost_factor, 1.0)
        return score
    
    def penalize_result(
        self,
        score: RankingScore,
        penalty_factor: float = 0.5,
    ) -> RankingScore:
        """
        Penalize a result's score.
        
        Args:
            score: RankingScore object
            penalty_factor: Penalty multiplier (default 0.5x)
        
        Returns:
            Penalized RankingScore
        """
        score.final_score = max(score.final_score * penalty_factor, 0.0)
        return score
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Set custom ranking weights.
        
        Args:
            weights: Dict with 'relevance', 'popularity', 'recency' keys
        """
        # Validate weights sum to ~1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, normalizing")
            # Normalize
            factor = 1.0 / total
            weights = {k: v * factor for k, v in weights.items()}
        
        self.weights = weights
        logger.info(f"Ranking weights set: {weights}")
    
    def update_domain_authority(self, domain: str, score: float) -> None:
        """
        Update domain authority score.
        
        Args:
            domain: Domain name
            score: Authority score (0-1)
        """
        if 0 <= score <= 1:
            self.DOMAIN_AUTHORITY[domain] = score
            logger.debug(f"Updated authority for {domain}: {score}")
        else:
            logger.warning(f"Invalid authority score: {score}")
