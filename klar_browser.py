#!/usr/bin/env python3
"""
Klar Browser - Simple Web Browser for KSE Search Engine
A lightweight browser client with integrated search functionality
"""

import sys
import logging
import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextBrowser, QLabel, QScrollArea,
    QFrame, QSplitter, QListWidget, QListWidgetItem, QMessageBox,
    QStatusBar, QToolBar, QMenu, QDialog, QTextEdit, QGroupBox,
    QGridLayout
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QAction, QTextOption

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchWorker(QThread):
    """Background worker for search requests"""
    
    search_completed = pyqtSignal(dict)
    search_error = pyqtSignal(str)
    
    def __init__(self, query: str, server_url: str):
        super().__init__()
        self.query = query
        self.server_url = server_url
    
    def run(self):
        """Execute search in background"""
        try:
            url = f"{self.server_url}/api/search"
            params = {'q': self.query}
            
            logger.info(f"Searching for: {self.query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.search_completed.emit(data)
            
        except requests.exceptions.ConnectionError:
            self.search_error.emit("Unable to connect to KSE server. Please ensure the server is running.")
        except requests.exceptions.Timeout:
            self.search_error.emit("Search request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            self.search_error.emit(f"Search error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            self.search_error.emit(f"Unexpected error: {str(e)}")


class ResultCard(QFrame):
    """Search result card widget"""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, result: Dict[str, Any]):
        super().__init__()
        self.result = result
        self.url = result.get('url', '')
        
        self.setStyleSheet("""
            ResultCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            ResultCard:hover {
                background-color: #f5f5f5;
                border-color: #1976d2;
            }
        """)
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(150)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title
        title = QLabel(result.get('title', 'No Title'))
        title.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-size: 16pt;
                font-weight: bold;
                text-decoration: underline;
            }
        """)
        title.setWordWrap(True)
        title.setMaximumHeight(60)
        title.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(title)
        
        # URL
        url_label = QLabel(self.url)
        url_label.setStyleSheet("""
            QLabel {
                color: #388e3c;
                font-size: 10pt;
            }
        """)
        url_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(url_label)
        
        # Snippet
        snippet = result.get('snippet', result.get('text', ''))
        if snippet:
            snippet_label = QLabel(snippet[:200] + ('...' if len(snippet) > 200 else ''))
            snippet_label.setStyleSheet("""
                QLabel {
                    color: #424242;
                    font-size: 11pt;
                }
            """)
            snippet_label.setWordWrap(True)
            snippet_label.setTextFormat(Qt.TextFormat.PlainText)
            layout.addWidget(snippet_label)
        
        # Score (if available)
        score = result.get('score', 0)
        if score:
            score_label = QLabel(f"Relevance: {score:.2f}")
            score_label.setStyleSheet("""
                QLabel {
                    color: #757575;
                    font-size: 9pt;
                }
            """)
            layout.addWidget(score_label)
    
    def mousePressEvent(self, event):
        """Handle click on result card"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.url)
        super().mousePressEvent(event)


