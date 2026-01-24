"""
Search Module Tests

Tests for query parsing, ranking, execution, and caching.
"""

import pytest
from datetime import datetime, timedelta
from kse.search import (
    SearchQuery,
    QueryType,
    QueryParser,
    Ranker,
    RankingStrategy,
    RankingScore,
    SearchResult,
    ResultSet,
    SearchCache,
)


class TestQueryParser:
    """Test query parsing."""
    
    def test_parser_init(self):
        """Test parser initialization."""
        parser = QueryParser()
        assert parser.min_term_length == 2
        assert parser.max_terms == 10
    
    def test_parse_simple_query(self):
        """Test parsing simple query."""
        parser = QueryParser()
        result = parser.parse("python programming")
        
        assert result.query_type in [QueryType.SIMPLE, QueryType.MIXED]
        assert len(result.terms) >= 1
    
    def test_parse_phrase_query(self):
        """Test parsing quoted phrase."""
        parser = QueryParser()
        result = parser.parse('"machine learning" AI')
        
        assert len(result.phrases) >= 1
        assert "machine learning" in result.phrases
    
    def test_parse_site_filter(self):
        """Test parsing site filter."""
        parser = QueryParser()
        result = parser.parse("python site:wikipedia.org")
        
        assert result.domain_filter == "wikipedia.org"
        assert "python" in result.terms
    
    def test_parse_exclude_terms(self):
        """Test parsing excluded terms."""
        parser = QueryParser()
        result = parser.parse("python -java -csharp")
        
        assert "python" in result.terms
        assert "java" in result.exclude_terms
        assert "csharp" in result.exclude_terms
    
    def test_parse_query_type(self):
        """Test query type classification."""
        parser = QueryParser()
        
        # Simple
        q1 = parser.parse("python")
        assert q1.query_type == QueryType.SIMPLE
        
        # Phrase
        q2 = parser.parse('"python programming"')
        assert q2.query_type == QueryType.PHRASE
        
        # Boolean
        q3 = parser.parse("python AND java")
        assert q3.query_type in [QueryType.BOOLEAN, QueryType.MIXED]
    
    def test_normalize_query(self):
        """Test query normalization."""
        parser = QueryParser()
        normalized = parser._normalize_query("  PYTHON  PROGRAMMING  ")
        
        assert normalized == "python programming"
        assert "  " not in normalized
    
    def test_validate_query(self):
        """Test query validation."""
        parser = QueryParser()
        
        # Valid query
        q1 = SearchQuery("test", QueryType.SIMPLE, terms=["test"])
        assert parser.validate_query(q1)
        
        # Empty query
        q2 = SearchQuery("empty", QueryType.SIMPLE)
        assert not parser.validate_query(q2)
    
    def test_suggest_correction(self):
        """Test query correction suggestion."""
        parser = QueryParser()
        
        suggestion = parser.suggest_correction("python  programming")
        assert suggestion == "python programming" or suggestion is None


class TestRanker:
    """Test result ranking."""
    
    def test_ranker_init(self):
        """Test ranker initialization."""
        ranker = Ranker()
        assert ranker.strategy == RankingStrategy.HYBRID
        assert ranker.weights['relevance'] == 0.50
    
    def test_calculate_relevance(self):
        """Test relevance score calculation."""
        ranker = Ranker()
        
        result = {'tfidf_score': 0.75}
        score = ranker._calculate_relevance(result)
        
        assert 0 <= score <= 1
        assert score == 0.75
    
    def test_calculate_popularity(self):
        """Test popularity score calculation."""
        ranker = Ranker()
        
        result = {
            'domain': 'sv.wikipedia.org',
            'inbound_links': 50,
        }
        score = ranker._calculate_popularity(result)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Wikipedia has high authority
    
    def test_calculate_recency(self):
        """Test recency score calculation."""
        ranker = Ranker()
        
        # Recent date
        recent = datetime.now()
        result = {'created_at': recent}
        score = ranker._calculate_recency(result)
        
        assert score >= 0.9  # Recent should be high
    
    def test_rank_results(self):
        """Test result ranking."""
        ranker = Ranker()
        
        results = [
            {'page_id': 1, 'url': 'url1', 'tfidf_score': 0.5, 'domain': 'example.com'},
            {'page_id': 2, 'url': 'url2', 'tfidf_score': 0.8, 'domain': 'sv.wikipedia.org'},
            {'page_id': 3, 'url': 'url3', 'tfidf_score': 0.3, 'domain': 'other.se'},
        ]
        
        ranked = ranker.rank(results)
        
        assert len(ranked) == 3
        # Higher scores should come first
        assert ranked[0].final_score >= ranked[-1].final_score
    
    def test_ranking_strategies(self):
        """Test different ranking strategies."""
        ranker = Ranker()
        
        results = [
            {'page_id': 1, 'url': 'url1', 'tfidf_score': 0.9, 'domain': 'other.com'},
            {'page_id': 2, 'url': 'url2', 'tfidf_score': 0.3, 'domain': 'sv.wikipedia.org'},
        ]
        
        # Relevance: url1 should rank higher (higher tfidf)
        rel_ranked = ranker.rank(results, RankingStrategy.RELEVANCE)
        assert rel_ranked[0].page_id == 1
        
        # Popularity: url2 should rank higher (better domain)
        pop_ranked = ranker.rank(results, RankingStrategy.POPULARITY)
        assert pop_ranked[0].page_id == 2
    
    def test_boost_result(self):
        """Test result boosting."""
        ranker = Ranker()
        score = RankingScore(1, "url", final_score=0.5)
        
        boosted = ranker.boost_result(score, boost_factor=2.0)
        
        assert boosted.final_score > 0.5
        assert boosted.final_score <= 1.0  # Capped at 1.0
    
    def test_penalize_result(self):
        """Test result penalty."""
        ranker = Ranker()
        score = RankingScore(1, "url", final_score=0.8)
        
        penalized = ranker.penalize_result(score, penalty_factor=0.5)
        
        assert penalized.final_score < 0.8
        assert penalized.final_score >= 0.0


