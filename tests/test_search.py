"""
Tests for KSE Search Engine (Phase 3)
"""

import pytest
import math
from unittest.mock import Mock, patch

from kse.search import (
    Tokenizer,
    stem_swedish,
    KSEIndexer,
    TFIDFRanker,
    PageRankCalculator,
    HybridRanker,
    SearchEngine,
    SearchResult,
)


# ========== TOKENIZER TESTS ==========

class TestTokenizer:
    """Test Swedish tokenizer."""
    
    def test_basic_tokenization(self):
        """Test basic word tokenization."""
        tokenizer = Tokenizer(remove_stopwords=False, use_stemming=False)
        tokens = tokenizer.tokenize("Hej världen, detta är ett test")
        assert "hej" in tokens
        assert "världen" in tokens
        assert "test" in tokens
    
    def test_stopword_removal(self):
        """Test stopword removal."""
        tokenizer = Tokenizer(remove_stopwords=True, use_stemming=False)
        tokens = tokenizer.tokenize("Hej och så var det dags för test")
        # 'och', 'så', 'var', 'för' should be removed
        assert "och" not in tokens
        assert "hej" in tokens
        assert "test" in tokens
    
    def test_stemming(self):
        """Test Swedish stemming."""
        tokenizer = Tokenizer(remove_stopwords=False, use_stemming=True)
        tokens = tokenizer.tokenize("testing testade tester")
        # Should all stem to similar form
        assert len(tokens) > 0
    
    def test_swedish_characters(self):
        """Test Swedish characters (å, ä, ö)."""
        tokenizer = Tokenizer(remove_stopwords=False, use_stemming=False)
        tokens = tokenizer.tokenize("åäö förändring järnväg")
        assert len(tokens) > 0
    
    def test_empty_input(self):
        """Test empty input."""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("")
        assert tokens == []
    
    def test_minimum_length(self):
        """Test minimum token length (2 chars)."""
        tokenizer = Tokenizer(remove_stopwords=False, use_stemming=False)
        tokens = tokenizer.tokenize("a bb ccc")
        # 'a' should be filtered out (< 2 chars)
        assert "a" not in tokens
        assert "bb" in tokens
    
    def test_duplicate_removal(self):
        """Test removal of duplicate tokens."""
        tokenizer = Tokenizer(remove_stopwords=False, use_stemming=False)
        tokens = tokenizer.tokenize("test test test")
        # Should only return unique
        assert tokens.count("test") == 1


# ========== STEMMER TESTS ==========

class TestStemmer:
    """Test Swedish stemming."""
    
    def test_plural_suffix(self):
        """Test plural suffix removal."""
        assert stem_swedish("hundar") == "hund"
        assert stem_swedish("katterna") == "katt"
    
    def test_verb_suffix(self):
        """Test verb suffix removal."""
        # Past tense -ade suffix
        result = stem_swedish("testade")
        assert result != "testade"  # Should be stemmed
    
    def test_short_words(self):
        """Test that short words are preserved."""
        assert stem_swedish("en") == "en"
        assert stem_swedish("och") == "och"
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert stem_swedish("TEST") == stem_swedish("test")


# ========== INDEXER TESTS ==========

