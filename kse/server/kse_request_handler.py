"""kse_request_handler.py - HTTP Request Handling

Processes HTTP requests:
- Parameter extraction
- Input validation
- Error handling
"""

import logging
from typing import Dict, Tuple

from kse.core import get_logger

logger = get_logger('server')


class RequestHandler:
    """Handle HTTP requests"""
    
    def __init__(self):
        """Initialize request handler"""
        logger.debug("RequestHandler initialized")
    
    def validate_search_params(self, params: Dict) -> Tuple[bool, str, Dict]:
        """Validate search request parameters
        
        Args:
            params: Request parameters
            
        Returns:
            (valid, error_message, validated_params)
        """
        validated = {
            'query': params.get('q', '').strip(),
            'limit': 10,
            'page': 1,
        }
        
        # Validate query
        if not validated['query']:
            return False, "Missing query parameter 'q'", {}
        
        if len(validated['query']) > 500:
            return False, "Query too long (max 500 chars)", {}
        
        if len(validated['query']) < 2:
            return False, "Query too short (min 2 chars)", {}
        
        # Validate limit
        try:
            limit = int(params.get('limit', 10))
            if limit < 1 or limit > 100:
                return False, "Limit must be 1-100", {}
            validated['limit'] = limit
        except ValueError:
            return False, "Invalid limit parameter", {}
        
        # Validate page
        try:
            page = int(params.get('page', 1))
            if page < 1:
                return False, "Page must be >= 1", {}
            validated['page'] = page
        except ValueError:
            return False, "Invalid page parameter", {}
        
        return True, "", validated
    
    def extract_headers(self, headers: Dict) -> Dict:
        """Extract relevant headers
        
        Args:
            headers: HTTP headers
            
        Returns:
            Extracted headers
        """
        return {
            'api_key': headers.get('X-API-Key', ''),
            'client_ip': headers.get('X-Forwarded-For', headers.get('Remote-Addr', 'unknown')),
            'user_agent': headers.get('User-Agent', 'unknown'),
        }


__all__ = ["RequestHandler"]
