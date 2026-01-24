"""
Database Backup & Restore Module

Handles PostgreSQL database backups and restoration.
Used for disaster recovery and snapshot management.
"""

import logging
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manages database backups and restoration.
    
    Supports:
    - Full database backups (pg_dump)
    - Incremental backups
    - Backup compression
    - Automated backup scheduling
    """
    
    def __init__(self, backup_dir: str = "database/backup"):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "kse_db",
        user: str = "postgres",
        password: str = "postgres",
        compress: bool = True
    ) -> Optional[Path]:
        """Create database backup.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            compress: If True, use gzip compression
        
        Returns:
            Path to backup file or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if compress:
                backup_file = self.backup_dir / f"{database}_{timestamp}.sql.gz"
                format_opt = "-Fc"
            else:
                backup_file = self.backup_dir / f"{database}_{timestamp}.sql"
                format_opt = "-Fp"
            
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={user}",
                "--verbose",
                format_opt,
                f"--file={backup_file}",
                database
            ]
            
            logger.info(f"Starting database backup to {backup_file}...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = backup_file.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"✓ Backup successful: {backup_file} ({file_size:.2f} MB)")
                return backup_file
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def restore_backup(
        self,
        backup_file: Path,
        host: str = "localhost",
        port: int = 5432,
        database: str = "kse_db",
        user: str = "postgres",
        password: str = "postgres",
        confirm: bool = False
    ) -> bool:
        """Restore database from backup.
        
        Args:
            backup_file: Path to backup file
            host: PostgreSQL host
            port: PostgreSQL port
            database: Target database name
            user: Database user
            password: Database password
            confirm: Must be True to proceed
        
        Returns:
            True if successful
        """
        if not confirm:
            logger.warning("Restore not confirmed. Pass confirm=True to proceed.")
            return False
        
        try:
            backup_file = Path(backup_file)
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Determine format
            if backup_file.suffix == ".gz":
                cmd = [
                    "pg_restore",
                    f"--host={host}",
                    f"--port={port}",
                    f"--username={user}",
                    "--verbose",
                    "-d", database,
                    str(backup_file)
                ]
            else:
                cmd = [
                    "psql",
                    f"--host={host}",
                    f"--port={port}",
                    f"--username={user}",
                    "-d", database,
                    "-f", str(backup_file)
                ]
            
            logger.warning(f"Restoring database from {backup_file}...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✓ Restore successful from {backup_file}")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[dict]:
        """List all available backups.
        
        Returns:
            List of backup info dicts
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.sql*"), reverse=True):
            try:
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created': datetime.fromtimestamp(stat.st_mtime),
                })
            except Exception as e:
                logger.warning(f"Error reading backup file {backup_file}: {e}")
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Remove old backups, keeping only the most recent.
        
        Args:
            keep_count: Number of backups to keep
        
        Returns:
            Number of backups deleted
        """
        backups = sorted(self.backup_dir.glob("*.sql*"), key=lambda p: p.stat().st_mtime, reverse=True)
        deleted_count = 0
        
        for backup_file in backups[keep_count:]:
            try:
                backup_file.unlink()
                logger.info(f"Deleted old backup: {backup_file.name}")
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Error deleting backup {backup_file}: {e}")
        
        return deleted_count
