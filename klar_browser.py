"""
Klar 3.1 - Standalone Swedish Browser
Complete browser application with integrated search engine
Features: LOKI offline search, Wikipedia direct search, Setup wizard
"""
import sys
import os
import json
import webbrowser 
def get_resource_path(relative_path):
    """Get absolute path to resource - works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller bundles files here
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
from engine.cookie_banners_db import CookieBannersDB

from pathlib import Path
from urllib.parse import urlparse, unquote
from datetime import datetime

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
from engine.loki_system import LOKISystem
from engine.custom_handlers import CustomHandlers
from engine.adblock import AdBlocker, AdBlockRules

from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

# ============================================
# SETUP WIZARD UI CLASS
# ============================================
from PyQt6.QtWidgets import QDialog, QFileDialog, QCheckBox, QTextEdit

class SetupWizard(QDialog):
    """First-run setup wizard for Klar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Klar 3.1 - Första gångs inställningar")
        self.setModal(True)
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet(self._get_styles())

        self.setup_data = {
            'first_run_completed': False,
            'loki_enabled': True,
            'data_path': str(Path.home() / "Klar-data")
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Klar 3.1")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #3b82f6;")
        layout.addWidget(header)
        
        subtitle = QLabel("Första gångs inställningar")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #a0a8c0; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # LOKI Section
        loki_label = QLabel("🔍 Offline-sökning (LOKI)")
        loki_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(loki_label)
        
        loki_desc = QTextEdit()
        loki_desc.setPlainText(
            "Med LOKI kan du söka på tidigare besökta sidor "
            "och domäner även utan internetanslutning.\n\n"
            "LOKI cachelagrar automatiskt sidor då du är online "
            "och gör dem sörbara offline. Du kan stänga av detta "
            "när som helst i inställningarna."
        )
        loki_desc.setReadOnly(True)
        loki_desc.setMaximumHeight(80)
        loki_desc.setStyleSheet("""
            QTextEdit {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
                padding: 10px;
                color: #a0a8c0;
                font-size: 12px;
            }
        """)
        layout.addWidget(loki_desc)
        
        # Enable LOKI checkbox
        self.loki_checkbox = QCheckBox("Aktivera LOKI offline-sökning")
        self.loki_checkbox.setFont(QFont("Segoe UI", 11))
        self.loki_checkbox.setChecked(True)
        self.loki_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e8eaf0;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout.addWidget(self.loki_checkbox)
        
        layout.addSpacing(15)
        
        # Storage Path Section
        storage_label = QLabel("💾 Välj lagringsplats för Klar-data")
        storage_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(storage_label)
        
        storage_desc = QLabel(
            "Klar-data innehåller sökhisrika, cachad data (om LOKI är aktiverad) "
            "och användarinställningar."
        )
        storage_desc.setStyleSheet("color: #6b7390; font-size: 11px;")
        storage_desc.setWordWrap(True)
        layout.addWidget(storage_desc)
        
        # Path selection
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.setup_data['data_path'])
        self.path_input.setReadOnly(False)
        self.path_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 6px;
                background: #1e2538;
                color: #e8eaf0;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
                background: #252d44;
            }
        """)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Bläddra...")
        browse_btn.setFixedWidth(100)
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #1e2538;
                color: #a0a8c0;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #252d44;
                color: #e8eaf0;
                border-color: #3b82f6;
            }
        """)
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Info
        info = QLabel(
            "ℹ Du kan alltid ändra detta senare i inställningarna"
        )
        info.setStyleSheet("color: #6b7390; font-size: 10px;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        skip_btn = QPushButton("Hoppa över")
        skip_btn.setFixedWidth(120)
        skip_btn.setStyleSheet("""
            QPushButton {
                background: #1e2538;
                color: #a0a8c0;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background: #252d44;
                border-color: #3b82f6;
            }
        """)
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        next_btn = QPushButton("✓ Nästa")
        next_btn.setFixedWidth(120)
        next_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
            QPushButton:pressed {
                background: #2563eb;
            }
        """)
        next_btn.clicked.connect(self._on_next)
        button_layout.addWidget(next_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _browse_folder(self):
        """Browse for folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Välj lagringsplats för Klar-data",
            str(Path.home())
        )
        if folder:
            self.path_input.setText(folder)
    
    def _on_next(self):
        """Handle next button"""
        self.setup_data['loki_enabled'] = self.loki_checkbox.isChecked()
        self.setup_data['data_path'] = self.path_input.text()
        self.setup_data['first_run_completed'] = True
        self.accept()
    
    def get_setup_data(self):
        """Get setup configuration"""
        return self.setup_data
    
    def _get_styles(self):
        """Get dialog styles"""
        return """
            QDialog {
                background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
                color: #e8eaf0;
            }
            QLabel { color: #e8eaf0; }
            QCheckBox { color: #e8eaf0; }
        """

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
            results = self.search_engine.search(
                self.query,
                demographic=self.demographic
            )
            results['detected_demographic'] = self.demographic
            results['confidence'] = self.metadata.get('all_scores', {})
            self.finished.emit(results)
        except Exception as e:
            print(f"[SearchWorker] Error: {e}")
            self.error.emit(f"Sökfel: {str(e)}")

class KlarBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # ============================================
        # FIRST RUN SETUP
        # ============================================
        self.config_path = Path.home() / "klar.json"
        self.config = self._load_or_create_config()
        # Initialize LOKI if enabled
        self.loki = None
        if self.config.get('loki', {}).get('enabled', False):
            try:
                self.loki = LOKISystem(self.data_path)
                print(f"[LOKI] Initialized at {self.data_path}")
                print(f"[LOKI] {self.loki.get_cache_stats()}")
            except Exception as e:
                print(f"[LOKI] Initialization error: {e}")
                self.loki = None
        else:
            print("[LOKI] Disabled by user") 
        self.data_path = self.config.get('loki', {}).get('storage_path', str(Path.home() / "Klar-data"))
        
        
        # ============================================
        # VIDEO CODEC SUPPORT
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
        
        self.setWindowTitle("Klar 3.1")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize search engine
        self.search_engine = SearchEngine()
        self.search_worker = None
        
        # Initialize security and demographic modules
        domainsfile = get_resource_path("domains.json")
        self.blacklist = DomainWhitelist(domainsfile)
        self.demographic_detector = DemographicDetector()

        project_dir = get_resource_path(".")  # Get project directory
        self.cookie_banners_db = CookieBannersDB()
        print("[Klar] Cookie Banners Database initialized")
        self.custom_handlers = CustomHandlers(self.data_path)
        print("[Klar] Custom Handlers initialized")
        # ============================================
        # ADBLOCK SETUP
        # ============================================
        self.adblock = AdBlocker(rules=None)  # Use defaults for now
        print(f"[Klar] AdBlock initialized: {self.adblock.get_stats()}")

        # Attach to the QWebEngineProfile
        profile = QWebEngineProfile.defaultProfile()
        profile.setUrlRequestInterceptor(KlarAdBlockInterceptor(self.adblock))
        print("[Klar] Ad blocker attached to network interceptor")

                
        # Track state
        self.is_searching = False
        self.pending_bypass_url = None
        
        # Setup UI
        self.setup_ui()
        self.apply_styles()
        
        # Show home
        self.show_home_page()
        
        # Show LOKI status if enabled
        if self.loki and self.loki.settings.get('enabled', False):
            self.status.showMessage("✓ LOKI offline-sökning aktiverad", 5000)

    def inject_cookie_handler_script(self, browser):
        """Inject JavaScript to auto-handle cookies based on domain policy"""
        try:
            domain = browser.url().host().replace('www.', '')
            action = self.cookie_manager.get_popup_action_for_domain(domain)
        
            if action['action'] == 'none':
                return  # Do nothing
        
            js_code = f"""
            (function() {{
                setTimeout(function() {{
                // Try multiple strategies to find and click decline button
                
                // Strategy 1: Look for buttons by text content
                var buttons = document.querySelectorAll('button');
                var declineBtn = null;
                var acceptBtn = null;
                
                for (var i = 0; i < buttons.length; i++) {{
                    var text = buttons[i].textContent.toLowerCase().trim();
                    
                    // Look for decline/reject buttons
                    if (text.includes('avvisa') || text.includes('decline') || text.includes('reject')) {{
                        declineBtn = buttons[i];
                    }}
                    
                    // Look for accept buttons
                    if (text.includes('acceptera') || text.includes('accept all')) {{
                        acceptBtn = buttons[i];
                    }}
                }}
                
                // Strategy 2: Common CSS selectors for cookie banners
                var bannerSelectors = [
                    '[class*="cookie"]',
                    '[id*="cookie"]',
                    '[class*="consent"]',
                    '[id*="consent"]',
                    '[class*="gdpr"]',
                    '[role="dialog"][class*="cookie"]',
                    '[role="alertdialog"]'
                ];
                
                // Click decline button if found
                if ('{action['action']}' === 'decline_all' || '{action['action']}' === 'accept_essential') {{
                    if (declineBtn) {{
                        declineBtn.click();
                        console.log('[Klar] Clicked decline button');
                    }}
                }}
                
                // Hide cookie banners as fallback
                bannerSelectors.forEach(function(selector) {{
                    try {{
                        var elements = document.querySelectorAll(selector);
                        elements.forEach(function(el) {{
                            if (el.offsetHeight > 0) {{
                                el.style.display = 'none';
                                el.style.visibility = 'hidden';
                            }}
                        }});
                    }} catch(e) {{}}
                }});
                
                console.log('[Klar] Cookie policy enforced for {domain}');
                
                }}, 800);  // Wait 800ms for popup to fully render
            }})();
            """
        
            browser.page().runJavaScript(js_code)
            print(f"[CookieHandler] Action '{action['action']}' injected for {domain}")
        except Exception as e:
            print(f"[CookieHandler] Error: {e}")


      

    def show_cookie_stats(self):
        """Show cookie management statistics"""
        stats = self.cookie_manager.get_statistics()
        message = (
            f"🍪 Cookies\n"
            f"Allowed: {stats['total_cookies_allowed']}\n"
            f"Blocked: {stats['total_cookies_blocked']}\n"
            f"Domains: {stats['whitelisted_domains_count']} whitelisted"
        )
        self.status.showMessage(message, 5000)

    def get_cookie_blocking_js(self, allow_cookies: bool = False) -> str:
        """Get JavaScript code to block cookies"""
        if allow_cookies:
            return ""
    
        js_code = """
        // Block document.cookie writes
        Object.defineProperty(document, 'cookie', {
            set: function(value) {
                console.log('[Klar] Cookie blocked by policy:', value);
            },
            get: function() {
                return '';
            }
        });
    
        // Block localStorage
        if (typeof(Storage) !== "undefined") {
            try {
                Storage.prototype.setItem = function() {
                    console.log('[Klar] localStorage blocked');
                };
            } catch(e) {}
        }
        """
        return js_code


    def setup_cookie_policies(self):
        """Configure QWebEngineProfile for cookie handling"""
        try:
            profile = QWebEngineProfile.defaultProfile()
            cookie_store = profile.cookieStore()
        
            # Connect cookie add signal to our filter
            cookie_store.cookieAdded.connect(self.on_cookie_added)
        
            print("[CookieManager] Cookie policies configured")
        except Exception as e:
            print(f"[CookieManager] Error setting up policies: {e}")

    def on_cookie_added(self, cookie):
        """Intercept cookies being added"""
        try:
            # Get cookie details
            cookie_name = cookie.name().data().decode('utf-8', errors='ignore') if hasattr(cookie.name(), 'data') else str(cookie.name())
            domain = cookie.domain()
            path = cookie.path()
        
            # Check if cookie should be allowed
            allow, reason = self.cookie_manager.should_allow_cookie(
                f"https://{domain}{path}",
                cookie_name
            )
        
            # Log the action
            self.cookie_manager.log_cookie_action(
                f"https://{domain}{path}",
                cookie_name,
                allow
            )
        
            if allow:
                print(f"[Cookie] ✓ Allowed: {cookie_name} from {domain} ({reason})")
            else:
                print(f"[Cookie] ✗ Blocked: {cookie_name} from {domain} ({reason})")
    
        except Exception as e:
            print(f"[Cookie] Error processing cookie: {e}")

    def _load_or_create_config(self):
        """Load config or show setup wizard on first run"""
        if not self.config_path.exists():
            # First run - show setup wizard
            print("[Setup] First run detected, showing wizard...")
            wizard = SetupWizard()
            
            if wizard.exec():
                # User completed setup
                setup_data = wizard.get_setup_data()
                config = {
                    "version": "3.1",
                    "first_run_completed": True,
                    "loki": {
                        "enabled": setup_data['loki_enabled'],
                        "storage_path": setup_data['data_path']
                    },
                    "created_date": datetime.now().isoformat()
                }
                
                # Save config
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"[Setup] Config saved: LOKI={config['loki']['enabled']}")
                return config
            else:
                # User skipped setup - use defaults
                config = {
                    "version": "3.1",
                    "first_run_completed": True,
                    "loki": {"enabled": False, "storage_path": str(Path.home() / "Klar-data")},
                    "created_date": datetime.now().isoformat()
                }
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print("[Setup] Setup skipped, using defaults")
                return config
        else:
            # Load existing config
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Setup] Error loading config: {e}")
                return {"loki": {"enabled": False}}
    
    def setup_ui(self):
        """Setup browser UI with centered search"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        nav_bar = self.create_top_nav()
        main_layout.addWidget(nav_bar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.home_widget = self.create_home_widget()
        self.stacked_widget.addWidget(self.home_widget)
        
        self.browser_widget = QWidget()
        browser_layout = QVBoxLayout()
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)
        self.browser_widget.setLayout(browser_layout)
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        browser_layout.addWidget(self.tabs)
        
        self.stacked_widget.addWidget(self.browser_widget)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.add_new_tab(None, "Ny flik")
        self.open_videos_externally = True
        
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
        
        back_btn = QPushButton("◄")
        back_btn.setObjectName("navButton")
        back_btn.setFixedSize(36, 36)
        back_btn.clicked.connect(self.navigate_back)
        back_btn.setToolTip("Bakåt (Alt+←)")
        nav_layout.addWidget(back_btn)
        
        forward_btn = QPushButton("►")
        forward_btn.setObjectName("navButton")
        forward_btn.setFixedSize(36, 36)
        forward_btn.clicked.connect(self.navigate_forward)
        forward_btn.setToolTip("Framåt (Alt+→)")
        nav_layout.addWidget(forward_btn)
        
        reload_btn = QPushButton("↻")
        reload_btn.setObjectName("navButton")
        reload_btn.setFixedSize(36, 36)
        reload_btn.clicked.connect(self.reload_page)
        reload_btn.setToolTip("Uppdatera (F5)")
        nav_layout.addWidget(reload_btn)
        
        home_btn = QPushButton("⌂")
        home_btn.setObjectName("navButton")
        home_btn.setFixedSize(36, 36)
        home_btn.clicked.connect(self.show_home_page)
        home_btn.setToolTip("Hem (Ctrl+H)")
        nav_layout.addWidget(home_btn)
        
        self.main_search_bar = QLineEdit()
        self.main_search_bar.setObjectName("mainSearchBar")
        self.main_search_bar.setPlaceholderText("Sök eller ange webbadress...")
        self.main_search_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.main_search_bar)
        
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
        
        logo = QLabel("Klar")
        logo.setObjectName("homePageLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        version = QLabel("3.1")
        version.setObjectName("homePageVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(40)
        
        search_container = QWidget()
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_container.setLayout(search_layout)
        
        search_layout.addStretch()
        
        self.home_search_bar = QLineEdit()
        self.home_search_bar.setObjectName("homeSearchBar")
        self.home_search_bar.setPlaceholderText("Sök eller ange webbadress...")
        self.home_search_bar.setMinimumWidth(600)
        self.home_search_bar.setMaximumWidth(800)
        self.home_search_bar.returnPressed.connect(self.home_search)
        search_layout.addWidget(self.home_search_bar)
        
        home_search_btn = QPushButton("Sök")
        home_search_btn.setObjectName("primaryButton")
        home_search_btn.clicked.connect(self.home_search)
        search_layout.addWidget(home_search_btn)
        
        search_layout.addStretch()
        
        layout.addWidget(search_container)
        layout.addSpacing(60)
        
        features_widget = QWidget()
        features_layout = QHBoxLayout()
        features_layout.setSpacing(20)
        features_widget.setLayout(features_layout)
        
        features_layout.addStretch()
        
        features = [
            ("🇸🇪", "115 Svenska domäner"),
            ("⚡", "Snabb och effektiv sökning"),
            ("🔒", "Integritet i fokus"),
            ("📶", "Offline-sökning med LOKI"),
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
        """Add new tab with ad blocking enabled."""
        browser = QWebEngineView()

        # Cookie handling (new strategy-based system)
        browser.loadFinished.connect(
            lambda: self._inject_strategy_handler(browser, browser.url())
        )

        # Cosmetic ad filtering
        browser.loadFinished.connect(lambda: self.inject_cosmetic_filters(browser))

        browser.urlChanged.connect(lambda url: self.on_url_changed(url, browser))

        if qurl:
            browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.update_url_bar(qurl, browser)
        )
        browser.loadFinished.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabText(
                i, browser.page().title()[:25]
            )
        )
        browser.loadProgress.connect(self.update_status)
        self.stacked_widget.setCurrentIndex(1)
        return browser

    def inject_cosmetic_filters(self, browser):
        """Inject JS to hide ad containers."""
        try:
            js_code = self.adblock.get_cosmetic_filters_js()
            browser.page().runJavaScript(js_code)
        except Exception as e:
            print(f"[Klar] Cosmetic filter injection error: {e}")
    def show_adblock_stats(self):
        """Display ad blocking statistics."""
        stats = self.adblock.get_stats()
        message = (
            f"🛡️ Klar AdBlock\n"
            f"Rules: {stats['total_rules_loaded']}\n"
            f"Blocked: {stats['total_blocks']} requests\n"
            f"Unique URLs: {stats['unique_blocked_urls']}"
        )
        self.status.showMessage(message, 5000)



    def _inject_strategy_handler(self, browser, url):
        """Inject cookie handler: custom > banners db > generic"""
        try:
            domain = url.host().replace('www.', '')
            
            # Step 1: Check custom handlers first (user-defined)
            custom_js = self.custom_handlers.get_handler(domain)
            if custom_js:
                browser.page().runJavaScript(custom_js)
                print(f"[CookieHandler] Custom handler injected for {domain}")
                return
            
            # Step 2: Check cookie banners database
            banner_type = self.cookie_banners_db.detect_banner_type(domain)
            js_code = self.cookie_banners_db.get_handler_js(banner_type)
            banner_info = self.cookie_banners_db.get_banner_info(banner_type)
            
            browser.page().runJavaScript(js_code)
            print(f"[CookieHandler] {banner_info['name']} detected for {domain}")
            
        except Exception as e:
            print(f"[CookieHandler] Error: {e}")




    def on_url_changed(self, qurl: QUrl, browser):
        """Handle URL changes"""
        url_string = qurl.toString()
        
        if url_string.startswith('klar-bypass://'):
            self.handle_bypass_redirect(url_string, browser)
            return
        
        # Cache page if LOKI enabled and valid content
        if self.loki and self.loki.settings.get('enabled', False):
            try:
                page = browser.page()
                page.toHtml(lambda html: self._cache_page_content(url_string, page, html))
            except:
                pass
        
        self.check_video_url(qurl)
    
    def _cache_page_content(self, url: str, page, html: str):
        """Cache page content if LOKI enabled"""
        if self.loki and self.loki.settings.get('enabled', False):
            try:
                self.loki.cache_page({
                    'url': url,
                    'title': page.title(),
                    'content': html[:10000]  # Limit to 10KB
                })
                print(f"[LOKI] Cached: {url}")
            except Exception as e:
                print(f"[LOKI] Cache error: {e}")
    
    def handle_bypass_redirect(self, protocol_url: str, browser):
        """Handle klar-bypass:// protocol redirect"""
        try:
            parts = protocol_url.replace('klar-bypass://', '').split('/', 1)
            if len(parts) != 2:
                self.status.showMessage("Bypass avbruten: Ogiltig format", 5000)
                return
            
            token, encoded_url = parts
            bypass_url = unquote(encoded_url)
            
            if not self.blacklist.verify_bypass_acknowledgment(token):
                self.status.showMessage("Bypass avbruten: Ogiltig token", 5000)
                print(f"[Security] Bypass rejected: Invalid token")
                return
            
            print(f"[Security] Bypass approved for: {bypass_url}")
            self.status.showMessage(f"✓ Säkerhetskontroll åsidosatt. Laddar...", 3000)
            
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
            self.current_browser().back()

    def close_tab(self, i):
        """Close tab"""
        if self.tabs.count() < 2:
            self.show_home_page()
            return
        
        self.tabs.removeTab(i)
    
    def is_url(self, text):
        """Check if text is a URL - IMPROVED"""
        text = text.strip()
        
        # Explicit protocols
        if text.startswith(('http://', 'https://', 'ftp://', 'file://')):
            return True
        
        # Has domain extension and no spaces
        if '.' in text and ' ' not in text:
            parts = text.split('/')
            domain_part = parts[0].lower()
            
            # Must have at least 2 parts separated by dot
            if domain_part.count('.') >= 1:
                # Check if ends with valid TLD
                tlds = ['se', 'com', 'org', 'net', 'edu', 'gov', 'co', 'uk', 'de', 'fr', 'it', 'es', 'nl', 'be', 'ch', 'at', 'no', 'fi', 'dk', 'pl', 'ru', 'cn', 'jp', 'kr', 'au', 'nz', 'za', 'br', 'mx', 'ca', 'us', 'io', 'ai', 'tv', 'cc', 'ws', 'pro', 'info', 'biz', 'name', 'mobi', 'asia']
                last_part = domain_part.split('.')[-1]
                if last_part in tlds or last_part.isdigit():  # .123 for IPs
                    return True
        
        return False
    
    def navigate_to_url(self):
        """Navigate to URL or perform search"""
        query = self.main_search_bar.text().strip()
        
        if not query:
            return
        
        if self.is_url(query):
            is_allowed, reason = self.blacklist.is_whitelisted(query)
            
            if not is_allowed:
                blocked_html = self.blacklist.get_blocked_html(query, reason)
                self.current_browser().setHtml(blocked_html, QUrl("about:blank"))
                self.stacked_widget.setCurrentIndex(1)
                self.status.showMessage(f"⚠️ Domän blockerad för säkerhet", 5000)
                print(f"[Security] Blocked: {query} - {reason}")
            else:
                url = query if query.startswith(('http://', 'https://', 'ftp://')) else 'https://' + query
                print(f"[Navigation] Loading URL: {url}")
                self.current_browser().setUrl(QUrl(url))
                self.stacked_widget.setCurrentIndex(1)
                self.status.showMessage(f"Laddar: {query}...", 2000)
                print(f"[Security] Allowed: {query}")
        else:
            print(f"[Search] Performing search for: {query}")
            self.perform_search(query)
    
    def perform_search(self, query):
        """Perform search"""
        if self.is_searching:
            self.status.showMessage("Sökning pågår redan...", 2000)
            return
        
        self.is_searching = True
        
        demographic, confidence, metadata = self.demographic_detector.detect(query)
        print(f"[Demographic] Detected: {demographic} (confidence: {confidence:.2f})")
        
        self.status.showMessage(f"Söker efter: {query}...")
        
        self.show_loading_page(query)
        self.stacked_widget.setCurrentIndex(1)
        
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
        
        results_html = ResultsPage.generate_html(query, results, demographic)
        self.current_browser().setHtml(results_html, QUrl("about:blank"))
        
        count = len(results.get('results', []))
        self.status.showMessage(f"Hittade {count} resultat för: {query}", 3000)
        print(f"[SearchComplete] {count} results found")
    
    def on_search_error(self, error):
        """Handle search error"""
        self.is_searching = False
        print(f"[SearchError] {error}")
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: #0a0e1a;
                    color: #e8eaf0;
                }}
                .error {{
                    max-width: 600px;
                    margin: 100px auto;
                    padding: 30px;
                    background: rgba(192, 21, 47, 0.1);
                    border: 1px solid rgba(192, 21, 47, 0.3);
                    border-radius: 12px;
                    text-align: center;
                }}
                .error-icon {{ font-size: 48px; margin-bottom: 20px; }}
                h2 {{ color: #e8eaf0; margin-bottom: 10px; }}
                p {{ color: #a0a8c0; }}
            </style>
        </head>
        <body>
            <div class="error">
                <div class="error-icon">⚠️</div>
                <h2>Sökfel</h2>
                <p>{error}</p>
                <p>Försök igen eller kontrollera din internetanslutning</p>
            </div>
        </body>
        </html>
        """
        self.current_browser().setHtml(error_html, QUrl("about:blank"))
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
            QMainWindow { background: #0a0e1a; }
            
            #topNav {
                background: #131824;
                border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            }
            
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
            
            #mainSearchBar, #homeSearchBar {
                padding: 10px 16px;
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                font-size: 15px;
                background: #1e2538;
                color: #e8eaf0;
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
            
            #primaryButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            
            #primaryButton:hover { background: #60a5fa; }
            #primaryButton:pressed { background: #2563eb; }
            
            QTabWidget::pane { border: none; background: #0a0e1a; }
            
            QTabBar::tab {
                background: #131824;
                color: #a0a8c0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: #1e2538;
                color: #e8eaf0;
            }
            
            QStatusBar {
                background: #131824;
                color: #a0a8c0;
                border-top: 1px solid rgba(59, 130, 246, 0.2);
            }
            
            #homePage { background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%); }
            
            #homePageLogo {
                font-size: 96px;
                font-weight: 700;
                color: #3b82f6;
            }
            
            #homePageVersion {
                font-size: 32px;
                color: #6b7390;
            }
            
            #featureCard {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 16px;
            }
            
            #featureIcon { font-size: 42px; }
            #featureText { font-size: 14px; color: #a0a8c0; }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Klar 3.1")
    icon_path = Path(__file__).with_name("klar.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    browser = KlarBrowser()
    browser.show()
    
    sys.exit(app.exec())


    
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo

class KlarAdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Intercept network requests and block ads/trackers.
    """
    
    def __init__(self, adblock: 'AdBlocker'):
        super().__init__()
        self.adblock = adblock
    
    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        """Called for every network request."""
        url = info.requestUrl().toString()
        first_party = info.firstPartyUrl().toString()
        
        # Map Qt resource types to strings
        resource_map = {
            QWebEngineUrlRequestInfo.ResourceType.ResourceTypeImage: "image",
            QWebEngineUrlRequestInfo.ResourceType.ResourceTypeScript: "script",
            QWebEngineUrlRequestInfo.ResourceType.ResourceTypeStylesheet: "stylesheet",
            QWebEngineUrlRequestInfo.ResourceType.ResourceTypeXhr: "xhr",
            QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMedia: "media",
        }
        resource_type = resource_map.get(info.resourceType(), "other")
        
        should_block, reason = self.adblock.should_block(url, first_party, resource_type)
        
        if should_block:
            info.block(True)
            print(f"[AdBlock] BLOCKED: {url[:80]} ({reason})")
        # Otherwise request proceeds normally



if __name__ == '__main__':
    main()

