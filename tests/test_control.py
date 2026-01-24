"""
Tests for KSE Control Center (Phase 4)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from kse.control import (
    KSEMainWindow,
    CrawlerControlDialog,
    IndexingDialog,
    SettingsDialog,
    DatabaseDialog,
    CrawlerWorker,
    IndexerWorker,
    SearchWorker,
    KSEControlApplication,
)


# ========== FIXTURES ==========

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_db():
    """Create mock database."""
    db = Mock()
    db.get_connection().cursor.return_value = Mock()
    return db


# ========== DIALOG TESTS ==========

class TestCrawlerControlDialog:
    """Test crawler control dialog."""
    
    def test_creation(self, qapp):
        """Test dialog creation."""
        dialog = CrawlerControlDialog()
        assert dialog is not None
        assert dialog.batch_size.value() == 100
        assert dialog.threads.value() == 4
    
    def test_get_settings(self, qapp):
        """Test getting settings."""
        dialog = CrawlerControlDialog()
        dialog.batch_size.setValue(200)
        dialog.threads.setValue(8)
        
        settings = dialog.get_settings()
        assert settings['batch_size'] == 200
        assert settings['threads'] == 8
        assert 'timeout' in settings
        assert 'politeness' in settings
    
    def test_default_values(self, qapp):
        """Test default values."""
        dialog = CrawlerControlDialog()
        settings = dialog.get_settings()
        
        assert settings['batch_size'] >= 1
        assert settings['threads'] >= 1
        assert settings['timeout'] >= 1
        assert settings['politeness'] >= 0.1
        assert isinstance(settings['respect_robots'], bool)


class TestIndexingDialog:
    """Test indexing dialog."""
    
    def test_creation(self, qapp):
        """Test dialog creation."""
        dialog = IndexingDialog()
        assert dialog is not None
        assert dialog.batch_size.value() == 1000
    
    def test_get_settings(self, qapp):
        """Test getting settings."""
        dialog = IndexingDialog()
        dialog.batch_size.setValue(5000)
        
        settings = dialog.get_settings()
        assert settings['batch_size'] == 5000
        assert settings['use_stemming'] is True
        assert settings['remove_stopwords'] is True
    
    def test_settings_checkboxes(self, qapp):
        """Test checkbox settings."""
        dialog = IndexingDialog()
        dialog.use_stemming.setChecked(False)
        dialog.remove_stopwords.setChecked(False)
        
        settings = dialog.get_settings()
        assert settings['use_stemming'] is False
        assert settings['remove_stopwords'] is False


class TestSettingsDialog:
    """Test settings dialog."""
    
    def test_creation(self, qapp):
        """Test dialog creation."""
        settings = {'db_host': 'localhost', 'db_port': 5432}
        dialog = SettingsDialog(settings)
        assert dialog is not None
    
    def test_get_settings(self, qapp):
        """Test getting settings."""
        initial_settings = {'db_host': 'localhost', 'db_port': 5432}
        dialog = SettingsDialog(initial_settings)
        dialog.db_host.setText('192.168.1.1')
        dialog.db_port.setValue(5433)
        
        settings = dialog.get_settings()
        assert settings['db_host'] == '192.168.1.1'
        assert settings['db_port'] == 5433


class TestDatabaseDialog:
    """Test database dialog."""
    
    def test_creation(self, qapp):
        """Test dialog creation."""
        dialog = DatabaseDialog()
        assert dialog is not None


# ========== WORKER THREAD TESTS ==========

class TestCrawlerWorker:
    """Test crawler worker thread."""
    
    def test_initialization(self):
        """Test worker initialization."""
        crawler = Mock()
        worker = CrawlerWorker(crawler, batch_size=100)
        
        assert worker.batch_size == 100
        assert worker.is_running is False
        assert worker.is_paused is False
    
    def test_statistics(self):
        """Test statistics tracking."""
        crawler = Mock()
        worker = CrawlerWorker(crawler)
        
        stats = worker.stats
        assert 'pages_crawled' in stats
        assert 'pages_failed' in stats
        assert 'start_time' in stats
        assert 'end_time' in stats
    
    def test_pause_resume(self):
        """Test pause and resume."""
        crawler = Mock()
        worker = CrawlerWorker(crawler)
        worker.is_running = True
        
        worker.pause()
        assert worker.is_paused is True
        
        worker.resume()
        assert worker.is_paused is False


class TestIndexerWorker:
    """Test indexer worker thread."""
    
    def test_initialization(self):
        """Test worker initialization."""
        search_engine = Mock()
        worker = IndexerWorker(search_engine, batch_size=1000)
        
        assert worker.batch_size == 1000
        assert worker.is_running is False
    
    def test_statistics(self):
        """Test statistics tracking."""
        search_engine = Mock()
        worker = IndexerWorker(search_engine)
        
        stats = worker.stats
        assert 'pages_indexed' in stats
        assert 'terms_indexed' in stats
        assert 'start_time' in stats
        assert 'end_time' in stats


class TestSearchWorker:
    """Test search worker thread."""
    
    def test_initialization(self):
        """Test worker initialization."""
        search_engine = Mock()
        worker = SearchWorker(search_engine, "test query", limit=10)
        
        assert worker.query == "test query"
        assert worker.limit == 10
    
    def test_query_storage(self):
        """Test query storage."""
        search_engine = Mock()
        queries = ["python", "javascript", "search engine"]
        
        for query in queries:
            worker = SearchWorker(search_engine, query)
            assert worker.query == query


# ========== APPLICATION TESTS ==========

class TestKSEControlApplication:
    """Test main application."""
    
    def test_creation(self, qapp):
        """Test application creation."""
        db = Mock()
        app = KSEControlApplication([], db_connection=db)
        
        assert app is not None
        assert app.db == db
    
    def test_application_properties(self, qapp):
        """Test application properties."""
        db = Mock()
        app = KSEControlApplication([], db_connection=db)
        
        assert app.applicationName() == "Klar Search Engine Control Center"
        assert app.applicationVersion() == "1.0.0"


# ========== INTEGRATION TESTS ==========

class TestControlCenterIntegration:
    """Integration tests for control center."""
    
    def test_dialog_workflow(self, qapp):
        """Test typical dialog workflow."""
        # Crawler settings
        crawler_dialog = CrawlerControlDialog()
        crawler_dialog.batch_size.setValue(50)
        crawler_settings = crawler_dialog.get_settings()
        assert crawler_settings['batch_size'] == 50
        
        # Indexing settings
        index_dialog = IndexingDialog()
        index_settings = index_dialog.get_settings()
        assert index_settings['batch_size'] > 0
    
    def test_worker_lifecycle(self):
        """Test worker lifecycle."""
        crawler = Mock()
        crawler.initialize_from_domains = Mock()
        crawler.crawl_batch = Mock(return_value={'pages_crawled': 10, 'pages_failed': 0})
        
        worker = CrawlerWorker(crawler, batch_size=100)
        assert worker.batch_size == 100
        assert worker.stats['pages_crawled'] == 0


# ========== MOCK TESTS ==========

class TestMainWindowMocking:
    """Test main window with mocking."""
    
    @patch('kse.control.kse_main_window.KSELogger')
    def test_main_window_initialization(self, mock_logger, qapp, mock_db):
        """Test main window initialization."""
        # This would require more setup due to PyQt6
        # Keeping basic structure
        pass
