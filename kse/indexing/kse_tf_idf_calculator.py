"""
KSE TF-IDF Calculator - Term Frequency-Inverse Document Frequency computation
"""
import math
from typing import Dict, List
from kse.indexing.kse_inverted_index import InvertedIndex
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class TFIDFCalculator:
    """Calculate TF-IDF scores for terms and documents"""
    
    def __init__(self, inverted_index: InvertedIndex):
        """
        Initialize TF-IDF calculator
        
        Args:
            inverted_index: Inverted index instance
        """
        self.index = inverted_index
        self.idf_cache: Dict[str, float] = {}
    
    def calculate_tf(self, term: str, doc_id: str) -> float:
        """
        Calculate term frequency (TF)
        
        Args:
            term: Term to calculate TF for
            doc_id: Document ID
        
        Returns:
            TF score (normalized)
        """
        # Get term frequency in document
        tf = self.index.get_term_frequency(term, doc_id)
        
        # Get document length
        doc_length = self.index.get_document_length(doc_id)
        
        if doc_length == 0:
            return 0.0
        
        # Normalized TF
        return tf / doc_length
    
    def calculate_idf(self, term: str) -> float:
        """
        Calculate inverse document frequency (IDF)
        
        Args:
            term: Term to calculate IDF for
        
        Returns:
            IDF score
        """
        # Check cache
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        # Get document frequency
        df = self.index.get_document_frequency(term)
        
        if df == 0:
            return 0.0
        
        # Calculate IDF: log(N / df)
        # Add 1 to avoid division by zero
        total_docs = self.index.total_documents
        idf = math.log((total_docs + 1) / (df + 1))
        
        # Cache result
        self.idf_cache[term] = idf
        
        return idf
    
    def calculate_tfidf(self, term: str, doc_id: str) -> float:
        """
        Calculate TF-IDF score
        
        Args:
            term: Term to calculate TF-IDF for
            doc_id: Document ID
        
        Returns:
            TF-IDF score
        """
        tf = self.calculate_tf(term, doc_id)
        idf = self.calculate_idf(term)
        return tf * idf
    
    def calculate_document_vector(self, doc_id: str) -> Dict[str, float]:
        """
        Calculate TF-IDF vector for document
        
        Args:
            doc_id: Document ID
        
        Returns:
            Dictionary of {term: tfidf_score}
        """
        vector = {}
        terms = self.index.get_document_terms(doc_id)
        
        for term in terms:
            tfidf = self.calculate_tfidf(term, doc_id)
            if tfidf > 0:
                vector[term] = tfidf
        
        return vector
    
    def calculate_query_vector(self, query_terms: List[str]) -> Dict[str, float]:
        """
        Calculate TF-IDF vector for query
        
        Args:
            query_terms: List of query terms
        
        Returns:
            Dictionary of {term: idf_score}
        """
        vector = {}
        
        # For queries, use IDF scores (TF is uniform)
        for term in query_terms:
            idf = self.calculate_idf(term)
            if idf > 0:
                vector[term] = idf
        
        return vector
    
    def calculate_similarity(self, query_terms: List[str], doc_id: str) -> float:
        """
        Calculate cosine similarity between query and document
        
        Args:
            query_terms: List of query terms
            doc_id: Document ID
        
        Returns:
            Similarity score (0-1)
        """
        # Get vectors
        query_vector = self.calculate_query_vector(query_terms)
        doc_vector = self.calculate_document_vector(doc_id)
        
        if not query_vector or not doc_vector:
            return 0.0
        
        # Calculate dot product
        dot_product = 0.0
        for term, query_score in query_vector.items():
            if term in doc_vector:
                dot_product += query_score * doc_vector[term]
        
        # Calculate magnitudes
        query_magnitude = math.sqrt(sum(score ** 2 for score in query_vector.values()))
        doc_magnitude = math.sqrt(sum(score ** 2 for score in doc_vector.values()))
        
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (query_magnitude * doc_magnitude)
        
        return similarity
    
    def rank_documents(self, query_terms: List[str], doc_ids: List[str] = None) -> List[tuple]:
        """
        Rank documents by TF-IDF similarity to query
        
        Args:
            query_terms: List of query terms
            doc_ids: List of document IDs to rank (None = all documents)
        
        Returns:
            List of (doc_id, score) tuples, sorted by score descending
        """
        if doc_ids is None:
            # Get all documents containing at least one query term
            doc_ids = self.index.get_documents_containing_any(query_terms)
        
        if not doc_ids:
            return []
        
        # Calculate similarity scores
        scores = []
        for doc_id in doc_ids:
            score = self.calculate_similarity(query_terms, doc_id)
            if score > 0:
                scores.append((doc_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores
    
    def clear_cache(self) -> None:
        """Clear IDF cache"""
        self.idf_cache.clear()
        logger.debug("TF-IDF cache cleared")
