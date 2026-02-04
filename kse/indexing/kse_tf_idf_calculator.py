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
        Calculate inverse document frequency (IDF) with proper smoothing
        
        Uses log-scaled normalization to prevent score collapse at scale.
        The formula: log((N - df + 0.5) / (df + 0.5)) + 1
        This ensures:
        - IDF never becomes 0 or negative
        - Scores don't shrink proportionally with document count
        - Smoothing prevents division issues
        
        Args:
            term: Term to calculate IDF for
        
        Returns:
            IDF score (always positive)
        """
        # Check cache
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        # Get document frequency
        df = self.index.get_document_frequency(term)
        
        if df == 0:
            # Term doesn't exist - return very high IDF (rare term bonus)
            return 10.0
        
        # Calculate IDF with smoothing to prevent score collapse
        # Using BM25-style smoothing: log((N - df + 0.5) / (df + 0.5)) + 1
        # This prevents issues when:
        # - df is very small (rare terms)
        # - df approaches N (common terms)
        # - N grows large (scale issue)
        total_docs = self.index.total_documents
        
        # Ensure we have documents
        if total_docs == 0:
            return 1.0
        
        # Smoothed IDF calculation
        numerator = max(total_docs - df + 0.5, 1.0)
        denominator = max(df + 0.5, 1.0)
        idf = math.log(numerator / denominator) + 1
        
        # Ensure IDF is always positive
        idf = max(idf, 0.1)
        
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
    
    def rank_documents(self, query_terms: List[str], doc_ids: List[str] = None, max_candidates: int = 1000) -> List[tuple]:
        """
        Rank documents by TF-IDF similarity to query
        
        Limits scoring to top candidates to prevent expensive full-corpus ranking.
        
        Args:
            query_terms: List of query terms
            doc_ids: List of document IDs to rank (None = retrieve from index)
            max_candidates: Maximum candidate documents to score (prevents O(N) explosion)
        
        Returns:
            List of (doc_id, score) tuples, sorted by score descending
        """
        if doc_ids is None:
            # Get all documents containing at least one query term
            doc_ids = self.index.get_documents_containing_any(query_terms)
        
        if not doc_ids:
            return []
        
        # Convert to list if it's a set
        if isinstance(doc_ids, set):
            doc_ids = list(doc_ids)
        
        # Cap candidates to prevent excessive computation
        # This implements: "Cap work per query, not data size"
        if len(doc_ids) > max_candidates:
            # Use a simple heuristic: prioritize documents with more query terms
            doc_term_counts = {}
            for doc_id in doc_ids:
                count = sum(1 for term in query_terms 
                          if self.index.get_term_frequency(term, doc_id) > 0)
                doc_term_counts[doc_id] = count
            
            # Sort by term count and take top candidates
            sorted_docs = sorted(doc_term_counts.items(), key=lambda x: x[1], reverse=True)
            doc_ids = [doc_id for doc_id, _ in sorted_docs[:max_candidates]]
            
            logger.info(f"Limited candidate documents from {len(doc_ids)} to {max_candidates} for ranking")
        
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
