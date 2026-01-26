"""
kse_index_storage.py - Index Save/Load Operations

Handles saving and loading of search indices to/from disk storage.
Manages index metadata, versioning, and integrity checking.

Index Files:
- inverted_index.pkl: Main searchable index
- metadata_index.pkl: Page titles, descriptions
- url_index.pkl: URL deduplication
- domain_index.pkl: Domain-specific index
- tfidf_cache.pkl: Pre-computed TF-IDF
- pagerank_cache.pkl: Pre-computed PageRank
- index_metadata.json: Index statistics

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from kse.core import get_logger, KSEStorageException, KSEIndexException, INDEX_DIR
from .kse_data_serializer import DataSerializer

logger = get_logger('storage')


class IndexStorage:
    """Handles index persistence operations"""
    
    def __init__(self, index_dir: Optional[Path] = None):
        """Initialize index storage"""
        self.index_dir = Path(index_dir) if index_dir else INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.serializer = DataSerializer()
        logger.debug(f"IndexStorage initialized at {self.index_dir}")
    
    def save_index(self, index_data: Dict[str, Any]) -> None:
        """
        Save inverted index to disk.
        
        Args:
            index_data: Index dictionary to save
            
        Raises:
            KSEIndexException: If save fails
        """
        try:
            path = self.index_dir / "inverted_index.pkl"
            self.serializer.save_to_file(index_data, path)
            logger.info(f"Index saved: {len(index_data)} terms")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise KSEIndexException(f"Failed to save index: {str(e)}")
    
    def load_index(self) -> Dict[str, Any]:
        """
        Load inverted index from disk.
        
        Returns:
            Index dictionary
            
        Raises:
            KSEIndexException: If load fails
        """
        try:
            path = self.index_dir / "inverted_index.pkl"
            if not path.exists():
                raise FileNotFoundError(f"Index file not found: {path}")
            
            index_data = self.serializer.load_from_file(path)
            logger.info(f"Index loaded: {len(index_data)} terms")
            return index_data
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise KSEIndexException(f"Failed to load index: {str(e)}")
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save index metadata"""
        try:
            path = self.index_dir / "index_metadata.json"
            self.serializer.save_to_file(metadata, path)
            logger.info("Index metadata saved")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about stored index"""
        info = {
            'exists': False,
            'size': 0,
            'timestamp': None,
        }
        
        path = self.index_dir / "inverted_index.pkl"
        if path.exists():
            info['exists'] = True
            info['size'] = path.stat().st_size
            info['timestamp'] = datetime.fromtimestamp(path.stat().st_mtime)
        
        return info


__all__ = ["IndexStorage"]
