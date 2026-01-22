"""
Multi-Factor Ranking Algorithm
Ranks search results using:
- TF-IDF (35%)
- PageRank (20%)
- Domain Trust (15%)
- Recency (10%)
- Geographic Relevance (10%)
- Entity Match (10%)

Optimized for Swedish queries and preferences.
"""

import logging
from typing import List, Dict, Tuple, Optional
import math
from collections import defaultdict
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class RankingEngine:
    """
    Production-grade ranking algorithm.
    Multi-factor ranking for optimal result ordering.
    """

    def __init__(self):
        """
        Initialize ranking engine.
        """
        self.pagerank_scores = {}  # page_id -> pagerank score
        self.domain_trust_cache = {}  # domain -> trust score
        self.recency_weights = {}  # page_id -> recency weight
        
        # Weights for each ranking factor
        self.weights = {
            'tf_idf': 0.35,
            'pagerank': 0.20,
            'domain_trust': 0.15,
            'recency': 0.10,
            'geography': 0.10,
            'entity_match': 0.10,
        }

    def rank(self, results: List[Tuple[int, str, float]], 
             query: str = "", entities: List[Tuple[str, str]] = None,
             intent: Dict[str, float] = None) -> List[Tuple[int, str, float]]:
        """
        Rank search results using multi-factor algorithm.
        
        Args:
            results: List of (page_id, url, tf_idf_score) tuples
            query: Original search query
            entities: Extracted entities from query
            intent: Intent classification
            
        Returns:
            Ranked list of (page_id, url, final_score)
            
        Ranking factors:
            - TF-IDF: How relevant page is to query (35%)
            - PageRank: How authoritative page is (20%)
            - Domain Trust: How trustworthy domain is (15%)
            - Recency: How recent page is (10%)
            - Geography: How relevant to geographic location (10%)
            - Entity Match: How well page matches entities (10%)
        """
        if not results:
            return []
        
        if entities is None:
            entities = []
        if intent is None:
            intent = {}
        
        # Calculate factor scores for each result
        scored_results = []
        
        for page_id, url, tf_idf_score in results:
            # Factor 1: TF-IDF score (normalized)
            f_tfidf = min(1.0, tf_idf_score / 10.0)  # Normalize
            
            # Factor 2: PageRank score
            f_pagerank = self.pagerank_scores.get(page_id, 0.5)
            
            # Factor 3: Domain trust
            domain = url.split('/')[2]
            f_domain_trust = self._get_domain_trust(domain)
            
            # Factor 4: Recency
            f_recency = self._calculate_recency_score(page_id)
            
            # Factor 5: Geographic relevance
            f_geography = self._calculate_geographic_relevance(url, query)
            
            # Factor 6: Entity match
            f_entity = self._calculate_entity_match(url, entities)
            
            # Combine factors with weights
            final_score = (
                self.weights['tf_idf'] * f_tfidf +
                self.weights['pagerank'] * f_pagerank +
                self.weights['domain_trust'] * f_domain_trust +
                self.weights['recency'] * f_recency +
                self.weights['geography'] * f_geography +
                self.weights['entity_match'] * f_entity
            )
            
            scored_results.append((page_id, url, final_score))
        
        # Sort by final score (descending)
        scored_results.sort(key=lambda x: x[2], reverse=True)
        
        return scored_results

    def calculate_pagerank(self, pages: Dict[int, List[int]]):
        """
        Calculate PageRank for all pages.
        PageRank measures page authority based on incoming links.
        
        Args:
            pages: Dict mapping page_id -> list of outgoing page_ids
        """
        # Initialize PageRank scores
        num_pages = len(pages)
        scores = {page_id: 1.0 / num_pages for page_id in pages.keys()}
        
        # Iterative algorithm (10 iterations)
        damping_factor = 0.85
        
        for iteration in range(10):
            new_scores = {}
            
            for page_id in pages.keys():
                # Find all pages linking to this one
                incoming_links = [
                    source for source in pages.keys()
                    if page_id in pages[source]
                ]
                
                # Calculate new PageRank
                rank = (1 - damping_factor) / num_pages
                
                for source in incoming_links:
                    num_outlinks = len(pages[source])
                    if num_outlinks > 0:
                        rank += damping_factor * (scores[source] / num_outlinks)
                
                new_scores[page_id] = rank
            
            scores = new_scores
        
        self.pagerank_scores = scores
        logger.info(f"PageRank calculated for {num_pages} pages")

    # Private methods
    
    def _get_domain_trust(self, domain: str) -> float:
        """
        Get domain trust score (0.0 - 1.0).
        Cached for performance.
        
        Args:
            domain: Domain name
            
        Returns:
            Trust score (0.0 - 1.0)
        """
        if domain in self.domain_trust_cache:
            return self.domain_trust_cache[domain]
        
        score = 0.5  # Default
        
        # Government domains: very high trust
        if any(gov in domain for gov in ['gov', 'regeringskansliet', 'riksdag', 'se']):
            score = 0.95
        
        # News sites: high trust
        elif any(news in domain for news in ['sverigesradio', 'aftonbladet', 'dn', 'gp', 'politiken']):
            score = 0.90
        
        # Wikipedia: high trust
        elif 'wikipedia' in domain:
            score = 0.88
        
        # University: high trust
        elif 'edu' in domain or any(uni in domain for uni in ['lund', 'uppsala', 'kth']):
            score = 0.85
        
        # Blogs: lower trust
        elif 'blog' in domain:
            score = 0.55
        
        # Forums: medium trust
        elif 'forum' in domain or 'reddit' in domain:
            score = 0.60
        
        # Commercial: medium trust
        elif 'com' in domain or '.se' in domain:
            score = 0.65
        
        self.domain_trust_cache[domain] = score
        return score

    def _calculate_recency_score(self, page_id: int) -> float:
        """
        Calculate how recent a page is.
        More recent pages score higher.
        
        Args:
            page_id: Page identifier
            
        Returns:
            Recency score (0.0 - 1.0)
        """
        # In production, get last_updated from database
        # For now, return default
        return 0.7

    def _calculate_geographic_relevance(self, url: str, query: str) -> float:
        """
        Calculate how relevant page is geographically.
        If query mentions Stockholm, boost Stockholm pages.
        
        Args:
            url: Page URL
            query: Search query
            
        Returns:
            Geographic relevance score (0.0 - 1.0)
        """
        query_lower = query.lower()
        url_lower = url.lower()
        
        # Swedish cities
        cities = ['stockholm', 'göteborg', 'malmö', 'uppsala', 'västerås',
                  'Örebro', 'linköping', 'helsingborg', 'jönköping']
        
        for city in cities:
            if city in query_lower and city in url_lower:
                return 0.95  # Strong geographic match
        
        # Check for any city in query
        for city in cities:
            if city in query_lower:
                # Boost Swedish pages slightly
                if '.se' in url:
                    return 0.80
        
        return 0.50  # Default

    def _calculate_entity_match(self, url: str, entities: List[Tuple[str, str]]) -> float:
        """
        Calculate how well page matches extracted entities.
        
        Args:
            url: Page URL
            entities: List of (entity, type) tuples
            
        Returns:
            Entity match score (0.0 - 1.0)
        """
        if not entities:
            return 0.50
        
        url_lower = url.lower()
        matches = 0
        
        for entity, entity_type in entities:
            if entity.lower() in url_lower:
                matches += 1
        
        # Score based on match rate
        match_rate = matches / len(entities)
        return 0.50 + (0.50 * match_rate)  # Range 0.5-1.0


if __name__ == "__main__":
    # Test ranking engine
    ranking = RankingEngine()
    
    # Test results
    results = [
        (1, "https://aftonbladet.se/page1", 8.5),
        (2, "https://blog.example.com/page2", 7.2),
        (3, "https://sverigesradio.se/page3", 9.1),
    ]
    
    ranked = ranking.rank(results, query="stockholm restauranger")
    print(f"Ranked results: {ranked}")
