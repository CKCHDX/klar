"""kse_index_statistics.py - Index Statistics and Monitoring

Tracks and reports indexing statistics:
- Index size metrics
- Term distribution
- Document statistics
- Performance metrics
"""

import logging
from typing import Dict

from kse.core import get_logger

logger = get_logger('indexing')


class IndexStatistics:
    """Track index statistics"""
    
    def __init__(self):
        """Initialize statistics tracker"""
        self.stats = {
            'total_documents': 0,
            'total_unique_terms': 0,
            'index_size_mb': 0,
            'average_terms_per_doc': 0,
            'build_time_seconds': 0,
        }
        logger.debug("IndexStatistics initialized")
    
    def calculate_statistics(self, inverted_index: Dict, pages: int, build_time: float) -> Dict:
        """Calculate index statistics
        
        Args:
            inverted_index: The inverted index
            pages: Number of indexed pages
            build_time: Time to build index
            
        Returns:
            Statistics dictionary
        """
        unique_terms = len(inverted_index)
        total_postings = sum(len(docs) for docs in inverted_index.values())
        
        self.stats['total_documents'] = pages
        self.stats['total_unique_terms'] = unique_terms
        self.stats['average_terms_per_doc'] = total_postings / max(pages, 1)
        self.stats['build_time_seconds'] = build_time
        
        # Estimate index size in MB (rough estimate)
        estimated_size = (unique_terms * 50 + total_postings * 20) / (1024 * 1024)
        self.stats['index_size_mb'] = estimated_size
        
        return self.stats
    
    def get_statistics(self) -> Dict:
        """Get current statistics
        
        Returns:
            Statistics dictionary
        """
        return self.stats.copy()
    
    def get_summary(self) -> str:
        """Get statistics summary
        
        Returns:
            Formatted summary string
        """
        s = self.stats
        return f"""
Index Statistics:
├─ Total Documents: {s['total_documents']:,}
├─ Unique Terms: {s['total_unique_terms']:,}
├─ Avg Terms/Doc: {s['average_terms_per_doc']:.2f}
├─ Index Size: {s['index_size_mb']:.2f} MB
└─ Build Time: {s['build_time_seconds']:.2f}s
""".strip()


__all__ = ["IndexStatistics"]
