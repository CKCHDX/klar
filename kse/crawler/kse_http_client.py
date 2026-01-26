"""
kse_http_client.py - HTTP Client with Retry Logic

Handles HTTP requests with automatic retries, timeout handling,
and user-agent rotation for web crawling.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import time
import hashlib

from kse.core import get_logger, KSEException, USER_AGENT, TIMEOUT, MAX_RETRIES

logger = get_logger('crawler')


class KSEHTTPException(KSEException):
    """HTTP client exception"""
    pass


class HTTPClient:
    """
    HTTP client with retry logic.
    
    Features:
    - Automatic retries on failure
    - Exponential backoff
    - Timeout handling
    - User-agent spoofing
    - Request rate limiting
    """
    
    # User-agent list for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6) AppleWebKit/605.1.15',
    ]
    
    def __init__(
        self,
        timeout: int = TIMEOUT,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._ua_index = 0
        self._last_request = None
        
        logger.debug(f"HTTPClient initialized: timeout={timeout}s, retries={max_retries}")
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Optional[bytes], int, Dict]:
        """
        Make GET request with retries.
        
        Args:
            url: URL to fetch
            headers: Optional request headers
            
        Returns:
            (content, status_code, response_headers) or (None, error_code, {})
        """
        try:
            import requests
        except ImportError:
            raise KSEHTTPException("requests library required")
        
        # Prepare headers
        req_headers = headers or {}
        req_headers['User-Agent'] = self._get_user_agent()
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Rate limiting
                if self._last_request:
                    elapsed = (datetime.now() - self._last_request).total_seconds()
                    if elapsed < 1:  # Min 1 second between requests
                        time.sleep(1 - elapsed)
                
                self._last_request = datetime.now()
                
                # Make request
                response = requests.get(
                    url,
                    headers=req_headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=True,
                )
                
                logger.debug(f"HTTP GET success: {url} (status={response.status_code})")
                
                return (
                    response.content,
                    response.status_code,
                    dict(response.headers),
                )
                
            except requests.Timeout:
                last_exception = KSEHTTPException(f"Request timeout: {url}")
                logger.warning(f"Timeout (attempt {attempt + 1}): {url}")
                
            except requests.ConnectionError as e:
                last_exception = KSEHTTPException(f"Connection error: {e}")
                logger.warning(f"Connection error (attempt {attempt + 1}): {url}")
                
            except requests.RequestException as e:
                last_exception = KSEHTTPException(f"Request failed: {e}")
                logger.warning(f"Request error (attempt {attempt + 1}): {url}")
                
            except Exception as e:
                last_exception = KSEHTTPException(f"Unexpected error: {e}")
                logger.error(f"Unexpected error (attempt {attempt + 1}): {url}")
            
            # Exponential backoff
            if attempt < self.max_retries:
                wait_time = self.backoff_factor * (2 ** attempt)
                logger.debug(f"Retrying after {wait_time}s...")
                time.sleep(wait_time)
        
        logger.error(f"Failed after {self.max_retries + 1} attempts: {url}")
        raise last_exception or KSEHTTPException(f"Failed to fetch: {url}")
    
    def head(self, url: str) -> Tuple[int, Dict]:
        """
        Make HEAD request.
        
        Args:
            url: URL to check
            
        Returns:
            (status_code, response_headers)
        """
        try:
            import requests
        except ImportError:
            raise KSEHTTPException("requests library required")
        
        try:
            headers = {'User-Agent': self._get_user_agent()}
            response = requests.head(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            return response.status_code, dict(response.headers)
        except Exception as e:
            raise KSEHTTPException(f"HEAD request failed: {e}") from e
    
    def _get_user_agent(self) -> str:
        """Get next user-agent from rotation"""
        ua = self.USER_AGENTS[self._ua_index % len(self.USER_AGENTS)]
        self._ua_index += 1
        return ua


__all__ = ["HTTPClient", "KSEHTTPException"]
