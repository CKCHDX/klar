"""kse_change_detection.py - Hash-based Change Detection"""

import logging
import hashlib
from typing import Dict, Optional
from datetime import datetime

from kse.core import get_logger

logger = get_logger('crawler')


class ChangeDetector:
    """Detect content changes using hashing"""
    
    def __init__(self):
        self._page_hashes: Dict[str, str] = {}
        logger.debug("ChangeDetector initialized")
    
    def get_hash(self, content: bytes) -> str:
        """Get SHA256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    def has_changed(self, url: str, content: bytes) -> bool:
        """Check if content has changed"""
        new_hash = self.get_hash(content)
        old_hash = self._page_hashes.get(url)
        
        if old_hash is None:
            self._page_hashes[url] = new_hash
            return True
        
        changed = old_hash != new_hash
        if changed:
            self._page_hashes[url] = new_hash
        
        return changed
    
    def record_hash(self, url: str, content: bytes) -> None:
        """Record content hash"""
        self._page_hashes[url] = self.get_hash(content)


__all__ = ["ChangeDetector"]
