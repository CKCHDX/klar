"""
KSE HTTP Client - HTTP requests with retry logic for web crawling
"""
import time
import requests
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse
from kse.core.kse_exceptions import HTTPError, TimeoutError as KSETimeoutError
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "crawler.log")


class HTTPClient:
    """HTTP client with retry logic and error handling"""
    
    def __init__(self, user_agent: str, timeout: int = 10, max_retries: int = 3):
        """
        Initialize HTTP client
        
        Args:
            user_agent: User agent string
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get(self, url: str) -> Tuple[str, int, Dict[str, str]]:
        """
        Perform HTTP GET request with retries
        
        Args:
            url: URL to fetch
        
        Returns:
            Tuple of (content, status_code, headers)
        
        Raises:
            HTTPError: If request fails after retries
            KSETimeoutError: If request times out
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # Check status code
                if response.status_code == 200:
                    logger.debug(f"Successfully fetched {url} ({len(response.content)} bytes)")
                    return response.text, response.status_code, dict(response.headers)
                
                elif response.status_code in [301, 302, 303, 307, 308]:
                    # Handle redirects (should be handled by allow_redirects=True)
                    logger.debug(f"Redirect from {url} to {response.url}")
                    return response.text, response.status_code, dict(response.headers)
                
                elif response.status_code == 404:
                    raise HTTPError(f"Page not found: {url}", status_code=404)
                
                elif response.status_code == 403:
                    raise HTTPError(f"Access forbidden: {url}", status_code=403)
                
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                    logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"Server error {response.status_code} on {url}")
                    last_error = HTTPError(
                        f"Server error {response.status_code}: {url}",
                        status_code=response.status_code
                    )
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                else:
                    raise HTTPError(
                        f"HTTP {response.status_code}: {url}",
                        status_code=response.status_code
                    )
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {url} (attempt {attempt + 1})")
                last_error = KSETimeoutError(f"Request timeout: {url}")
                time.sleep(1)
                continue
            
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on {url}: {e}")
                last_error = HTTPError(f"Connection error: {url}")
                time.sleep(2)
                continue
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on {url}: {e}")
                raise HTTPError(f"Request failed: {url}")
        
        # All retries failed
        if last_error:
            raise last_error
        raise HTTPError(f"Failed to fetch {url} after {self.max_retries} attempts")
    
    def head(self, url: str) -> Tuple[int, Dict[str, str]]:
        """
        Perform HTTP HEAD request
        
        Args:
            url: URL to check
        
        Returns:
            Tuple of (status_code, headers)
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code, dict(response.headers)
        except requests.exceptions.RequestException as e:
            logger.error(f"HEAD request failed for {url}: {e}")
            raise HTTPError(f"HEAD request failed: {url}")
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid
        
        Args:
            url: URL to validate
        
        Returns:
            True if URL is valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: URL to parse
        
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    def close(self) -> None:
        """Close the session"""
        self.session.close()
        logger.debug("HTTP session closed")
