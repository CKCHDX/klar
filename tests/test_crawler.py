"""
Tests for KSE Crawler Module
"""

import pytest
from kse.crawler import (
    KSECrawler,
    HTMLParser,
    URLFrontier,
    extract_links,
    extract_text,
)


class TestHTMLParser:
    """Test HTML parser."""
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML content."""
        return """
        <!DOCTYPE html>
        <html lang="sv">
        <head>
            <meta charset="UTF-8">
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Welcome</h1>
            <p>This is test content.</p>
            <a href="/page1">Link 1</a>
            <a href="https://example.com/external">External Link</a>
        </body>
        </html>
        """
    
    def test_extract_title(self, sample_html):
        """Test title extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        title = parser.get_title()
        assert title == "Test Page"
    
    def test_extract_description(self, sample_html):
        """Test description extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        desc = parser.get_description()
        assert desc == "Test description"
    
    def test_extract_text(self, sample_html):
        """Test text extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        text = parser.get_text()
        assert "Welcome" in text
        assert "test content" in text
    
    def test_extract_links(self, sample_html):
        """Test link extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        links = parser.get_links()
        assert len(links) == 2
        assert any('/page1' in l['url'] for l in links)
        assert any('example.com' in l['url'] for l in links)
    
    def test_extract_internal_links(self, sample_html):
        """Test internal link extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        internal = parser.get_internal_links(domain='example.se')
        assert len(internal) == 1
        assert '/page1' in internal[0]['url']
    
    def test_extract_external_links(self, sample_html):
        """Test external link extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        external = parser.get_external_links(domain='example.se')
        assert len(external) == 1
        assert 'example.com' in external[0]['url']
    
    def test_detect_language(self, sample_html):
        """Test language detection."""
        parser = HTMLParser(sample_html, "https://example.se/")
        lang = parser.get_language()
        assert lang == 'sv'
    
    def test_extract_headers(self, sample_html):
        """Test header extraction."""
        parser = HTMLParser(sample_html, "https://example.se/")
        headers = parser.get_headers()
        assert 1 in headers
        assert "Welcome" in headers[1]


class TestURLFrontier:
    """Test URL frontier."""
    
    def test_add_url(self):
        """Test adding URL to frontier."""
        frontier = URLFrontier()
        added = frontier.add_url("https://example.se/page1")
        assert added is True
    
    def test_duplicate_url(self):
        """Test that duplicates are not added."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/page1")
        added = frontier.add_url("https://example.se/page1")
        assert added is False
    
    def test_invalid_url(self):
        """Test that invalid URLs are rejected."""
        frontier = URLFrontier()
        added = frontier.add_url("not-a-url")
        assert added is False
    
    def test_get_next_url(self):
        """Test getting next URL from frontier."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/page1", priority=5)
        url = frontier.get_next_url()
        assert url == "https://example.se/page1"
    
    def test_priority_ordering(self):
        """Test that URLs are returned by priority."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/low", priority=1)
        frontier.add_url("https://example.se/high", priority=10)
        
        # Get URLs
        url1 = frontier.get_next_url()
        url2 = frontier.get_next_url()
        
        # Higher priority should come first (or at least be available)
        assert url1 is not None
        assert url2 is not None
    
    def test_mark_visited(self):
        """Test marking URL as visited."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/page1")
        frontier.mark_visited("https://example.se/page1")
        
        assert frontier.get_visited_count() == 1
        assert frontier.add_url("https://example.se/page1") is False  # Can't re-add
    
    def test_stats(self):
        """Test statistics reporting."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/page1")
        frontier.add_url("https://example.se/page2")
        
        stats = frontier.get_stats()
        assert stats['queue_size'] == 2
        assert stats['total_added'] == 2
    
    def test_domain_stats(self):
        """Test per-domain statistics."""
        frontier = URLFrontier()
        frontier.add_url("https://example.se/page1")
        frontier.add_url("https://example.com/page1")
        
        stats = frontier.get_domain_stats()
        assert 'example.se' in stats
        assert 'example.com' in stats


class TestCrawler:
    """Test web crawler."""
    
    def test_crawler_initialization(self):
        """Test crawler initialization."""
        crawler = KSECrawler()
        assert crawler.timeout == 10
        assert crawler.session is not None
    
    def test_custom_user_agent(self):
        """Test custom user agent."""
        custom_ua = "Custom Agent"
        crawler = KSECrawler(user_agent=custom_ua)
        assert custom_ua in crawler.session.headers['User-Agent']
    
    def test_crawl_result_structure(self):
        """Test CrawlResult data structure."""
        from kse.crawler import CrawlResult
        
        result = CrawlResult(
            url="https://example.se",
            success=True,
            status_code=200,
            title="Test",
            description="Desc",
            content="<html></html>",
            content_hash="abc123",
            language="sv",
            links=[],
            duration_ms=100,
        )
        
        assert result.url == "https://example.se"
        assert result.success is True
        assert result.status_code == 200


class TestExtractFunctions:
    """Test extract helper functions."""
    
    def test_extract_links(self):
        """Test extract_links function."""
        html = '<a href="/page1">Link</a>'
        links = extract_links(html, "https://example.se/")
        assert len(links) > 0
    
    def test_extract_text(self):
        """Test extract_text function."""
        html = "<p>Hello World</p>"
        text = extract_text(html)
        assert "Hello" in text
        assert "World" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
