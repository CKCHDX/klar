"""
KSE Storage Manager - File I/O orchestration for Klar Search Engine
"""
from pathlib import Path
from typing import Any, Dict, Optional, Set
from kse.core.kse_exceptions import StorageError
from kse.core.kse_logger import get_logger
from kse.storage.kse_data_serializer import DataSerializer

logger = get_logger(__name__, "storage.log")


class StorageManager:
    """Main storage orchestration layer for file-based data"""
    
    def __init__(self, base_path: Path):
        """
        Initialize storage manager
        
        Args:
            base_path: Base directory for all storage
        """
        self.base_path = Path(base_path)
        self._serializer = DataSerializer()
        self._ensure_directories()
        logger.info(f"Storage initialized at {self.base_path}")
    
    def _ensure_directories(self) -> None:
        """Create all required directories"""
        directories = [
            self.base_path / "storage" / "index",
            self.base_path / "storage" / "cache",
            self.base_path / "storage" / "crawl_state",
            self.base_path / "storage" / "snapshots",
            self.base_path / "logs",
            self.base_path / "exports",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.debug("All storage directories verified")
    
    # Index operations
    def save_index(self, index_data: Dict[str, Any], index_type: str = "inverted") -> None:
        """
        Save search index to disk
        
        Args:
            index_data: Index data to save
            index_type: Type of index (inverted, metadata, url, etc.)
        """
        try:
            file_path = self.base_path / "storage" / "index" / f"{index_type}_index.pkl"
            self._serializer.save_pickle(index_data, file_path)
            logger.info(f"{index_type} index saved: {len(index_data)} entries")
        except Exception as e:
            raise StorageError(f"Failed to save {index_type} index: {e}")
    
    def load_index(self, index_type: str = "inverted") -> Optional[Dict[str, Any]]:
        """
        Load search index from disk
        
        Args:
            index_type: Type of index to load
        
        Returns:
            Index data or None if not found
        """
        try:
            file_path = self.base_path / "storage" / "index" / f"{index_type}_index.pkl"
            data = self._serializer.load_pickle(file_path)
            if data:
                logger.info(f"{index_type} index loaded: {len(data)} entries")
            return data
        except Exception as e:
            logger.error(f"Failed to load {index_type} index: {e}")
            return None
    
    # Cache operations
    def save_cache(self, cache_data: Dict[str, Any], cache_type: str = "search") -> None:
        """
        Save cache to disk
        
        Args:
            cache_data: Cache data to save
            cache_type: Type of cache (search, query, etc.)
        """
        try:
            file_path = self.base_path / "storage" / "cache" / f"{cache_type}_cache.pkl"
            self._serializer.save_pickle(cache_data, file_path)
            logger.debug(f"{cache_type} cache saved: {len(cache_data)} entries")
        except Exception as e:
            raise StorageError(f"Failed to save {cache_type} cache: {e}")
    
    def load_cache(self, cache_type: str = "search") -> Optional[Dict[str, Any]]:
        """
        Load cache from disk
        
        Args:
            cache_type: Type of cache to load
        
        Returns:
            Cache data or None if not found
        """
        try:
            file_path = self.base_path / "storage" / "cache" / f"{cache_type}_cache.pkl"
            return self._serializer.load_pickle(file_path)
        except Exception as e:
            logger.error(f"Failed to load {cache_type} cache: {e}")
            return None
    
    # Crawl state operations
    def save_crawl_state(self, state_data: Any, state_type: str) -> None:
        """
        Save crawl state
        
        Args:
            state_data: State data to save
            state_type: Type of state (domain_status, url_queue, visited_urls)
        """
        try:
            file_path = self.base_path / "storage" / "crawl_state" / f"{state_type}.pkl"
            
            # JSON for domain status, pickle for others
            if state_type == "domain_status":
                self._serializer.save_json(state_data, 
                    self.base_path / "storage" / "crawl_state" / f"{state_type}.json")
            else:
                self._serializer.save_pickle(state_data, file_path)
            
            logger.debug(f"Crawl state saved: {state_type}")
        except Exception as e:
            raise StorageError(f"Failed to save crawl state {state_type}: {e}")
    
    def load_crawl_state(self, state_type: str) -> Optional[Any]:
        """
        Load crawl state
        
        Args:
            state_type: Type of state to load
        
        Returns:
            State data or None if not found
        """
        try:
            if state_type == "domain_status":
                file_path = self.base_path / "storage" / "crawl_state" / f"{state_type}.json"
                return self._serializer.load_json(file_path)
            else:
                file_path = self.base_path / "storage" / "crawl_state" / f"{state_type}.pkl"
                return self._serializer.load_pickle(file_path)
        except Exception as e:
            logger.error(f"Failed to load crawl state {state_type}: {e}")
            return None
    
    # Statistics and metadata
    def save_metadata(self, metadata: Dict[str, Any], metadata_type: str) -> None:
        """
        Save metadata
        
        Args:
            metadata: Metadata to save
            metadata_type: Type of metadata
        """
        try:
            file_path = self.base_path / "storage" / "index" / f"{metadata_type}_metadata.json"
            self._serializer.save_json(metadata, file_path)
            logger.debug(f"Metadata saved: {metadata_type}")
        except Exception as e:
            raise StorageError(f"Failed to save metadata {metadata_type}: {e}")
    
    def load_metadata(self, metadata_type: str) -> Dict[str, Any]:
        """
        Load metadata
        
        Args:
            metadata_type: Type of metadata to load
        
        Returns:
            Metadata dictionary
        """
        try:
            file_path = self.base_path / "storage" / "index" / f"{metadata_type}_metadata.json"
            return self._serializer.load_json(file_path)
        except Exception as e:
            logger.error(f"Failed to load metadata {metadata_type}: {e}")
            return {}
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "base_path": str(self.base_path),
            "total_size_mb": 0,
            "index_files": [],
            "cache_files": [],
            "crawl_state_files": [],
        }
        
        try:
            # Calculate total size
            total_size = sum(f.stat().st_size for f in self.base_path.rglob('*') if f.is_file())
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # List files
            index_dir = self.base_path / "storage" / "index"
            if index_dir.exists():
                stats["index_files"] = [f.name for f in index_dir.iterdir() if f.is_file()]
            
            cache_dir = self.base_path / "storage" / "cache"
            if cache_dir.exists():
                stats["cache_files"] = [f.name for f in cache_dir.iterdir() if f.is_file()]
            
            crawl_dir = self.base_path / "storage" / "crawl_state"
            if crawl_dir.exists():
                stats["crawl_state_files"] = [f.name for f in crawl_dir.iterdir() if f.is_file()]
        
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
        
        return stats
