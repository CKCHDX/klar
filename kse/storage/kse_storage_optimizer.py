"""
kse_storage_optimizer.py - Storage Optimization and Cleanup

Optimizes storage usage, removes old files, consolidates data.
Maintains storage efficiency and prevents disk space waste.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

from kse.core import (
    get_logger,
    KSEStorageException,
    STORAGE_DIR,
    CACHE_DIR,
    LOGS_DIR,
)

logger = get_logger('storage')


class StorageOptimizer:
    """Optimizes and cleans up storage"""
    
    def __init__(self):
        """Initialize storage optimizer"""
        logger.debug("StorageOptimizer initialized")
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Delete log files older than specified days.
        
        Args:
            days: Days to keep
            
        Returns:
            Number of files deleted
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for log_file in LOGS_DIR.glob("*.log*"):
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old log: {log_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup logs: {e}")
            return 0
    
    def cleanup_cache(self, ttl_seconds: int = 86400) -> int:
        """
        Delete cache files older than TTL.
        
        Args:
            ttl_seconds: Time to live in seconds
            
        Returns:
            Number of files deleted
        """
        try:
            cutoff_time = datetime.now() - timedelta(seconds=ttl_seconds)
            deleted_count = 0
            
            for cache_file in CACHE_DIR.glob("*.pkl"):
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if mtime < cutoff_time:
                    cache_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old cache: {cache_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old cache files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
            return 0
    
    def get_optimization_recommendations(self) -> Dict[str, str]:
        """
        Get storage optimization recommendations.
        
        Returns:
            Dictionary with recommendations
        """
        recommendations = {}
        
        try:
            # Check log sizes
            total_log_size = sum(f.stat().st_size for f in LOGS_DIR.glob("*.log*"))
            if total_log_size > 100 * 1024 * 1024:  # >100MB
                recommendations['logs'] = (
                    f"Large log directory ({total_log_size / (1024*1024):.1f}MB). "
                    "Consider cleanup."
                )
            
            # Check cache sizes
            total_cache_size = sum(f.stat().st_size for f in CACHE_DIR.glob("*.pkl"))
            if total_cache_size > 50 * 1024 * 1024:  # >50MB
                recommendations['cache'] = (
                    f"Large cache directory ({total_cache_size / (1024*1024):.1f}MB). "
                    "Consider clearing expired cache."
                )
        
        except Exception as e:
            logger.warning(f"Error getting recommendations: {e}")
        
        return recommendations


__all__ = ["StorageOptimizer"]
