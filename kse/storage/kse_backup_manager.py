"""
kse_backup_manager.py - Backup and Restore Operations

Handles creation and restoration of backup snapshots for indices and data.
Maintains backup history and metadata.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from kse.core import (
    get_logger,
    KSEStorageException,
    SNAPSHOTS_DIR,
    STORAGE_BACKUP_ENABLED,
    STORAGE_MAX_BACKUPS,
)
from .kse_data_serializer import DataSerializer

logger = get_logger('storage')


class BackupManager:
    """Handles backup and restore operations"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """Initialize backup manager"""
        self.backup_dir = Path(backup_dir) if backup_dir else SNAPSHOTS_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.serializer = DataSerializer()
        logger.debug(f"BackupManager initialized at {self.backup_dir}")
    
    def create_backup(self, data: Dict, backup_name: Optional[str] = None) -> Path:
        """
        Create backup snapshot.
        
        Args:
            data: Data to backup
            backup_name: Optional backup name (default: timestamp)
            
        Returns:
            Path to backup file
        """
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = self.backup_dir / f"{backup_name}.pkl"
            self.serializer.save_to_file(data, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise KSEStorageException(f"Backup creation failed: {str(e)}")
    
    def restore_backup(self, backup_path: Path) -> Dict:
        """
        Restore from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Restored data
        """
        try:
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_path}")
            
            data = self.serializer.load_from_file(backup_path)
            logger.info(f"Backup restored: {backup_path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise KSEStorageException(f"Backup restore failed: {str(e)}")
    
    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dicts
        """
        backups = []
        try:
            for backup_file in sorted(self.backup_dir.glob("*.pkl"), reverse=True):
                info = {
                    'name': backup_file.stem,
                    'path': str(backup_file),
                    'size': backup_file.stat().st_size,
                    'timestamp': datetime.fromtimestamp(backup_file.stat().st_mtime),
                }
                backups.append(info)
        except Exception as e:
            logger.warning(f"Error listing backups: {e}")
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = STORAGE_MAX_BACKUPS) -> int:
        """
        Delete old backups, keeping only recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        try:
            backups = sorted(self.backup_dir.glob("*.pkl"), reverse=True)
            deleted_count = 0
            
            for backup_file in backups[keep_count:]:
                backup_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old backup: {backup_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backups")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
            return 0


__all__ = ["BackupManager"]
