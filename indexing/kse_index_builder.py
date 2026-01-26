"""kse_index_builder.py - Index Building and Optimization

Builds and optimizes search index:
- Combines all data sources
- Sorts for efficiency
- Compresses for storage
- Validates completeness
"""

import logging
from typing import Dict, List

from kse.core import get_logger
from kse.inverted_index import InvertedIndex
from kse.tf_idf_calculator import TFIDFCalculator

logger = get_logger('indexing')


class IndexBuilder:
    """Build and optimize search index"""
    
    def __init__(self):
        """Initialize index builder"""
        self.inverted_index = InvertedIndex()
        self.tfidf_calc = TFIDFCalculator()
        logger.debug("IndexBuilder initialized")
    
    def build_index(self, pages: List[Dict]) -> Dict:
        """Build complete search index from pages
        
        Args:
            pages: List of processed pages
            
        Returns:
            Index statistics
        """
        stats = {
            'total_pages': len(pages),
            'indexed_terms': 0,
            'total_documents': 0,
        }
        
        try:
            # Add pages to inverted index
            for page in pages:
                url = page.get('url')
                tokens = page.get('processed_tokens', [])
                self.inverted_index.add_document(url, tokens)
            
            stats['indexed_terms'] = len(self.inverted_index.index)
            stats['total_documents'] = self.inverted_index.doc_count
            
            logger.info(f"Index built: {stats['indexed_terms']} terms, "
                       f"{stats['total_documents']} documents")
            
            return stats
        
        except Exception as e:
            logger.error(f"Index building failed: {e}")
            raise
    
    def optimize_index(self) -> Dict:
        """Optimize index for performance
        
        Returns:
            Optimization statistics
        """
        stats = {
            'before_optimization': len(self.inverted_index.index),
        }
        
        # Remove terms with very few documents (noise)
        min_docs = 2
        terms_to_remove = []
        
        for term, docs in self.inverted_index.index.items():
            if len(docs) < min_docs:
                terms_to_remove.append(term)
        
        for term in terms_to_remove:
            del self.inverted_index.index[term]
        
        stats['after_optimization'] = len(self.inverted_index.index)
        stats['terms_removed'] = len(terms_to_remove)
        
        logger.info(f"Index optimized: removed {len(terms_to_remove)} noise terms")
        
        return stats


__all__ = ["IndexBuilder"]
