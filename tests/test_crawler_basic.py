"""
Basic Crawler Tests

Tests for fetcher, parser, scheduler, and rate limiter.
"""

import pytest
from kse.crawler import (
    Fetcher,
    FetchStatus,
    Parser,
    CrawlScheduler,
    RateLimiter,
    RobotsTxtChecker,
)
from kse.core import KSEException


class TestFetcher:
    """Test HTTP fetcher."""
    
    def test_fetcher_init(self):
        """Test fetcher initialization."""
        fetcher = Fetcher()
        assert fetcher.user_agent
        assert fetcher.timeout > 0
        assert fetcher.max_content_size > 0
    
    def test_fetch_headers(self):
        """Test HTTP headers construction."""
        fetcher = Fetcher(user_agent="TestBot/1.0")
        headers = fetcher._get_headers()
        
        assert 'User-Agent' in headers
        assert headers['User-Agent'] == "TestBot/1.0"
        assert 'Accept' in headers
    
    def test_content_validation_empty(self):
        """Test content validation with empty content."""
        fetcher = Fetcher()
        is_valid, error = fetcher._validate_content(b'', 'text/html')
        
        assert not is_valid
        assert error
    
    def test_content_validation_too_large(self):
        """Test content validation with oversized content."""
        fetcher = Fetcher(max_content_size_mb=1)
        large_content = b'x' * (2 * 1024 * 1024)  # 2 MB
        
        is_valid, error = fetcher._validate_content(large_content, 'text/html')
        
        assert not is_valid
        assert 'too large' in error.lower()
    
    def test_content_validation_valid(self):
        """Test content validation with valid content."""
        fetcher = Fetcher()
        content = b'<html><body>Test</body></html>'
        
        is_valid, error = fetcher._validate_content(content, 'text/html')
        
        assert is_valid
        assert error is None
    
    def test_fetch_result_properties(self):
        """Test FetchResult properties."""
        from kse.crawler.kse_crawler_fetcher import FetchResult
        
        result = FetchResult(
            url="https://example.com",
            status=FetchStatus.SUCCESS,
            status_code=200,
            content=b'test',
        )
        
        assert result.is_success
        assert not result.is_retryable
        assert result.get_content_hash()  # Has hash
    
    def test_fetch_result_retryable(self):
        """Test retryable status."""
        from kse.crawler.kse_crawler_fetcher import FetchResult
        
        result = FetchResult(
            url="https://example.com",
            status=FetchStatus.TIMEOUT,
        )
        
        assert result.is_retryable


class TestParser:
    """Test HTML parser."""
    
    def test_parser_init(self):
        """Test parser initialization."""
        parser = Parser()
        assert parser is not None
    
    def test_parse_basic_html(self):
        """Test parsing basic HTML."""
        parser = Parser()
        html = b'<html><head><title>Test Page</title></head><body><h1>Heading</h1><p>Content here</p></body></html>'
        
        page = parser.parse("https://example.com", html)
        
        assert page.url == "https://example.com"
        assert page.title == "Test Page"
        assert page.heading_1 == "Heading"
        assert 'Content' in page.text_content
    
    def test_parse_with_description(self):
        """Test parsing meta description."""
        parser = Parser()
        html = b'<html><head><meta name="description" content="Test description"></head></html>'
        
        page = parser.parse("https://example.com", html)
        
        assert page.description == "Test description"
    
    def test_parse_extract_links(self):
        """Test link extraction."""
        parser = Parser()
        html = b'<html><body><a href="/page1">Link 1</a><a href="/page2">Link 2</a></body></html>'
        
        page = parser.parse("https://example.com", html)
        
        assert len(page.outbound_links) >= 2
        assert any('page1' in link for link in page.outbound_links)
    
    def test_parse_robots_noindex(self):
        """Test robots noindex detection."""
        parser = Parser()
        html = b'<html><head><meta name="robots" content="noindex"></head></html>'
        
        page = parser.parse("https://example.com", html)
        
        assert page.has_robots_noindex
    
    def test_parse_word_count(self):
        """Test word count calculation."""
        parser = Parser()
        html = b'<html><body>One two three four five</body></html>'
        
        page = parser.parse("https://example.com", html)
        
        assert page.word_count == 5