class TestSearchCache:
    """Test search result caching."""
    
    def test_cache_init(self):
        """Test cache initialization."""
        cache = SearchCache()
        assert cache.max_entries == 1000
        assert cache.default_ttl == 3600
    
    def test_cache_put_get(self):
        """Test cache put and get."""
        cache = SearchCache()
        result_set = ResultSet("test", 5, 5)
        
        cache.put("test query", result_set)
        retrieved = cache.get("test query")
        
        assert retrieved is not None
        assert retrieved.query == "test"
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = SearchCache()
        
        retrieved = cache.get("nonexistent")
        
        assert retrieved is None
        assert cache.stats['misses'] == 1
    
    def test_cache_hit_tracking(self):
        """Test hit count tracking."""
        cache = SearchCache()
        result_set = ResultSet("test", 5, 5)
        
        cache.put("query", result_set)
        cache.get("query")
        cache.get("query")
        
        stats = cache.get_statistics()
        assert stats['hits'] == 2
    
    def test_cache_expiration(self):
        """Test cache entry expiration."""
        cache = SearchCache(default_ttl_seconds=1)
        result_set = ResultSet("test", 5, 5)
        
        cache.put("query", result_set, ttl_seconds=1)
        
        # Should be retrievable immediately
        retrieved = cache.get("query")
        assert retrieved is not None
        
        # Simulate expiration
        import time
        time.sleep(1.1)
        
        # Should be expired now
        expired = cache.get("query")
        assert expired is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = SearchCache()
        result_set = ResultSet("test", 5, 5)
        
        cache.put("query1", result_set)
        cache.put("query2", result_set)
        
        assert len(cache.cache) == 2
        
        cache.clear("query1")
        assert len(cache.cache) == 1
        
        cache.clear()
        assert len(cache.cache) == 0
    
    def test_cache_statistics(self):
        """Test cache statistics."""
        cache = SearchCache()
        result_set = ResultSet("test", 5, 5)
        
        cache.put("query", result_set)
        cache.get("query")
        cache.get("nonexistent")
        
        stats = cache.get_statistics()
        
        assert stats['puts'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate_percent'] > 0
    
    def test_top_queries(self):
        """Test getting top queries."""
        cache = SearchCache()
        result_set = ResultSet("test", 5, 5)
        
        cache.put("query1", result_set)
        cache.put("query2", result_set)
        
        # Access query1 more times
        for _ in range(5):
            cache.get("query1")
        
        cache.get("query2")
        
        top = cache.get_top_queries(limit=2)
        
        assert len(top) <= 2
        assert top[0][0] == "query1"  # query1 has more hits


class TestSearchResult:
    """Test search result objects."""
    
    def test_search_result_creation(self):
        """Test SearchResult creation."""
        result = SearchResult(
            page_id=1,
            url="https://example.com",
            title="Example",
            description="Example site",
            domain="example.com",
            score=0.85,
        )
        
        assert result.page_id == 1
        assert result.score == 0.85
    
    def test_result_set_pagination(self):
        """Test ResultSet pagination properties."""
        results = [SearchResult(i, f"url{i}", f"Title{i}", "Desc", "domain", 0.5) for i in range(5)]
        result_set = ResultSet(
            query="test",
            total_results=20,
            returned_results=5,
            results=results,
            offset=0,
            limit=5,
        )
        
        assert result_set.has_more
        
        result_set.offset = 15
        assert not result_set.has_more
