"""kse_crawler_resilience.py - Error Recovery and Retry Logic"""

import logging
import time
from typing import Callable, Optional, Any

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class CrawlerResilience:
    """Handle errors and recovery"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._error_count = 0
        logger.debug(f"CrawlerResilience initialized (retries={max_retries})")
    
    def retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute function with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._error_count += 1
                if attempt < self.max_retries:
                    wait = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1} after {wait}s: {e}")
                    time.sleep(wait)
                else:
                    logger.error(f"Failed after {self.max_retries + 1} attempts: {e}")
                    return None
    
    def get_error_count(self) -> int:
        """Get error count"""
        return self._error_count


__all__ = ["CrawlerResilience"]