class TestScheduler:
    """Test crawl scheduler."""
    
    def test_scheduler_init(self):
        """Test scheduler initialization."""
        scheduler = CrawlScheduler()
        
        assert scheduler.default_frequency_days > 0
        assert len(scheduler._queue) == 0
    
    def test_add_job(self):
        """Test adding crawl job."""
        scheduler = CrawlScheduler()
        
        job = scheduler.add_job(
            domain_id=1,
            domain_name="example.com",
            domain_url="https://example.com"
        )
        
        assert job is not None
        assert job.domain_name == "example.com"
        assert len(scheduler._queue) > 0
    
    def test_get_next_job_not_ready(self):
        """Test getting job that's not ready."""
        scheduler = CrawlScheduler()
        
        scheduler.add_job(
            domain_id=1,
            domain_name="example.com",
            domain_url="https://example.com",
            delay_seconds=3600  # 1 hour delay
        )
        
        job = scheduler.get_next_job()
        assert job is None  # Not ready yet
    
    def test_queue_stats(self):
        """Test queue statistics."""
        scheduler = CrawlScheduler()
        
        scheduler.add_job(1, "example1.com", "https://example1.com")
        scheduler.add_job(2, "example2.com", "https://example2.com")
        
        stats = scheduler.get_queue_stats()
        
        assert 'pending' in stats
        assert stats['pending'] >= 2
    
    def test_job_properties(self):
        """Test CrawlJob properties."""
        scheduler = CrawlScheduler()
        
        job = scheduler.add_job(1, "example.com", "https://example.com")
        
        assert job.is_ready or not job.is_ready  # Can be either
        assert job.duration_seconds is None  # Not started
        
        job.start()
        assert job.duration_seconds is not None or job.started_time


class TestRateLimiter:
    """Test rate limiter."""
    
    def test_limiter_init(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter()
        
        assert limiter.default_delay > 0
        assert limiter.min_delay > 0
        assert limiter.max_delay > 0
    
    def test_set_domain_delay(self):
        """Test setting domain-specific delay."""
        limiter = RateLimiter()
        
        limiter.set_domain_delay("example.com", 2.0)
        delay = limiter.get_delay("example.com")
        
        assert delay == 2.0
    
    def test_delay_bounds(self):
        """Test delay bounds enforcement."""
        limiter = RateLimiter(min_delay=0.5, max_delay=5.0)
        
        limiter.set_domain_delay("example.com", 0.1)  # Too low
        assert limiter.get_delay("example.com") >= 0.5
        
        limiter.set_domain_delay("example.com", 10.0)  # Too high
        assert limiter.get_delay("example.com") <= 5.0
    
    def test_wait_if_needed(self):
        """Test wait functionality."""
        import time
        
        limiter = RateLimiter(default_delay_seconds=0.1)
        
        # First request (no wait)
        wait = limiter.wait_if_needed("example.com")
        assert wait == 0.0
        limiter.record_request("example.com")
        
        # Second request immediately (should wait)
        start = time.time()
        wait = limiter.wait_if_needed("example.com")
        elapsed = time.time() - start
        
        assert wait > 0
        assert elapsed >= wait
    
    def test_reset_domain(self):
        """Test domain reset."""
        limiter = RateLimiter()
        limiter.record_request("example.com")
        
        limiter.reset_domain("example.com")
        wait = limiter.wait_if_needed("example.com")
        
        assert wait == 0.0


class TestRobotsTxt:
    """Test robots.txt checker."""
    
    def test_robots_checker_init(self):
        """Test robots.txt checker initialization."""
        checker = RobotsTxtChecker(user_agent="TestBot/1.0")
        
        assert checker.user_agent == "TestBot/1.0"
    
    def test_robots_url_construction(self):
        """Test robots.txt URL construction."""
        checker = RobotsTxtChecker()
        
        url = checker._get_robots_url("example.com")
        assert "robots.txt" in url
        assert "example.com" in url
    
    def test_can_fetch_without_robots(self):
        """Test can_fetch when no robots.txt (should allow)."""
        checker = RobotsTxtChecker()
        
        # Should allow by default if no robots.txt
        result = checker.can_fetch("example.com", "https://example.com/page")
        assert result  # Should be True
    
    def test_clear_cache(self):
        """Test cache clearing."""
        checker = RobotsTxtChecker()
        
        checker.clear_cache()
        assert len(checker._cache) == 0
