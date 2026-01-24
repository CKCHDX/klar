"""
Database Connection Manager

Handles PostgreSQL connection pooling with psycopg2.
Provides thread-safe connection management and resource cleanup.
"""

import logging
import os
from typing import Optional, Dict, Any
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2 import pool
except ImportError:
    raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


class DatabaseConnection:
    """
    Manages PostgreSQL database connections and connection pooling.
    
    Attributes:
        host (str): Database host
        port (int): Database port
        database (str): Database name
        user (str): Database user
        password (str): Database password
        min_connections (int): Minimum pool size
        max_connections (int): Maximum pool size
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "kse_db",
        user: str = "postgres",
        password: str = "postgres",
        min_connections: int = 2,
        max_connections: int = 20,
    ):
        """Initialize database connection configuration."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        
    def initialize_pool(self) -> None:
        """Create and initialize connection pool."""
        try:
            self._pool = pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=5,
            )
            logger.info(
                f"Database connection pool initialized. "
                f"Size: {self.min_connections}-{self.max_connections} connections"
            )
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """Get a connection from the pool."""
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call initialize_pool() first.")
        
        try:
            conn = self._pool.getconn()
            logger.debug(f"Connection retrieved from pool. Available: {self._pool.closed}")
            return conn
        except pool.PoolError as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise
    
    def return_connection(self, conn: psycopg2.extensions.connection) -> None:
        """Return a connection to the pool."""
        if self._pool is None:
            logger.warning("Attempted to return connection but pool is not initialized")
            return
        
        try:
            self._pool.putconn(conn)
            logger.debug("Connection returned to pool")
        except pool.PoolError as e:
            logger.error(f"Failed to return connection to pool: {e}")
    
    @contextmanager
    def get_connection_context(self):
        """Context manager for getting and returning connections.
        
        Usage:
            with db_connection.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM kse_domains")
        """
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)
    
    def close_pool(self) -> None:
        """Close all connections in the pool."""
        if self._pool is not None:
            try:
                self._pool.closeall()
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")
        self._pool = None
    
    def __del__(self):
        """Ensure pool is closed when object is destroyed."""
        self.close_pool()


def get_connection_pool(
    host: str = "localhost",
    port: int = 5432,
    database: str = "kse_db",
    user: str = "postgres",
    password: str = "postgres",
    min_connections: int = 2,
    max_connections: int = 20,
) -> DatabaseConnection:
    """Get or create global connection pool.
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
        min_connections: Minimum pool size
        max_connections: Maximum pool size
    
    Returns:
        DatabaseConnection: Global connection pool instance
    """
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = DatabaseConnection(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            min_connections=min_connections,
            max_connections=max_connections,
        )
        _connection_pool.initialize_pool()
    
    return _connection_pool


def close_connection_pool() -> None:
    """Close global connection pool."""
    global _connection_pool
    
    if _connection_pool is not None:
        _connection_pool.close_pool()
        _connection_pool = None
        logger.info("Global connection pool closed")


def test_connection(
    host: str = "localhost",
    port: int = 5432,
    database: str = "kse_db",
    user: str = "postgres",
    password: str = "postgres",
) -> bool:
    """Test database connection without pooling.
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"Database connection successful. Version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return False
