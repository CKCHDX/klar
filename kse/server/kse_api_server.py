"""kse_api_server.py - Main API Server

Handles HTTP requests and coordinates the search pipeline:
- Flask/FastAPI setup
- Route handling
- Request validation
- Response formatting
"""

import logging
from typing import Dict
import time

from kse.core import get_logger, KSEException

logger = get_logger('server')


class APIServer:
    """Main API server"""
    
    def __init__(self,
                 search_engine,
                 auth_manager=None,
                 rate_limiter=None):
        """Initialize API server
        
        Args:
            search_engine: SearchCore instance
            auth_manager: Authentication manager
            rate_limiter: Rate limiter
        """
        self.search = search_engine
        self.auth = auth_manager
        self.rate_limiter = rate_limiter
        
        logger.info("APIServer initialized")
    
    def handle_search_request(self, query: str, **kwargs) -> Dict:
        """Handle search API request
        
        Args:
            query: Search query string
            **kwargs: Additional parameters (limit, page, etc.)
            
        Returns:
            API response
        """
        try:
            start_time = time.time()
            
            # Extract parameters
            limit = kwargs.get('limit', 10)
            page = kwargs.get('page', 1)
            
            # Validate query
            if not query or len(query.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Empty query',
                    'code': 400,
                }
            
            # Check rate limiting
            if self.rate_limiter:
                if not self.rate_limiter.is_allowed(kwargs.get('client_ip', 'unknown')):
                    return {
                        'success': False,
                        'error': 'Rate limit exceeded',
                        'code': 429,
                    }
            
            # Execute search
            results = self.search.search(query, limit=limit)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Format response
            return {
                'success': True,
                'query': query,
                'total_results': results['total_results'],
                'results': results['results'],
                'execution_time': round(execution_time, 3),
                'cached': execution_time < 0.01,
            }
        
        except Exception as e:
            logger.error(f"Search request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 500,
            }
    
    def handle_health_check(self) -> Dict:
        """Handle health check request
        
        Returns:
            Health status
        """
        return {
            'status': 'healthy',
            'service': 'kse-search-api',
            'version': '1.0.0',
        }


__all__ = ["APIServer"]
