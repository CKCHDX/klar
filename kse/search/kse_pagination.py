"""kse_pagination.py - Result Pagination

Handles pagination of search results:
- Page calculation
- Result limiting
- Offset management
"""

import logging
from typing import Dict, List, Tuple

from kse.core import get_logger

logger = get_logger('search')


class Pagination:
    """Handle pagination of search results"""
    
    def __init__(self, default_page_size: int = 10):
        """Initialize pagination
        
        Args:
            default_page_size: Results per page
        """
        self.default_page_size = default_page_size
        logger.debug("Pagination initialized")
    
    def paginate(self,
                results: List[Tuple[str, float]],
                page: int = 1,
                page_size: int = None) -> Dict:
        """Paginate search results
        
        Args:
            results: List of (url, score) tuples
            page: Page number (1-based)
            page_size: Results per page
            
        Returns:
            Paginated results
        """
        if page_size is None:
            page_size = self.default_page_size
        
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size
        
        # Validate page
        page = max(1, min(page, total_pages))
        
        # Calculate offsets
        offset = (page - 1) * page_size
        end_offset = offset + page_size
        
        # Get page results
        page_results = results[offset:end_offset]
        
        return {
            'results': page_results,
            'page': page,
            'page_size': page_size,
            'total_results': total_results,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'offset': offset,
        }
    
    def get_page(self,
                results: List[Tuple[str, float]],
                page: int = 1,
                page_size: int = None) -> List[Tuple[str, float]]:
        """Get specific page of results
        
        Args:
            results: All results
            page: Page number
            page_size: Results per page
            
        Returns:
            Results for page
        """
        if page_size is None:
            page_size = self.default_page_size
        
        offset = max(0, (page - 1) * page_size)
        end_offset = offset + page_size
        
        return results[offset:end_offset]


__all__ = ["Pagination"]
