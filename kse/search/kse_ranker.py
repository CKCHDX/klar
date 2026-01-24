"""
KSE Ranker

Ranking algorithms for search results (TF-IDF, PageRank, etc).
"""

from typing import Dict, List, Tuple
import math
import logging

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class KSERanker:
    """Base ranker class."""
    
    def rank(self, doc_id: int, term: str, term_freq: float, idf: float) -> float:
        """
        Calculate relevance score.
        
        Args:
            doc_id: Document ID
            term: Search term
            term_freq: Term frequency in document
            idf: Inverse document frequency
            
        Returns:
            Relevance score
        """
        raise NotImplementedError


class TFIDFRanker(KSERanker):
    """TF-IDF based ranking."""
    
    def __init__(self):
        """Initialize TF-IDF ranker."""
        self.doc_lengths: Dict[int, int] = {}
    
    def set_doc_length(self, doc_id: int, length: int):
        """
        Set document length (for TF normalization).
        
        Args:
            doc_id: Document ID
            length: Number of tokens in document
        """
        self.doc_lengths[doc_id] = length
    
    def rank(self, doc_id: int, term: str, term_freq: float, idf: float) -> float:
        """
        Calculate TF-IDF score.
        
        Args:
            doc_id: Document ID
            term: Search term
            term_freq: Raw term frequency
            idf: Inverse document frequency
            
        Returns:
            TF-IDF score
        """
        # Normalize TF by document length
        doc_length = self.doc_lengths.get(doc_id, 1)
        normalized_tf = term_freq / max(doc_length, 1)
        
        # TF-IDF = TF * IDF
        return normalized_tf * idf
    
    def rank_multiple_terms(self, doc_id: int, term_scores: List[Tuple[str, float, float]]) -> float:
        """
        Calculate combined TF-IDF for multiple terms.
        
        Args:
            doc_id: Document ID
            term_scores: List of (term, term_freq, idf) tuples
            
        Returns:
            Combined score
        """
        scores = [self.rank(doc_id, term, tf, idf) for term, tf, idf in term_scores]
        return sum(scores) if scores else 0.0


class PageRankCalculator:
    """Calculates PageRank scores."""
    
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 30, epsilon: float = 0.0001):
        """
        Initialize PageRank calculator.
        
        Args:
            damping_factor: Damping factor (0.85 typical)
            max_iterations: Maximum iterations for convergence
            epsilon: Convergence threshold
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.epsilon = epsilon
        self.page_ranks: Dict[int, float] = {}
    
    def calculate(self, links: Dict[int, List[int]]) -> Dict[int, float]:
        """
        Calculate PageRank for all pages.
        
        Args:
            links: Dictionary {page_id: [outgoing_link_ids]}
            
        Returns:
            Dictionary {page_id: pagerank}
        """
        num_pages = len(links)
        if num_pages == 0:
            return {}
        
        # Initialize all pages with equal rank
        ranks = {page_id: 1.0 / num_pages for page_id in links}
        
        # Iterate until convergence
        for iteration in range(self.max_iterations):
            new_ranks = {}
            max_diff = 0
            
            for page_id in links:
                # Base rank from damping factor
                base_rank = (1 - self.damping_factor) / num_pages
                
                # Add contributions from pages linking to this one
                incoming_rank = 0
                for source_page, outgoing_links in links.items():
                    if page_id in outgoing_links:
                        num_outgoing = len(outgoing_links)
                        if num_outgoing > 0:
                            incoming_rank += ranks[source_page] / num_outgoing
                
                new_rank = base_rank + self.damping_factor * incoming_rank
                new_ranks[page_id] = new_rank
                
                # Check convergence
                diff = abs(new_rank - ranks[page_id])
                max_diff = max(max_diff, diff)
            
            ranks = new_ranks
            
            if max_diff < self.epsilon:
                logger.info(f"PageRank converged in {iteration + 1} iterations")
                break
        
        self.page_ranks = ranks
        return ranks
    
    def get_rank(self, page_id: int) -> float:
        """
        Get PageRank for a page.
        
        Args:
            page_id: Page ID
            
        Returns:
            PageRank score (default 0 if not found)
        """
        return self.page_ranks.get(page_id, 0.0)
    
    def normalize_ranks(self, min_value: float = 0.0, max_value: float = 1.0) -> Dict[int, float]:
        """
        Normalize PageRank values to a range.
        
        Args:
            min_value: Minimum normalized value
            max_value: Maximum normalized value
            
        Returns:
            Normalized ranks
        """
        if not self.page_ranks:
            return {}
        
        min_rank = min(self.page_ranks.values())
        max_rank = max(self.page_ranks.values())
        
        if min_rank == max_rank:
            return {page_id: (min_value + max_value) / 2 for page_id in self.page_ranks}
        
        range_size = max_rank - min_rank
        normalized = {}
        
        for page_id, rank in self.page_ranks.items():
            normalized_rank = min_value + (rank - min_rank) / range_size * (max_value - min_value)
            normalized[page_id] = normalized_rank
        
        return normalized


class HybridRanker:
    """Combines multiple ranking signals."""
    
    def __init__(self):
        """
        Initialize hybrid ranker.
        """
        self.tf_idf_ranker = TFIDFRanker()
        self.page_rank_scores: Dict[int, float] = {}
        self.url_scores: Dict[int, float] = {}  # Boost for specific domains
        self.freshness_scores: Dict[int, float] = {}  # Boost for recent content
    
    def rank(self,
             doc_id: int,
             term_freq: float,
             idf: float,
             tf_idf_weight: float = 0.6,
             pagerank_weight: float = 0.3,
             url_weight: float = 0.05,
             freshness_weight: float = 0.05) -> float:
        """
        Calculate hybrid score combining multiple signals.
        
        Args:
            doc_id: Document ID
            term_freq: Term frequency
            idf: Inverse document frequency
            tf_idf_weight: Weight for TF-IDF component
            pagerank_weight: Weight for PageRank component
            url_weight: Weight for URL authority
            freshness_weight: Weight for freshness
            
        Returns:
            Combined relevance score
        """
        # TF-IDF component
        tfidf_score = self.tf_idf_ranker.rank(doc_id, "", term_freq, idf)
        
        # PageRank component
        pagerank = self.page_rank_scores.get(doc_id, 0.5)
        
        # URL authority component
        url_score = self.url_scores.get(doc_id, 0.5)
        
        # Freshness component
        freshness = self.freshness_scores.get(doc_id, 0.5)
        
        # Combine with weights
        combined_score = (
            tfidf_score * tf_idf_weight +
            pagerank * pagerank_weight +
            url_score * url_weight +
            freshness * freshness_weight
        )
        
        return combined_score
    
    def set_pagerank_scores(self, scores: Dict[int, float]):
        """
        Set PageRank scores.
        
        Args:
            scores: Dictionary {doc_id: score}
        """
        self.page_rank_scores = scores
    
    def set_url_authority(self, doc_id: int, score: float):
        """
        Set URL authority score.
        
        Args:
            doc_id: Document ID
            score: Authority score (0-1)
        """
        self.url_scores[doc_id] = score
    
    def set_freshness_score(self, doc_id: int, score: float):
        """
        Set freshness score.
        
        Args:
            doc_id: Document ID
            score: Freshness score (0-1)
        """
        self.freshness_scores[doc_id] = score
