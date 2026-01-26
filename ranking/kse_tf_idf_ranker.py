"""kse_tf_idf_ranker.py - TF-IDF Based Ranking

Factor 1: Term Frequency-Inverse Document Frequency
- Measures relevance of query terms to documents
- Weight: 25% of final score
- High for documents matching query well
"""

import logging
from typing import Dict

from kse.core import get_logger

logger = get_logger('ranking')


class TFIDFRanker:
    """TF-IDF based ranking factor"""
    
    def __init__(self):
        """Initialize TF-IDF ranker"""
        logger.debug("TFIDFRanker initialized")
    
    def score_document(self, 
                      url: str,
                      tfidf_scores: Dict[str, float]) -> float:
        """Score document by TF-IDF
        
        Args:
            url: Document URL
            tfidf_scores: Term → TF-IDF score mapping
            
        Returns:
            Score (0-1)
        """
        if not tfidf_scores:
            return 0.0
        
        # Get TF-IDF score for this document
        score = tfidf_scores.get(url, 0.0)
        
        # Normalize to 0-1
        return min(score / 100.0, 1.0)
    
    def rank_documents(self, 
                      documents: Dict[str, Dict],
                      query_terms: list) -> Dict[str, float]:
        """Rank documents by TF-IDF
        
        Args:
            documents: URL → document data
            query_terms: Query terms to match
            
        Returns:
            URL → score mapping
        """
        scores = {}
        
        for url, doc in documents.items():
            # Get TF-IDF scores for query terms
            tfidf_sum = 0.0
            for term in query_terms:
                term_score = doc.get('tfidf_scores', {}).get(term, 0.0)
                tfidf_sum += term_score
            
            # Average TF-IDF for query
            avg_tfidf = tfidf_sum / max(len(query_terms), 1)
            scores[url] = min(avg_tfidf / 100.0, 1.0)
        
        return scores


__all__ = ["TFIDFRanker"]
