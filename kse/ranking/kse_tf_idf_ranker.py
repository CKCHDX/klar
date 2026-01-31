"""
TF-IDF Ranker - Factor 1: Term Frequency-Inverse Document Frequency scoring
Core relevance scoring based on term importance
"""

import math
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TFIDFRanker:
    """TF-IDF based relevance scoring"""
    
    def __init__(self):
        """Initialize TF-IDF ranker"""
        logger.info("TFIDFRanker initialized")
    
    def calculate_tfidf_score(
        self,
        document: Dict[str, Any],
        query_terms: List[str],
        inverted_index: Dict[str, Any]
    ) -> float:
        """
        Calculate TF-IDF score for a document given query terms
        
        Args:
            document: Document with term frequencies
            query_terms: List of query terms
            inverted_index: Inverted index with IDF values
        
        Returns:
            TF-IDF score (0.0-100.0)
        """
        if not query_terms:
            return 0.0
        
        doc_id = document.get('doc_id', '')
        term_frequencies = document.get('term_frequencies', {})
        
        score = 0.0
        for term in query_terms:
            tf = self._calculate_tf(term, term_frequencies)
            idf = self._get_idf(term, inverted_index)
            score += tf * idf
        
        # Normalize by number of query terms
        if query_terms:
            score = score / len(query_terms)
        
        # Scale to 0-100
        score = min(100.0, score * 10)
        
        logger.debug(f"TF-IDF score for doc {doc_id}: {score:.2f}")
        return score
    
    def _calculate_tf(self, term: str, term_frequencies: Dict[str, int]) -> float:
        """
        Calculate Term Frequency with logarithmic scaling
        
        Args:
            term: Term to calculate frequency for
            term_frequencies: Dictionary of term frequencies in document
        
        Returns:
            TF value
        """
        raw_count = term_frequencies.get(term, 0)
        if raw_count == 0:
            return 0.0
        
        # Logarithmic term frequency: 1 + log(raw_count)
        return 1.0 + math.log10(raw_count)
    
    def _get_idf(self, term: str, inverted_index: Dict[str, Any]) -> float:
        """
        Get Inverse Document Frequency from inverted index
        
        Args:
            term: Term to get IDF for
            inverted_index: Inverted index with IDF values
        
        Returns:
            IDF value
        """
        if term not in inverted_index:
            # High IDF for unseen terms (rare terms are more important)
            return 10.0
        
        term_data = inverted_index[term]
        
        # Check if IDF is pre-computed
        if 'idf' in term_data:
            return term_data['idf']
        
        # Calculate IDF if not pre-computed
        doc_count = term_data.get('doc_count', 1)
        total_docs = term_data.get('total_docs', doc_count)
        
        if doc_count == 0:
            return 10.0
        
        # IDF = log(total_docs / doc_count)
        idf = math.log10(total_docs / doc_count) if total_docs > doc_count else 1.0
        
        return idf
    
    def calculate_cosine_similarity(
        self,
        query_vector: Dict[str, float],
        doc_vector: Dict[str, float]
    ) -> float:
        """
        Calculate cosine similarity between query and document vectors
        
        Args:
            query_vector: Query term weights
            doc_vector: Document term weights
        
        Returns:
            Cosine similarity (0.0-1.0)
        """
        # Calculate dot product
        dot_product = 0.0
        for term, query_weight in query_vector.items():
            doc_weight = doc_vector.get(term, 0.0)
            dot_product += query_weight * doc_weight
        
        # Calculate magnitudes
        query_magnitude = math.sqrt(sum(w * w for w in query_vector.values()))
        doc_magnitude = math.sqrt(sum(w * w for w in doc_vector.values()))
        
        # Avoid division by zero
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (query_magnitude * doc_magnitude)
        
        return max(0.0, min(1.0, similarity))
    
    def boost_exact_matches(
        self,
        score: float,
        document: Dict[str, Any],
        query_terms: List[str]
    ) -> float:
        """
        Apply boost for exact query matches in title or content
        
        Args:
            score: Base TF-IDF score
            document: Document metadata
            query_terms: Query terms
        
        Returns:
            Boosted score
        """
        title = document.get('title', '').lower()
        description = document.get('description', '').lower()
        
        query_phrase = ' '.join(query_terms)
        
        # 50% boost for exact match in title
        if query_phrase in title:
            score *= 1.5
            logger.debug(f"Applied title exact match boost")
        
        # 25% boost for exact match in description
        elif query_phrase in description:
            score *= 1.25
            logger.debug(f"Applied description exact match boost")
        
        return score
    
    def calculate_bm25_score(
        self,
        document: Dict[str, Any],
        query_terms: List[str],
        avg_doc_length: float,
        k1: float = 1.5,
        b: float = 0.75
    ) -> float:
        """
        Calculate BM25 score (alternative to TF-IDF)
        
        Args:
            document: Document with term frequencies
            query_terms: Query terms
            avg_doc_length: Average document length in corpus
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        
        Returns:
            BM25 score
        """
        doc_length = document.get('length', avg_doc_length)
        term_frequencies = document.get('term_frequencies', {})
        
        score = 0.0
        for term in query_terms:
            tf = term_frequencies.get(term, 0)
            if tf == 0:
                continue
            
            # BM25 formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            
            term_score = numerator / denominator
            score += term_score
        
        return score
