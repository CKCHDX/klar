#!/usr/bin/env python3
"""
Klar Browser Backend
Minimal Python backend that loads the HTML UI and handles API requests
Run: python klar_backend.py
Build: build.bat (Windows) or build.sh (Linux/macOS)
"""

import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl, QObject, pyqtSlot

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


class SearchAPI(QObject):
    """Backend API exposed to JavaScript"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        super().__init__()
        self.server_url = server_url
        self.config_file = Path.home() / '.kse' / 'klar_config.json'
        self._load_config()

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

    @pyqtSlot(str, result=str)
    def search(self, query: str) -> str:
        """Execute search and return JSON results"""
        try:
            if not query.strip():
                return json.dumps({"results": [], "error": "Empty query"})

            url = f"{self.server_url}/api/search"
            params = {'q': query}
            
            logger.info(f"Searching: {query}")
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
            
            return json.dumps({
                "results": normalized,
                "count": len(normalized),
                "query": query
            })
            
        except requests.exceptions.ConnectionError:
            error = f"Cannot connect to {self.server_url}"
            logger.error(error)
            return json.dumps({"results": [], "error": error})
        except requests.exceptions.Timeout:
            error = "Search timeout"
            logger.error(error)
            return json.dumps({"results": [], "error": error})
        except Exception as e:
            error = str(e)
            logger.error(f"Search error: {error}")
            return json.dumps({"results": [], "error": error})

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


class KlarBrowser(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Klar - Nordic Search Browser")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Initialize backend API
        self.api = SearchAPI()
        
        # Create web view
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        
        # Configure web engine
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        
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
        
        # Load HTML UI
        self._load_html()
        
        logger.info("Klar Browser initialized")

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
