"""kse_rate_limiter.py - Rate Limiting

Implements rate limiting for API:
- Per-client limits
- Time-window based
- Request tracking
"""

import logging
from typing import Dict
from collections import defaultdict
import time

from kse.core import get_logger

logger = get_logger('server')


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, requests_per_hour: int = 1000):
        """Initialize rate limiter
        
        Args:
            requests_per_hour: Max requests per hour per client
        """
        self.limit = requests_per_hour
        self.requests: Dict = defaultdict(list)
        logger.debug("RateLimiter initialized")
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        hour_ago = now - 3600
        
        # Clean old requests
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if ts > hour_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.limit:
            logger.warning(f"Rate limit exceeded for: {client_id}")
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        hour_ago = now - 3600
        
        recent = [ts for ts in self.requests[client_id] if ts > hour_ago]
        return max(0, self.limit - len(recent))
    
    def get_reset_time(self, client_id: str) -> float:
        """Get when limit resets
        
        Args:
            client_id: Client identifier
            
        Returns:
            Unix timestamp of reset time
        """
        if not self.requests[client_id]:
            return time.time()
        
        oldest = min(self.requests[client_id])
        return oldest + 3600


__all__ = ["RateLimiter"]
