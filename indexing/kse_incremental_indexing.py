"""kse_incremental_indexing.py - Incremental Index Updates

Handles incremental index updates:
- Add new pages
- Remove outdated pages
- Update changed pages
- Maintain index consistency
"""

import logging
from typing import Dict, List

from kse.core import get_logger

logger = get_logger('indexing')


class IncrementalIndexing:
    """Handle incremental index updates"""
    
    def __init__(self, inverted_index):
        """Initialize incremental indexing
        
        Args:
            inverted_index: The inverted index to update
        """
        self.index = inverted_index
        logger.debug("IncrementalIndexing initialized")
    
    def add_page(self, page: Dict) -> Dict:
        """Add new page to index
        
        Args:
            page: Processed page data
            
        Returns:
            Update statistics
        """
        stats = {
            'url': page.get('url'),
            'status': 'added',
            'terms_added': 0,
        }
        
        try:
            url = page.get('url')
            tokens = page.get('processed_tokens', [])
            
            # Add page to index
            self.index.add_document(url, tokens)
            stats['terms_added'] = len(tokens)
            
            logger.debug(f"Added page to index: {url}")
            
        except Exception as e:
            logger.error(f"Failed to add page: {e}")
            stats['status'] = 'error'
        
        return stats
    
    def remove_page(self, url: str) -> Dict:
        """Remove page from index
        
        Args:
            url: Page URL to remove
            
        Returns:
            Update statistics
        """
        stats = {
            'url': url,
            'status': 'removed',
            'terms_removed': 0,
        }
        
        try:
            terms_to_remove = []
            
            # Find all terms for this URL
            for term, docs in self.index.index.items():
                if url in docs:
                    docs.discard(url)
                    if len(docs) == 0:
                        terms_to_remove.append(term)
            
            # Remove empty term entries
            for term in terms_to_remove:
                del self.index.index[term]
            
            stats['terms_removed'] = len(terms_to_remove)
            logger.debug(f"Removed page from index: {url}")
            
        except Exception as e:
            logger.error(f"Failed to remove page: {e}")
            stats['status'] = 'error'
        
        return stats
    
    def batch_add_pages(self, pages: List[Dict]) -> Dict:
        """Add multiple pages to index
        
        Args:
            pages: List of processed pages
            
        Returns:
            Batch update statistics
        """
        stats = {
            'total': len(pages),
            'added': 0,
            'failed': 0,
        }
        
        for page in pages:
            result = self.add_page(page)
            if result['status'] == 'added':
                stats['added'] += 1
            else:
                stats['failed'] += 1
        
        return stats


__all__ = ["IncrementalIndexing"]
