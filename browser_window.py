"""
Browser Window - Main UI for the custom browser
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea, QLabel, QMessageBox
)
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QSize
from render_engine import RenderEngine
from http_client import HTTPClient


class RenderViewport(QWidget):
    """
    Custom viewport widget for rendering HTML content
    """
    
    def __init__(self):
        super().__init__()
        self.render_engine = RenderEngine()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        
    def load_html(self, html_content, url=None):
        """Load HTML content into the render engine"""
        self.render_engine.load_html(html_content, url)
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Paint event - renders the content"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Render using our custom engine
        self.render_engine.render(
            painter,
            self.width(),
            self.height()
        )
        
    def sizeHint(self):
        """Preferred size hint"""
        return QSize(800, 600)


class BrowserWindow(QMainWindow):
    """
    Main browser window with custom render engine
    """
    
    def __init__(self):
        super().__init__()
        self.http_client = HTTPClient()
        self.history = []
        self.history_index = -1
        self.current_url = ""
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Klar Browser - Custom Render Engine")
        self.setGeometry(100, 100, 1024, 768)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 5)
        
        # Back button
        self.back_button = QPushButton("←")
        self.back_button.setFixedWidth(40)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        nav_layout.addWidget(self.back_button)
        
        # Forward button
        self.forward_button = QPushButton("→")
        self.forward_button.setFixedWidth(40)
        self.forward_button.clicked.connect(self.go_forward)
        self.forward_button.setEnabled(False)
        nav_layout.addWidget(self.forward_button)
        
        # Refresh button
        self.refresh_button = QPushButton("⟳")
        self.refresh_button.setFixedWidth(40)
        self.refresh_button.clicked.connect(self.refresh)
        nav_layout.addWidget(self.refresh_button)
        
        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL (e.g., example.com or http://example.com)")
        self.address_bar.returnPressed.connect(self.navigate)
        nav_layout.addWidget(self.address_bar)
        
        # Go button
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.navigate)
        nav_layout.addWidget(self.go_button)
        
        layout.addLayout(nav_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Scroll area for viewport
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Render viewport
        self.viewport = RenderViewport()
        scroll_area.setWidget(self.viewport)
        
        layout.addWidget(scroll_area)
        
        # Load a default page
        self.load_default_page()
    
    def load_default_page(self):
        """Load a default welcome page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Klar Browser - Welcome</title>
        </head>
        <body>
            <h1>Welcome to Klar Browser</h1>
            <p>This is a custom browser with a built-from-scratch render engine.</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Custom HTML parser</li>
                <li>Custom rendering pipeline</li>
                <li>No QT WebEngine dependency</li>
                <li>Basic CSS support</li>
            </ul>
            <h2>Getting Started</h2>
            <p>Enter a URL in the address bar above to start browsing.</p>
            <p><em>Try: example.com or any other website</em></p>
            <h3>Test Sites</h3>
            <p>Good sites to test:</p>
            <ul>
                <li>example.com</li>
                <li>info.cern.ch</li>
                <li>Simple text-based websites</li>
            </ul>
        </body>
        </html>
        """
        self.viewport.load_html(html, "about:blank")
        self.address_bar.setText("about:blank")
        self.status_label.setText("Ready")
    
    def navigate(self):
        """Navigate to the URL in the address bar"""
        url = self.address_bar.text().strip()
        if not url:
            return
        
        self.load_url(url)
    
    def load_url(self, url, update_history=True):
        """
        Load content from a URL
        
        Args:
            url: URL to load
            update_history: Whether to add this URL to history (default True)
        """
        self.status_label.setText(f"Loading {url}...")
        self.status_label.repaint()
        
        # Fetch content
        response = self.http_client.fetch(url)
        
        if response['success']:
            # Load HTML into render engine
            self.viewport.load_html(response['content'], response['url'])
            
            # Update address bar with final URL (after redirects)
            self.address_bar.setText(response['url'])
            
            # Update history only if requested
            if update_history:
                self.current_url = response['url']
                if self.history_index < len(self.history) - 1:
                    # Remove forward history
                    self.history = self.history[:self.history_index + 1]
                self.history.append(response['url'])
                self.history_index = len(self.history) - 1
            else:
                self.current_url = response['url']
            
            # Update navigation buttons
            self.update_nav_buttons()
            
            self.status_label.setText(f"Loaded {response['url']} - Status: {response['status_code']}")
        else:
            self.status_label.setText(f"Error: {response['error']}")
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load {url}\n\nError: {response['error']}"
            )
    
    def go_back(self):
        """Navigate back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            self.address_bar.setText(url)
            self.load_url(url, update_history=False)
    
    def go_forward(self):
        """Navigate forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            self.address_bar.setText(url)
            self.load_url(url, update_history=False)
    
    def refresh(self):
        """Refresh current page"""
        if self.current_url:
            self.load_url(self.current_url, update_history=False)
    
    def update_nav_buttons(self):
        """Update navigation button states"""
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)
