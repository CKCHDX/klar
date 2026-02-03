"""
KSE Inverted Index - Inverted index structure for search
"""
from typing import Dict, List, Set
from collections import defaultdict
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class InvertedIndex:
    """Inverted index: term -> list of documents containing that term"""
    
    def __init__(self):
        """Initialize inverted index"""
        # Term -> {doc_id: [positions]}
        self.index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        
        # Document metadata: doc_id -> metadata
        self.documents: Dict[str, Dict] = {}
        
        # Statistics
        self.total_documents = 0
        self.total_terms = 0
    
    def add_document(self, doc_id: str, tokens: List[str], metadata: Dict = None) -> None:
        """
        Add document to index
        
        Args:
            doc_id: Document identifier (URL)
            tokens: List of tokens from document
            metadata: Document metadata
        """
        # Store metadata
        self.documents[doc_id] = metadata or {}
        
        # Index tokens with positions
        for position, token in enumerate(tokens):
            if token:  # Skip empty tokens
                self.index[token][doc_id].append(position)
        
        self.total_documents += 1
        logger.debug(f"Added document {doc_id} with {len(tokens)} tokens")
    
    def search(self, term: str) -> Dict[str, List[int]]:
        """
        Search for term in index
        
        Args:
            term: Search term
        
        Returns:
            Dictionary of {doc_id: [positions]}
        """
        return dict(self.index.get(term.lower(), {}))
    
    def search_multiple(self, terms: List[str]) -> Dict[str, Set[str]]:
        """
        Search for multiple terms
        
        Args:
            terms: List of search terms
        
        Returns:
            Dictionary of {term: set(doc_ids)}
        """
        results = {}
        for term in terms:
            docs = set(self.index.get(term.lower(), {}).keys())
            if docs:
                results[term] = docs
        return results
    
    def get_document_frequency(self, term: str) -> int:
        """
        Get document frequency of term (how many documents contain it)
        
        Args:
            term: Term to check
        
        Returns:
            Number of documents containing term
        """
        return len(self.index.get(term.lower(), {}))
    
    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """
        Get term frequency in document
        
        Args:
            term: Term to check
            doc_id: Document ID
        
        Returns:
            Number of times term appears in document
        """
        return len(self.index.get(term.lower(), {}).get(doc_id, []))
    
    def get_document_terms(self, doc_id: str) -> Set[str]:
        """
        Get all terms in a document
        
        Args:
            doc_id: Document ID
        
        Returns:
            Set of terms in document
        """
        terms = set()
        for term, docs in self.index.items():
            if doc_id in docs:
                terms.add(term)
        return terms
    
    def get_document_length(self, doc_id: str) -> int:
        """
        Get document length (number of terms)
        
        Args:
            doc_id: Document ID
        
        Returns:
            Number of terms in document
        """
        length = 0
        for term, docs in self.index.items():
            if doc_id in docs:
                length += len(docs[doc_id])
        return length
    
    def get_all_terms(self) -> List[str]:
        """
        Get all terms in index
        
        Returns:
            List of all unique terms
        """
        return list(self.index.keys())
    
    def get_documents_containing_all(self, terms: List[str]) -> Set[str]:
        """
        Get documents containing all terms (AND search)
        
        Args:
            terms: List of terms
        
        Returns:
            Set of document IDs containing all terms
        """
        if not terms:
            return set()
        
        # Start with documents containing first term
        result = set(self.index.get(terms[0].lower(), {}).keys())
        
        # Intersect with documents containing other terms
        for term in terms[1:]:
            docs = set(self.index.get(term.lower(), {}).keys())
            result &= docs
        
        return result
    
    def get_documents_containing_any(self, terms: List[str]) -> Set[str]:
        """
        Get documents containing any term (OR search)
        
        Args:
            terms: List of terms
        
        Returns:
            Set of document IDs containing any term
        """
        result = set()
        for term in terms:
            docs = set(self.index.get(term.lower(), {}).keys())
            result |= docs
        return result
    
    def get_statistics(self) -> Dict:
        """
        Get index statistics
        
        Returns:
            Dictionary with statistics
        """
        total_postings = sum(len(docs) for docs in self.index.values())
        avg_terms = total_postings / max(self.total_documents, 1)
        
        return {
            "total_documents": self.total_documents,
            "total_terms": len(self.index),
            "total_postings": total_postings,
            "average_terms_per_document": round(avg_terms, 2),
            "index_size_bytes": self._estimate_size(),
            "index_size_mb": round(self._estimate_size() / (1024 * 1024), 2)
        }
    
    def _estimate_size(self) -> int:
        """
        Estimate memory size of index
        
        Note: This is an approximation and may not account for all Python overhead
        """
        import sys
        
        # Calculate actual size including nested structures
        size = sys.getsizeof(self.index)
        
        # Add size of nested dicts and lists
        for term, docs in self.index.items():
            size += sys.getsizeof(term)
            size += sys.getsizeof(docs)
            for doc_id, positions in docs.items():
                size += sys.getsizeof(doc_id)
                size += sys.getsizeof(positions)
        
        # Add documents metadata size
        size += sys.getsizeof(self.documents)
        for doc_id, metadata in self.documents.items():
            size += sys.getsizeof(doc_id)
            size += sys.getsizeof(metadata)
            for key, value in metadata.items():
                size += sys.getsizeof(key) + sys.getsizeof(value)
        
        return size
    
    def clear(self) -> None:
        """Clear the index"""
        self.index.clear()
        self.documents.clear()
        self.total_documents = 0
        self.total_terms = 0
        logger.info("Index cleared")