class SearchHistoryDialog(QDialog):
    """Search history dialog"""
    
    def __init__(self, history: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search History")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Recent Searches")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        
        for query in history:
            item = QListWidgetItem(query)
            self.history_list.addItem(item)
        
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.history_list.clear)
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, current_url: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setModal(True)
        self.resize(450, 300)
        
        # Config file location
        self.config_file = Path.home() / '.kse' / 'klar_browser_config.json'
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "Configure the KSE server connection.\n\n"
            "Examples:\n"
            "  • Local: http://localhost:5000\n"
            "  • Remote IP: http://192.168.1.100:5000\n"
            "  • Remote hostname: http://my-server.com:5000"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # Server settings
        server_group = QGroupBox("Server Configuration")
        server_layout = QGridLayout(server_group)
        
        server_layout.addWidget(QLabel("KSE Server URL:"), 0, 0)
        self.server_url_input = QLineEdit(current_url)
        self.server_url_input.setPlaceholderText("http://localhost:5000")
        server_layout.addWidget(self.server_url_input, 0, 1)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_connection)
        server_layout.addWidget(test_btn, 1, 1)
        
        self.connection_status = QLabel("Not tested")
        self.connection_status.setStyleSheet("color: #757575; padding: 5px;")
        server_layout.addWidget(self.connection_status, 2, 0, 1, 2)
        
        layout.addWidget(server_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                'server_url': self.server_url_input.text().strip()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _test_connection(self):
        """Test connection to server"""
        url = self.server_url_input.text().strip()
        try:
            response = requests.get(f"{url}/api/health", timeout=5)
            if response.status_code == 200:
                self.connection_status.setText("✓ Connection successful")
                self.connection_status.setStyleSheet("color: #4caf50; font-weight: bold; padding: 5px;")
            else:
                self.connection_status.setText(f"✗ Server returned status {response.status_code}")
                self.connection_status.setStyleSheet("color: #f44336; padding: 5px;")
        except Exception as e:
            self.connection_status.setText(f"✗ Connection failed: {str(e)}")
            self.connection_status.setStyleSheet("color: #f44336; padding: 5px;")
    
    def accept(self):
        """Save and close"""
        self.save_config()
        super().accept()
    
    def get_server_url(self) -> str:
        """Get configured server URL"""
        return self.server_url_input.text().strip()


class KlarBrowser(QMainWindow):
    """Main Klar Browser window"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration file
        self.config_file = Path.home() / '.kse' / 'klar_browser_config.json'
        
        # Configuration
        self.server_url = self.load_config()
        self.search_history = []
        self.current_results = []
        self.search_worker = None
        
        # Setup window
        self.setWindowTitle("Klar Browser - KSE Search Client")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Apply styling
        self._apply_styles()
        
        # Show welcome message
        self._show_welcome()
        
        logger.info(f"Klar Browser initialized with server: {self.server_url}")
    
    def load_config(self) -> str:
        """Load server URL from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    url = config.get('server_url', 'http://localhost:5000')
                    logger.info(f"Loaded server URL from config: {url}")
                    return url
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        # Return default if config doesn't exist or fails to load
        return os.getenv("KSE_SERVER_URL", "http://localhost:5000")
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        search_action = QAction("&New Search", self)
        search_action.setShortcut(QKeySequence("Ctrl+N"))
        search_action.triggered.connect(self._focus_search)
        file_menu.addAction(search_action)
        
        file_menu.addSeparator()
        
        history_action = QAction("Search &History", self)
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        history_action.triggered.connect(self._show_history)
        file_menu.addAction(history_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        tools_menu.addSeparator()
        
        clear_action = QAction("&Clear Results", self)
        clear_action.triggered.connect(self._clear_results)
        tools_menu.addAction(clear_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_input.setMinimumWidth(400)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 24px;
                font-size: 12pt;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1976d2;
            }
        """)
        self.search_input.returnPressed.connect(self._perform_search)
        toolbar.addWidget(self.search_input)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        search_btn.clicked.connect(self._perform_search)
        toolbar.addWidget(search_btn)
        
        toolbar.addSeparator()
        
        # Clear button
        clear_btn = QPushButton("✕ Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        clear_btn.clicked.connect(self._clear_results)
        toolbar.addWidget(clear_btn)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self._show_settings)
        toolbar.addWidget(settings_btn)
        
        self.addToolBar(toolbar)
    
    def _create_central_widget(self):
        """Create central widget with results area"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Results header
        header_layout = QHBoxLayout()
        
        self.results_label = QLabel("Enter a search query to begin")
        self.results_label.setStyleSheet("""
            QLabel {
                color: #424242;
                font-size: 12pt;
                padding: 8px;
            }
        """)
        header_layout.addWidget(self.results_label)
        
        header_layout.addStretch()
        
        # Search time label
        self.search_time_label = QLabel("")
        self.search_time_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 10pt;
                padding: 8px;
            }
        """)
        header_layout.addWidget(self.search_time_label)
        
        layout.addLayout(header_layout)
        
        # Results scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #fafafa;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(8)
        self.results_layout.setContentsMargins(8, 8, 8, 8)
        self.results_layout.addStretch()
        
        scroll.setWidget(self.results_widget)
        layout.addWidget(scroll)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status
        self.connection_label = QLabel("⚫ Disconnected")
        self.connection_label.setStyleSheet("color: #f44336; padding: 4px;")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # Check server on startup
        QTimer.singleShot(500, self._check_server_connection)
    
    def _apply_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
                spacing: 8px;
            }
            QStatusBar {
                background-color: white;
                border-top: 1px solid #e0e0e0;
            }
        """)
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome = QLabel("""
            <div style='text-align: center; padding: 40px;'>
                <h1 style='color: #1976d2; font-size: 32pt;'>Welcome to Klar Browser</h1>
                <p style='color: #424242; font-size: 14pt; margin-top: 20px;'>
                    Your gateway to the KSE Search Engine
                </p>
                <p style='color: #757575; font-size: 12pt; margin-top: 30px;'>
                    Enter a search query above to get started
                </p>
            </div>
        """)
        welcome.setTextFormat(Qt.TextFormat.RichText)
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.insertWidget(0, welcome)
    
    def _focus_search(self):
        """Focus on search input"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def _perform_search(self):
        """Perform search"""
        query = self.search_input.text().strip()
        
        if not query:
            self.status_bar.showMessage("Please enter a search query", 3000)
            return
        
        # Add to history
        if query not in self.search_history:
            self.search_history.insert(0, query)
            if len(self.search_history) > 50:
                self.search_history.pop()
        
        # Clear previous results
        self._clear_results(keep_header=True)
        
        # Show loading message
        loading = QLabel("🔍 Searching...")
        loading.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-size: 16pt;
                font-weight: bold;
                padding: 40px;
            }
        """)
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.insertWidget(0, loading)
        
        self.results_label.setText(f"Searching for: {query}")
        self.status_bar.showMessage(f"Searching for: {query}")
        
        # Start search worker
        self.search_worker = SearchWorker(query, self.server_url)
        self.search_worker.search_completed.connect(self._on_search_completed)
        self.search_worker.search_error.connect(self._on_search_error)
        self.search_worker.start()
        
        logger.info(f"Search initiated: {query}")
    
    def _on_search_completed(self, data: Dict[str, Any]):
        """Handle search completion"""
        # Clear loading message
        self._clear_results(keep_header=True)
        
        results = data.get('results', [])
        query = data.get('query', '')
        search_time = data.get('search_time', 0)
        total = len(results)
        
        self.current_results = results
        
        # Update header
        self.results_label.setText(f"Found {total} result(s) for: {query}")
        self.search_time_label.setText(f"Search time: {search_time:.3f}s")
        
        if total == 0:
            # No results
            no_results = QLabel("""
                <div style='text-align: center; padding: 40px;'>
                    <p style='color: #757575; font-size: 18pt;'>
                        No results found
                    </p>
                    <p style='color: #9e9e9e; font-size: 12pt; margin-top: 20px;'>
                        Try different keywords or check your spelling
                    </p>
                </div>
            """)
            no_results.setTextFormat(Qt.TextFormat.RichText)
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.insertWidget(0, no_results)
        else:
            # Display results
            for i, result in enumerate(results):
                card = ResultCard(result)
                card.clicked.connect(self._on_result_clicked)
                self.results_layout.insertWidget(i, card)
        
        self.status_bar.showMessage(f"Search completed: {total} result(s) found", 5000)
        logger.info(f"Search completed: {total} results")
    
    def _on_search_error(self, error: str):
        """Handle search error"""
        self._clear_results(keep_header=True)
        
        error_label = QLabel(f"""
            <div style='text-align: center; padding: 40px;'>
                <p style='color: #f44336; font-size: 16pt; font-weight: bold;'>
                    Search Error
                </p>
                <p style='color: #757575; font-size: 12pt; margin-top: 20px;'>
                    {error}
                </p>
            </div>
        """)
        error_label.setTextFormat(Qt.TextFormat.RichText)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.insertWidget(0, error_label)
        
        self.results_label.setText("Search failed")
        self.status_bar.showMessage(f"Error: {error}", 5000)
        
        QMessageBox.warning(self, "Search Error", error)
        logger.error(f"Search error: {error}")
    
    def _on_result_clicked(self, url: str):
        """Handle result click"""
        logger.info(f"Result clicked: {url}")
        self.status_bar.showMessage(f"Opening: {url}", 3000)
        
        # Show result details dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Result Details")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # URL
        url_label = QLabel(f"<b>URL:</b> <a href='{url}'>{url}</a>")
        url_label.setTextFormat(Qt.TextFormat.RichText)
        url_label.setOpenExternalLinks(True)
        url_label.setWordWrap(True)
        url_label.setStyleSheet("padding: 10px; font-size: 11pt;")
        layout.addWidget(url_label)
        
        # Find full result
        result = next((r for r in self.current_results if r.get('url') == url), {})
        
        # Content
        content_label = QLabel("<b>Content:</b>")
        content_label.setStyleSheet("padding: 10px; font-size: 11pt;")
        layout.addWidget(content_label)
        
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setPlainText(result.get('text', 'No content available'))
        content_text.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 4px; padding: 8px;")
        layout.addWidget(content_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _clear_results(self, keep_header: bool = False):
        """Clear search results"""
        # Remove all widgets from results layout
        while self.results_layout.count() > (0 if not keep_header else 0):
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not keep_header:
            self.results_label.setText("Enter a search query to begin")
            self.search_time_label.setText("")
            self.current_results = []
    
    def _show_history(self):
        """Show search history"""
        if not self.search_history:
            QMessageBox.information(
                self,
                "Search History",
                "No search history available"
            )
            return
        
        dialog = SearchHistoryDialog(self.search_history, self)
        if dialog.exec():
            # User can select a query from history
            selected = dialog.history_list.currentItem()
            if selected:
                self.search_input.setText(selected.text())
    
    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.server_url, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_url = dialog.get_server_url()
            if new_url != self.server_url:
                self.server_url = new_url
                self.status_bar.showMessage(f"Server URL updated: {self.server_url}", 3000)
                self._check_server_connection()
    
    def _check_server_connection(self):
        """Check server connection status"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=3)
            if response.status_code == 200:
                self.connection_label.setText("🟢 Connected")
                self.connection_label.setStyleSheet("color: #4caf50; padding: 4px;")
                logger.info("Server connection successful")
            else:
                self.connection_label.setText("🔴 Server Error")
                self.connection_label.setStyleSheet("color: #f44336; padding: 4px;")
        except:
            self.connection_label.setText("⚫ Disconnected")
            self.connection_label.setStyleSheet("color: #f44336; padding: 4px;")
            logger.warning("Server connection failed")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Klar Browser</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> A lightweight browser client for the KSE Search Engine</p>
        <hr>
        <p>Klar Browser provides a simple and intuitive interface for searching</p>
        <p>and browsing content indexed by the Klar Search Engine (KSE).</p>
        <hr>
        <p><b>Features:</b></p>
        <ul>
            <li>Fast and efficient search</li>
            <li>Clean and modern interface</li>
            <li>Search history tracking</li>
            <li>Configurable server connection</li>
            <li>Real-time result display</li>
        </ul>
        <hr>
        <p>© 2024 Klar Search Engine Project</p>
        """
        
        QMessageBox.about(self, "About Klar Browser", about_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Klar Browser")
    app.setOrganizationName("KSE Project")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show browser
    browser = KlarBrowser()
    browser.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
