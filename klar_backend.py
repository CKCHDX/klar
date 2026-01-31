#!/usr/bin/env python3
"""
Klar Browser Backend
Minimal Python backend that loads the HTML UI and handles API requests
Run: python klar_backend.py
Build: build.bat (Windows) or build.sh (Linux/macOS)
"""

import sys
import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QThread, Qt, QPoint, QRect
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QTimer

# Try to import QWebChannel - handle both PyQt6 versions
try:
    from PyQt6.QtWebChannel import QWebChannel
except ImportError:
    try:
        from PyQt6.QtCore import QWebChannel
    except ImportError:
        # Fallback: use simpler approach without WebChannel
        print("Warning: QWebChannel not found, using alternative approach")
        QWebChannel = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default server URL - uses public domain
# This allows the client to work from anywhere
DEFAULT_SERVER_URL = "http://klar.oscyra.solutions:5000"


class CustomTitleBar(QWidget):
    """Custom window title bar with minimize, maximize, and close buttons"""
    
    def __init__(self, parent=None, title="Klar - Search Browser"):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = None
        self.is_maximized = False
        
        # Setup title bar
        self.setFixedHeight(35)
        self.setStyleSheet("""
            QWidget {
                background: #0f172a;
                border-bottom: 1px solid #1e293b;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(0)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #f1f5f9;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                padding: 0px 8px;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #cbd5e0;
                border: none;
                font-size: 18px;
                font-weight: bold;
                padding: 0px 12px;
                min-width: 40px;
                min-height: 35px;
            }
            QPushButton:hover {
                background: #334155;
                color: #00e5ff;
            }
            QPushButton:pressed {
                background: #1e293b;
            }
        """)
        self.minimize_btn.clicked.connect(self.minimize_window)
        
        # Maximize button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #cbd5e0;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 0px 12px;
                min-width: 40px;
                min-height: 35px;
            }
            QPushButton:hover {
                background: #334155;
                color: #00e5ff;
            }
            QPushButton:pressed {
                background: #1e293b;
            }
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #cbd5e0;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 0px 12px;
                min-width: 40px;
                min-height: 35px;
            }
            QPushButton:hover {
                background: #ff6b35;
                color: #f1f5f9;
            }
            QPushButton:pressed {
                background: #cc5529;
            }
        """)
        self.close_btn.clicked.connect(self.close_window)
        
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """Handle title bar drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Drag window when title bar is dragged"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            if not self.is_maximized:
                self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Release drag when mouse button is released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to maximize/restore"""
        self.toggle_maximize()
        event.accept()
    
    def minimize_window(self):
        """Minimize the window"""
        self.parent_window.showMinimized()
    
    def toggle_maximize(self):
        """Toggle maximize/restore"""
        if self.is_maximized:
            self.parent_window.showNormal()
            self.is_maximized = False
            self.maximize_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.is_maximized = True
            self.maximize_btn.setText("❐")
    
    def close_window(self):
        """Close the window"""
        self.parent_window.close()
    
    def set_title(self, title: str):
        """Update the window title"""
        self.title_label.setText(title)


class SearchWorker(QThread):
    """Background thread for search requests"""
    finished = pyqtSignal(str)  # Signal to emit results
    
    def __init__(self, server_url: str, query: str):
        super().__init__()
        self.server_url = server_url
        self.query = query
    
    def run(self):
        """Execute search in background thread"""
        try:
            if not self.query.strip():
                self.finished.emit(json.dumps({"results": [], "error": "Empty query"}))
                return

            url = f"{self.server_url}/api/search"
            params = {'q': self.query}
            
            logger.info(f"Searching: {self.query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            # Normalize fields
            normalized = []
            for result in results:
                normalized.append({
                    'url': result.get('url') or result.get('link', ''),
                    'title': result.get('title') or result.get('name', 'Untitled'),
                    'snippet': result.get('snippet') or result.get('description') or '',
                    'score': result.get('score', 0)
                })
            
            result_json = json.dumps({
                "results": normalized,
                "count": len(normalized),
                "query": self.query
            })
            self.finished.emit(result_json)
            
        except requests.exceptions.ConnectionError:
            error = f"Cannot connect to {self.server_url}"
            logger.error(error)
            self.finished.emit(json.dumps({"results": [], "error": error}))
        except requests.exceptions.Timeout:
            error = "Search timeout"
            logger.error(error)
            self.finished.emit(json.dumps({"results": [], "error": error}))
        except Exception as e:
            error = str(e)
            logger.error(f"Search error: {error}")
            self.finished.emit(json.dumps({"results": [], "error": error}))


class SearchAPI(QObject):
    """Backend API exposed to JavaScript"""
    searchComplete = pyqtSignal(str)  # Signal to send results to JavaScript
    navigateRequested = pyqtSignal(str)  # Signal to request navigation
    
    def __init__(self, server_url: str = DEFAULT_SERVER_URL):
        super().__init__()
        self.server_url = server_url
        self.config_file = Path.home() / '.kse' / 'klar_config.json'
        self._load_config()
        self.worker = None

    def _load_config(self):
        """Load server configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.server_url = config.get('server_url', self.server_url)
                    logger.info(f"Loaded server URL: {self.server_url}")
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

    @pyqtSlot(str)
    def search(self, query: str):
        """Execute search asynchronously"""
        # Cancel any existing search
        if self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        
        # Start new search in background thread
        self.worker = SearchWorker(self.server_url, query)
        self.worker.finished.connect(self._on_search_complete)
        self.worker.start()
    
    def _on_search_complete(self, result: str):
        """Handle search completion"""
        self.searchComplete.emit(result)

    @pyqtSlot(result=str)
    def get_config(self) -> str:
        """Return current configuration"""
        return json.dumps({
            "server_url": self.server_url,
            "config_path": str(self.config_file)
        })

    @pyqtSlot(str, result=bool)
    def set_server(self, server_url: str) -> bool:
        """Update and save server URL"""
        try:
            # Test connection first
            response = requests.get(f"{server_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.server_url = server_url
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump({'server_url': server_url}, f, indent=2)
                logger.info(f"Server URL updated: {server_url}")
                return True
            return False
        except Exception as e:
            logger.error(f"Server test failed: {e}")
            return False

    @pyqtSlot(str, result=str)
    def check_domain(self, domain: str) -> str:
        """Check if a domain is allowed by the server"""
        try:
            # Clean up domain
            domain = domain.lower().strip()
            if domain.startswith('http://') or domain.startswith('https://'):
                from urllib.parse import urlparse
                domain = urlparse(domain).netloc
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check with server
            url = f"{self.server_url}/api/check-domain"
            params = {'domain': domain}
            
            logger.info(f"Checking domain: {domain}")
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return json.dumps({
                "allowed": data.get('allowed', False),
                "domain": domain,
                "message": data.get('message', '')
            })
            
        except requests.exceptions.ConnectionError:
            error = f"Cannot connect to server"
            logger.error(error)
            return json.dumps({"allowed": False, "domain": domain, "error": error})
        except Exception as e:
            error = str(e)
            logger.error(f"Domain check error: {error}")
            return json.dumps({"allowed": False, "domain": domain, "error": error})
    
    @pyqtSlot(str)
    def navigate_to(self, url: str):
        """Navigate to URL - emit signal for main window to handle"""
        logger.info(f"Navigation requested from JavaScript: {url}")
        self.navigateRequested.emit(url)


class KlarBrowser(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set frameless window with custom title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Window setup
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Set stylesheet for the main window background
        self.setStyleSheet("QMainWindow { background: #0f172a; }")
        
        # Initialize backend API
        self.api = SearchAPI()
        
        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add custom title bar
        self.title_bar = CustomTitleBar(self, "Klar - Search Browser")
        layout.addWidget(self.title_bar)
        
        # Create navigation bar (hidden by default)
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(40)
        self.nav_bar.setStyleSheet("""
            QWidget { background: #1e293b; border-bottom: 1px solid #475569; }
            QPushButton { background: transparent; border: 1px solid #475569; color: #cbd5e0; 
                         font-size: 16px; padding: 4px 8px; min-width: 32px; }
            QPushButton:hover { background: #334155; border-color: #00e5ff; color: #00e5ff; }
            QPushButton:disabled { color: #475569; }
            QLineEdit { background: #0f172a; border: 1px solid #475569; color: #f1f5f9; 
                       padding: 6px 12px; font-size: 14px; }
            QLineEdit:focus { border-color: #00e5ff; }
        """)
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(8, 4, 8, 4)
        nav_layout.setSpacing(4)
        
        # Navigation buttons
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Tillbaka")
        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn = QPushButton("→")
        self.forward_btn.setToolTip("Framåt")
        self.forward_btn.clicked.connect(self.go_forward)
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setToolTip("Ladda om")
        self.reload_btn.clicked.connect(self.reload_page)
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("Hem")
        self.home_btn.clicked.connect(self.go_home)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Webbadress...")
        self.url_bar.returnPressed.connect(self.navigate_from_url_bar)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.url_bar)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Connect URL changed signal
        self.web_view.urlChanged.connect(self.on_url_changed)
        
        # Add widgets to layout (nav bar hidden initially)
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.web_view)
        self.nav_bar.hide()
        
        # Configure web engine
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        
        # Connect API signals
        self.api.navigateRequested.connect(self.navigate_to_url)
        
        # Set up WebChannel if available
        if QWebChannel is not None:
            try:
                self.channel = QWebChannel()
                self.channel.registerObject("api", self.api)
                self.web_view.page().setWebChannel(self.channel)
                logger.info("WebChannel initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize WebChannel: {e}")
        else:
            logger.warning("QWebChannel not available - JavaScript↔Python bridge may not work")
        
        # Track navigation state
        self.is_on_search_page = True
        
        # Load HTML UI
        self._load_html()
        
        logger.info("Klar Browser initialized")
    
    def navigate_to_url(self, url: str):
        """Navigate to a URL"""
        if not url:
            return
        
        # Add protocol if missing
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        logger.info(f"Navigating to: {url}")
        
        # Show navigation bar
        self.nav_bar.show()
        self.is_on_search_page = False
        
        # Load URL
        self.web_view.load(QUrl(url))
    
    def navigate_from_url_bar(self):
        """Navigate to URL from address bar"""
        url = self.url_bar.text().strip()
        self.navigate_to_url(url)
    
    def go_back(self):
        """Go back in history"""
        if self.web_view.history().canGoBack():
            self.web_view.back()
    
    def go_forward(self):
        """Go forward in history"""
        if self.web_view.history().canGoForward():
            self.web_view.forward()
    
    def reload_page(self):
        """Reload current page"""
        self.web_view.reload()
    
    def go_home(self):
        """Return to search page"""
        self.nav_bar.hide()
        self.is_on_search_page = True
        self._load_html()
    
    def on_url_changed(self, url: QUrl):
        """Update URL bar when page changes"""
        url_string = url.toString()
        
        # Check if we're back on the search page (local file or about:blank)
        if url_string.startswith('file:') or url_string.startswith('about:') or url_string == '':
            # Back on search page - hide nav bar
            self.nav_bar.hide()
            self.is_on_search_page = True
        else:
            # On external website - show nav bar and update
            self.nav_bar.show()
            self.is_on_search_page = False
            self.url_bar.setText(url_string)
            
            # Update button states
            self.back_btn.setEnabled(self.web_view.history().canGoBack())
            self.forward_btn.setEnabled(self.web_view.history().canGoForward())

    def _load_html(self):
        """Load HTML UI from file"""
        # Try to find HTML file in same directory
        html_paths = [
            Path(__file__).parent / "klar_ui.html",
            Path(__file__).parent / "klar_browser.html",
            Path.cwd() / "klar_ui.html",
            Path.cwd() / "klar_browser.html",
        ]
        
        html_file = None
        for path in html_paths:
            if path.exists():
                html_file = path
                break
        
        if html_file:
            logger.info(f"Loading HTML: {html_file}")
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject WebChannel script if not already present
            if 'qrc:///qtwebchannel/qwebchannel.js' not in html_content:
                inject_point = """
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script>
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.KlarAPI = channel.objects.api;
                });
            </script>
            """
                
                # Insert before closing body tag
                if '</body>' in html_content:
                    html_content = html_content.replace(
                        '</body>',
                        inject_point + '\n</body>'
                    )
                else:
                    html_content += inject_point
            
            self.web_view.setHtml(
                html_content,
                QUrl.fromLocalFile(str(html_file.parent) + '/')
            )
        else:
            logger.error("HTML file not found!")
            self.web_view.setHtml(self._get_error_page())

    def _get_error_page(self) -> str:
        """Error page if HTML not found"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Error</title>
            <style>
                body { 
                    background: #0f172a; 
                    color: #f1f5f9; 
                    font-family: sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .container { text-align: center; }
                h1 { color: #00e5ff; margin-bottom: 20px; }
                p { font-size: 16px; line-height: 1.6; max-width: 500px; }
                code { background: #1e293b; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠ HTML File Not Found</h1>
                <p>Place <code>klar_ui.html</code> or <code>klar_browser.html</code> in the same directory as this script.</p>
                <p>Current directory: <code>""" + str(Path.cwd()) + """</code></p>
            </div>
        </body>
        </html>
        """


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    browser = KlarBrowser()
    browser.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
