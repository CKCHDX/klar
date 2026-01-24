"""
KSE Worker Threads

Background worker threads for crawler, indexer, and search operations.
"""

from typing import Optional, List, Dict
import logging
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal

from kse.core import KSELogger
from kse.crawler import KSECrawlerManager
from kse.search import SearchEngine

logger = KSELogger.get_logger(__name__)


class CrawlerWorker(QThread):
    """Worker thread for web crawling."""
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(int, int)  # Current, Total
    page_crawled = pyqtSignal(str, str)  # URL, Title
    error = pyqtSignal(str)
    finished = pyqtSignal(dict)  # Statistics
    
    def __init__(self, crawler_manager: KSECrawlerManager, batch_size: int = 100):
        """
        Initialize crawler worker.
        
        Args:
            crawler_manager: Crawler manager instance
            batch_size: Pages to crawl per batch
        """
        super().__init__()
        self.crawler_manager = crawler_manager
        self.batch_size = batch_size
        self.is_running = False
        self.is_paused = False
        self.stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def run(self):
        """
        Run crawler worker.
        """
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        self.started.emit()
        
        try:
            # Initialize crawler
            self.crawler_manager.initialize_from_domains()
            
            batch_count = 0
            while self.is_running:
                if self.is_paused:
                    self.msleep(100)
                    continue
                
                # Crawl batch
                try:
                    crawl_stats = self.crawler_manager.crawl_batch(self.batch_size)
                    
                    self.stats['pages_crawled'] += crawl_stats.get('pages_crawled', 0)
                    self.stats['pages_failed'] += crawl_stats.get('pages_failed', 0)
                    batch_count += 1
                    
                    self.progress.emit(
                        self.stats['pages_crawled'],
                        self.stats['pages_crawled'] + 1000  # Estimate
                    )
                    
                except Exception as e:
                    self.error.emit(f"Batch error: {str(e)}")
                    logger.error(f"Crawler batch error: {e}")
                    break
        
        except Exception as e:
            self.error.emit(f"Crawler error: {str(e)}")
            logger.error(f"Crawler error: {e}")
        
        finally:
            self.is_running = False
            self.stats['end_time'] = datetime.now()
            self.finished.emit(self.stats)
    
    def pause(self):
        """Pause crawler."""
        self.is_paused = True
    
    def resume(self):
        """Resume crawler."""
        self.is_paused = False
    
    def stop(self):
        """Stop crawler."""
        self.is_running = False
        self.wait()


class IndexerWorker(QThread):
    """Worker thread for search indexing."""
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(int, int)  # Current, Total
    term_indexed = pyqtSignal(str, int)  # Term, Frequency
    error = pyqtSignal(str)
    finished = pyqtSignal(dict)  # Statistics
    
    def __init__(self, search_engine: SearchEngine, batch_size: int = 1000):
        """
        Initialize indexer worker.
        
        Args:
            search_engine: Search engine instance
            batch_size: Pages to index per batch
        """
        super().__init__()
        self.search_engine = search_engine
        self.batch_size = batch_size
        self.is_running = False
        self.stats = {
            'pages_indexed': 0,
            'terms_indexed': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def run(self):
        """
        Run indexer worker.
        """
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        self.started.emit()
        
        try:
            # Build index from database
            index_stats = self.search_engine.index_all_pages(limit=None)
            
            self.stats['pages_indexed'] = index_stats.get('pages_indexed', 0)
            self.stats['terms_indexed'] = index_stats.get('terms_indexed', 0)
            
            self.progress.emit(self.stats['pages_indexed'], self.stats['pages_indexed'])
        
        except Exception as e:
            self.error.emit(f"Indexer error: {str(e)}")
            logger.error(f"Indexer error: {e}")
        
        finally:
            self.is_running = False
            self.stats['end_time'] = datetime.now()
            self.finished.emit(self.stats)
    
    def stop(self):
        """Stop indexer."""
        self.is_running = False
        self.wait()


class SearchWorker(QThread):
    """Worker thread for search queries."""
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(int)  # Progress percentage
    results_ready = pyqtSignal(list, dict)  # Results, Stats
    error = pyqtSignal(str)
    
    def __init__(self, search_engine: SearchEngine, query: str, limit: int = 10):
        """
        Initialize search worker.
        
        Args:
            search_engine: Search engine instance
            query: Search query
            limit: Maximum results
        """
        super().__init__()
        self.search_engine = search_engine
        self.query = query
        self.limit = limit
    
    def run(self):
        """
        Run search worker.
        """
        self.started.emit()
        
        try:
            self.progress.emit(25)
            
            # Execute search
            results, stats = self.search_engine.search(
                self.query,
                limit=self.limit,
                explain=True
            )
            
            self.progress.emit(100)
            self.results_ready.emit(results, stats)
        
        except Exception as e:
            self.error.emit(f"Search error: {str(e)}")
            logger.error(f"Search error: {e}")
