"""
HTTP Fetcher for Web Pages

Handles HTTP requests with proper headers, error handling, and content validation.
"""

import hashlib
from enum import Enum
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    requests = None

from kse.core import KSELogger, KSEException

logger = KSELogger.get_logger(__name__)


class FetchStatus(Enum):
    """Fetch operation status."""
    SUCCESS = "success"
    HTTP_ERROR = "http_error"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    INVALID_CONTENT = "invalid_content"
    BLOCKED_BY_ROBOTS = "blocked_by_robots"
    REDIRECT_LOOP = "redirect_loop"
    SSL_ERROR = "ssl_error"
    TOO_LARGE = "too_large"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class FetchResult:
    """Result of a fetch operation."""
    url: str
    status: FetchStatus
    status_code: Optional[int] = None
    content: Optional[bytes] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    encoding: Optional[str] = None
    headers: Optional[dict] = None
    error_message: Optional[str] = None
    fetch_time_ms: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @property
    def is_success(self) -> bool:
        """Check if fetch was successful."""
        return self.status == FetchStatus.SUCCESS
    
    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable."""
        return self.status in [
            FetchStatus.TIMEOUT,
            FetchStatus.CONNECTION_ERROR,
        ]
    
    def get_content_hash(self) -> str:
        """Get SHA256 hash of content.
        
        Returns:
            Hex string hash
        """
        if self.content:
            return hashlib.sha256(self.content).hexdigest()
        return ""


class Fetcher:
    """
    HTTP fetcher for web pages.
    
    Features:
    - Configurable timeouts
    - Automatic retries
    - Content validation
    - Proper user-agent headers
    """
    
    def __init__(
        self,
        user_agent: str = "KSE-Bot/1.0 (+https://klar.se/bot)",
        timeout_seconds: float = 30.0,
        max_content_size_mb: float = 50.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """
        Initialize fetcher.
        
        Args:
            user_agent: User-Agent header value
            timeout_seconds: Request timeout
            max_content_size_mb: Maximum content size
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
        """
        if requests is None:
            raise KSEException("requests library required for crawling")
        
        self.user_agent = user_agent
        self.timeout = timeout_seconds
        self.max_content_size = int(max_content_size_mb * 1024 * 1024)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_headers(self, referer: Optional[str] = None) -> dict:
        """Build request headers.
        
        Args:
            referer: Referer URL
        
        Returns:
            Headers dictionary
        """
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    def _validate_content(
        self,
        content: bytes,
        content_type: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """Validate fetched content.
        
        Args:
            content: Content bytes
            content_type: Content-Type header value
        
        Returns:
            (is_valid, error_message)
        """
        if not content:
            return False, "Empty content"
        
        if len(content) > self.max_content_size:
            return False, f"Content too large: {len(content)} > {self.max_content_size}"
        
        if content_type:
            # Check for text content types
            if not any(ct in content_type.lower() for ct in [
                'text/html', 'text/plain', 'application/xhtml',
                'application/xml', 'application/json', 'application/pdf'
            ]):
                return False, f"Unsupported content type: {content_type}"
        
        return True, None
    
    def fetch(
        self,
        url: str,
        referer: Optional[str] = None,
        allow_redirects: bool = True
    ) -> FetchResult:
        """Fetch a URL.
        
        Args:
            url: URL to fetch
            referer: Referer header
            allow_redirects: Follow redirects
        
        Returns:
            FetchResult with status and content
        """
        import time
        start_time = time.time()
        
        try:
            logger.debug(f"Fetching: {url}")
            
            response = self.session.get(
                url,
                headers=self._get_headers(referer),
                timeout=self.timeout,
                allow_redirects=allow_redirects,
                stream=False  # Load entire content
            )
            
            fetch_time_ms = (time.time() - start_time) * 1000
            
            # Check status code
            if response.status_code >= 400:
                logger.warning(f"HTTP {response.status_code}: {url}")
                status = FetchStatus.HTTP_ERROR if response.status_code < 500 else FetchStatus.TIMEOUT
                return FetchResult(
                    url=url,
                    status=status,
                    status_code=response.status_code,
                    fetch_time_ms=fetch_time_ms,
                    error_message=f"HTTP {response.status_code}"
                )
            
            # Validate content
            content = response.content
            content_type = response.headers.get('Content-Type')
            
            is_valid, error_msg = self._validate_content(content, content_type)
            if not is_valid:
                logger.warning(f"Invalid content from {url}: {error_msg}")
                return FetchResult(
                    url=url,
                    status=FetchStatus.INVALID_CONTENT if 'Unsupported' in error_msg else FetchStatus.TOO_LARGE,
                    status_code=response.status_code,
                    fetch_time_ms=fetch_time_ms,
                    error_message=error_msg
                )
            
            # Success
            logger.debug(f"Successfully fetched {url} ({len(content)} bytes)")
            return FetchResult(
                url=url,
                status=FetchStatus.SUCCESS,
                status_code=response.status_code,
                content=content,
                content_type=content_type,
                content_length=len(content),
                encoding=response.encoding,
                headers=dict(response.headers),
                fetch_time_ms=fetch_time_ms
            )
        
        except requests.exceptions.Timeout:
            fetch_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Timeout fetching {url}")
            return FetchResult(
                url=url,
                status=FetchStatus.TIMEOUT,
                fetch_time_ms=fetch_time_ms,
                error_message="Request timeout"
            )
        
        except requests.exceptions.SSLError as e:
            fetch_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"SSL error for {url}: {e}")
            return FetchResult(
                url=url,
                status=FetchStatus.SSL_ERROR,
                fetch_time_ms=fetch_time_ms,
                error_message=str(e)
            )
        
        except requests.exceptions.ConnectionError as e:
            fetch_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Connection error for {url}: {e}")
            return FetchResult(
                url=url,
                status=FetchStatus.CONNECTION_ERROR,
                fetch_time_ms=fetch_time_ms,
                error_message=str(e)
            )
        
        except Exception as e:
            fetch_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
            return FetchResult(
                url=url,
                status=FetchStatus.UNKNOWN_ERROR,
                fetch_time_ms=fetch_time_ms,
                error_message=str(e)
            )
    
    def close(self) -> None:
        """Close session."""
        self.session.close()
        logger.debug("Fetcher session closed")
