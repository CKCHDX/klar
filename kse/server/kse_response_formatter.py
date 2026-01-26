"""kse_response_formatter.py - API Response Formatting

Formats API responses:
- JSON serialization
- Status codes
- Error messages
- Metadata
"""

import logging
from typing import Dict, Any
import json

from kse.core import get_logger

logger = get_logger('server')


class ResponseFormatter:
    """Format API responses"""
    
    def __init__(self):
        """Initialize response formatter"""
        logger.debug("ResponseFormatter initialized")
    
    def success_response(self, 
                        data: Dict,
                        status_code: int = 200,
                        headers: Dict = None) -> Tuple[Dict, int]:
        """Format success response
        
        Args:
            data: Response data
            status_code: HTTP status code
            headers: Response headers
            
        Returns:
            (response_dict, status_code)
        """
        response = {
            'success': True,
            'data': data,
            'timestamp': self._get_timestamp(),
        }
        
        if headers is None:
            headers = {}
        
        headers['Content-Type'] = 'application/json'
        
        return response, status_code, headers
    
    def error_response(self,
                      error: str,
                      code: str,
                      status_code: int = 400,
                      details: Dict = None) -> Tuple[Dict, int]:
        """Format error response
        
        Args:
            error: Error message
            code: Error code
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            (response_dict, status_code)
        """
        response = {
            'success': False,
            'error': error,
            'error_code': code,
            'timestamp': self._get_timestamp(),
        }
        
        if details:
            response['details'] = details
        
        headers = {'Content-Type': 'application/json'}
        
        return response, status_code, headers
    
    def format_search_results(self, results: Dict) -> Dict:
        """Format search results
        
        Args:
            results: Raw search results
            
        Returns:
            Formatted results
        """
        return {
            'query': results.get('query'),
            'total_results': results.get('total_results'),
            'results': [
                {
                    'rank': r.get('rank'),
                    'url': r.get('url'),
                    'title': r.get('title'),
                    'score': r.get('score'),
                    'snippet': r.get('snippet', ''),
                }
                for r in results.get('results', [])
            ],
            'execution_time_ms': round(results.get('execution_time', 0) * 1000, 1),
            'cached': results.get('cached', False),
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


__all__ = ["ResponseFormatter"]
