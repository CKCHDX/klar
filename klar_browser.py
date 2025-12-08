"""
Klar 3.0 - Standalone Swedish Browser
Complete browser application with integrated search engine
Features: Domain whitelisting, demographic-aware search, multi-user safety
"""
import sys
import os
import webbrowser 
from pathlib import Path
from urllib.parse import urlparse, unquote

from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTabWidget,
    QStatusBar, QProgressBar, QLabel, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QFont

# Import search engine and security modules
from engine.search_engine import SearchEngine
from engine.results_page import ResultsPage
from engine.domain_whitelist import DomainWhitelist
from engine.demographic_detector import DemographicDetector

from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

class SearchWorker(QThread):
    """Background thread for searching with demographic support"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, search_engine, query, demographic="general", metadata=None):
        super().__init__()
        self.search_engine = search_engine
        self.query = query
        self.demographic = demographic
        self.metadata = metadata or {}
    
    def run(self):
        try:
            # Pass demographic context to search engine
            results = self.search_engine.search(
                self.query,
                demographic=self.demographic
            )
            results['detected_demographic'] = self.demographic
            results['confidence'] = self.metadata.get('all_scores', {})
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class KlarBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # ============================================
        # VIDEO CODEC SUPPORT - PyQt6 CORRECT WAY
        # ============================================
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()
        
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        
        print("[Klar] Video codec support enabled")
        # ============================================
        
        self.setWindowTitle("Klar 3.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize search engine
        self.search_engine = SearchEngine()
        self.search_worker = None
        
        # NEW: Initialize security and demographic modules
        self.whitelist = DomainWhitelist("domains.json")
        self.demographic_detector = DemographicDetector()
        
        # Track state
        self.is_searching = False
        self.pending_bypass_url = None  # Track URL waiting for bypass confirmation
        
        # Setup UI
        self.setup_ui()
        self.apply_styles()
        
        # Show home
        self.show_home_page()
    
    def setup_ui(self):
        """Setup browser UI with centered search"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Top navigation bar (compact)
        nav_bar = self.create_top_nav()
        main_layout.addWidget(nav_bar)
        
        # Stacked widget for home/browser view
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Home page (centered search)
        self.home_widget = self.create_home_widget()
        self.stacked_widget.addWidget(self.home_widget)
        
        # Browser view (tabs)
        self.browser_widget = QWidget()
        browser_layout = QVBoxLayout()
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)
        self.browser_widget.setLayout(browser_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        browser_layout.addWidget(self.tabs)
        
        self.stacked_widget.addWidget(self.browser_widget)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Add first tab
        self.add_new_tab(None, "Ny flik")
        self.open_videos_externally = True
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.main_search_bar.setFocus())
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_home_page)
    
    def create_top_nav(self):
        """Create compact top navigation"""
        nav_widget = QWidget()
        nav_widget.setObjectName("topNav")
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(12, 8, 12, 8)
        nav_layout.setSpacing(8)
        nav_widget.setLayout(nav_layout)
        
        # Back button
        back_btn = QPushButton("◄")
        back_btn.setObjectName("navButton")
        back_btn.setFixedSize(36, 36)
        back_btn.clicked.connect(self.navigate_back)
        back_btn.setToolTip("Bakåt (Alt+←)")
        nav_layout.addWidget(back_btn)
        
        # Forward button
        forward_btn = QPushButton("►")
        forward_btn.setObjectName("navButton")
        forward_btn.setFixedSize(36, 36)
        forward_btn.clicked.connect(self.navigate_forward)
        forward_btn.setToolTip("Framåt (Alt+→)")
        nav_layout.addWidget(forward_btn)
        
        # Reload button
        reload_btn = QPushButton("↻")
        reload_btn.setObjectName("navButton")
        reload_btn.setFixedSize(36, 36)
        reload_btn.clicked.connect(self.reload_page)
        reload_btn.setToolTip("Uppdatera (F5)")
        nav_layout.addWidget(reload_btn)
        
        # Home button
        home_btn = QPushButton("⌂")
        home_btn.setObjectName("navButton")
        home_btn.setFixedSize(36, 36)
        home_btn.clicked.connect(self.show_home_page)
        home_btn.setToolTip("Hem (Ctrl+H)")
        nav_layout.addWidget(home_btn)
        
        # Main search/URL bar
        self.main_search_bar = QLineEdit()
        self.main_search_bar.setObjectName("mainSearchBar")
        self.main_search_bar.setPlaceholderText("Sök eller ange webbadress...")
        self.main_search_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.main_search_bar)
        
        # Search button
        search_btn = QPushButton("Sök")
        search_btn.setObjectName("primaryButton")
        search_btn.setFixedWidth(80)
        search_btn.clicked.connect(self.navigate_to_url)
        nav_layout.addWidget(search_btn)
        
        return nav_widget
    
    def create_home_widget(self):
        """Create home page with centered search"""
        home = QWidget()
        home.setObjectName("homePage")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home.setLayout(layout)
        
        # Logo
        logo = QLabel("Klar")
        logo.setObjectName("homePageLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # Version
        version = QLabel("3.0")
        version.setObjectName("homePageVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Spacer
        layout.addSpacing(40)
        
        # Search bar container
        search_container = QWidget()
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_container.setLayout(search_layout)
        
        # Add spacers for centering
        search_layout.addStretch()
        
        # Search bar
        self.home_search_bar = QLineEdit()
        self.home_search_bar.setObjectName("homeSearchBar")
        self.home_search_bar.setPlaceholderText("Sök eller ange webbadress...")
        self.home_search_bar.setMinimumWidth(600)
        self.home_search_bar.setMaximumWidth(800)
        self.home_search_bar.returnPressed.connect(self.home_search)
        search_layout.addWidget(self.home_search_bar)
        
        # Search button
        home_search_btn = QPushButton("Sök")
        home_search_btn.setObjectName("primaryButton")
        home_search_btn.clicked.connect(self.home_search)
        search_layout.addWidget(home_search_btn)
        
        search_layout.addStretch()
        
        layout.addWidget(search_container)
        
        # Spacer
        layout.addSpacing(60)
        
        # Features
        features_widget = QWidget()
        features_layout = QHBoxLayout()
        features_layout.setSpacing(20)
        features_widget.setLayout(features_layout)
        
        features_layout.addStretch()
        
        features = [
            ("🇸🇪", "111 Svenska domäner"),
            ("⚡", "Snabb och effektiv sökning"),
            ("🔒", "Integritet i fokus"),
            ("🌐", "Utforska webben smidigt"),
            ("🖼️", "Inbyggd bildvisare"),
            ("🎥", "Spela upp videor direkt")
        ]
        
        for icon, text in features:
            feature = self.create_feature_card(icon, text)
            features_layout.addWidget(feature)
        
        features_layout.addStretch()
        
        layout.addWidget(features_widget)
        
        
        return home
    
    def create_feature_card(self, icon, text):
        """Create feature card"""
        card = QWidget()
        card.setObjectName("featureCard")
        card.setFixedSize(180, 120)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setLayout(layout)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("featureIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        text_label = QLabel(text)
        text_label.setObjectName("featureText")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        return card
    
    def home_search(self):
        """Search from home page"""
        query = self.home_search_bar.text().strip()
        if query:
            self.main_search_bar.setText(query)
            self.navigate_to_url()
    
    def add_new_tab(self, qurl=None, label="Ny flik"):
        """Add new tab"""
        browser = QWebEngineView()
        browser.urlChanged.connect(lambda url: self.on_url_changed(url, browser))
        if qurl:
            browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser: 
                                   self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()[:25]))
        browser.loadProgress.connect(self.update_status)
        
        # Switch to browser view
        self.stacked_widget.setCurrentIndex(1)
        
        return browser
    
    def on_url_changed(self, qurl: QUrl, browser):
        """Handle URL changes - check for bypass protocol and video URLs"""
        url_string = qurl.toString()
        
        # Handle bypass protocol
        if url_string.startswith('klar-bypass://'):
            self.handle_bypass_redirect(url_string, browser)
            return
        
        # Check for videos
        self.check_video_url(qurl)
    
    def handle_bypass_redirect(self, protocol_url: str, browser):
        """Handle klar-bypass:// protocol redirect"""
        try:
            # Parse: klar-bypass://TOKEN/URL
            parts = protocol_url.replace('klar-bypass://', '').split('/', 1)
            if len(parts) != 2:
                self.status.showMessage("Bypass avbruten: Ogiltig format", 5000)
                return
            
            token, encoded_url = parts
            bypass_url = unquote(encoded_url)
            
            # Verify token
            if not self.whitelist.verify_bypass_acknowledgment(token):
                self.status.showMessage("Bypass avbruten: Ogiltig token", 5000)
                print(f"[Security] Bypass rejected: Invalid token")
                return
            
            # Token valid - proceed with URL
            print(f"[Security] Bypass approved for: {bypass_url}")
            self.status.showMessage(f"✓ Säkerhetskontroll åsidosatt. Laddar...", 3000)
            
            # Load the bypassed URL
            if not bypass_url.startswith('http'):
                bypass_url = 'https://' + bypass_url
            
            browser.setUrl(QUrl(bypass_url))
        
        except Exception as e:
            print(f"[Security] Bypass error: {str(e)}")
            self.status.showMessage(f"Bypass fel: {str(e)}", 5000)
    
    def check_video_url(self, qurl: QUrl):
        """Check if URL is a video and open externally"""
        url_string = qurl.toString()
    
        video_indicators = [
            'youtube.com/watch',
            'youtu.be/',
            'vimeo.com/',
            'dailymotion.com/',
            '.mp4',
            '.webm',
            '.m3u8'
        ]
    
        if any(indicator in url_string.lower() for indicator in video_indicators):
            print(f"[Video] Opening externally: {url_string}")
            webbrowser.open(url_string)
            # Navigate back to prevent loading in Klar
            self.current_browser().back()

    def close_tab(self, i):
        """Close tab"""
        if self.tabs.count() < 2:
            self.show_home_page()
            return
        
        self.tabs.removeTab(i)
    
    def navigate_to_url(self):
        """Navigate to URL or perform search with security validation"""
        query = self.main_search_bar.text().strip()
        
        if not query:
            return
        
        # Check if it's a URL
        if self.is_url(query):
            # NEW: Check whitelist first for security
            is_safe, reason = self.whitelist.is_whitelisted(query)
            
            if not is_safe:
                # Show security warning page
                blocked_html = self.whitelist.get_blocked_html(query, reason)
                self.current_browser().setHtml(blocked_html, QUrl("about:blank"))
                self.stacked_widget.setCurrentIndex(1)
                self.status.showMessage(f"⚠️ Domän blockerad för säkerhet", 5000)
                print(f"[Security] Blocked: {query} - {reason}")
            else:
                # Domain is whitelisted, load it
                url = query if query.startswith('http') else 'https://' + query
                self.current_browser().setUrl(QUrl(url))
                self.stacked_widget.setCurrentIndex(1)
                print(f"[Security] Allowed: {query}")
        else:
            # It's a search query
            self.perform_search(query)
    
    def is_url(self, text):
        """Check if text is a URL"""
        # More lenient URL detection
        if text.startswith('http://') or text.startswith('https://'):
            return True
        if '.' in text and ' ' not in text and len(text.split('.')) >= 2:
            return True
        return False
    
    def perform_search(self, query):
        """Perform search using background thread with demographic awareness"""
        if self.is_searching:
            self.status.showMessage("Sökning pågår redan...", 2000)
            return
        
        self.is_searching = True
        
        # NEW: Detect user demographic
        demographic, confidence, metadata = self.demographic_detector.detect(query)
        print(f"[Demographic] Detected: {demographic} (confidence: {confidence:.2f})")
        
        self.status.showMessage(f"Söker efter: {query}...")
        
        # Show loading in browser
        self.show_loading_page(query)
        self.stacked_widget.setCurrentIndex(1)
        
        # Start background search with demographic context
        self.search_worker = SearchWorker(
            self.search_engine, 
            query,
            demographic=demographic,
            metadata=metadata
        )
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.start()
    
    def show_loading_page(self, query):
        """Show loading page while searching"""
        loading_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: #0a0e1a;
                    color: #e8eaf0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .loader {{
                    text-align: center;
                }}
                .spinner {{
                    border: 4px solid rgba(59, 130, 246, 0.1);
                    border-top: 4px solid #3b82f6;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                .text {{
                    font-size: 18px;
                    color: #a0a8c0;
                }}
                .query {{
                    color: #3b82f6;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="loader">
                <div class="spinner"></div>
                <div class="text">Söker efter <span class="query">{query}</span>...</div>
            </div>
        </body>
        </html>
        """
        self.current_browser().setHtml(loading_html, QUrl("about:blank"))
    
    def on_search_finished(self, results):
        """Handle search completion"""
        self.is_searching = False
        query = results.get('query', '')
        demographic = results.get('detected_demographic', 'general')
        
        # Display results
        results_html = ResultsPage.generate_html(query, results, demographic)
        self.current_browser().setHtml(results_html, QUrl("about:blank"))
        
        count = len(results.get('results', []))
        self.status.showMessage(f"Hittade {count} resultat för: {query}", 3000)
    
    def on_search_error(self, error):
        """Handle search error"""
        self.is_searching = False
        self.status.showMessage(f"Sökfel: {error}", 5000)
    
    def show_home_page(self):
        """Show home page"""
        self.stacked_widget.setCurrentIndex(0)
        self.home_search_bar.clear()
        self.main_search_bar.clear()
        self.home_search_bar.setFocus()
    
    def current_browser(self):
        """Get current browser tab"""
        return self.tabs.currentWidget()
    
    def navigate_back(self):
        if self.current_browser():
            self.current_browser().back()
    
    def navigate_forward(self):
        if self.current_browser():
            self.current_browser().forward()
    
    def reload_page(self):
        if self.current_browser():
            self.current_browser().reload()
    
    def update_url_bar(self, qurl, browser=None):
        """Update URL bar"""
        if browser != self.current_browser():
            return
        
        url_string = qurl.toString()
        
        # Don't show data: URLs or bypass URLs
        if not url_string.startswith('data:') and not url_string.startswith('klar-bypass://'):
            self.main_search_bar.setText(url_string)
    
    def update_status(self, progress):
        """Update status during page load"""
        if progress < 100:
            self.status.showMessage(f"Laddar... {progress}%")
        else:
            self.status.clearMessage()
    
    def apply_styles(self):
        """Apply modern Swedish design"""
        self.setStyleSheet("""
            /* Main window */
            QMainWindow {
                background: #0a0e1a;
            }
            
            /* Top navigation */
            #topNav {
                background: #131824;
                border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            }
            
            #logo {
                font-size: 24px;
                font-weight: 700;
                color: #3b82f6;
                padding-right: 20px;
            }
            
            /* Navigation buttons */
            #navButton {
                background: #1e2538;
                color: #a0a8c0;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            
            #navButton:hover {
                background: #252d44;
                color: #e8eaf0;
                border-color: #3b82f6;
            }
            
            #navButton:pressed {
                background: #1a2032;
            }
            
            /* Search bars */
            #mainSearchBar, #homeSearchBar {
                padding: 10px 16px;
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                font-size: 15px;
                background: #1e2538;
                color: #e8eaf0;
                selection-background-color: #3b82f6;
            }
            
            #mainSearchBar:focus, #homeSearchBar:focus {
                border-color: #3b82f6;
                background: #252d44;
            }
            
            #homeSearchBar {
                padding: 14px 20px;
                font-size: 16px;
                border-radius: 16px;
            }
            
            /* Primary button */
            #primaryButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            
            #primaryButton:hover {
                background: #60a5fa;
            }
            
            #primaryButton:pressed {
                background: #2563eb;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: none;
                background: #0a0e1a;
            }
            
            QTabBar::tab {
                background: #131824;
                color: #a0a8c0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QTabBar::tab:selected {
                background: #1e2538;
                color: #e8eaf0;
            }
            
            QTabBar::tab:hover:!selected {
                background: #1a2032;
            }
            
            /* Status bar */
            QStatusBar {
                background: #131824;
                color: #a0a8c0;
                border-top: 1px solid rgba(59, 130, 246, 0.2);
            }
            
            /* Home page */
            #homePage {
                background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
            }
            
            #homePageLogo {
                font-size: 96px;
                font-weight: 700;
                color: #3b82f6;
            }
            
            #homePageVersion {
                font-size: 32px;
                color: #6b7390;
                margin-bottom: 20px;
            }
            
            #homePageTagline {
                font-size: 18px;
                color: #a0a8c0;
            }
            
            #homePageStats {
                font-size: 14px;
                color: #6b7390;
            }
            
            /* Feature cards */
            #featureCard {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 16px;
            }
            
            #featureIcon {
                font-size: 42px;
            }
            
            #featureText {
                font-size: 14px;
                color: #a0a8c0;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Klar 3.0")
    
    # Set font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show browser
    browser = KlarBrowser()
    browser.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
