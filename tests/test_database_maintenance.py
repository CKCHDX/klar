"""
Database Maintenance Tests

Tests for backup, migration, and consistency checking functionality.
"""

import pytest
import tempfile
from pathlib import Path
from kse.database import (
    BackupManager,
    MigrationManager,
    Migration001InitialSchema,
    ConsistencyChecker,
    DomainLoader,
    Repository,
)


class TestBackupManager:
    """Test database backup and restore functionality."""
    
    def test_backup_manager_init(self):
        """Test backup manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BackupManager(backup_dir=tmpdir)
            assert manager.backup_dir.exists()
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BackupManager(backup_dir=tmpdir)
            backups = manager.list_backups()
            assert len(backups) == 0
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BackupManager(backup_dir=tmpdir)
            backup_dir = Path(tmpdir)
            
            # Create fake backup files
            for i in range(10):
                (backup_dir / f"backup_{i}.sql.gz").touch()
            
            # Cleanup, keeping 3
            deleted = manager.cleanup_old_backups(keep_count=3)
            assert deleted == 7
            
            # Verify 3 files remain
            remaining = list(backup_dir.glob("*.sql*"))
            assert len(remaining) == 3


class TestMigrationManager:
    """Test database migration functionality."""
    
    def test_migration_table_created(self, db_connection):
        """Test that migration tracking table is created."""
        with db_connection.get_connection_context() as conn:
            manager = MigrationManager(conn)
            
            # Should not raise error
            migrations = manager.get_applied_migrations()
            assert isinstance(migrations, list)
    
    def test_record_migration(self, db_connection):
        """Test recording a migration."""
        with db_connection.get_connection_context() as conn:
            manager = MigrationManager(conn)
            
            success = manager.record_migration("test_migration", 100)
            assert success
            
            # Verify it was recorded
            assert manager.is_migration_applied("test_migration")
    
    def test_migration_history(self, db_connection):
        """Test retrieving migration history."""
        with db_connection.get_connection_context() as conn:
            manager = MigrationManager(conn)
            
            # Record some migrations
            manager.record_migration("migration_1", 50)
            manager.record_migration("migration_2", 75)
            manager.record_migration("migration_3", 100)
            
            history = manager.get_migration_history(limit=10)
            assert len(history) >= 3
    
    def test_migration_001_up(self, test_db_config):
        """Test initial schema migration."""
        from kse.database import DatabaseConnection
        
        db_conn = DatabaseConnection(**test_db_config)
        db_conn.initialize_pool()
        
        with db_conn.get_connection_context() as conn:
            # Run migration
            migration = Migration001InitialSchema(conn)
            success = migration.up()
            assert success
            
            # Verify tables exist
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name LIKE 'kse_%';
            """)
            count = cursor.fetchone()[0]
            assert count >= 8  # At least 8 tables
            cursor.close()
        
        db_conn.close_pool()
    
    def test_migration_001_down(self, test_db_config):
        """Test migration rollback."""
        from kse.database import DatabaseConnection
        
        db_conn = DatabaseConnection(**test_db_config)
        db_conn.initialize_pool()
        
        with db_conn.get_connection_context() as conn:
            # Apply migration
            migration = Migration001InitialSchema(conn)
            migration.up()
            
            # Rollback
            success = migration.down()
            assert success
            
            # Verify tables are gone
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name LIKE 'kse_%';
            """)
            count = cursor.fetchone()[0]
            assert count == 0
            cursor.close()
        
        db_conn.close_pool()


class TestConsistencyChecker:
    """Test database consistency checking."""
    
    def test_consistency_check_empty_db(self, test_schema, db_connection):
        """Test consistency check on empty database."""
        with db_connection.get_connection_context() as conn:
            checker = ConsistencyChecker(conn)
            results = checker.run_full_check()
            
            assert 'status' in results
            assert 'checks' in results
            assert 'errors' in results
            assert 'warnings' in results
    
    def test_statistics_check(self, populated_db):
        """Test statistics check."""
        with populated_db.get_connection_context() as conn:
            checker = ConsistencyChecker(conn)
            results = checker.run_full_check()
            
            assert 'statistics' in results['checks']
            stats = results['checks']['statistics']['statistics']
            assert 'total_domains' in stats
            assert 'total_pages' in stats
            assert stats['total_domains'] > 0
    
    def test_table_sizes_check(self, populated_db):
        """Test table size analysis."""
        with populated_db.get_connection_context() as conn:
            checker = ConsistencyChecker(conn)
            results = checker.run_full_check()
            
            assert 'table_sizes' in results['checks']
            sizes = results['checks']['table_sizes']
            assert 'table_sizes' in sizes
            assert 'total_size_gb' in sizes
    
    def test_orphaned_pages_detection(self, test_schema, db_connection):
        """Test detection of orphaned pages."""
        with db_connection.get_connection_context() as conn:
            # Create domain and page
            loader = DomainLoader(conn)
            loader.load_domains(clear_existing=True)
            
            repo = Repository(conn)
            domains = loader.get_active_domains()
            domain_id = domains[0]['id']
            
            # Add page
            page_id = repo.add_page(
                domain_id=domain_id,
                url="https://test.com/page",
                title="Test"
            )
            
            # Delete domain directly (orphaning the page)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kse_domains WHERE domain_id = %s;", (domain_id,))
            conn.commit()
            cursor.close()
            
            # Check for orphaned pages
            checker = ConsistencyChecker(conn)
            results = checker.run_full_check()
            
            assert results['checks']['orphaned_pages']['orphaned_count'] > 0
    
    def test_repair_orphaned_pages(self, test_schema, db_connection):
        """Test repairing orphaned pages."""
        with db_connection.get_connection_context() as conn:
            # Setup orphaned pages
            loader = DomainLoader(conn)
            loader.load_domains(clear_existing=True)
            
            repo = Repository(conn)
            domains = loader.get_active_domains()
            domain_id = domains[0]['id']
            
            # Add pages
            for i in range(3):
                repo.add_page(
                    domain_id=domain_id,
                    url=f"https://test.com/page{i}",
                    title=f"Page {i}"
                )
            
            # Delete domain
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kse_domains WHERE domain_id = %s;", (domain_id,))
            conn.commit()
            cursor.close()
            
            # Repair
            checker = ConsistencyChecker(conn)
            deleted = checker.repair_orphaned_pages(confirm=True)
            
            assert deleted == 3
            
            # Verify pages are gone
            repo2 = Repository(conn)
            assert repo2.get_page_count() == 0


class TestConsistencyIntegration:
    """Integration tests for consistency checking."""
    
    def test_full_check_with_data(self, populated_db):
        """Test complete consistency check on populated database."""
        with populated_db.get_connection_context() as conn:
            # Add some data
            repo = Repository(conn)
            loader = DomainLoader(conn)
            
            domains = loader.get_active_domains()
            for i in range(5):
                repo.add_page(
                    domain_id=domains[0]['id'],
                    url=f"https://example.com/page{i}",
                    title=f"Page {i}",
                    content_text=f"Content {i}"
                )
            
            # Run full check
            checker = ConsistencyChecker(conn)
            results = checker.run_full_check()
            
            # Verify results
            assert results['status'] in ['OK', 'ISSUES_FOUND']
            assert len(results['errors']) == 0  # No errors on clean data
            assert 'timestamp' in results
