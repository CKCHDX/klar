"""
Database Migration System

Manages database schema migrations and version control.
Ensures consistent schema evolution across deployments.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 is required")

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Manages database migrations.
    
    Handles:
    - Migration execution
    - Rollback support
    - Migration history tracking
    - Schema versioning
    """
    
    def __init__(self, connection):
        """Initialize migration manager.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
        self._ensure_migration_table()
    
    def _ensure_migration_table(self) -> None:
        """Ensure migration tracking table exists."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_migrations (
                    migration_id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    migration_file VARCHAR(255),
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms INT,
                    status VARCHAR(20) DEFAULT 'applied'
                );
            """)
            self.connection.commit()
            logger.debug("Migration tracking table ready")
        except Exception as e:
            logger.error(f"Error creating migration table: {e}")
        finally:
            cursor.close()
    
    def get_applied_migrations(self) -> List[Dict]:
        """Get list of already applied migrations.
        
        Returns:
            List of migration dicts
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT migration_id, migration_name, applied_at, execution_time_ms
                FROM kse_migrations
                WHERE status = 'applied'
                ORDER BY migration_id ASC;
            """)
            
            migrations = []
            for row in cursor.fetchall():
                migrations.append({
                    'id': row[0],
                    'name': row[1],
                    'applied': row[2],
                    'duration_ms': row[3]
                })
            return migrations
        finally:
            cursor.close()
    
    def record_migration(self, migration_name: str, duration_ms: int) -> bool:
        """Record a successful migration.
        
        Args:
            migration_name: Name of migration
            duration_ms: Execution time in milliseconds
        
        Returns:
            True if successful
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO kse_migrations (migration_name, execution_time_ms, status)
                VALUES (%s, %s, 'applied');
            """, (migration_name, duration_ms))
            self.connection.commit()
            logger.info(f"Recorded migration: {migration_name} ({duration_ms}ms)")
            return True
        except Exception as e:
            logger.error(f"Error recording migration: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def is_migration_applied(self, migration_name: str) -> bool:
        """Check if a migration has been applied.
        
        Args:
            migration_name: Name of migration
        
        Returns:
            True if applied
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM kse_migrations
                WHERE migration_name = %s AND status = 'applied';
            """, (migration_name,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()
    
    def get_migration_history(self, limit: int = 20) -> List[Dict]:
        """Get migration history.
        
        Args:
            limit: Maximum number of records
        
        Returns:
            List of migration records
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT migration_id, migration_name, applied_at, execution_time_ms, status
                FROM kse_migrations
                ORDER BY migration_id DESC
                LIMIT %s;
            """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'name': row[1],
                    'applied': row[2],
                    'duration_ms': row[3],
                    'status': row[4]
                })
            return history
        finally:
            cursor.close()


class Migration:
    """
    Base class for individual migrations.
    
    Each migration should:
    - Have a unique name
    - Implement up() method
    - Optionally implement down() for rollback
    """
    
    # Override in subclasses
    name = None
    description = None
    
    def __init__(self, connection):
        """Initialize migration.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
    
    def up(self) -> bool:
        """Apply migration. Override in subclasses.
        
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement up()")
    
    def down(self) -> bool:
        """Rollback migration. Override if needed.
        
        Returns:
            True if successful
        """
        logger.warning(f"Rollback not implemented for {self.name}")
        return False


class Migration001InitialSchema(Migration):
    """
    Migration 001: Create initial database schema.
    
    Creates all core tables:
    - kse_domains
    - kse_pages
    - kse_index_terms
    - kse_page_terms
    - kse_crawl_stats
    - kse_search_queries
    - kse_index_snapshots
    - kse_system_logs
    """
    
    name = "001_initial_schema"
    description = "Create initial database schema"
    
    def up(self) -> bool:
        """Create all core tables."""
        cursor = self.connection.cursor()
        
        try:
            # This uses the schema from kse_database_schema.py
            # In production, this SQL would be in database/migrations/001_initial_schema.sql
            logger.info(f"Applying migration: {self.name}")
            
            # Create domains table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_domains (
                    domain_id SERIAL PRIMARY KEY,
                    domain_name VARCHAR(255) NOT NULL UNIQUE,
                    domain_url VARCHAR(255) NOT NULL UNIQUE,
                    category VARCHAR(100),
                    trust_score FLOAT DEFAULT 0.5,
                    is_active BOOLEAN DEFAULT TRUE,
                    crawl_frequency INT DEFAULT 7,
                    last_crawled_at TIMESTAMP NULL,
                    next_crawl_at TIMESTAMP NULL,
                    page_count INT DEFAULT 0,
                    error_count INT DEFAULT 0,
                    last_error_message TEXT NULL,
                    robots_txt_url VARCHAR(255) NULL,
                    robots_txt_content TEXT NULL,
                    robots_txt_last_checked TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_pages (
                    page_id BIGSERIAL PRIMARY KEY,
                    domain_id INT NOT NULL REFERENCES kse_domains(domain_id) ON DELETE CASCADE,
                    url VARCHAR(2048) NOT NULL UNIQUE,
                    title VARCHAR(255),
                    description TEXT,
                    content_text TEXT,
                    content_hash VARCHAR(64) UNIQUE,
                    status_code INT,
                    content_type VARCHAR(100),
                    content_length INT,
                    language VARCHAR(10) DEFAULT 'sv',
                    page_rank FLOAT DEFAULT 0.0,
                    inbound_links INT DEFAULT 0,
                    outbound_links INT DEFAULT 0,
                    last_indexed_at TIMESTAMP,
                    last_crawled_at TIMESTAMP,
                    crawl_duration_ms INT,
                    is_indexed BOOLEAN DEFAULT FALSE,
                    last_modified TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index terms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_index_terms (
                    term_id SERIAL PRIMARY KEY,
                    term VARCHAR(100) NOT NULL UNIQUE,
                    term_type VARCHAR(50),
                    collection_frequency INT DEFAULT 0,
                    idf FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create page terms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_page_terms (
                    page_term_id BIGSERIAL PRIMARY KEY,
                    page_id BIGINT NOT NULL REFERENCES kse_pages(page_id) ON DELETE CASCADE,
                    term_id INT NOT NULL REFERENCES kse_index_terms(term_id) ON DELETE CASCADE,
                    term_frequency INT DEFAULT 0,
                    tf_idf FLOAT DEFAULT 0.0,
                    position_in_title BOOLEAN DEFAULT FALSE,
                    position_in_description BOOLEAN DEFAULT FALSE,
                    position_in_content BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(page_id, term_id)
                );
            """)
            
            # Create crawl stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_crawl_stats (
                    stat_id SERIAL PRIMARY KEY,
                    domain_id INT REFERENCES kse_domains(domain_id) ON DELETE SET NULL,
                    pages_crawled INT DEFAULT 0,
                    pages_indexed INT DEFAULT 0,
                    pages_failed INT DEFAULT 0,
                    crawl_duration_seconds INT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    average_response_time_ms FLOAT,
                    error_messages TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create search queries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_search_queries (
                    query_id BIGSERIAL PRIMARY KEY,
                    query_text VARCHAR(255) NOT NULL,
                    query_language VARCHAR(10),
                    results_count INT,
                    execution_time_ms INT,
                    user_ip VARCHAR(45),
                    user_agent TEXT,
                    clicked_result_id BIGINT REFERENCES kse_pages(page_id),
                    click_position INT,
                    result_satisfaction SMALLINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_index_snapshots (
                    snapshot_id SERIAL PRIMARY KEY,
                    snapshot_name VARCHAR(100) NOT NULL UNIQUE,
                    snapshot_path VARCHAR(255) NOT NULL,
                    total_pages INT,
                    total_terms INT,
                    snapshot_size_bytes BIGINT,
                    creation_time TIMESTAMP NOT NULL,
                    description TEXT,
                    is_latest BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create system logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kse_system_logs (
                    log_id BIGSERIAL PRIMARY KEY,
                    log_level VARCHAR(20),
                    logger_name VARCHAR(100),
                    message TEXT,
                    exception_traceback TEXT,
                    context_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.connection.commit()
            logger.info(f"✓ Migration {self.name} completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Migration {self.name} failed: {e}")
            self.connection.rollback()
            return False
        
        finally:
            cursor.close()
    
    def down(self) -> bool:
        """Rollback: drop all tables."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                DROP TABLE IF EXISTS kse_system_logs CASCADE;
                DROP TABLE IF EXISTS kse_index_snapshots CASCADE;
                DROP TABLE IF EXISTS kse_search_queries CASCADE;
                DROP TABLE IF EXISTS kse_crawl_stats CASCADE;
                DROP TABLE IF EXISTS kse_page_terms CASCADE;
                DROP TABLE IF EXISTS kse_index_terms CASCADE;
                DROP TABLE IF EXISTS kse_pages CASCADE;
                DROP TABLE IF EXISTS kse_domains CASCADE;
            """)
            self.connection.commit()
            logger.info(f"✓ Migration {self.name} rolled back")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
