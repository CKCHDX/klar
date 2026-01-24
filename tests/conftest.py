"""
Pytest Configuration and Fixtures

Provides fixtures for database testing and common test utilities.
"""

import pytest
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kse.database import (
    DatabaseConnection,
    DatabaseSchema,
    DomainLoader,
    Repository,
)

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def test_db_config():
    """Database configuration for testing."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "kse_test_db",
        "user": "postgres",
        "password": "postgres",
    }


@pytest.fixture(scope="function")
def db_connection(test_db_config):
    """Create test database connection."""
    conn = DatabaseConnection(**test_db_config)
    conn.initialize_pool()
    yield conn
    conn.close_pool()


@pytest.fixture(scope="function")
def test_schema(db_connection):
    """Create test database schema."""
    with db_connection.get_connection_context() as conn:
        schema = DatabaseSchema(conn)
        schema.drop_schema(confirm=True)  # Clean slate
        schema.create_schema()
        yield schema


@pytest.fixture(scope="function")
def test_loader(db_connection):
    """Create domain loader for testing."""
    with db_connection.get_connection_context() as conn:
        loader = DomainLoader(conn)
        yield loader


@pytest.fixture(scope="function")
def test_repository(db_connection):
    """Create repository for testing."""
    with db_connection.get_connection_context() as conn:
        repo = Repository(conn)
        yield repo


@pytest.fixture(scope="function")
def populated_db(test_schema, test_loader, db_connection):
    """Create database with test data."""
    with db_connection.get_connection_context() as conn:
        loader = DomainLoader(conn)
        loader.load_domains(clear_existing=True)
    yield db_connection


@pytest.fixture(autouse=True)
def reset_db_after_test(db_connection, request):
    """Reset database after each test."""
    yield
    # Cleanup
    with db_connection.get_connection_context() as conn:
        cursor = conn.cursor()
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
            conn.commit()
        except Exception:
            conn.rollback()
