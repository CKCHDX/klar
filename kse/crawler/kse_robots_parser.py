"""
KSE Robots Parser - robots.txt compliance checker
"""
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
from typing import Dict, Optional
from kse.core.kse_logger import get_logger
from kse.core.kse_exceptions import RobotsBlockedError

logger = get_logger(__name__, "crawler.log")


class RobotsParser:
    """Handle robots.txt parsing and compliance"""
    
    def __init__(self, user_agent: str):
        """
        Initialize robots parser
        
        Args:
            user_agent: User agent string to check against robots.txt
        """
        self.user_agent = user_agent
        self._parsers: Dict[str, RobotFileParser] = {}
        self._cache: Dict[str, bool] = {}  # Cache allowed/disallowed results
    
    def can_fetch(self, url: str, respect_robots: bool = True) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        
        Args:
            url: URL to check
            respect_robots: Whether to respect robots.txt (default: True)
        
        Returns:
            True if URL can be fetched
        """
        if not respect_robots:
            return True
        
        # Check cache first
        if url in self._cache:
            return self._cache[url]
        
        try:
            # Get base URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Get or create parser for this domain
            if base_url not in self._parsers:
                self._load_robots(base_url)
            
            parser = self._parsers.get(base_url)
            
            if parser:
                allowed = parser.can_fetch(self.user_agent, url)
                self._cache[url] = allowed
                
                if not allowed:
                    logger.warning(f"robots.txt blocks: {url}")
                    logger.info(f"  You may need to configure a custom user agent or contact {parsed.netloc} for access")
                
                return allowed
            else:
                # No robots.txt or failed to load - allow by default
                logger.debug(f"No robots.txt for {base_url}, allowing access")
                self._cache[url] = True
                return True
        
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            # On error, be lenient and allow
            return True
    
    def _load_robots(self, base_url: str) -> None:
        """
        Load robots.txt for a domain
        
        Args:
            base_url: Base URL of domain
        """
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            
            parser = RobotFileParser()
            parser.set_url(robots_url)
            
            try:
                # Set a reasonable timeout to avoid hanging
                import socket
                default_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(10)
                
                parser.read()
                
                # Restore default timeout
                socket.setdefaulttimeout(default_timeout)
                
                self._parsers[base_url] = parser
                logger.info(f"✓ Loaded robots.txt from {robots_url}")
            except Exception as e:
                logger.info(f"No robots.txt at {robots_url} (allowing all): {e}")
                # Create permissive parser (None means allow all)
                self._parsers[base_url] = None
        
        except Exception as e:
            logger.warning(f"Failed to load robots.txt for {base_url}: {e}")
            self._parsers[base_url] = None
    
    def get_crawl_delay(self, base_url: str) -> Optional[float]:
        """
        Get crawl delay from robots.txt
        
        Args:
            base_url: Base URL of domain
        
        Returns:
            Crawl delay in seconds or None if not specified
        """
        try:
            if base_url not in self._parsers:
                self._load_robots(base_url)
            
            parser = self._parsers.get(base_url)
            if parser:
                delay = parser.crawl_delay(self.user_agent)
                if delay:
                    return float(delay)
        
        except Exception as e:
            logger.error(f"Error getting crawl delay for {base_url}: {e}")
        
        return None
    
    def clear_cache(self) -> None:
        """Clear the cache of allowed/disallowed URLs"""
        self._cache.clear()
        logger.debug("Cleared robots.txt cache")
    
    def clear_parsers(self) -> None:
        """Clear all loaded robots.txt parsers"""
        self._parsers.clear()
        self._cache.clear()
        logger.debug("Cleared all robots.txt parsers")
