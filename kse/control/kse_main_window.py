"""
KSE Main Window

Main GUI window for the Klar Search Engine Control Center.
"""

from typing import Optional, Dict, List
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QComboBox,
    QSpinBox, QCheckBox, QMessageBox, QProgressBar,
    QTextEdit, QTableWidget, QTableWidgetItem, QGroupBox,
    QGridLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont

from kse.core import KSELogger
from kse.database import KSEDatabase
from .kse_workers import CrawlerWorker, IndexerWorker, SearchWorker

logger = KSELogger.get_logger(__name__)


class KSEMainWindow(QMainWindow):
    """Main window for KSE Control Center."""
    
    def __init__(self, db_connection: KSEDatabase):
        """
        Initialize main window.
        
        Args:
            db_connection: Database connection object
        """
        super().__init__()
        self.db = db_connection
        self.setWindowTitle("Klar Search Engine - Control Center")
        self.setGeometry(100, 100, 1200, 800)
        
        # Worker threads
        self.crawler_worker = None
        self.indexer_worker = None
        self.search_worker = None
        
        # Initialize UI
        self._init_ui()
        self._connect_signals()
        self._load_statistics()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_statistics)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        logger.info("KSEMainWindow initialized")
    
    def _init_ui(self):
        """
        Initialize user interface.
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Dashboard tab
        self.tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        
        # Crawler tab
        self.tabs.addTab(self._create_crawler_tab(), "Crawler")
        
        # Indexer tab
        self.tabs.addTab(self._create_indexer_tab(), "Indexer")
        
        # Search tab
        self.tabs.addTab(self._create_search_tab(), "Search")
        
        # Database tab
        self.tabs.addTab(self._create_database_tab(), "Database")
        
        # Settings tab
        self.tabs.addTab(self._create_settings_tab(), "Settings")
    
    def _create_dashboard_tab(self) -> QWidget:
        """
        Create dashboard tab with statistics.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistics group
        stats_group = QGroupBox("System Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Add statistics labels
        self.stats_labels = {}
        row = 0
        
        stats = [
            ("Total Pages", "total_pages"),
            ("Indexed Terms", "indexed_terms"),
            ("Indexed Domains", "indexed_domains"),
            ("Average Page Size", "avg_page_size"),
            ("Last Crawl", "last_crawl"),
            ("Last Index", "last_index"),
            ("Database Size", "db_size"),
            ("Index Size", "index_size"),
        ]
        
        for label_text, key in stats:
            label = QLabel(label_text + ":")
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            value = QLabel("-")
            self.stats_labels[key] = value
            stats_layout.addWidget(label, row, 0)
            stats_layout.addWidget(value, row, 1)
            row += 1
        
        layout.addWidget(stats_group)
        
        # Status group
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.crawler_status = QLabel("Status: Idle")
        self.indexer_status = QLabel("Status: Idle")
        self.search_status = QLabel("Status: Ready")
        
        status_layout.addWidget(self.crawler_status)
        status_layout.addWidget(self.indexer_status)
        status_layout.addWidget(self.search_status)
        
        layout.addWidget(status_group)
        
        # Progress bars
        progress_group = QGroupBox("Current Operations")
        progress_layout = QVBoxLayout(progress_group)
        
        progress_layout.addWidget(QLabel("Crawler Progress:"))
        self.crawler_progress = QProgressBar()
        progress_layout.addWidget(self.crawler_progress)
        
        progress_layout.addWidget(QLabel("Indexer Progress:"))
        self.indexer_progress = QProgressBar()
        progress_layout.addWidget(self.indexer_progress)
        
        layout.addWidget(progress_group)
        layout.addStretch()
        
        return widget
    
    def _create_crawler_tab(self) -> QWidget:
        """
        Create crawler control tab.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Crawler control group
        control_group = QGroupBox("Crawler Control")
        control_layout = QVBoxLayout(control_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_crawler_btn = QPushButton("Start Crawling")
        self.start_crawler_btn.clicked.connect(self._start_crawler)
        button_layout.addWidget(self.start_crawler_btn)
        
        self.pause_crawler_btn = QPushButton("Pause")
        self.pause_crawler_btn.clicked.connect(self._pause_crawler)
        self.pause_crawler_btn.setEnabled(False)
        button_layout.addWidget(self.pause_crawler_btn)
        
        self.stop_crawler_btn = QPushButton("Stop")
        self.stop_crawler_btn.clicked.connect(self._stop_crawler)
        self.stop_crawler_btn.setEnabled(False)
        button_layout.addWidget(self.stop_crawler_btn)
        
        control_layout.addLayout(button_layout)
        
        # Settings
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel("Batch Size:"))
        self.crawler_batch_size = QSpinBox()
        self.crawler_batch_size.setValue(100)
        self.crawler_batch_size.setMinimum(1)
        self.crawler_batch_size.setMaximum(10000)
        settings_layout.addWidget(self.crawler_batch_size)
        
        settings_layout.addWidget(QLabel("Threads:"))
        self.crawler_threads = QSpinBox()
        self.crawler_threads.setValue(4)
        self.crawler_threads.setMinimum(1)
        self.crawler_threads.setMaximum(16)
        settings_layout.addWidget(self.crawler_threads)
        
        control_layout.addLayout(settings_layout)
        layout.addWidget(control_group)
        
        # Log area
        log_group = QGroupBox("Crawler Log")
        log_layout = QVBoxLayout(log_group)
        self.crawler_log = QTextEdit()
        self.crawler_log.setReadOnly(True)
        log_layout.addWidget(self.crawler_log)
        layout.addWidget(log_group)
        
        return widget
    
    def _create_indexer_tab(self) -> QWidget:
        """
        Create indexer control tab.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Indexer control group
        control_group = QGroupBox("Indexer Control")
        control_layout = QVBoxLayout(control_group)
        
        button_layout = QHBoxLayout()
        
        self.start_indexer_btn = QPushButton("Start Indexing")
        self.start_indexer_btn.clicked.connect(self._start_indexer)
        button_layout.addWidget(self.start_indexer_btn)
        
        self.stop_indexer_btn = QPushButton("Stop")
        self.stop_indexer_btn.clicked.connect(self._stop_indexer)
        self.stop_indexer_btn.setEnabled(False)
        button_layout.addWidget(self.stop_indexer_btn)
        
        control_layout.addLayout(button_layout)
        
        # Settings
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Batch Size:"))
        
        self.indexer_batch_size = QSpinBox()
        self.indexer_batch_size.setValue(1000)
        self.indexer_batch_size.setMinimum(1)
        self.indexer_batch_size.setMaximum(100000)
        settings_layout.addWidget(self.indexer_batch_size)
        
        control_layout.addLayout(settings_layout)
        layout.addWidget(control_group)
        
        # Log area
        log_group = QGroupBox("Indexer Log")
        log_layout = QVBoxLayout(log_group)
        self.indexer_log = QTextEdit()
        self.indexer_log.setReadOnly(True)
        log_layout.addWidget(self.indexer_log)
        layout.addWidget(log_group)
        
        return widget
    
    def _create_search_tab(self) -> QWidget:
        """
        Create search interface tab.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        search_group = QGroupBox("Search Test")
        search_layout = QVBoxLayout(search_group)
        
        # Search input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Query:"))
        from PyQt6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        input_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._execute_search)
        input_layout.addWidget(search_btn)
        search_layout.addLayout(input_layout)
        
        # Results
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(5)
        self.search_results.setHorizontalHeaderLabels(
            ["Rank", "Title", "URL", "Score", "Terms"]
        )
        search_layout.addWidget(self.search_results)
        
        layout.addWidget(search_group)
        return widget
    
    def _create_database_tab(self) -> QWidget:
        """
        Create database management tab.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        db_group = QGroupBox("Database Management")
        db_layout = QVBoxLayout(db_group)
        
        button_layout = QHBoxLayout()
        
        backup_btn = QPushButton("Backup Database")
        backup_btn.clicked.connect(self._backup_database)
        button_layout.addWidget(backup_btn)
        
        verify_btn = QPushButton("Verify Integrity")
        verify_btn.clicked.connect(self._verify_database)
        button_layout.addWidget(verify_btn)
        
        db_layout.addLayout(button_layout)
        layout.addWidget(db_group)
        
        # Statistics
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText("Database Statistics...")
        layout.addWidget(info_text)
        
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """
        Create settings tab.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        settings_group = QGroupBox("Application Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Add settings controls
        row = 0
        
        settings_layout.addWidget(QLabel("Database Host:"), row, 0)
        self.db_host_input = QLineEdit()
        self.db_host_input.setText("localhost")
        settings_layout.addWidget(self.db_host_input, row, 1)
        row += 1
        
        settings_layout.addWidget(QLabel("Database Port:"), row, 0)
        self.db_port_input = QSpinBox()
        self.db_port_input.setValue(5432)
        settings_layout.addWidget(self.db_port_input, row, 1)
        row += 1
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        return widget
    
    def _connect_signals(self):
        """
        Connect signals and slots.
        """
        pass
    
    def _load_statistics(self):
        """
        Load and display statistics.
        """
        try:
            # Get stats from database
            cursor = self.db.get_connection().cursor()
            
            # Total pages
            cursor.execute("SELECT COUNT(*) FROM pages")
            total_pages = cursor.fetchone()[0]
            self.stats_labels['total_pages'].setText(str(total_pages))
            
            # Indexed terms
            cursor.execute("SELECT COUNT(DISTINCT term) FROM inverted_index")
            indexed_terms = cursor.fetchone()[0]
            self.stats_labels['indexed_terms'].setText(str(indexed_terms))
            
            cursor.close()
        
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
    
    def _start_crawler(self):
        """
        Start web crawler.
        """
        self.start_crawler_btn.setEnabled(False)
        self.pause_crawler_btn.setEnabled(True)
        self.stop_crawler_btn.setEnabled(True)
        self.crawler_status.setText("Status: Crawling...")
        self._log_crawler("Crawler started at " + datetime.now().isoformat())
    
    def _pause_crawler(self):
        """
        Pause web crawler.
        """
        self.pause_crawler_btn.setEnabled(False)
        self.crawler_status.setText("Status: Paused")
        self._log_crawler("Crawler paused")
    
    def _stop_crawler(self):
        """
        Stop web crawler.
        """
        self.start_crawler_btn.setEnabled(True)
        self.pause_crawler_btn.setEnabled(False)
        self.stop_crawler_btn.setEnabled(False)
        self.crawler_status.setText("Status: Idle")
        self._log_crawler("Crawler stopped")
    
    def _start_indexer(self):
        """
        Start indexer.
        """
        self.start_indexer_btn.setEnabled(False)
        self.stop_indexer_btn.setEnabled(True)
        self.indexer_status.setText("Status: Indexing...")
        self._log_indexer("Indexer started at " + datetime.now().isoformat())
    
    def _stop_indexer(self):
        """
        Stop indexer.
        """
        self.start_indexer_btn.setEnabled(True)
        self.stop_indexer_btn.setEnabled(False)
        self.indexer_status.setText("Status: Idle")
        self._log_indexer("Indexer stopped")
    
    def _execute_search(self):
        """
        Execute search query.
        """
        query = self.search_input.text()
        if not query:
            QMessageBox.warning(self, "Search", "Please enter a search query")
            return
        
        self._log_indexer(f"Searching for: {query}")
    
    def _backup_database(self):
        """
        Backup database.
        """
        QMessageBox.information(self, "Backup", "Database backup started...")
    
    def _verify_database(self):
        """
        Verify database integrity.
        """
        QMessageBox.information(self, "Verify", "Verifying database...")
    
    def _log_crawler(self, message: str):
        """
        Add message to crawler log.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.crawler_log.append(f"[{timestamp}] {message}")
    
    def _log_indexer(self, message: str):
        """
        Add message to indexer log.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.indexer_log.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """
        Handle window close event.
        """
        self.refresh_timer.stop()
        
        if self.crawler_worker and self.crawler_worker.isRunning():
            self.crawler_worker.stop()
        
        if self.indexer_worker and self.indexer_worker.isRunning():
            self.indexer_worker.stop()
        
        event.accept()
