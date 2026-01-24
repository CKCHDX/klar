"""
KSE Dialog Windows

Configuration and control dialogs for the KSE Control Center.
"""

from typing import Optional, Dict, Any
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox,
    QGridLayout, QLineEdit, QComboBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class CrawlerControlDialog(QDialog):
    """Dialog for crawler configuration and control."""
    
    crawling_started = pyqtSignal(dict)  # Settings
    
    def __init__(self, parent=None):
        """
        Initialize crawler control dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Crawler Control")
        self.setGeometry(200, 200, 400, 300)
        self._init_ui()
    
    def _init_ui(self):
        """
        Initialize UI.
        """
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Crawler Settings")
        settings_layout = QGridLayout(settings_group)
        
        row = 0
        
        # Batch size
        settings_layout.addWidget(QLabel("Batch Size:"), row, 0)
        self.batch_size = QSpinBox()
        self.batch_size.setValue(100)
        self.batch_size.setMinimum(1)
        self.batch_size.setMaximum(10000)
        settings_layout.addWidget(self.batch_size, row, 1)
        row += 1
        
        # Threads
        settings_layout.addWidget(QLabel("Threads:"), row, 0)
        self.threads = QSpinBox()
        self.threads.setValue(4)
        self.threads.setMinimum(1)
        self.threads.setMaximum(16)
        settings_layout.addWidget(self.threads, row, 1)
        row += 1
        
        # Timeout
        settings_layout.addWidget(QLabel("Timeout (s):"), row, 0)
        self.timeout = QSpinBox()
        self.timeout.setValue(10)
        self.timeout.setMinimum(1)
        self.timeout.setMaximum(300)
        settings_layout.addWidget(self.timeout, row, 1)
        row += 1
        
        # Politeness delay
        settings_layout.addWidget(QLabel("Politeness Delay (s):"), row, 0)
        self.politeness = QDoubleSpinBox()
        self.politeness.setValue(1.0)
        self.politeness.setMinimum(0.1)
        self.politeness.setMaximum(10.0)
        self.politeness.setSingleStep(0.1)
        settings_layout.addWidget(self.politeness, row, 1)
        row += 1
        
        # Respect robots.txt
        self.respect_robots = QCheckBox("Respect robots.txt")
        self.respect_robots.setChecked(True)
        settings_layout.addWidget(self.respect_robots, row, 0)
        row += 1
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.accept)
        button_layout.addWidget(start_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current settings.
        
        Returns:
            Settings dictionary
        """
        return {
            'batch_size': self.batch_size.value(),
            'threads': self.threads.value(),
            'timeout': self.timeout.value(),
            'politeness': self.politeness.value(),
            'respect_robots': self.respect_robots.isChecked(),
        }


class IndexingDialog(QDialog):
    """Dialog for indexer configuration."""
    
    indexing_started = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize indexing dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Indexing Configuration")
        self.setGeometry(200, 200, 400, 250)
        self._init_ui()
    
    def _init_ui(self):
        """
        Initialize UI.
        """
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Indexing Settings")
        settings_layout = QGridLayout(settings_group)
        
        row = 0
        
        # Batch size
        settings_layout.addWidget(QLabel("Batch Size:"), row, 0)
        self.batch_size = QSpinBox()
        self.batch_size.setValue(1000)
        self.batch_size.setMinimum(1)
        self.batch_size.setMaximum(100000)
        settings_layout.addWidget(self.batch_size, row, 1)
        row += 1
        
        # Use stemming
        self.use_stemming = QCheckBox("Use Stemming")
        self.use_stemming.setChecked(True)
        settings_layout.addWidget(self.use_stemming, row, 0)
        row += 1
        
        # Remove stopwords
        self.remove_stopwords = QCheckBox("Remove Stopwords")
        self.remove_stopwords.setChecked(True)
        settings_layout.addWidget(self.remove_stopwords, row, 0)
        row += 1
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        start_btn = QPushButton("Start Indexing")
        start_btn.clicked.connect(self.accept)
        button_layout.addWidget(start_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current settings.
        
        Returns:
            Settings dictionary
        """
        return {
            'batch_size': self.batch_size.value(),
            'use_stemming': self.use_stemming.isChecked(),
            'remove_stopwords': self.remove_stopwords.isChecked(),
        }


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: Dict[str, Any], parent=None):
        """
        Initialize settings dialog.
        
        Args:
            settings: Current settings
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Application Settings")
        self.setGeometry(200, 200, 500, 400)
        self.settings = settings
        self._init_ui()
    
    def _init_ui(self):
        """
        Initialize UI.
        """
        layout = QVBoxLayout(self)
        
        # Database settings
        db_group = QGroupBox("Database")
        db_layout = QGridLayout(db_group)
        
        db_layout.addWidget(QLabel("Host:"), 0, 0)
        self.db_host = QLineEdit()
        self.db_host.setText(self.settings.get('db_host', 'localhost'))
        db_layout.addWidget(self.db_host, 0, 1)
        
        db_layout.addWidget(QLabel("Port:"), 1, 0)
        self.db_port = QSpinBox()
        self.db_port.setValue(self.settings.get('db_port', 5432))
        db_layout.addWidget(self.db_port, 1, 1)
        
        layout.addWidget(db_group)
        
        # Search settings
        search_group = QGroupBox("Search")
        search_layout = QGridLayout(search_group)
        
        search_layout.addWidget(QLabel("Default Result Limit:"), 0, 0)
        self.result_limit = QSpinBox()
        self.result_limit.setValue(self.settings.get('result_limit', 10))
        search_layout.addWidget(self.result_limit, 0, 1)
        
        layout.addWidget(search_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current settings.
        
        Returns:
            Settings dictionary
        """
        return {
            'db_host': self.db_host.text(),
            'db_port': self.db_port.value(),
            'result_limit': self.result_limit.value(),
        }


class DatabaseDialog(QDialog):
    """Dialog for database management."""
    
    def __init__(self, parent=None):
        """
        Initialize database dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Database Management")
        self.setGeometry(200, 200, 500, 400)
        self._init_ui()
    
    def _init_ui(self):
        """
        Initialize UI.
        """
        layout = QVBoxLayout(self)
        
        # Statistics
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Actions
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout(action_group)
        
        backup_btn = QPushButton("Backup")
        backup_btn.clicked.connect(self._backup)
        action_layout.addWidget(backup_btn)
        
        verify_btn = QPushButton("Verify Integrity")
        verify_btn.clicked.connect(self._verify)
        action_layout.addWidget(verify_btn)
        
        vacuum_btn = QPushButton("Vacuum")
        vacuum_btn.clicked.connect(self._vacuum)
        action_layout.addWidget(vacuum_btn)
        
        layout.addWidget(action_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _backup(self):
        """Backup database."""
        QMessageBox.information(self, "Backup", "Backup started...")
    
    def _verify(self):
        """Verify database integrity."""
        QMessageBox.information(self, "Verify", "Verifying database...")
    
    def _vacuum(self):
        """Vacuum database."""
        QMessageBox.information(self, "Vacuum", "Vacuuming database...")
