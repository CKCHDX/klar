"""
Ranking Core - Main ranking orchestrator for KSE
Combines multiple ranking factors to produce final search result scores
Enhanced for Swedish enterprise search with semantic understanding
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RankingWeights:
    """Configurable weights for ranking factors
    
    Optimized for Swedish enterprise search (Naver-style):
    - Higher weight on regional relevance (Swedish content prioritization)
    - Balanced TF-IDF for content matching
    - Strong domain authority for trusted sources
    - PageRank for link-based quality
    - Semantic similarity for natural language queries
    """
    tf_idf: float = 0.25  # Content relevance
    pagerank: float = 0.15  # Link-based quality
    domain_authority: float = 0.15  # Trusted Swedish domains
    regional_relevance: float = 0.20  # Swedish content boost (4x increase!)
    semantic_similarity: float = 0.15  # Natural language understanding
    recency: float = 0.06  # Freshness factor
    keyword_density: float = 0.03  # Keyword optimization
    link_structure: float = 0.01  # Internal/external links


class RankingCore:
    """Main ranking orchestrator with enhanced Swedish and semantic ranking"""
    
    def __init__(self, weights: Optional[RankingWeights] = None):
        """
        Initialize ranking core with configurable weights
        
        Args:
            weights: Custom ranking weights (uses defaults if None)
        """
        self.weights = weights or RankingWeights()
        
        # Initialize semantic similarity module
        try:
            from kse.ranking.kse_semantic_similarity import SemanticSimilarity
            self.semantic_scorer = SemanticSimilarity()
            self.has_semantic = True
            logger.info("Semantic similarity module loaded")
        except Exception as e:
            logger.warning(f"Could not load semantic similarity: {e}")
            self.has_semantic = False
        
        logger.info(f"RankingCore initialized with weights: {self.weights}")
    
    def rank_results(
        self,
        results: List[Dict[str, Any]],
        query_terms: List[str],
        ranking_data: Optional[Dict[str, Any]] = None,
        original_query: str = "",
        query_intent: str = None
    ) -> List[Dict[str, Any]]:
        """
        Apply comprehensive ranking to search results
        
        Args:
            results: List of search results with basic TF-IDF scores
            query_terms: Processed query terms
            ranking_data: Optional pre-computed ranking data (PageRank, Domain Authority, etc.)
            original_query: Original user query for semantic analysis
            query_intent: Detected query intent
        
        Returns:
            Ranked and scored results
        """
        if not results:
            logger.debug("No results to rank")
            return []
        
        logger.debug(f"Ranking {len(results)} results with {len(query_terms)} query terms")
        
        # Initialize ranking data if not provided
        ranking_data = ranking_data or {}
        pagerank_scores = ranking_data.get('pagerank', {})
        domain_authority = ranking_data.get('domain_authority', {})
        
        # Apply ranking to each result
        ranked_results = []
        for result in results:
            url = result.get('url', '')
            domain = self._extract_domain(url)
            
            # Calculate individual ranking factors
            scores = {
                'tf_idf': result.get('score', 0.0),
                'pagerank': pagerank_scores.get(url, 0.5),
                'domain_authority': domain_authority.get(domain, 0.5),
                'regional_relevance': self._calculate_regional_score(result),
                'semantic_similarity': self._calculate_semantic_score(
                    original_query, result, query_intent
                ) if self.has_semantic else 0.5,
                'recency': self._calculate_recency_score(result),
                'keyword_density': self._calculate_keyword_density(result, query_terms),
                'link_structure': self._calculate_link_score(result)
            }
            
            # Calculate weighted final score
            final_score = self._calculate_weighted_score(scores)
            
            # Add ranking metadata to result
            result['final_score'] = final_score
            result['ranking_breakdown'] = scores
            
            ranked_results.append(result)
        
        # Sort by final score
        ranked_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Add rank numbers
        for i, result in enumerate(ranked_results):
            result['rank'] = i + 1
        
        logger.info(f"Ranked {len(ranked_results)} results")
        return ranked_results
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate final weighted score from individual factors
        
        Args:
            scores: Dictionary of individual ranking scores
        
        Returns:
            Weighted final score (0.0-100.0)
        """
        weighted_sum = (
            scores['tf_idf'] * self.weights.tf_idf +
            scores['pagerank'] * 100 * self.weights.pagerank +
            scores['domain_authority'] * 100 * self.weights.domain_authority +
            scores['regional_relevance'] * 100 * self.weights.regional_relevance +
            scores['semantic_similarity'] * 100 * self.weights.semantic_similarity +
            scores['recency'] * 100 * self.weights.recency +
            scores['keyword_density'] * 100 * self.weights.keyword_density +
            scores['link_structure'] * 100 * self.weights.link_structure
        )
        
        return round(weighted_sum, 2)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception as e:
            logger.warning(f"Failed to extract domain from {url}: {e}")
            return ""
    
    def _calculate_regional_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate regional relevance score using RegionalRelevance module
        
        Args:
            result: Search result with metadata
        
        Returns:
            Regional score (0.0-1.0)
        """
        try:
            from kse.ranking.kse_regional_relevance import RegionalRelevance
            scorer = RegionalRelevance()
            return scorer.calculate_regional_score(result)
        except Exception as e:
            logger.warning(f"Regional scoring failed: {e}")
            return 0.5
    
    def _calculate_semantic_score(
        self, 
        query: str, 
        result: Dict[str, Any],
        query_intent: str = None
    ) -> float:
        """
        Calculate semantic similarity score
        
        Args:
            query: Original user query
            result: Search result
            query_intent: Detected query intent
        
        Returns:
            Semantic score (0.0-1.0)
        """
        if not self.has_semantic or not query:
            return 0.5
        
        try:
            return self.semantic_scorer.calculate_semantic_score(query, result, query_intent)
        except Exception as e:
            logger.warning(f"Semantic scoring failed: {e}")
            return 0.5
    
    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate recency score (placeholder - will be implemented in kse_recency_scorer.py)
        
        Args:
            result: Search result with metadata
        
        Returns:
            Recency score (0.0-1.0)
        """
        # Default neutral score for now
        return 0.5
    
    def _calculate_keyword_density(self, result: Dict[str, Any], query_terms: List[str]) -> float:
        """
        Calculate keyword density score (placeholder - will be implemented in kse_keyword_density.py)
        
        Args:
            result: Search result
            query_terms: Query terms to check density for
        
        Returns:
            Keyword density score (0.0-1.0)
        """
        # Default neutral score for now
        return 0.5
    
    def _calculate_link_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate link structure score (placeholder - will be implemented in kse_link_structure.py)
        
        Args:
            result: Search result with link metadata
        
        Returns:
            Link structure score (0.0-1.0)
        """
        # Default neutral score for now
        return 0.5
    
    def _calculate_regional_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate regional relevance score (placeholder - will be implemented in kse_regional_relevance.py)
        
        Args:
            result: Search result with regional metadata
        
        Returns:
            Regional relevance score (0.0-1.0)
        """
        # Default neutral score for now - assume Swedish sites are relevant
        url = result.get('url', '').lower()
        if '.se' in url or '.nu' in url:
            return 0.8
        return 0.3
    
    def update_weights(self, new_weights: RankingWeights) -> None:
        """
        Update ranking weights
        
        Args:
            new_weights: New ranking weights to apply
        """
        self.weights = new_weights
        logger.info(f"Updated ranking weights: {self.weights}")
    
    def get_weights(self) -> RankingWeights:
        """Get current ranking weights"""
        return self.weights
