"""
Database Schema Manager

Handles PostgreSQL schema creation, validation, and migrations.
Defines all tables, indexes, and constraints for KSE.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    raise ImportError("psycopg2 is required")

logger = logging.getLogger(__name__)


class DatabaseSchema:
    """
    Manages PostgreSQL database schema creation and validation.
    
    Handles:
    - Table creation with proper types and constraints
    - Index creation for performance
    - Foreign key relationships
    - Constraint enforcement
    """
    
    def __init__(self, connection):
        """Initialize schema manager with database connection.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
    
    def create_schema(self) -> bool:
        """Create complete KSE database schema.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Create domains table
            self._create_domains_table(cursor)
            
            # Create pages table
            self._create_pages_table(cursor)
            
            # Create index terms table
            self._create_index_terms_table(cursor)
            
            # Create page terms table (inverted index)
            self._create_page_terms_table(cursor)
            
            # Create crawl stats table
            self._create_crawl_stats_table(cursor)
            
            # Create search queries table (for analytics)
            self._create_search_queries_table(cursor)
            
            # Create index snapshots table
            self._create_index_snapshots_table(cursor)
            
            # Create system logs table
            self._create_system_logs_table(cursor)
            
            # Create all indexes
            self._create_indexes(cursor)
            
            # Commit all changes
            self.connection.commit()
            logger.info("Database schema created successfully")
            cursor.close()
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error creating database schema: {e}")
            self.connection.rollback()
            return False
    
    def _create_domains_table(self, cursor) -> None:
        """Create domains table (2,543 Swedish domains)."""
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
        logger.info("Created kse_domains table")
    
    def _create_pages_table(self, cursor) -> None:
        """Create pages table for crawled content (2.8M+ pages)."""
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
        logger.info("Created kse_pages table")
    
    def _create_index_terms_table(self, cursor) -> None:
        """Create inverted index terms table."""
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
        logger.info("Created kse_index_terms table")
    
    def _create_page_terms_table(self, cursor) -> None:
        """Create page-term inverted index mapping."""
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
        logger.info("Created kse_page_terms table")
    
    def _create_crawl_stats_table(self, cursor) -> None:
        """Create crawling statistics table."""
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
        logger.info("Created kse_crawl_stats table")
    
    def _create_search_queries_table(self, cursor) -> None:
        """Create search query analytics table."""
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
        logger.info("Created kse_search_queries table")
    
    def _create_index_snapshots_table(self, cursor) -> None:
        """Create index snapshot metadata table."""
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
        logger.info("Created kse_index_snapshots table")
    
    def _create_system_logs_table(self, cursor) -> None:
        """Create system logs table for monitoring and debugging."""
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
        logger.info("Created kse_system_logs table")
    
    def _create_indexes(self, cursor) -> None:
        """Create performance indexes on critical tables."""
        indexes = [
            # Domains indexes
            ("idx_domains_domain_name", "CREATE INDEX IF NOT EXISTS idx_domains_domain_name ON kse_domains(domain_name);"),
            ("idx_domains_is_active", "CREATE INDEX IF NOT EXISTS idx_domains_is_active ON kse_domains(is_active);"),
            ("idx_domains_next_crawl", "CREATE INDEX IF NOT EXISTS idx_domains_next_crawl ON kse_domains(next_crawl_at) WHERE is_active = TRUE;"),
            
            # Pages indexes
            ("idx_pages_domain_id", "CREATE INDEX IF NOT EXISTS idx_pages_domain_id ON kse_pages(domain_id);"),
            ("idx_pages_url", "CREATE INDEX IF NOT EXISTS idx_pages_url ON kse_pages(url);"),
            ("idx_pages_is_indexed", "CREATE INDEX IF NOT EXISTS idx_pages_is_indexed ON kse_pages(is_indexed);"),
            ("idx_pages_content_hash", "CREATE INDEX IF NOT EXISTS idx_pages_content_hash ON kse_pages(content_hash);"),
            ("idx_pages_page_rank", "CREATE INDEX IF NOT EXISTS idx_pages_page_rank ON kse_pages(page_rank DESC);"),
            
            # Index terms indexes
            ("idx_terms_term", "CREATE INDEX IF NOT EXISTS idx_terms_term ON kse_index_terms(term);"),
            ("idx_terms_term_type", "CREATE INDEX IF NOT EXISTS idx_terms_term_type ON kse_index_terms(term_type);"),
            
            # Page terms indexes
            ("idx_page_terms_page_id", "CREATE INDEX IF NOT EXISTS idx_page_terms_page_id ON kse_page_terms(page_id);"),
            ("idx_page_terms_term_id", "CREATE INDEX IF NOT EXISTS idx_page_terms_term_id ON kse_page_terms(term_id);"),
            ("idx_page_terms_tf_idf", "CREATE INDEX IF NOT EXISTS idx_page_terms_tf_idf ON kse_page_terms(tf_idf DESC);"),
            
            # Search queries indexes
            ("idx_search_queries_text", "CREATE INDEX IF NOT EXISTS idx_search_queries_text ON kse_search_queries(query_text);"),
            ("idx_search_queries_created", "CREATE INDEX IF NOT EXISTS idx_search_queries_created ON kse_search_queries(created_at);"),
            
            # System logs indexes
            ("idx_logs_level", "CREATE INDEX IF NOT EXISTS idx_logs_level ON kse_system_logs(log_level);"),
            ("idx_logs_created", "CREATE INDEX IF NOT EXISTS idx_logs_created ON kse_system_logs(created_at DESC);"),
        ]
        
        for idx_name, idx_sql in indexes:
            try:
                cursor.execute(idx_sql)
                logger.debug(f"Created index: {idx_name}")
            except psycopg2.Error as e:
                logger.warning(f"Index {idx_name} creation skipped: {e}")
    
    def drop_schema(self, confirm: bool = False) -> bool:
        """Drop entire database schema (careful!).
        
        Args:
            confirm: Must be True to actually drop
        
        Returns:
            bool: True if successful
        """
        if not confirm:
            logger.warning("Schema drop not confirmed. Pass confirm=True to proceed.")
            return False
        
        try:
            cursor = self.connection.cursor()
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
            logger.warning("Database schema dropped")
            cursor.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"Error dropping schema: {e}")
            self.connection.rollback()
            return False
    
    def validate_schema(self) -> Dict[str, bool]:
        """Validate that all required tables exist.
        
        Returns:
            dict: Status of each table
        """
        required_tables = [
            "kse_domains",
            "kse_pages",
            "kse_index_terms",
            "kse_page_terms",
            "kse_crawl_stats",
            "kse_search_queries",
            "kse_index_snapshots",
            "kse_system_logs",
        ]
        
        status = {}
        cursor = self.connection.cursor()
        
        for table in required_tables:
            try:
                cursor.execute(
                    f"SELECT to_regclass('public.{table}');"
                )
                exists = cursor.fetchone()[0] is not None
                status[table] = exists
            except psycopg2.Error:
                status[table] = False
        
        cursor.close()
        return status
