"""
TF-IDF (Term Frequency-Inverse Document Frequency)

Computes relevance scores for keywords across the corpus.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import math

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


@dataclass
class TFIDFScore:
    """TF-IDF score for a term."""
    term: str
    tf: float  # Term Frequency
    idf: float  # Inverse Document Frequency
    tfidf: float  # Combined score
    document_frequency: int = 0  # How many documents contain this term
    total_documents: int = 0
    
    @property
    def is_significant(self) -> bool:
        """Check if term is significant (TF-IDF > 0.1)."""
        return self.tfidf > 0.1


class TFIDFComputer:
    """
    TF-IDF computation engine.
    
    Formulas:
    - TF = (term_count / total_terms_in_doc)
    - IDF = log(total_documents / documents_containing_term)
    - TF-IDF = TF * IDF
    """
    
    def __init__(
        self,
        min_df: int = 1,
        max_df_ratio: float = 0.9,
        use_log: bool = True,
    ):
        """
        Initialize TF-IDF computer.
        
        Args:
            min_df: Minimum document frequency (filter rare terms)
            max_df_ratio: Maximum ratio for document frequency (filter common terms)
            use_log: Use logarithmic IDF (standard)
        """
        self.min_df = min_df
        self.max_df_ratio = max_df_ratio
        self.use_log = use_log
        
        self.document_frequency = defaultdict(int)  # How many docs have this term
        self.total_documents = 0
    
    def add_document(self, terms: List[str]) -> None:
        """
        Add document to corpus for IDF computation.
        
        Args:
            terms: List of terms in document
        """
        unique_terms = set(terms)
        
        for term in unique_terms:
            self.document_frequency[term] += 1
        
        self.total_documents += 1
    
    def add_documents(self, documents: List[List[str]]) -> None:
        """
        Add multiple documents to corpus.
        
        Args:
            documents: List of document term lists
        """
        for doc_terms in documents:
            self.add_document(doc_terms)
    
    def compute_tf(self, term: str, document_terms: List[str]) -> float:
        """
        Compute Term Frequency for a term in a document.
        
        Args:
            term: Term to compute TF for
            document_terms: All terms in document
        
        Returns:
            TF score (0-1)
        """
        if not document_terms:
            return 0.0
        
        term_count = document_terms.count(term)
        total_terms = len(document_terms)
        
        return term_count / total_terms
    
    def compute_idf(self, term: str) -> float:
        """
        Compute Inverse Document Frequency for a term.
        
        Args:
            term: Term to compute IDF for
        
        Returns:
            IDF score
        """
        if self.total_documents == 0:
            return 0.0
        
        doc_freq = self.document_frequency.get(term, 0)
        
        # Handle edge cases
        if doc_freq == 0:
            # Term not in any document
            if self.use_log:
                return math.log(self.total_documents)
            else:
                return self.total_documents
        
        # Standard IDF formula
        if self.use_log:
            return math.log(self.total_documents / doc_freq)
        else:
            return self.total_documents / doc_freq
    
    def compute_tfidf(self, term: str, document_terms: List[str]) -> TFIDFScore:
        """
        Compute complete TF-IDF score.
        
        Args:
            term: Term to compute TF-IDF for
            document_terms: All terms in document
        
        Returns:
            TFIDFScore object
        """
        tf = self.compute_tf(term, document_terms)
        idf = self.compute_idf(term)
        tfidf = tf * idf
        
        return TFIDFScore(
            term=term,
            tf=tf,
            idf=idf,
            tfidf=tfidf,
            document_frequency=self.document_frequency.get(term, 0),
            total_documents=self.total_documents,
        )
    
    def compute_document_scores(
        self,
        document_terms: List[str],
        top_n: Optional[int] = None,
    ) -> List[TFIDFScore]:
        """
        Compute TF-IDF scores for all terms in a document.
        
        Args:
            document_terms: List of terms in document
            top_n: Return only top N scores
        
        Returns:
            List of TFIDFScore objects sorted by score
        """
        # Get unique terms
        unique_terms = set(document_terms)
        
        scores = []
        for term in unique_terms:
            score = self.compute_tfidf(term, document_terms)
            
            # Filter by document frequency
            doc_freq = self.document_frequency.get(term, 0)
            
            if doc_freq < self.min_df:
                continue  # Too rare
            
            if self.max_df_ratio > 0:
                df_ratio = doc_freq / self.total_documents
                if df_ratio > self.max_df_ratio:
                    continue  # Too common
            
            scores.append(score)
        
        # Sort by TF-IDF score
        scores.sort(key=lambda s: s.tfidf, reverse=True)
        
        return scores[:top_n] if top_n else scores
    
    def get_important_terms(
        self,
        document_terms: List[str],
        threshold: float = 0.1,
    ) -> List[str]:
        """
        Get important terms (TF-IDF > threshold).
        
        Args:
            document_terms: List of terms in document
            threshold: Minimum TF-IDF score
        
        Returns:
            List of important terms
        """
        scores = self.compute_document_scores(document_terms)
        return [s.term for s in scores if s.tfidf > threshold]
    
    def compute_corpus_stats(self) -> Dict:
        """
        Get corpus statistics.
        
        Returns:
            Dictionary with corpus info
        """
        if not self.document_frequency:
            return {
                'total_documents': 0,
                'unique_terms': 0,
                'avg_df': 0,
                'max_df': 0,
                'min_df': 0,
            }
        
        df_values = list(self.document_frequency.values())
        
        return {
            'total_documents': self.total_documents,
            'unique_terms': len(self.document_frequency),
            'avg_df': sum(df_values) / len(df_values),
            'max_df': max(df_values),
            'min_df': min(df_values),
            'top_terms': sorted(
                self.document_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
        }
    
    def reset(self) -> None:
        """
        Reset corpus data."""
        self.document_frequency.clear()
        self.total_documents = 0
