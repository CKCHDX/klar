"""
KSE Indexer

Builds and maintains inverted indexes for full-text search.
"""

from typing import Dict, List, Set, Tuple
import math
import logging

from kse.core import KSELogger
from .kse_tokenizer import Tokenizer

logger = KSELogger.get_logger(__name__)


class DocumentFrequency:
    """Stores frequency information for a term in a document."""
    
    def __init__(self, doc_id: int, term_freq: int, positions: List[int] = None):
        """
        Initialize document frequency.
        
        Args:
            doc_id: Document ID
            term_freq: Frequency of term in document
            positions: Positions where term appears
        """
        self.doc_id = doc_id
        self.term_freq = term_freq
        self.positions = positions or []
    
    def __repr__(self):
        return f"DocFreq(doc={self.doc_id}, freq={self.term_freq}, pos={len(self.positions)})"


class InvertedIndexEntry:
    """Entry in the inverted index for a single term."""
    
    def __init__(self, term: str):
        """
        Initialize index entry.
        
        Args:
            term: The term/token
        """
        self.term = term
        self.postings: Dict[int, DocumentFrequency] = {}  # doc_id -> DocumentFrequency
        self.document_frequency = 0  # Number of documents containing term
    
    def add_occurrence(self, doc_id: int, term_freq: int, positions: List[int] = None):
        """
        Add document occurrence of term.
        
        Args:
            doc_id: Document ID
            term_freq: Frequency in document
            positions: Positions of occurrences
        """
        if doc_id not in self.postings:
            self.document_frequency += 1
        
        self.postings[doc_id] = DocumentFrequency(doc_id, term_freq, positions or [])
    
    def get_postings(self) -> List[DocumentFrequency]:
        """Get all postings for this term."""
        return list(self.postings.values())
    
    def __repr__(self):
        return f"IndexEntry(term='{self.term}', docs={self.document_frequency})"


