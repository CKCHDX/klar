"""kse_tf_idf_calculator.py - TF-IDF Score Calculation

Computes Term Frequency-Inverse Document Frequency scores:
- TF: How important is term in document
- IDF: How rare is term across all documents
- TF-IDF: Combined relevance score
"""

import logging
import math
from typing import Dict, List, Tuple

from kse.core import get_logger

logger = get_logger('indexing')


class TFIDFCalculator:
    """TF-IDF score calculator"""
    
    def __init__(self):
        """Initialize TF-IDF calculator"""
        self.document_count = 0
        self.term_document_count: Dict[str, int] = {}
        logger.debug("TFIDFCalculator initialized")
    
    def calculate_tf(self, term: str, document_length: int, term_frequency: int) -> float:
        """Calculate Term Frequency
        
        TF = (frequency of term in document) / (total terms in document)
        
        Args:
            term: Term
            document_length: Total terms in document
            term_frequency: Frequency of term in document
            
        Returns:
            TF score (0-1)
        """
        if document_length == 0:
            return 0.0
        return term_frequency / document_length
    
    def calculate_idf(self, documents_with_term: int, total_documents: int) -> float:
        """Calculate Inverse Document Frequency
        
        IDF = log(total documents / documents containing term)
        
        Args:
            documents_with_term: Number of documents with term
            total_documents: Total documents in index
            
        Returns:
            IDF score
        """
        if documents_with_term == 0 or total_documents == 0:
            return 0.0
        return math.log(total_documents / documents_with_term)
    
    def calculate_tfidf(self, tf: float, idf: float) -> float:
        """Calculate TF-IDF score
        
        TF-IDF = TF × IDF
        
        Args:
            tf: Term Frequency score
            idf: Inverse Document Frequency score
            
        Returns:
            TF-IDF score
        """
        return tf * idf
    
    def score_document(self, 
                      document_url: str,
                      terms: List[str],
                      total_documents: int,
                      documents_per_term: Dict[str, int]) -> Dict[str, float]:
        """Score all terms in a document
        
        Args:
            document_url: Document URL
            terms: Terms in document
            total_documents: Total documents indexed
            documents_per_term: Term → document count mapping
            
        Returns:
            Term → TF-IDF score mapping
        """
        scores = {}
        doc_length = len(terms)
        
        # Calculate term frequency for each unique term
        term_freq = {}
        for term in terms:
            term_freq[term] = term_freq.get(term, 0) + 1
        
        # Calculate TF-IDF for each term
        for term, frequency in term_freq.items():
            tf = self.calculate_tf(term, doc_length, frequency)
            idf = self.calculate_idf(
                documents_per_term.get(term, 1),
                total_documents
            )
            tfidf = self.calculate_tfidf(tf, idf)
            scores[term] = tfidf
        
        return scores
    
    def get_top_terms(self, scores: Dict[str, float], k: int = 10) -> List[Tuple[str, float]]:
        """Get top K terms by TF-IDF score
        
        Args:
            scores: Term → score mapping
            k: Number of top terms
            
        Returns:
            List of (term, score) tuples
        """
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]


__all__ = ["TFIDFCalculator"]