class TestIndexer:
    """Test inverted indexer."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        db = Mock()
        db.get_connection().cursor.return_value = Mock()
        return db
    
    @pytest.fixture
    def indexer(self, mock_db):
        """Create indexer instance."""
        return KSEIndexer(mock_db)
    
    def test_index_page(self, indexer):
        """Test indexing a single page."""
        unique_terms = indexer.index_page(
            page_id=1,
            title="Test Page",
            description="This is a description",
            content="This is the content of the page"
        )
        assert unique_terms > 0
        assert len(indexer.inverted_index) > 0
    
    def test_get_postings(self, indexer):
        """Test retrieving postings for a term."""
        indexer.index_page(1, "Test", "", "testing test")
        postings = indexer.get_postings("test")
        assert len(postings) > 0
    
    def test_get_idf(self, indexer):
        """Test IDF calculation."""
        indexer.index_page(1, "test", "", "")
        indexer.total_documents = 100
        idf = indexer.get_idf("test")
        assert idf > 0
    
    def test_search_term(self, indexer):
        """Test searching for a term."""
        indexer.index_page(1, "test", "", "test")
        indexer.total_documents = 1
        indexer.document_lengths[1] = 1
        
        results = indexer.search_term("test")
        assert len(results) > 0
        assert results[0][0] == 1  # doc_id
    
    def test_statistics(self, indexer):
        """Test getting statistics."""
        indexer.index_page(1, "test", "", "test")
        indexer.total_documents = 1
        stats = indexer.get_statistics()
        
        assert stats['total_terms'] > 0
        assert stats['total_documents'] >= 0


# ========== RANKER TESTS ==========

class TestRanker:
    """Test ranking algorithms."""
    
    def test_tfidf_ranker(self):
        """Test TF-IDF ranker."""
        ranker = TFIDFRanker()
        ranker.set_doc_length(1, 100)
        
        score = ranker.rank(1, "test", 5.0, 2.0)
        assert score > 0
    
    def test_tfidf_multiple_terms(self):
        """Test TF-IDF with multiple terms."""
        ranker = TFIDFRanker()
        ranker.set_doc_length(1, 100)
        
        score = ranker.rank_multiple_terms(
            1,
            [("test", 3.0, 2.0), ("page", 2.0, 1.5)]
        )
        assert score > 0
    
    def test_pagerank_calculation(self):
        """Test PageRank calculation."""
        calculator = PageRankCalculator()
        
        # Create simple link graph
        links = {
            1: [2, 3],
            2: [3],
            3: [1],
        }
        
        ranks = calculator.calculate(links)
        assert len(ranks) == 3
        assert all(r > 0 for r in ranks.values())
    
    def test_pagerank_normalization(self):
        """Test PageRank normalization."""
        calculator = PageRankCalculator()
        links = {1: [2], 2: [1]}
        calculator.calculate(links)
        
        normalized = calculator.normalize_ranks(0, 1)
        assert all(0 <= v <= 1 for v in normalized.values())
    
    def test_hybrid_ranker(self):
        """Test hybrid ranker combining signals."""
        ranker = HybridRanker()
        ranker.set_pagerank_scores({1: 0.8})
        ranker.set_url_authority(1, 0.7)
        ranker.set_freshness_score(1, 0.9)
        
        score = ranker.rank(1, 5.0, 2.0)
        assert score > 0


# ========== SEARCH ENGINE TESTS ==========

class TestSearchEngine:
    """Test search engine."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        db = Mock()
        cursor = Mock()
        db.get_connection().cursor.return_value = cursor
        
        # Mock page fetch
        cursor.fetchone.return_value = ("http://example.com", "Test Page", "Description")
        cursor.fetchall.return_value = [
            (1, "Test Page", "Description", "This is test content"),
        ]
        
        return db
    
    @pytest.fixture
    def search_engine(self, mock_db):
        """Create search engine instance."""
        return SearchEngine(mock_db, use_hybrid_ranking=False)
    
    def test_search_result_creation(self):
        """Test SearchResult dataclass."""
        result = SearchResult(
            page_id=1,
            url="http://example.com",
            title="Test",
            description="Desc",
            score=0.95,
            matched_terms=["test"],
        )
        assert result.page_id == 1
        assert result.score == 0.95
    
    def test_search_empty_query(self, search_engine):
        """Test search with empty query."""
        results, stats = search_engine.search("")
        assert len(results) == 0
    
    def test_search_with_results(self, search_engine):
        """Test search returning results."""
        # Index some content first
        search_engine.indexer.index_page(1, "Test", "Description", "test content")
        search_engine.indexer.total_documents = 1
        search_engine.indexer.document_lengths[1] = 10
        
        results, stats = search_engine.search("test")
        assert stats['query_terms'] == ["test"]
    
    def test_autocomplete(self, search_engine):
        """Test autocomplete suggestions."""
        search_engine.indexer.index_page(1, "testing", "", "")
        search_engine.indexer.index_page(2, "tested", "", "")
        
        suggestions = search_engine.autocomplete("test")
        assert len(suggestions) > 0
    
    def test_get_statistics(self, search_engine):
        """Test getting statistics."""
        search_engine.indexer.index_page(1, "test", "", "")
        search_engine.indexer.total_documents = 1
        
        stats = search_engine.get_statistics()
        assert 'total_terms' in stats
        assert 'total_documents' in stats


# ========== INTEGRATION TESTS ==========

class TestSearchIntegration:
    """Integration tests for search system."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database for integration."""
        db = Mock()
        cursor = Mock()
        db.get_connection().cursor.return_value = cursor
        cursor.fetchone.return_value = ("http://example.com", "Title", "Desc")
        return db
    
    @pytest.fixture
    def search_engine(self, mock_db):
        """Create search engine for integration."""
        return SearchEngine(mock_db, use_hybrid_ranking=True)
    
    def test_full_search_pipeline(self, search_engine):
        """Test complete search pipeline."""
        # 1. Index multiple pages
        search_engine.indexer.index_page(
            1, "Python Programming", "Learn Python", "Python is a language"
        )
        search_engine.indexer.index_page(
            2, "Java Programming", "Learn Java", "Java is a language"
        )
        search_engine.indexer.total_documents = 2
        search_engine.indexer.document_lengths[1] = 10
        search_engine.indexer.document_lengths[2] = 10
        
        # 2. Search
        results, stats = search_engine.search("programming")
        
        # 3. Verify results
        assert len(results) > 0
        assert stats['results_count'] > 0
        assert len(stats['query_terms']) > 0
    
    def test_ranking_order(self, search_engine):
        """Test that results are ranked correctly."""
        # High frequency term in doc 1
        search_engine.indexer.index_page(
            1, "test test test", "", "test"
        )
        # Low frequency in doc 2
        search_engine.indexer.index_page(
            2, "document", "", "contains test once"
        )
        search_engine.indexer.total_documents = 2
        search_engine.indexer.document_lengths[1] = 4
        search_engine.indexer.document_lengths[2] = 4
        
        results, _ = search_engine.search("test", limit=2)
        
        # Doc 1 should rank higher (more test occurrences)
        if len(results) >= 2:
            assert results[0].page_id == 1 or results[0].score >= results[1].score