class KSEIndexer:
    """Builds inverted indexes for search."""
    
    def __init__(self, db_connection):
        """
        Initialize indexer.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        self.tokenizer = Tokenizer(remove_stopwords=True, use_stemming=True)
        self.inverted_index: Dict[str, InvertedIndexEntry] = {}
        self.document_lengths = {}  # doc_id -> number of tokens
        self.total_documents = 0
        logger.info("KSEIndexer initialized")
    
    def index_page(self, page_id: int, title: str, description: str, content: str) -> int:
        """
        Index a page for search.
        
        Args:
            page_id: Page ID from database
            title: Page title (higher weight)
            description: Page description (medium weight)
            content: Page content (normal weight)
            
        Returns:
            Number of unique terms indexed
        """
        unique_terms = set()
        
        # Title tokens (weight: 3x)
        title_tokens = self.tokenizer.tokenize(title or "")
        for token in title_tokens:
            unique_terms.add(token)
            self._add_to_index(token, page_id, 3)  # 3x weight
        
        # Description tokens (weight: 2x)
        desc_tokens = self.tokenizer.tokenize(description or "")
        for token in desc_tokens:
            unique_terms.add(token)
            self._add_to_index(token, page_id, 2)  # 2x weight
        
        # Content tokens (weight: 1x)
        content_tokens = self.tokenizer.tokenize(content or "")
        for token in content_tokens:
            unique_terms.add(token)
            self._add_to_index(token, page_id, 1)  # 1x weight
        
        # Store document length
        total_tokens = len(title_tokens) * 3 + len(desc_tokens) * 2 + len(content_tokens)
        self.document_lengths[page_id] = total_tokens
        
        return len(unique_terms)
    
    def _add_to_index(self, term: str, doc_id: int, weight: float = 1.0):
        """
        Add term occurrence to index.
        
        Args:
            term: Term to add
            doc_id: Document ID
            weight: Weight multiplier for this occurrence
        """
        if term not in self.inverted_index:
            self.inverted_index[term] = InvertedIndexEntry(term)
        
        entry = self.inverted_index[term]
        
        if doc_id in entry.postings:
            # Update existing
            entry.postings[doc_id].term_freq += weight
        else:
            # New document
            entry.add_occurrence(doc_id, weight, [])
    
    def build_from_database(self, limit: int = None) -> Dict[str, int]:
        """
        Build index from all pages in database.
        
        Args:
            limit: Maximum pages to index (None for all)
            
        Returns:
            Statistics dict with counts
        """
        stats = {
            'pages_indexed': 0,
            'terms_indexed': 0,
            'total_occurrences': 0,
        }
        
        try:
            # Get all pages from database
            query = "SELECT id, title, description, content FROM pages"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = self.db.get_connection().cursor()
            cursor.execute(query)
            
            for page_id, title, description, content in cursor.fetchall():
                unique_terms = self.index_page(page_id, title, description, content)
                stats['pages_indexed'] += 1
                
                if stats['pages_indexed'] % 1000 == 0:
                    logger.info(f"Indexed {stats['pages_indexed']} pages...")
            
            cursor.close()
            
            stats['terms_indexed'] = len(self.inverted_index)
            stats['total_occurrences'] = sum(
                sum(entry.postings[did].term_freq for did in entry.postings)
                for entry in self.inverted_index.values()
            )
            self.total_documents = stats['pages_indexed']
            
            logger.info(f"Index built: {stats['pages_indexed']} pages, "
                       f"{stats['terms_indexed']} terms, "
                       f"{stats['total_occurrences']} occurrences")
        
        except Exception as e:
            logger.error(f"Error building index: {e}")
            raise
        
        return stats
    
    def get_postings(self, term: str) -> List[DocumentFrequency]:
        """
        Get all documents containing a term.
        
        Args:
            term: Term to search
            
        Returns:
            List of DocumentFrequency objects
        """
        if term not in self.inverted_index:
            return []
        
        return self.inverted_index[term].get_postings()
    
    def get_idf(self, term: str) -> float:
        """
        Calculate IDF (Inverse Document Frequency) for term.
        
        Args:
            term: Term to calculate IDF for
            
        Returns:
            IDF value
        """
        if term not in self.inverted_index or self.total_documents == 0:
            return 0.0
        
        doc_freq = self.inverted_index[term].document_frequency
        return math.log(self.total_documents / doc_freq) if doc_freq > 0 else 0.0
    
    def search_term(self, term: str) -> List[Tuple[int, float]]:
        """
        Search for a single term.
        
        Args:
            term: Term to search
            
        Returns:
            List of (doc_id, tfidf_score) tuples
        """
        postings = self.get_postings(term)
        if not postings:
            return []
        
        idf = self.get_idf(term)
        results = []
        
        for posting in postings:
            # TF-IDF = (term_freq / doc_length) * IDF
            doc_length = self.document_lengths.get(posting.doc_id, 1)
            tf = posting.term_freq / max(doc_length, 1)
            tfidf = tf * idf
            results.append((posting.doc_id, tfidf))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def save_to_database(self):
        """
        Save inverted index to database.
        """
        try:
            cursor = self.db.get_connection().cursor()
            
            # Clear existing index
            cursor.execute("TRUNCATE TABLE inverted_index")
            
            # Insert new entries
            for term, entry in self.inverted_index.items():
                for posting in entry.get_postings():
                    cursor.execute(
                        "INSERT INTO inverted_index (term, page_id, frequency) VALUES (%s, %s, %s)",
                        (term, posting.doc_id, posting.term_freq)
                    )
            
            self.db.get_connection().commit()
            cursor.close()
            logger.info(f"Saved {len(self.inverted_index)} terms to database")
        
        except Exception as e:
            logger.error(f"Error saving index to database: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """
        Get indexing statistics.
        
        Returns:
            Statistics dictionary
        """
        total_postings = sum(
            len(entry.postings) for entry in self.inverted_index.values()
        )
        
        return {
            'total_terms': len(self.inverted_index),
            'total_documents': self.total_documents,
            'total_postings': total_postings,
            'avg_postings_per_term': total_postings / max(len(self.inverted_index), 1),
            'memory_usage_mb': sum(
                len(entry.term) + len(entry.postings) * 16
                for entry in self.inverted_index.values()
            ) / 1024 / 1024,
        }
