"""
Database Layer Tests

Tests for connection pooling, schema management, and data access.
"""

import pytest
from kse.database import DatabaseConnection, DatabaseSchema, DomainLoader, Repository
from kse.core import DatabaseException, SchemaException


class TestDatabaseConnection:
    """Test database connection pooling."""
    
    def test_connection_pool_initialization(self, db_connection):
        """Test that connection pool initializes correctly."""
        assert db_connection._pool is not None
    
    def test_get_connection(self, db_connection):
        """Test getting connection from pool."""
        conn = db_connection.get_connection()
        assert conn is not None
        db_connection.return_connection(conn)
    
    def test_context_manager(self, db_connection):
        """Test connection context manager."""
        with db_connection.get_connection_context() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()


class TestDatabaseSchema:
    """Test database schema creation and management."""
    
    def test_schema_creation(self, test_schema):
        """Test that all tables are created."""
        validation = test_schema.validate_schema()
        assert all(validation.values()), f"Schema validation failed: {validation}"
    
    def test_all_tables_exist(self, test_schema):
        """Test existence of all required tables."""
        expected_tables = [
            "kse_domains",
            "kse_pages",
            "kse_index_terms",
            "kse_page_terms",
            "kse_crawl_stats",
            "kse_search_queries",
            "kse_index_snapshots",
            "kse_system_logs",
        ]
        
        validation = test_schema.validate_schema()
        for table in expected_tables:
            assert table in validation, f"Table {table} not found"
            assert validation[table], f"Table {table} does not exist"
    
    def test_schema_constraints(self, test_schema, db_connection):
        """Test that constraints are properly defined."""
        with db_connection.get_connection_context() as conn:
            cursor = conn.cursor()
            
            # Test domain unique constraint
            cursor.execute("""
                INSERT INTO kse_domains (domain_name, domain_url, category, trust_score)
                VALUES ('Test', 'https://test.com', 'Test', 0.5);
            """)
            conn.commit()
            
            # Attempt duplicate should fail
            with pytest.raises(Exception):
                cursor.execute("""
                    INSERT INTO kse_domains (domain_name, domain_url, category, trust_score)
                    VALUES ('Test2', 'https://test.com', 'Test', 0.5);
                """)
                conn.commit()
            
            conn.rollback()
            cursor.close()


class TestDomainLoader:
    """Test domain loading functionality."""
    
    def test_load_domains(self, test_schema, test_loader, db_connection):
        """Test loading Swedish domains."""
        with db_connection.get_connection_context() as conn:
            loader = DomainLoader(conn)
            success = loader.load_domains()
            assert success
            assert loader.get_domain_count() > 0
    
    def test_domain_count(self, populated_db):
        """Test that correct number of domains are loaded."""
        with populated_db.get_connection_context() as conn:
            loader = DomainLoader(conn)
            count = loader.get_domain_count()
            # Should have loaded at least the sample domains
            assert count >= 10, f"Expected at least 10 domains, got {count}"
    
    def test_get_active_domains(self, populated_db):
        """Test retrieving active domains."""
        with populated_db.get_connection_context() as conn:
            loader = DomainLoader(conn)
            active = loader.get_active_domains()
            assert len(active) > 0
            assert all(d['id'] > 0 for d in active)
            assert all(d['name'] for d in active)
            assert all(d['url'] for d in active)
    
    def test_get_domains_needing_crawl(self, populated_db):
        """Test getting domains that need crawling."""
        with populated_db.get_connection_context() as conn:
            loader = DomainLoader(conn)
            to_crawl = loader.get_domains_needing_crawl(limit=5)
            assert len(to_crawl) > 0
            assert len(to_crawl) <= 5


class TestRepository:
    """Test data repository functionality."""
    
    def test_add_domain(self, test_schema, test_repository, db_connection):
        """Test adding a domain."""
        with db_connection.get_connection_context() as conn:
            repo = Repository(conn)
            domain_id = repo.add_domain(
                name="Test Domain",
                url="https://test-example.com",
                category="Test",
                trust=0.8
            )
            assert domain_id is not None
            assert domain_id > 0
    
    def test_get_domain(self, test_schema, test_repository, db_connection):
        """Test retrieving a domain."""
        with db_connection.get_connection_context() as conn:
            repo = Repository(conn)
            domain_id = repo.add_domain(
                name="Test Domain 2",
                url="https://test-domain-2.com",
                trust=0.7
            )
            
            domain = repo.get_domain(domain_id)
            assert domain is not None
            assert domain['name'] == "Test Domain 2"
            assert domain['trust'] == 0.7
    
    def test_add_page(self, test_schema, populated_db):
        """Test adding a page."""
        with populated_db.get_connection_context() as conn:
            repo = Repository(conn)
            loader = DomainLoader(conn)
            
            # Get first domain
            domains = loader.get_active_domains()
            assert len(domains) > 0
            domain_id = domains[0]['id']
            
            page_id = repo.add_page(
                domain_id=domain_id,
                url="https://example.com/page",
                title="Test Page",
                description="Test page description",
                content_text="Test page content"
            )
            assert page_id is not None
            assert page_id > 0
    
    def test_get_statistics(self, populated_db):
        """Test getting system statistics."""
        with populated_db.get_connection_context() as conn:
            repo = Repository(conn)
            stats = repo.get_statistics()
            
            assert 'domains' in stats
            assert 'pages' in stats
            assert 'terms' in stats
            assert stats['domains'] > 0
            assert stats['indexing_percentage'] >= 0
    
    def test_page_count(self, test_schema, populated_db):
        """Test page counting."""
        with populated_db.get_connection_context() as conn:
            repo = Repository(conn)
            
            # Initially 0 pages
            assert repo.get_page_count() == 0
            
            loader = DomainLoader(conn)
            domains = loader.get_active_domains()
            
            # Add some pages
            for i in range(5):
                repo.add_page(
                    domain_id=domains[0]['id'],
                    url=f"https://example.com/page{i}",
                    title=f"Page {i}"
                )
            
            assert repo.get_page_count() == 5


class TestDatabaseIntegration:
    """Integration tests for database layer."""
    
    def test_full_initialization_flow(self, test_db_config):
        """Test complete database initialization flow."""
        # Create connection
        db_conn = DatabaseConnection(**test_db_config)
        db_conn.initialize_pool()
        
        with db_conn.get_connection_context() as conn:
            # Create schema
            schema = DatabaseSchema(conn)
            schema.drop_schema(confirm=True)
            assert schema.create_schema()
            
            # Load domains
            loader = DomainLoader(conn)
            assert loader.load_domains()
            
            # Add pages
            repo = Repository(conn)
            domains = loader.get_active_domains()
            assert len(domains) > 0
            
            page_id = repo.add_page(
                domain_id=domains[0]['id'],
                url="https://integration-test.com",
                title="Integration Test"
            )
            assert page_id is not None
            
            # Verify stats
            stats = repo.get_statistics()
            assert stats['domains'] > 0
            assert stats['pages'] == 1
        
        db_conn.close_pool()
