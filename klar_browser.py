#!/usr/bin/env python3
"""
Klar Browser - Simple Web Browser for KSE Search Engine
Modern redesign with enhanced visual design system
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
    QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QAction, QTextOption, QColor
from PyQt6.QtWidgets import QApplication

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
    """Search result card widget with modern design"""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, result: Dict[str, Any]):
        super().__init__()
        self.result = result
        self.url = result.get('url', '')
        
        self.setStyleSheet("""
            ResultCard {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(45, 166, 178, 0.03) 100%);
                border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 12px;
                padding: 16px;
                margin: 6px 0px;
            }
            ResultCard:hover {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(45, 166, 178, 0.08) 100%);
                border-color: rgba(59, 130, 246, 0.3);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            }
        """)
        
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMaximumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title
        title = QLabel(result.get('title', 'No Title'))
        title.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: -0.5px;
            }
        """)
        title.setWordWrap(True)
        title.setMaximumHeight(50)
        layout.addWidget(title)
        
        # URL
        url_label = QLabel(self.url)
        url_label.setStyleSheet("""
            QLabel {
                color: #32b8c6;
                font-size: 11px;
                font-weight: 500;
                text-decoration: none;
            }
        """)
        url_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(url_label)
        
        # Snippet
        snippet = result.get('snippet', result.get('text', ''))
        if snippet:
            snippet_label = QLabel(snippet[:220] + ('...' if len(snippet) > 220 else ''))
            snippet_label.setStyleSheet("""
                QLabel {
                    color: #62748f;
                    font-size: 12px;
                    line-height: 1.5;
                }
            """)
            snippet_label.setWordWrap(True)
            snippet_label.setTextFormat(Qt.TextFormat.PlainText)
            layout.addWidget(snippet_label)
        
        # Score badge
        score = result.get('score', 0)
        if score:
            score_container = QWidget()
            score_layout = QHBoxLayout(score_container)
            score_layout.setContentsMargins(0, 0, 0, 0)
            score_layout.setSpacing(0)
            
            score_badge = QLabel(f"Relevance: {score:.0%}")
            score_badge.setStyleSheet("""
                QLabel {
                    background: rgba(59, 130, 246, 0.2);
                    color: #3b82f6;
                    font-size: 10px;
                    font-weight: 600;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
            """)
            score_layout.addWidget(score_badge)
            score_layout.addStretch()
            layout.addWidget(score_container)
    
    def mousePressEvent(self, event):
        """Handle click on result card"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.url)
        super().mousePressEvent(event)


class SearchHistoryDialog(QDialog):
    """Search history dialog with modern styling"""
    
    def __init__(self, history: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search History")
        self.setModal(True)
        self.resize(500, 400)
        self.setStyleSheet(self._get_dialog_styles())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("Recent Searches")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #3b82f6;")
        layout.addWidget(title)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
                background: #f8fafc;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(59, 130, 246, 0.1);
                color: #62748f;
            }
            QListWidget::item:hover {
                background-color: rgba(59, 130, 246, 0.08);
            }
            QListWidget::item:selected {
                background-color: rgba(59, 130, 246, 0.15);
                color: #3b82f6;
            }
        """)
        
        for query in history:
            item = QListWidgetItem("🔍 " + query)
            self.history_list.addItem(item)
        
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet(self._get_secondary_button_style())
        clear_btn.clicked.connect(self.history_list.clear)
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(self._get_primary_button_style())
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    @staticmethod
    def _get_dialog_styles():
        return """
            QDialog {
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            }
        """
    
    @staticmethod
    def _get_primary_button_style():
        return """
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
            QPushButton:pressed {
                background: #2563eb;
            }
        """
    
    @staticmethod
    def _get_secondary_button_style():
        return """
            QPushButton {
                background: #e2e8f0;
                color: #62748f;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #cbd5e1;
            }
        """


