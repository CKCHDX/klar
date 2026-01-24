"""
Tests for KSE Database Module
"""

import pytest
import os
from kse.database import (
    KSEDatabase,
    initialize_database,
    get_db_connection,
)
from kse.database.kse_queries import KSEQueries
from kse.database.kse_domains_loader import SwedishDomainsLoader


@pytest.fixture
def test_db():
    """
    Create test database fixture.
    """
    # Use environment variables for test database
    db = KSEDatabase(
        host=os.getenv("KSE_TEST_DB_HOST", "localhost"),
        port=int(os.getenv("KSE_TEST_DB_PORT", 5432)),
        database=os.getenv("KSE_TEST_DB_NAME", "kse_test"),
        user=os.getenv("KSE_TEST_DB_USER", "postgres"),
        password=os.getenv("KSE_TEST_DB_PASSWORD", "postgres"),
    )
    
    # Connect and initialize schema
    if db.connect():
        db.drop_schema()  # Clean slate for tests
        db.create_schema()
        yield db
        db.disconnect()
    else:
        pytest.skip("Could not connect to test database")


class TestDatabaseConnection:
    """Test database connection."""
    
    def test_connect_to_database(self, test_db):
        """Test database connection."""
        assert test_db.conn is not None
    
    def test_disconnect_from_database(self, test_db):
        """Test database disconnection."""
        test_db.disconnect()
        assert test_db.conn is None
    
    def test_schema_verification(self, test_db):
        """Test schema verification."""
        stats = test_db.verify_schema()
        assert "domains" in stats
        assert "pages" in stats
        assert "terms" in stats
        assert "inverted_index" in stats


class TestDomainQueries:
    """Test domain-related queries."""
    
    def test_load_domains(self, test_db):
        """Test loading Swedish domains."""
        loader = SwedishDomainsLoader(test_db)
        loaded = loader.load_sample_domains()
        assert loaded > 0
    
    def test_get_pending_domains(self, test_db):
        """Test getting pending domains for crawling."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        pending = queries.get_pending_domains(limit=10)
        
        assert len(pending) > 0
        assert all("url" in d for d in pending)
        assert all("trust_score" in d for d in pending)
    
    def test_update_domain_crawl_time(self, test_db):
        """Test updating domain crawl time."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        domain = queries.get_pending_domains(limit=1)[0]
        
        success = queries.update_domain_crawl_time(domain["id"], status="active")
        assert success
    
    def test_get_high_trust_domains(self, test_db):
        """Test getting high-trust domains."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        high_trust = loader.get_high_trust_domains(min_trust=0.9)
        assert len(high_trust) > 0
        assert all(d["trust_score"] >= 0.9 for d in high_trust)


class TestPageQueries:
    """Test page-related queries."""
    
    def test_insert_page(self, test_db):
        """Test inserting a page."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        
        page_id = queries.insert_page(
            domain_id=1,
            url="https://example.se/page1",
            title="Test Page",
            description="Test description",
            content="This is test content",
            content_hash="abc123",
            status_code=200,
            content_type="text/html",
            size_bytes=1024,
        )
        
        assert page_id is not None
    
    def test_get_unindexed_pages(self, test_db):
        """Test getting unindexed pages."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        
        # Insert a page
        queries.insert_page(
            domain_id=1,
            url="https://example.se/page1",
            title="Test Page",
            description="Test description",
            content="This is test content",
            content_hash="abc123",
            status_code=200,
            content_type="text/html",
            size_bytes=1024,
        )
        
        # Get unindexed pages
        unindexed = queries.get_unindexed_pages(limit=10)
        assert len(unindexed) > 0
    
    def test_mark_page_indexed(self, test_db):
        """Test marking page as indexed."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        
        # Insert a page
        page_id = queries.insert_page(
            domain_id=1,
            url="https://example.se/page1",
            title="Test Page",
            description="Test description",
            content="This is test content",
            content_hash="abc123",
            status_code=200,
            content_type="text/html",
            size_bytes=1024,
        )
        
        # Mark as indexed
        success = queries.mark_page_indexed(page_id)
        assert success


