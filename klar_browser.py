""" Klar 3.0 - Standalone Swedish Browser
Complete browser application with integrated search engine
"""

import sys
import os
import webbrowser
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget, QStatusBar, QProgressBar,
    QLabel, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QFont

# Import search engine
from engine.search_engine import SearchEngine
from engine.results_page import ResultsPage


class SearchWorker(QThread):
    """Background thread for searching"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, search_engine, query):
        super().__init__()
        self.search_engine = search_engine
        self.query = query

    def run(self):
        try:
            results = self.search_engine.search(self.query)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class KlarBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Klar 3.0")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize search engine
        self.search_engine = SearchEngine()
        self.search_worker = None

        # Track state
        self.is_searching = False

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
        browser.urlChanged.connect(lambda url: self.check_video_url(url))

        if qurl:
            browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()[:25]))
        browser.loadProgress.connect(self.update_status)

        # Switch to browser view
        self.stacked_widget.setCurrentIndex(1)

        return browser

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
        """Navigate to URL or perform search"""
        query = self.main_search_bar.text().strip()
        if not query:
            return

        # Check if it's a URL
        if self.is_url(query):
            url = query if query.startswith('http') else 'https://' + query
            self.current_browser().setUrl(QUrl(url))
            self.stacked_widget.setCurrentIndex(1)
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
        """Perform search using background thread"""
        if self.is_searching:
            self.status.showMessage("Sökning pågår redan...", 2000)
            return

        self.is_searching = True
        self.status.showMessage(f"Söker efter: {query}...")

        # Show loading in browser
        self.show_loading_page(query)
        self.stacked_widget.setCurrentIndex(1)

        # Start background search
        self.search_worker = SearchWorker(self.search_engine, query)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.start()

    def show_loading_page(self, query):
        """Show loading page while searching"""
        loading_html = f"""
        <html>
            <body style="font-family: Arial; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f5f5f5;">
                <div style="text-align: center;">
                    <h2>Söker...</h2>
                    <p>Söker efter: <b>{query}</b></p>
                    <div style="font-size: 24px;">⏳</div>
                </div>
            </body>
        </html>
        """
        self.current_browser().setHtml(loading_html)

    def on_search_finished(self, results):
        """Handle search completion"""
        self.is_searching = False

        # Generate results HTML
        results_page = ResultsPage(results)
        html = results_page.generate()

        # Display results
        self.current_browser().setHtml(html)
        self.status.showMessage(f"Sökning slutförd. Hittade {len(results.get('results', []))} resultat", 3000)

    def on_search_error(self, error_msg):
        """Handle search error"""
        self.is_searching = False
        error_html = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2>Sökning misslyckades</h2>
                <p style="color: red;">{error_msg}</p>
            </body>
        </html>
        """
        self.current_browser().setHtml(error_html)
        self.status.showMessage(f"Fel: {error_msg}", 3000)

    def current_browser(self):
        """Get current browser tab"""
        return self.tabs.currentWidget()

    def update_url_bar(self, qurl: QUrl, browser):
        """Update URL bar when page loads"""
        if browser == self.current_browser():
            self.main_search_bar.setText(qurl.toString())

    def update_status(self, progress):
        """Update loading progress"""
        if progress < 100:
            self.status.showMessage(f"Läser in... {progress}%")
        else:
            self.status.showMessage("Klar")

    def navigate_back(self):
        """Navigate back"""
        self.current_browser().back()

    def navigate_forward(self):
        """Navigate forward"""
        self.current_browser().forward()

    def reload_page(self):
        """Reload page"""
        self.current_browser().reload()

    def show_home_page(self):
        """Show home page"""
        self.stacked_widget.setCurrentIndex(0)
        self.main_search_bar.setText("")
        self.home_search_bar.setText("")

    def apply_styles(self):
        """Apply CSS styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }

            #topNav {
                background-color: #f8f8f8;
                border-bottom: 1px solid #e0e0e0;
            }

            #mainSearchBar {
                padding: 8px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-size: 14px;
            }

            #mainSearchBar:focus {
                border: 1px solid #2196F3;
                outline: none;
            }

            #primaryButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                cursor: pointer;
            }

            #primaryButton:hover {
                background-color: #1976D2;
            }

            #navButton {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            }

            #navButton:hover {
                background-color: #f0f0f0;
            }

            #homePage {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            #homePageLogo {
                font-size: 72px;
                font-weight: bold;
                color: white;
            }

            #homePageVersion {
                font-size: 24px;
                color: rgba(255, 255, 255, 0.8);
            }

            #homeSearchBar {
                padding: 12px 16px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            #homeSearchBar:focus {
                outline: none;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            #featureCard {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            #featureIcon {
                font-size: 32px;
            }

            #featureText {
                font-size: 12px;
                color: #333;
                font-weight: 500;
            }

            QTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 6px 12px;
            }

            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #2196F3;
            }

            QStatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #e0e0e0;
                color: #333;
            }
        """)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Try to load icon
    try:
        if os.path.exists("icon.ico"):
            app.setApplicationIcon(QIcon("icon.ico"))
    except Exception as e:
        print(f"[Warning] Could not load icon: {e}")

    browser = KlarBrowser()
    browser.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
