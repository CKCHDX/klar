"""
kse_storage_manager.py - Main Storage Orchestration Layer

This module provides the central storage management system for KSE.
Orchestrates all file I/O operations for index, cache, and crawl state.

Responsibilities:
- Directory creation and validation
- File I/O coordination
- Storage monitoring
- Backup coordination
- Data serialization delegation

Architecture:
    StorageManager
    ├── kse_domain_manager.py      (Domain list management)
    ├── kse_index_storage.py       (Index save/load)
    ├── kse_cache_storage.py       (Cache file operations)
    ├── kse_data_serializer.py     (JSON/pickle serialization)
    ├── kse_backup_manager.py      (Backup & restore)
    ├── kse_storage_optimizer.py   (Storage cleanup)
    └── kse_storage_monitor.py     (Storage usage monitoring)

Usage:
    >>> from kse.storage import StorageManager
    >>> storage = StorageManager()
    >>> storage.save_index(index_data)
    >>> loaded_index = storage.load_index()

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from kse.core import (
    get_logger,
    KSEStorageException,
    KSEStorageIOError,
    KSEStorageNotFound,
    KSEStorageCorrupted,
    STORAGE_DIR,
    INDEX_DIR,
    CACHE_DIR,
    CRAWL_STATE_DIR,
    SNAPSHOTS_DIR,
    DATA_DIR,
)

logger = get_logger('storage')


class StorageManager:
    """
    Central storage management system for KSE.
    
    Handles all file I/O operations for:
    - Index storage and retrieval
    - Cache management
    - Crawl state persistence
    - Backup and restore operations
    - Storage monitoring and optimization
    
    All storage is file-based (no database server required).
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize storage manager.
        
        Args:
            base_dir: Base directory for storage (default: STORAGE_DIR)
            
        Raises:
            KSEStorageException: If initialization fails
        """
        self.base_dir = Path(base_dir) if base_dir else STORAGE_DIR
        self._initialized = False
        
        try:
            self._ensure_directories()
            self._initialized = True
            logger.info(f"Storage initialized at {self.base_dir}")
        except Exception as e:
            logger.error(f"Storage initialization failed: {e}")
            raise KSEStorageException(
                f"Failed to initialize storage: {str(e)}",
                error_code="STORAGE_INIT_ERROR"
            )
    
    def _ensure_directories(self) -> None:
        """Create all required storage directories"""
        directories = [
            self.base_dir,
            INDEX_DIR,
            CACHE_DIR,
            CRAWL_STATE_DIR,
            SNAPSHOTS_DIR,
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory verified: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def get_directory(self, section: str) -> Path:
        """
        Get path to storage subdirectory.
        
        Args:
            section: Section name (index, cache, crawl_state, snapshots)
            
        Returns:
            Path to directory
        """
        sections = {
            'index': INDEX_DIR,
            'cache': CACHE_DIR,
            'crawl_state': CRAWL_STATE_DIR,
            'snapshots': SNAPSHOTS_DIR,
        }
        
        return sections.get(section, self.base_dir)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage info:
            - total_size: Total size in bytes
            - index_size: Index directory size
            - cache_size: Cache directory size
            - file_count: Total number of files
            - directory_count: Number of directories
        """
        def get_dir_size(path: Path) -> int:
            """Recursively calculate directory size"""
            total = 0
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
            except Exception as e:
                logger.warning(f"Error calculating size for {path}: {e}")
            return total
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_size': 0,
            'index_size': 0,
            'cache_size': 0,
            'crawl_state_size': 0,
            'snapshots_size': 0,
            'file_count': 0,
            'directory_count': 0,
        }
        
        try:
            stats['index_size'] = get_dir_size(INDEX_DIR)
            stats['cache_size'] = get_dir_size(CACHE_DIR)
            stats['crawl_state_size'] = get_dir_size(CRAWL_STATE_DIR)
            stats['snapshots_size'] = get_dir_size(SNAPSHOTS_DIR)
            
            stats['total_size'] = (
                stats['index_size'] + stats['cache_size'] +
                stats['crawl_state_size'] + stats['snapshots_size']
            )
            
            # Count files and directories
            for path in self.base_dir.rglob('*'):
                if path.is_file():
                    stats['file_count'] += 1
                elif path.is_dir():
                    stats['directory_count'] += 1
            
            logger.debug(f"Storage stats: {stats['total_size']} bytes")
        except Exception as e:
            logger.error(f"Error calculating storage stats: {e}")
        
        return stats
    
    def is_initialized(self) -> bool:
        """Check if storage is initialized"""
        return self._initialized
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on storage.
        
        Returns:
            Dictionary with health status:
            - status: 'healthy', 'warning', or 'error'
            - issues: List of issues found
        """
        issues = []
        
        try:
            # Check if directories exist and are readable
            for directory in [INDEX_DIR, CACHE_DIR, CRAWL_STATE_DIR, SNAPSHOTS_DIR]:
                if not directory.exists():
                    issues.append(f"Directory missing: {directory}")
                elif not directory.is_dir():
                    issues.append(f"Path is not a directory: {directory}")
                elif not os.access(directory, os.W_OK):
                    issues.append(f"Directory not writable: {directory}")
            
            # Check disk space (if available)
            try:
                import shutil
                stat = shutil.disk_usage(self.base_dir)
                if stat.free < 100 * 1024 * 1024:  # Less than 100MB free
                    issues.append(f"Low disk space: {stat.free / (1024*1024):.1f}MB free")
            except:
                pass  # Disk space check not critical
        
        except Exception as e:
            logger.error(f"Health check error: {e}")
            issues.append(str(e))
        
        status = 'healthy' if not issues else ('warning' if len(issues) < 3 else 'error')
        
        return {
            'status': status,
            'issues': issues,
            'timestamp': datetime.now().isoformat(),
        }


import os


__all__ = [
    "StorageManager",
]