class TestTermQueries:
    """Test term/index queries."""
    
    def test_insert_or_get_term(self, test_db):
        """Test inserting/getting terms."""
        queries = KSEQueries(test_db)
        
        term_id1 = queries.insert_or_get_term("test")
        term_id2 = queries.insert_or_get_term("test")
        
        assert term_id1 is not None
        assert term_id2 is not None
        assert term_id1 == term_id2  # Should return same ID
    
    def test_insert_inverted_index(self, test_db):
        """Test inserting into inverted index."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        
        # Insert page
        page_id = queries.insert_page(
            domain_id=1,
            url="https://example.se/page1",
            title="Test Page",
            description="Test description",
            content="This is test content",
            content_hash="abc123",
            status_code=200,
            content_type="text/html",
            size_bytes=1024,
        )
        
        # Insert term and index
        term_id = queries.insert_or_get_term("test")
        success = queries.insert_inverted_index(
            term_id=term_id,
            page_id=page_id,
            position=0,
            field="content",
            tf_idf_score=0.85,
        )
        
        assert success
    
    def test_search_inverted_index(self, test_db):
        """Test searching inverted index."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        
        # Insert page
        page_id = queries.insert_page(
            domain_id=1,
            url="https://example.se/page1",
            title="Test Page",
            description="Test description",
            content="This is test content",
            content_hash="abc123",
            status_code=200,
            content_type="text/html",
            size_bytes=1024,
        )
        
        # Insert term and index
        term_id = queries.insert_or_get_term("test")
        queries.insert_inverted_index(
            term_id=term_id,
            page_id=page_id,
            position=0,
            field="content",
            tf_idf_score=0.85,
        )
        
        # Search
        results = queries.search_inverted_index(term_id, limit=10)
        assert len(results) > 0
        assert results[0]["page_id"] == page_id


class TestCrawlQueue:
    """Test crawl queue operations."""
    
    def test_add_to_crawl_queue(self, test_db):
        """Test adding URLs to crawl queue."""
        queries = KSEQueries(test_db)
        
        success = queries.add_to_crawl_queue(
            url="https://example.se/page1",
            domain_id=1,
            priority=5,
        )
        
        assert success
    
    def test_get_next_url_to_crawl(self, test_db):
        """Test getting next URL from queue."""
        queries = KSEQueries(test_db)
        
        # Add URLs
        queries.add_to_crawl_queue("https://example1.se", priority=5)
        queries.add_to_crawl_queue("https://example2.se", priority=10)
        
        # Get next (should be highest priority)
        url = queries.get_next_url_to_crawl()
        assert url is not None
        assert url["url"] in ["https://example1.se", "https://example2.se"]
    
    def test_mark_url_crawled(self, test_db):
        """Test marking URL as crawled."""
        queries = KSEQueries(test_db)
        
        # Add URL
        queries.add_to_crawl_queue("https://example.se", priority=5)
        
        # Get and mark as done
        url = queries.get_next_url_to_crawl()
        success = queries.mark_url_crawled(url["id"], success=True)
        assert success


class TestStatistics:
    """Test statistics operations."""
    
    def test_log_crawl_event(self, test_db):
        """Test logging crawl events."""
        queries = KSEQueries(test_db)
        
        success = queries.log_crawl_event(
            event_type="fetched",
            domain_id=1,
            url="https://example.se",
            status_code=200,
            duration_ms=150,
            message="Successfully fetched",
        )
        
        assert success
    
    def test_get_statistics(self, test_db):
        """Test getting database statistics."""
        loader = SwedishDomainsLoader(test_db)
        loader.load_sample_domains()
        
        queries = KSEQueries(test_db)
        stats = queries.get_statistics()
        
        assert stats["total_domains"] > 0
        assert stats["total_pages"] == 0  # No pages inserted yet
        assert stats["total_terms"] == 0  # No terms inserted yet


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
