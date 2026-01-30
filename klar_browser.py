#!/usr/bin/env python3
"""
Klar Browser - Modern Web-Based Browser for KSE Search Engine
A lightweight browser client with integrated search functionality and modern UI
"""

import sys
import logging
import requests
import json
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KlarBridge(QObject):
    """Bridge object for communication between JavaScript and Python"""
    
    search_completed = pyqtSignal(str)  # JSON string of results
    search_error = pyqtSignal(str)
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        super().__init__()
        self.server_url = server_url
        self.config_file = Path.home() / '.kse' / 'klar_browser_config.json'
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.server_url = config.get('server_url', self.server_url)
                    logger.info(f"Loaded config: {self.server_url}")
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
    
    @pyqtSlot(str)
    def performSearch(self, query: str):
        """Execute search and return results to JavaScript"""
        try:
            url = f"{self.server_url}/api/search"
            params = {'q': query}
            
            logger.info(f"Searching for: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            # Emit results as JSON string
            self.search_completed.emit(json.dumps(data))
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            self.search_error.emit("Unable to connect to KSE server. Please ensure the server is running.")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            self.search_error.emit("Search request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            self.search_error.emit(f"Search error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            self.search_error.emit("Invalid response from server.")
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}", exc_info=True)
            self.search_error.emit(f"Unexpected error: {str(e)}")
    
    @pyqtSlot(result=str)
    def getServerUrl(self):
        """Get current server URL"""
        return self.server_url
    
    @pyqtSlot(str)
    def setServerUrl(self, url: str):
        """Set server URL and save to config"""
        url = url.strip()
        
        # Validate URL format
        if not url:
            logger.warning("Empty URL provided")
            return
        
        # Check for protocol
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.warning(f"Invalid URL format (missing protocol): {url}")
            return
        
        # Validate URL structure
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                logger.warning(f"Invalid URL format (no hostname): {url}")
                return
        except Exception as e:
            logger.warning(f"Invalid URL format: {e}")
            return
        
        self.server_url = url
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {'server_url': self.server_url}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Server URL saved: {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to save server URL: {e}")
    
    @pyqtSlot(result=str)
    def checkServerHealth(self):
        """Check server health status"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=3)
            if response.status_code == 200:
                return json.dumps({"status": "connected", "url": self.server_url})
            else:
                return json.dumps({"status": "error", "url": self.server_url})
        except requests.exceptions.RequestException as e:
            logger.warning(f"Health check failed: {e}")
            return json.dumps({"status": "disconnected", "url": self.server_url})
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return json.dumps({"status": "error", "url": self.server_url})


class KlarBrowser(QMainWindow):
    """Main Klar Browser window with modern web-based UI"""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.setWindowTitle("Klar - Search Engine")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create bridge for JavaScript communication
        self.bridge = KlarBridge()
        
        # Setup web view
        self.web_view = QWebEngineView()
        
        # Create web channel for JS-Python communication
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Load the HTML UI
        self._load_html_ui()
        
        # Set web view as central widget
        self.setCentralWidget(self.web_view)
        
        # Connect signals
        self.bridge.search_completed.connect(self._on_search_completed)
        self.bridge.search_error.connect(self._on_search_error)
        
        logger.info("Klar Browser initialized with web-based UI")
    
    def _load_html_ui(self):
        """Load the HTML UI from file"""
        html_path = Path(__file__).parent / "klar_browser.html"
        
        if not html_path.exists():
            # If HTML file doesn't exist, show error
            error_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1 style="color: #f44336;">Error: UI File Not Found</h1>
                <p>The klar_browser.html file could not be found.</p>
                <p>Expected location: {}</p>
            </body>
            </html>
            """.format(html_path)
            self.web_view.setHtml(error_html)
            logger.error(f"HTML UI file not found: {html_path}")
            return
        
        # Read and inject webchannel script into HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject qwebchannel.js and bridge initialization before </body>
        injection_script = """
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var bridge = null;
        
        // Helper function to show notifications instead of alert
        function showNotification(message, type = 'error') {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                background: ${type === 'error' ? 'var(--accent-warm)' : 'var(--accent)'};
                color: var(--primary);
                border-radius: 4px;
                font-weight: 600;
                z-index: 10000;
                animation: slideInRight 0.3s ease-out;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(notification);
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
        }
        
        // Add notification animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        // Initialize QWebChannel
        new QWebChannel(qt.webChannelTransport, function(channel) {
            bridge = channel.objects.bridge;
            
            // Verify bridge is connected
            if (!bridge) {
                console.error('Bridge object not found');
                return;
            }
            
            // Connect search result handler
            bridge.search_completed.connect(function(jsonResults) {
                try {
                    const data = JSON.parse(jsonResults);
                    handleSearchResults(data);
                } catch(e) {
                    console.error('Error parsing search results:', e);
                    showNotification('Failed to parse search results', 'error');
                }
            });
            
            // Connect error handler
            bridge.search_error.connect(function(errorMessage) {
                handleSearchError(errorMessage);
            });
            
            console.log('Bridge connected successfully');
        });
        
        // Override handleSearch to use bridge (with validation)
        if (typeof handleSearch === 'function') {
            const originalHandleSearch = handleSearch;
            handleSearch = function() {
                const query = searchInput ? searchInput.value.trim() : '';
                if (!query) {
                    showNotification('Please enter a search query', 'error');
                    return;
                }
                
                if (!bridge) {
                    showNotification('Connection not ready. Please wait...', 'error');
                    return;
                }
                
                // Show loading indicators
                const indicators = document.querySelectorAll('.indicator');
                indicators.forEach(ind => ind.classList.add('active'));
                
                // Call Python backend
                bridge.performSearch(query);
            };
        } else {
            console.error('handleSearch function not found in HTML');
        }
        
        // Handle search results from Python
        function handleSearchResults(data) {
            const results = data.results || [];
            const query = searchInput ? searchInput.value.trim() : '';
            
            // Clear loading indicators
            const indicators = document.querySelectorAll('.indicator');
            indicators.forEach(ind => ind.classList.remove('active'));
            
            // Verify displayResults function exists
            if (typeof displayResults !== 'function') {
                console.error('displayResults function not found in HTML');
                showNotification('UI function missing. Please reload.', 'error');
                return;
            }
            
            // Convert to format expected by displayResults
            const formattedResults = results.map(result => ({
                domain: extractDomain(result.url),
                title: result.title || 'No Title',
                description: result.snippet || result.text || 'No description available',
                url: result.url,
                badge: result.score ? 'Score: ' + result.score.toFixed(2) : null
            }));
            
            displayResults(formattedResults, query);
        }
        
        // Handle search errors from Python
        function handleSearchError(errorMessage) {
            // Clear loading indicators
            const indicators = document.querySelectorAll('.indicator');
            indicators.forEach(ind => ind.classList.remove('active'));
            
            showNotification(errorMessage, 'error');
        }
        
        // Extract domain from URL
        function extractDomain(url) {
            try {
                const urlObj = new URL(url);
                return urlObj.hostname;
            } catch(e) {
                return url;
            }
        }
        
        // Override settings to use bridge (with validation)
        if (typeof showSettings === 'function') {
            const originalShowSettings = showSettings;
            showSettings = function() {
                if (!bridge) {
                    showNotification('Connection not ready', 'error');
                    return;
                }
                
                const currentUrl = bridge.getServerUrl();
                const newUrl = prompt('Enter KSE Server URL:\\n(e.g., http://localhost:5000)', currentUrl);
                if (newUrl && newUrl.trim()) {
                    bridge.setServerUrl(newUrl.trim());
                    showNotification('Server URL updated: ' + newUrl.trim(), 'info');
                }
            };
        } else {
            console.error('showSettings function not found in HTML');
        }
    </script>
</body>
        """
        
        # Replace </body> with injection + </body>
        html_content = html_content.replace('</body>', injection_script)
        
        # Load the modified HTML
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(str(html_path)))
        logger.info("HTML UI loaded successfully")
    
    def _on_search_completed(self, json_results: str):
        """Handle search completion (already sent to JavaScript)"""
        logger.info("Search completed and results sent to UI")
    
    def _on_search_error(self, error: str):
        """Handle search error (already sent to JavaScript)"""
        logger.error(f"Search error: {error}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Klar")
    app.setOrganizationName("KSE Project")
    
    # Create and show browser
    browser = KlarBrowser()
    browser.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
