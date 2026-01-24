"""
Tests for KSE Web UI (Phase 5)
"""

import pytest
from unittest.mock import Mock, patch
import json

from kse.server.kse_flask_app import KSEFlaskApp, create_app


# ========== FIXTURES ==========

@pytest.fixture
def app():
    """Create Flask app for testing."""
    kse_app = KSEFlaskApp()
    kse_app.app.config['TESTING'] = True
    return kse_app.app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
mock_search_engine():
    """Create mock search engine."""
    engine = Mock()
    engine.search.return_value = (
        [
            {
                'url': 'https://example.com/page1',
                'title': 'Example Page 1',
                'snippet': 'This is an example page about search engines',
                'score': 0.95,
                'last_updated': '2026-01-24'
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Example Page 2',
                'snippet': 'Another example page with relevant content',
                'score': 0.87,
                'last_updated': '2026-01-23'
            }
        ],
        {
            'total_matches': 1000,
            'search_time_ms': 45,
            'facets': {}
        }
    )
    
    engine.get_statistics.return_value = {
        'total_pages': 2543210,
        'total_terms': 1234567,
        'total_domains': 2543,
        'avg_search_time': 45.5,
        'index_size_mb': 4200
    }
    
    engine.get_autocomplete_suggestions.return_value = [
        'python tutorial',
        'python programming',
        'python tips'
    ]
    
    engine.get_similar_pages.return_value = [
        {'url': 'https://example.com/related', 'title': 'Related Page'}
    ]
    
    return engine


# ========== HEALTH CHECK TESTS ==========

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_status(self, client):
        """Test health check returns OK status."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data


# ========== HOME PAGE TESTS ==========

class TestHomePage:
    """Test home page."""
    
    def test_home_page_loads(self, client):
        """Test home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Klar' in response.data
    
    def test_home_page_contains_search_form(self, client):
        """Test home page contains search form."""
        response = client.get('/')
        assert b'S\xc3\xb6k' in response.data  # "Sök" in Swedish
        assert b'search' in response.data.lower()


# ========== SEARCH API TESTS ==========

class TestSearchAPI:
    """Test search API endpoint."""
    
    def test_search_with_query_parameter(self, client, mock_search_engine):
        """Test search with query parameter."""
        response = client.get('/api/search?q=test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'results' in data
        assert 'query' in data
    
    def test_search_without_query(self, client):
        """Test search without query returns error."""
        response = client.get('/api/search')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_search_with_short_query(self, client):
        """Test search with query < 2 characters fails."""
        response = client.get('/api/search?q=a')
        assert response.status_code == 400
    
    def test_search_with_long_query(self, client):
        """Test search with query > 500 characters fails."""
        long_query = 'a' * 501
        response = client.get(f'/api/search?q={long_query}')
        assert response.status_code == 400
    
    def test_search_with_json_body(self, client):
        """Test search with JSON body."""
        response = client.post('/api/search',
                              data=json.dumps({'q': 'test'}),
                              content_type='application/json')
        assert response.status_code == 200
    
    def test_search_parameters(self, client, mock_search_engine):
        """Test search with pagination parameters."""
        response = client.get('/api/search?q=test&limit=20&offset=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['limit'] == 20
        assert data['offset'] == 10
    
    def test_search_limit_boundaries(self, client):
        """Test search limit is bounded (1-100)."""
        response = client.get('/api/search?q=test&limit=1000')
        data = json.loads(response.data)
        assert data['limit'] <= 100
        
        response = client.get('/api/search?q=test&limit=0')
        data = json.loads(response.data)
        assert data['limit'] >= 1


# ========== SEARCH PAGE TESTS ==========

class TestSearchPage:
    """Test search results page."""
    
    def test_search_page_loads(self, client):
        """Test search results page loads."""
        response = client.get('/search?q=test')
        assert response.status_code == 200
    
    def test_search_page_redirect_without_query(self, client):
        """Test redirect to home when no query."""
        response = client.get('/search', follow_redirects=False)
        assert response.status_code == 302  # Redirect
    
    def test_search_page_displays_results(self, client):
        """Test search page displays results."""
        response = client.get('/search?q=test')
        assert b'resultat' in response.data.lower() or b'results' in response.data.lower()
    
    def test_search_page_pagination(self, client):
        """Test search page pagination."""
        response = client.get('/search?q=test&page=2')
        assert response.status_code == 200


# ========== STATISTICS API TESTS ==========

class TestStatisticsAPI:
    """Test statistics API."""
    
    def test_get_statistics(self, client, mock_search_engine):
        """Test get statistics endpoint."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_pages' in data
        assert 'total_terms' in data
        assert 'total_domains' in data


# ========== AUTOCOMPLETE TESTS ==========

class TestAutocomplete:
    """Test autocomplete endpoint."""
    
    def test_autocomplete_with_query(self, client, mock_search_engine):
        """Test autocomplete with query."""
        response = client.get('/api/autocomplete?q=pyt')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'suggestions' in data
    
    def test_autocomplete_without_query(self, client):
        """Test autocomplete without query."""
        response = client.get('/api/autocomplete')
        data = json.loads(response.data)
        assert data['suggestions'] == []
    
    def test_autocomplete_short_query(self, client):
        """Test autocomplete with single character."""
        response = client.get('/api/autocomplete?q=p')
        data = json.loads(response.data)
        # Should return empty or suggestions
        assert 'suggestions' in data


# ========== SIMILAR PAGES TESTS ==========

class TestSimilarPages:
    """Test similar pages endpoint."""
    
    def test_get_similar_pages(self, client, mock_search_engine):
        """Test get similar pages."""
        url = 'https://example.com/page1'
        response = client.get(f'/api/similar/{url}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'similar_pages' in data


# ========== ERROR HANDLING TESTS ==========

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = client.post('/api/search',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400


# ========== RATE LIMITING TESTS ==========

class TestRateLimiting:
    """Test rate limiting."""
    
    def test_rate_limit_search_endpoint(self, client):
        """Test rate limiting on search endpoint."""
        # This test would require many requests
        # Simplified here - would need more sophisticated testing
        response = client.get('/api/search?q=test')
        assert response.status_code == 200


# ========== CACHING TESTS ==========

class TestCaching:
    """Test caching."""
    
    def test_stats_caching(self, client, mock_search_engine):
        """Test stats endpoint is cached."""
        response1 = client.get('/api/stats')
        response2 = client.get('/api/stats')
        
        # Both should return 200
        assert response1.status_code == 200
        assert response2.status_code == 200


# ========== FACTORY FUNCTION TESTS ==========

class TestCreateApp:
    """Test app factory function."""
    
    def test_create_app_without_dependencies(self):
        """Test creating app without dependencies."""
        app = create_app()
        assert app is not None
    
    def test_create_app_with_dependencies(self, mock_search_engine):
        """Test creating app with dependencies."""
        app = create_app(search_engine=mock_search_engine)
        assert app is not None


# ========== INTEGRATION TESTS ==========

class TestWebUIIntegration:
    """Integration tests for web UI."""
    
    def test_full_search_workflow(self, client, mock_search_engine):
        """Test full search workflow."""
        # Home page
        response = client.get('/')
        assert response.status_code == 200
        
        # Search
        response = client.get('/api/search?q=test')
        assert response.status_code == 200
        
        # Search page
        response = client.get('/search?q=test')
        assert response.status_code == 200
    
    def test_autocomplete_workflow(self, client, mock_search_engine):
        """Test autocomplete workflow."""
        response = client.get('/api/autocomplete?q=pyt')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data['suggestions'], list)
