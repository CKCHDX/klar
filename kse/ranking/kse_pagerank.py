"""
PageRank - Factor 2: Link-based authority scoring algorithm
Implements Google's PageRank algorithm for ranking web pages by link structure
"""

import logging
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class PageRank:
    """PageRank algorithm implementation"""
    
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 0.0001):
        """
        Initialize PageRank calculator
        
        Args:
            damping_factor: Probability of following a link (default: 0.85)
            max_iterations: Maximum number of iterations (default: 100)
            tolerance: Convergence threshold (default: 0.0001)
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        logger.info(f"PageRank initialized (d={damping_factor}, max_iter={max_iterations})")
    
    def calculate(self, link_graph: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Calculate PageRank scores for all pages in the graph
        
        Args:
            link_graph: Dictionary mapping page URL to list of outgoing link URLs
        
        Returns:
            Dictionary mapping page URL to PageRank score (0.0-1.0)
        """
        if not link_graph:
            logger.warning("Empty link graph provided")
            return {}
        
        # Build reverse link graph (incoming links)
        incoming_links = self._build_incoming_links(link_graph)
        
        # Get all unique pages
        all_pages = set(link_graph.keys())
        for links in link_graph.values():
            all_pages.update(links)
        
        all_pages = list(all_pages)
        n = len(all_pages)
        
        if n == 0:
            return {}
        
        logger.info(f"Calculating PageRank for {n} pages")
        
        # Initialize PageRank scores (uniform distribution)
        pagerank = {page: 1.0 / n for page in all_pages}
        
        # Iterative PageRank calculation
        for iteration in range(self.max_iterations):
            new_pagerank = {}
            max_change = 0.0
            
            for page in all_pages:
                # Base score (teleportation)
                rank = (1 - self.damping_factor) / n
                
                # Add contributions from incoming links
                for incoming_page in incoming_links.get(page, []):
                    outgoing_count = len(link_graph.get(incoming_page, []))
                    if outgoing_count > 0:
                        rank += self.damping_factor * (pagerank[incoming_page] / outgoing_count)
                
                new_pagerank[page] = rank
                
                # Track convergence
                change = abs(new_pagerank[page] - pagerank[page])
                max_change = max(max_change, change)
            
            pagerank = new_pagerank
            
            # Check for convergence
            if max_change < self.tolerance:
                logger.info(f"PageRank converged after {iteration + 1} iterations")
                break
        
        else:
            logger.info(f"PageRank completed {self.max_iterations} iterations")
        
        return pagerank
    
    def _build_incoming_links(self, link_graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Build reverse link graph (incoming links)
        
        Args:
            link_graph: Forward link graph (page -> outgoing links)
        
        Returns:
            Reverse link graph (page -> incoming links)
        """
        incoming = defaultdict(list)
        
        for source, targets in link_graph.items():
            for target in targets:
                incoming[target].append(source)
        
        return dict(incoming)
    
    def normalize_scores(self, pagerank: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize PageRank scores to 0-1 range
        
        Args:
            pagerank: Raw PageRank scores
        
        Returns:
            Normalized scores (0.0-1.0)
        """
        if not pagerank:
            return {}
        
        min_score = min(pagerank.values())
        max_score = max(pagerank.values())
        
        if max_score == min_score:
            # All scores are the same
            return {page: 0.5 for page in pagerank}
        
        # Min-max normalization
        normalized = {
            page: (score - min_score) / (max_score - min_score)
            for page, score in pagerank.items()
        }
        
        return normalized
    
    def get_top_pages(self, pagerank: Dict[str, float], n: int = 10) -> List[tuple]:
        """
        Get top N pages by PageRank score
        
        Args:
            pagerank: PageRank scores
            n: Number of top pages to return
        
        Returns:
            List of (page, score) tuples sorted by score
        """
        sorted_pages = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return sorted_pages[:n]
    
    def calculate_incremental(
        self,
        current_pagerank: Dict[str, float],
        link_graph: Dict[str, List[str]],
        new_pages: Set[str]
    ) -> Dict[str, float]:
        """
        Incrementally update PageRank with new pages
        
        Args:
            current_pagerank: Existing PageRank scores
            link_graph: Complete link graph including new pages
            new_pages: Set of newly added page URLs
        
        Returns:
            Updated PageRank scores
        """
        logger.info(f"Incrementally updating PageRank with {len(new_pages)} new pages")
        
        # For now, just recalculate completely
        # TODO: Implement true incremental PageRank algorithm
        return self.calculate(link_graph)
    
    def detect_link_spam(self, link_graph: Dict[str, List[str]], threshold: int = 1000) -> Set[str]:
        """
        Detect potential link spam pages (pages with excessive outgoing links)
        
        Args:
            link_graph: Link graph to analyze
            threshold: Maximum number of outgoing links before flagging as spam
        
        Returns:
            Set of potentially spammy page URLs
        """
        spam_pages = set()
        
        for page, outgoing_links in link_graph.items():
            if len(outgoing_links) > threshold:
                spam_pages.add(page)
                logger.warning(f"Potential link spam detected: {page} has {len(outgoing_links)} outgoing links")
        
        return spam_pages
    
    def calculate_personalized(
        self,
        link_graph: Dict[str, List[str]],
        personalization: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate Personalized PageRank (biased towards certain pages)
        
        Args:
            link_graph: Link graph
            personalization: Dictionary mapping page URL to personalization weight
        
        Returns:
            Personalized PageRank scores
        """
        if not link_graph or not personalization:
            return self.calculate(link_graph)
        
        # Normalize personalization weights
        total_weight = sum(personalization.values())
        if total_weight > 0:
            personalization = {
                page: weight / total_weight
                for page, weight in personalization.items()
            }
        
        # Build reverse link graph
        incoming_links = self._build_incoming_links(link_graph)
        
        # Get all pages
        all_pages = set(link_graph.keys())
        for links in link_graph.values():
            all_pages.update(links)
        all_pages = list(all_pages)
        n = len(all_pages)
        
        # Initialize
        pagerank = {page: 1.0 / n for page in all_pages}
        
        # Iterative calculation with personalization
        for iteration in range(self.max_iterations):
            new_pagerank = {}
            max_change = 0.0
            
            for page in all_pages:
                # Personalized teleportation
                if page in personalization:
                    rank = (1 - self.damping_factor) * personalization[page]
                else:
                    rank = (1 - self.damping_factor) / n
                
                # Add contributions from incoming links
                for incoming_page in incoming_links.get(page, []):
                    outgoing_count = len(link_graph.get(incoming_page, []))
                    if outgoing_count > 0:
                        rank += self.damping_factor * (pagerank[incoming_page] / outgoing_count)
                
                new_pagerank[page] = rank
                change = abs(new_pagerank[page] - pagerank[page])
                max_change = max(max_change, change)
            
            pagerank = new_pagerank
            
            if max_change < self.tolerance:
                logger.info(f"Personalized PageRank converged after {iteration + 1} iterations")
                break
        
        return pagerank
