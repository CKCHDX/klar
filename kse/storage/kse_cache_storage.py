"""
kse_cache_storage.py - Cache File Operations

Handles reading/writing of search result cache and query cache files.
Manages cache lifecycle, TTL, and cleanup.

Cache Files:
- search_cache.pkl: Recent search results
- query_cache.pkl: Preprocessed queries
- cache_manifest.json: Cache metadata and TTL

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from kse.core import get_logger, KSEStorageException, CACHE_DIR
from .kse_data_serializer import DataSerializer

logger = get_logger('storage')


class CacheStorage:
    """Handles cache file persistence"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache storage"""
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.serializer = DataSerializer()
        logger.debug(f"CacheStorage initialized at {self.cache_dir}")
    
    def save_search_cache(self, cache_data: Dict[str, Any]) -> None:
        """
        Save search result cache.
        
        Args:
            cache_data: Cache dictionary
        """
        try:
            path = self.cache_dir / "search_cache.pkl"
            self.serializer.save_to_file(cache_data, path)
            logger.debug(f"Search cache saved: {len(cache_data)} entries")
        except Exception as e:
            logger.error(f"Failed to save search cache: {e}")
            raise KSEStorageException(f"Cache save failed: {str(e)}")
    
    def load_search_cache(self) -> Dict[str, Any]:
        """
        Load search result cache.
        
        Returns:
            Cache dictionary or empty dict if not found
        """
        try:
            path = self.cache_dir / "search_cache.pkl"
            if not path.exists():
                return {}
            
            cache_data = self.serializer.load_from_file(path)
            logger.debug(f"Search cache loaded: {len(cache_data)} entries")
            return cache_data
        except Exception as e:
            logger.warning(f"Failed to load search cache: {e}")
            return {}
    
    def save_query_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save preprocessed query cache"""
        try:
            path = self.cache_dir / "query_cache.pkl"
            self.serializer.save_to_file(cache_data, path)
            logger.debug(f"Query cache saved: {len(cache_data)} entries")
        except Exception as e:
            logger.error(f"Failed to save query cache: {e}")
            raise
    
    def load_query_cache(self) -> Dict[str, Any]:
        """Load preprocessed query cache"""
        try:
            path = self.cache_dir / "query_cache.pkl"
            if not path.exists():
                return {}
            return self.serializer.load_from_file(path)
        except Exception as e:
            logger.warning(f"Failed to load query cache: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Clear all cache files"""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise


__all__ = ["CacheStorage"]