class SettingsDialog(QDialog):
    """Settings dialog with modern design"""
    
    def __init__(self, current_url: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setModal(True)
        self.resize(500, 350)
        self.setStyleSheet("""
            QDialog {
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            }
        """)
        
        # Config file location
        self.config_file = Path.home() / '.kse' / 'klar_browser_config.json'
        
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Info label
        info_label = QLabel(
            "🌐 Configure the KSE server connection.\n\n"
            "Examples:\n"
            "  • Local: http://localhost:5000\n"
            "  • Remote IP: http://192.168.1.100:5000\n"
            "  • Remote hostname: http://my-server.com:5000"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background: rgba(59, 130, 246, 0.08);
                color: #62748f;
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid #3b82f6;
            }
        """)
        layout.addWidget(info_label)
        
        # Server settings
        server_group = QGroupBox("Server Configuration")
        server_group.setStyleSheet("""
            QGroupBox {
                color: #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                padding-top: 12px;
                padding-left: 12px;
                padding-right: 12px;
                margin-top: 6px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        server_layout = QGridLayout(server_group)
        
        server_layout.addWidget(QLabel("KSE Server URL:"), 0, 0)
        self.server_url_input = QLineEdit(current_url)
        self.server_url_input.setPlaceholderText("http://localhost:5000")
        self.server_url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 6px;
                background: white;
                color: #3b82f6;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: rgba(59, 130, 246, 0.02);
            }
        """)
        server_layout.addWidget(self.server_url_input, 0, 1)
        
        test_btn = QPushButton("Test Connection")
        test_btn.setStyleSheet("""
            QPushButton {
                background: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.3);
            }
        """)
        test_btn.clicked.connect(self._test_connection)
        server_layout.addWidget(test_btn, 1, 1)
        
        self.connection_status = QLabel("Not tested")
        self.connection_status.setStyleSheet("color: #62748f; padding: 5px;")
        server_layout.addWidget(self.connection_status, 2, 0, 1, 2)
        
        layout.addWidget(server_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #e2e8f0;
                color: #62748f;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #cbd5e1;
            }
        """)
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
            logger.info("Configuration saved successfully")
        except Exception as e:
            error_msg = f"Failed to save config: {e}"
            logger.error(error_msg)
            QMessageBox.warning(self, "Save Failed", f"Could not save configuration:\n{error_msg}")
    
    def _test_connection(self):
        """Test connection to server"""
        url = self.server_url_input.text().strip()
        
        if not url:
            self.connection_status.setText("✗ Please enter a server URL")
            self.connection_status.setStyleSheet("color: #f44336; padding: 5px;")
            return
        
        if not (url.startswith('http://') or url.startswith('https://')):
            self.connection_status.setText("✗ URL must start with http:// or https://")
            self.connection_status.setStyleSheet("color: #f44336; padding: 5px;")
            return
        
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
    """Main Klar Browser window with modern design"""
    
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
        self.setWindowTitle("Klar Browser - KSE Search")
        self.setGeometry(100, 100, 1300, 850)
        
        # Setup UI
        self._create_menu_bar()
        self._create_central_widget()
        self._apply_styles()
        
        # Show welcome message
        self._show_welcome()
        
        # Check server
        QTimer.singleShot(500, self._check_server_connection)
        
        logger.info(f"Klar Browser initialized with server: {self.server_url}")
    
    def load_config(self) -> str:
        """Load server URL from config file"""
        env_url = os.getenv("KSE_SERVER_URL")
        if env_url:
            logger.info(f"Using server URL from environment: {env_url}")
            return env_url
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    url = config.get('server_url')
                    if url:
                        logger.info(f"Loaded server URL from config: {url}")
                        return url
        except:
            logger.warning("Config file error, using defaults")
        
        default_url = "http://localhost:5000"
        logger.info(f"Using default server URL: {default_url}")
        return default_url
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: white;
                border-bottom: 1px solid rgba(59, 130, 246, 0.1);
                color: #62748f;
            }
            QMenuBar::item:selected {
                background: rgba(59, 130, 246, 0.08);
            }
            QMenu {
                background: white;
                border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 6px;
            }
            QMenu::item:selected {
                background: rgba(59, 130, 246, 0.12);
            }
        """)
        
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
    
    def _create_central_widget(self):
        """Create central widget with modern design"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top bar with search
        top_bar = self._create_top_bar()
        layout.addWidget(top_bar)
        
        # Results area
        self.stacked_widget = QStackedWidget()
        
        # Welcome page
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_widget = None
        self.stacked_widget.addWidget(self.welcome_page)
        
        # Results page
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(59, 130, 246, 0.4);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(59, 130, 246, 0.6);
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(8)
        self.results_layout.setContentsMargins(24, 24, 24, 24)
        self.results_layout.addStretch()
        
        scroll.setWidget(self.results_widget)
        self.stacked_widget.addWidget(scroll)
        
        layout.addWidget(self.stacked_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: white;
                border-top: 1px solid rgba(59, 130, 246, 0.1);
                color: #62748f;
            }
        """)
        
        self.connection_label = QLabel("⚫ Disconnected")
        self.connection_label.setStyleSheet("color: #f44336; padding: 4px 8px;")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        self.setStatusBar(self.status_bar)
    
    def _create_top_bar(self):
        """Create top search bar with modern design"""
        top_bar = QWidget()
        top_bar.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, white 0%, #f8fafc 100%);
                border-bottom: 1px solid rgba(59, 130, 246, 0.1);
            }
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)
        
        # Logo
        logo = QLabel("🔍 Klar")
        logo_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        logo.setFont(logo_font)
        logo.setStyleSheet("color: #3b82f6;")
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_input.setMinimumWidth(400)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                font-size: 12px;
                background: white;
                color: #3b82f6;
                selection-background-color: rgba(59, 130, 246, 0.3);
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: rgba(59, 130, 246, 0.01);
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)
        self.search_input.returnPressed.connect(self._perform_search)
        layout.addWidget(self.search_input, 1)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setFixedWidth(100)
        search_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
            QPushButton:pressed {
                background: #2563eb;
            }
        """)
        search_btn.clicked.connect(self._perform_search)
        layout.addWidget(search_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: rgba(59, 130, 246, 0.1);
                color: #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.2);
            }
        """)
        settings_btn.clicked.connect(self._show_settings)
        layout.addWidget(settings_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        return top_bar
    
    def _apply_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            }
        """)
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome = QWidget()
        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(24)
        
        # Logo/Title
        title = QLabel("Klar Browser")
        title_font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #3b82f6; margin-bottom: 12px;")
        welcome_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Your gateway to the KSE Search Engine")
        subtitle_font = QFont("Segoe UI", 16)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #62748f;")
        welcome_layout.addWidget(subtitle)
        
        welcome_layout.addSpacing(40)
        
        # Features
        features_widget = QWidget()
        features_layout = QHBoxLayout(features_widget)
        features_layout.setSpacing(20)
        features = [
            ("🚀", "Fast & Efficient"),
            ("🔒", "Privacy Focused"),
            ("🎯", "Accurate Results"),
        ]
        
        for icon, text in features:
            feature = QLabel(f"{icon}\n{text}")
            feature.setAlignment(Qt.AlignmentFlag.AlignCenter)
            feature.setStyleSheet("""
                QLabel {
                    background: rgba(59, 130, 246, 0.08);
                    border-radius: 8px;
                    padding: 20px;
                    font-weight: 600;
                    color: #3b82f6;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                }
            """)
            features_layout.addWidget(feature)
        
        welcome_layout.addWidget(features_widget)
        
        welcome_layout.addStretch()
        
        # Replace welcome page widget
        while self.welcome_page.layout().count():
            self.welcome_page.layout().takeAt(0).widget().deleteLater()
        self.welcome_page.layout().addWidget(welcome)
        
        self.stacked_widget.setCurrentIndex(0)
    
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
        self._clear_results()
        
        # Show loading
        loading = QLabel("🔍 Searching...")
        loading.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                font-size: 16px;
                font-weight: 600;
                padding: 40px;
            }
        """)
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.insertWidget(0, loading)
        
        self.stacked_widget.setCurrentIndex(1)
        self.status_bar.showMessage(f"Searching for: {query}")
        
        # Start search worker
        self.search_worker = SearchWorker(query, self.server_url)
        self.search_worker.search_completed.connect(self._on_search_completed)
        self.search_worker.search_error.connect(self._on_search_error)
        self.search_worker.start()
        
        logger.info(f"Search initiated: {query}")
    
    def _on_search_completed(self, data: Dict[str, Any]):
        """Handle search completion"""
        self._clear_results()
        
        results = data.get('results', [])
        query = data.get('query', '')
        search_time = data.get('search_time', 0)
        total = len(results)
        
        self.current_results = results
        
        # Add header
        header = QLabel(f"<b>{total} result(s)</b> for <b>{query}</b> · {search_time:.3f}s")
        header.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                font-size: 13px;
                padding: 12px 0px;
                border-bottom: 1px solid rgba(59, 130, 246, 0.1);
                margin-bottom: 8px;
            }
        """)
        self.results_layout.insertWidget(0, header)
        
        if total == 0:
            no_results = QLabel("No results found. Try different keywords.")
            no_results.setStyleSheet("""
                QLabel {
                    color: #94a3b8;
                    font-size: 14px;
                    padding: 40px;
                    text-align: center;
                }
            """)
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.insertWidget(1, no_results)
        else:
            for i, result in enumerate(results):
                card = ResultCard(result)
                card.clicked.connect(self._on_result_clicked)
                self.results_layout.insertWidget(i + 1, card)
        
        self.status_bar.showMessage(f"Found {total} result(s)", 3000)
        logger.info(f"Search completed: {total} results")
    
    def _on_search_error(self, error: str):
        """Handle search error"""
        self._clear_results()
        
        error_label = QLabel(f"<b>Search Error</b><br>{error}")
        error_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-size: 14px;
                padding: 40px;
                text-align: center;
            }
        """)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.insertWidget(0, error_label)
        
        self.status_bar.showMessage(f"Error: {error}", 5000)
        logger.error(f"Search error: {error}")
    
    def _on_result_clicked(self, url: str):
        """Handle result click"""
        logger.info(f"Result clicked: {url}")
        self.status_bar.showMessage(f"Opening: {url}", 3000)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Result Details")
        dialog.resize(700, 500)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # URL
        url_label = QLabel(f"<b>URL:</b> <a href='{url}' style='color: #3b82f6;'>{url}</a>")
        url_label.setTextFormat(Qt.TextFormat.RichText)
        url_label.setOpenExternalLinks(True)
        url_label.setWordWrap(True)
        url_label.setStyleSheet("padding: 8px; font-size: 11px;")
        layout.addWidget(url_label)
        
        # Find full result
        result = next((r for r in self.current_results if r.get('url') == url), {})
        
        # Content
        content_label = QLabel("<b>Content:</b>")
        content_label.setStyleSheet("padding: 8px; font-size: 11px; color: #3b82f6;")
        layout.addWidget(content_label)
        
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setPlainText(result.get('text', 'No content available'))
        content_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 6px;
                padding: 8px;
                background: #f8fafc;
            }
        """)
        layout.addWidget(content_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _clear_results(self):
        """Clear search results"""
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.current_results = []
    
    def _show_history(self):
        """Show search history"""
        if not self.search_history:
            QMessageBox.information(self, "Search History", "No search history available")
            return
        
        dialog = SearchHistoryDialog(self.search_history, self)
        if dialog.exec():
            selected = dialog.history_list.currentItem()
            if selected:
                query = selected.text().replace("🔍 ", "")
                self.search_input.setText(query)
                self._perform_search()
    
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
                self.connection_label.setStyleSheet("color: #4caf50; padding: 4px 8px; font-weight: 600;")
                logger.info("Server connection successful")
            else:
                self.connection_label.setText("🔴 Server Error")
                self.connection_label.setStyleSheet("color: #f44336; padding: 4px 8px;")
        except:
            self.connection_label.setText("⚫ Disconnected")
            self.connection_label.setStyleSheet("color: #f44336; padding: 4px 8px;")
            logger.warning("Server connection failed")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Klar Browser")
    app.setOrganizationName("KSE Project")
    app.setStyle('Fusion')
    
    browser = KlarBrowser()
    browser.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
