"""kse_robots_parser.py - robots.txt Compliance Handler"""

import logging
from typing import Optional, List
from urllib.parse import urlparse
import time

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class KSERobotsException(KSEException):
    """Robots parser exception"""
    pass


class RobotsParser:
    """Parse and enforce robots.txt rules"""
    
    def __init__(self, user_agent: str = '*'):
        self.user_agent = user_agent
        self._rules_cache = {}
        self._fetch_times = {}
        logger.debug(f"RobotsParser initialized for UA: {user_agent}")
    
    def is_allowed(self, url: str, respect_rules: bool = True) -> bool:
        """Check if URL can be crawled"""
        if not respect_rules:
            return True
        
        try:
            domain = urlparse(url).netloc
            
            if domain not in self._rules_cache:
                self._fetch_robots(domain)
            
            rules = self._rules_cache.get(domain, [])
            path = urlparse(url).path or '/'
            
            for rule_path, allowed in rules:
                if path.startswith(rule_path):
                    return allowed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots: {e}")
            return True
    
    def _fetch_robots(self, domain: str) -> None:
        """Fetch and cache robots.txt"""
        try:
            from kse.crawler.kse_http_client import HTTPClient
            
            client = HTTPClient()
            url = f"https://{domain}/robots.txt"
            
            content, status_code, _ = client.get(url)
            
            if status_code == 200:
                self._parse_robots(domain, content.decode('utf-8'))
            else:
                self._rules_cache[domain] = []
            
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt: {e}")
            self._rules_cache[domain] = []
    
    def _parse_robots(self, domain: str, content: str) -> None:
        """Parse robots.txt content"""
        rules = []
        current_ua = None
        
        for line in content.split('\n'):
            line = line.strip().split('#')[0].strip()
            if not line:
                continue
            
            if line.lower().startswith('user-agent:'):
                current_ua = line.split(':', 1)[1].strip().lower()
            
            elif line.lower().startswith('disallow:') and current_ua in ('*', self.user_agent):
                path = line.split(':', 1)[1].strip()
                rules.append((path, False))
            
            elif line.lower().startswith('allow:') and current_ua in ('*', self.user_agent):
                path = line.split(':', 1)[1].strip()
                rules.append((path, True))
        
        self._rules_cache[domain] = rules


__all__ = ["RobotsParser", "KSERobotsException"]
