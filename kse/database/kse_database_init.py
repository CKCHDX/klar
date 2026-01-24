"""
KSE Database Initialization

Handles PostgreSQL connection, schema creation, and database setup.
"""

import psycopg2
from psycopg2 import sql, Error
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

from .kse_schema import SCHEMA_TABLES, SCHEMA_INDEXES, create_schema
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class KSEDatabase:
    """PostgreSQL database connection and management."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "kse",
        user: str = "postgres",
        password: str = "postgres",
    ):
        """
        Initialize database connection parameters.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Username
            password: Password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
    
    def connect(self) -> bool:
        """
        Connect to PostgreSQL database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            logger.info(f"✅ Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")
            return True
        except Error as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from PostgreSQL")
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor.
        
        Yields:
            Cursor object
        """
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Cursor object
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """
        Fetch one result.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            One row or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """
        Fetch all results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def create_schema(self) -> bool:
        """
        Create database schema (all tables).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            statements = create_schema()
            
            with self.get_cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
                    table_name = statement.split()[5] if len(statement.split()) > 5 else "unknown"
                    logger.info(f"✅ Created table: {table_name}")
            
            # Create indexes
            self._create_indexes()
            
            logger.info("✅ Database schema created successfully")
            return True
            
        except Error as e:
            logger.error(f"❌ Failed to create schema: {e}")
            return False
    
    def _create_indexes(self) -> None:
        """
        Create database indexes for performance.
        """
        indexes_created = 0
        
        for table_name, index_list in SCHEMA_INDEXES.items():
            for column, index_name in index_list:
                try:
                    sql_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column});"
                    self.execute(sql_query)
                    indexes_created += 1
                except Error as e:
                    logger.warning(f"Failed to create index {index_name}: {e}")
        
        logger.info(f"✅ Created {indexes_created} indexes")
    
    def drop_schema(self) -> bool:
        """
        Drop all tables (USE WITH CAUTION!).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                # Drop in reverse order to avoid foreign key issues
                for table in reversed(SCHEMA_TABLES):
                    cursor.execute(f"DROP TABLE IF EXISTS {table.name} CASCADE;")
                    logger.info(f"Dropped table: {table.name}")
            
            logger.info("✅ Database schema dropped")
            return True
        except Error as e:
            logger.error(f"❌ Failed to drop schema: {e}")
            return False
    
    def verify_schema(self) -> Dict[str, int]:
        """
        Verify that all tables exist and count rows.
        
        Returns:
            Dictionary with table names and row counts
        """
        stats = {}
        try:
            for table in SCHEMA_TABLES:
                query = f"SELECT COUNT(*) FROM {table.name};"
                result = self.fetch_one(query)
                row_count = result[0] if result else 0
                stats[table.name] = row_count
                logger.info(f"✅ {table.name}: {row_count} rows")
        except Error as e:
            logger.error(f"❌ Error verifying schema: {e}")
        
        return stats


def initialize_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "kse",
    user: str = "postgres",
    password: str = "postgres",
    drop_existing: bool = False,
) -> Optional[KSEDatabase]:
    """
    Initialize the KSE database.
    
    Args:
        host: PostgreSQL host
        port: PostgreSQL port
        database: Database name
        user: Username
        password: Password
        drop_existing: If True, drop and recreate schema
        
    Returns:
        KSEDatabase instance if successful, None otherwise
    """
    logger.info("="*60)
    logger.info("KSE Database Initialization")
    logger.info("="*60)
    
    db = KSEDatabase(host, port, database, user, password)
    
    # Connect
    if not db.connect():
        return None
    
    # Drop existing if requested
    if drop_existing:
        logger.warning("⚠️  Dropping existing schema...")
        db.drop_schema()
    
    # Create schema
    if not db.create_schema():
        db.disconnect()
        return None
    
    # Verify
    stats = db.verify_schema()
    logger.info(f"✅ Database initialized with {len(stats)} tables")
    
    return db


def get_db_connection(
    host: str = "localhost",
    port: int = 5432,
    database: str = "kse",
    user: str = "postgres",
    password: str = "postgres",
) -> Optional[KSEDatabase]:
    """
    Get a database connection without initializing.
    
    Args:
        Same as initialize_database
        
    Returns:
        KSEDatabase instance if successful, None otherwise
    """
    db = KSEDatabase(host, port, database, user, password)
    if db.connect():
        return db
    return None
