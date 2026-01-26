"""kse_inverted_index.py - Inverted Index Data Structure

Implements inverted index for fast term lookups:
- term → [list of pages containing term]
- Supports compression and persistence
"""

import logging
from typing import Dict, List, Set
from collections import defaultdict
import pickle

from kse.core import get_logger

logger = get_logger('indexing')


class InvertedIndex:
    """Inverted index data structure"""
    
    def __init__(self):
        """Initialize inverted index"""
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.doc_count = 0
        logger.debug("InvertedIndex initialized")
    
    def add_term(self, term: str, document_id: str) -> None:
        """Add term to index for document
        
        Args:
            term: Term/token
            document_id: Document URL
        """
        self.index[term].add(document_id)
    
    def add_document(self, document_id: str, terms: List[str]) -> None:
        """Add document with terms to index
        
        Args:
            document_id: Document URL
            terms: List of terms in document
        """
        for term in terms:
            self.add_term(term, document_id)
        self.doc_count += 1
    
    def get_documents(self, term: str) -> Set[str]:
        """Get all documents containing term
        
        Args:
            term: Search term
            
        Returns:
            Set of document IDs
        """
        return self.index.get(term, set())
    
    def search(self, terms: List[str]) -> Set[str]:
        """Search for documents containing ALL terms
        
        Args:
            terms: List of search terms
            
        Returns:
            Set of matching document IDs
        """
        if not terms:
            return set()
        
        # Get documents for first term
        result = self.get_documents(terms[0])
        
        # Intersect with other terms
        for term in terms[1:]:
            result = result.intersection(self.get_documents(term))
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get index statistics"""
        return {
            'unique_terms': len(self.index),
            'total_documents': self.doc_count,
            'avg_docs_per_term': len(self.index) / max(self.doc_count, 1),
        }
    
    def save(self, filepath: str) -> None:
        """Save index to file
        
        Args:
            filepath: File path for saving
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(dict(self.index), f)
            logger.info(f"Index saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def load(self, filepath: str) -> None:
        """Load index from file
        
        Args:
            filepath: File path to load from
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            self.index = defaultdict(set)
            for term, docs in data.items():
                self.index[term] = set(docs)
            logger.info(f"Index loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise


__all__ = ["InvertedIndex"]
