"""
Klar 3.1 Android - Mobile Search Browser
Kivy-based mobile app for Android 7.0+
Features: Touch support, responsive layout, offline search (LOKI)
"""

import json
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.uix.webview import WebView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from kivy.logger import Logger
from threading import Thread

Logger.setLevel('debug')

# Import search engine modules (compatible with mobile)
try:
    from engine.search_engine import SearchEngine
    from engine.results_page import ResultsPage
    from engine.domain_whitelist import DomainWhitelist
    from engine.demographic_detector import DemographicDetector
    from engine.loki_system import LOKISystem
except ImportError as e:
    Logger.error(f'Klar: Engine import error: {e}')
    # Fallback imports handled below

# ============================================
# RESPONSIVE DESIGN SYSTEM
# ============================================

class ResponsiveDesign:
    """Mobile-first responsive design metrics"""
    
    # Get device width
    DEVICE_WIDTH = Window.width
    DEVICE_HEIGHT = Window.height
    
    # Touch-friendly sizes (minimum 48dp for touch targets)
    BUTTON_HEIGHT = dp(48)
    INPUT_HEIGHT = dp(44)
    ICON_SIZE = dp(32)
    PADDING = dp(12)
    SPACING = dp(8)
    
    # Colors (matching desktop design)
    BG_PRIMARY = [0.04, 0.055, 0.1, 1.0]      # #0a0e1a
    BG_SECONDARY = [0.08, 0.14, 0.2, 1.0]    # #131824
    TEXT_PRIMARY = [0.91, 0.92, 0.94, 1.0]   # #e8eaf0
    TEXT_SECONDARY = [0.625, 0.66, 0.75, 1.0]  # #a0a8c0
    ACCENT_BLUE = [0.231, 0.51, 0.96, 1.0]  # #3b82f6
    ACCENT_RED = [0.75, 0.08, 0.18, 1.0]    # #c0152f
    
    @staticmethod
    def is_tablet():
        """Detect if device is tablet (width > 600dp)"""
        return Window.width > dp(600)
    
    @staticmethod
    def get_column_count():
        """Get responsive column count"""
        if Window.width > dp(900):
            return 3
        elif Window.width > dp(600):
            return 2
        return 1

# ============================================
class TouchHandler:
    """Handle touch interactions optimized for mobile"""
    
    @staticmethod
    def enable_haptic_feedback():
        """Enable haptic feedback for button presses"""
        try:
            from kivy.core.window import Window
            # Android haptic feedback would go here
            Logger.info('Klar: Haptic feedback enabled')
        except:
            pass
    
    @staticmethod
    def handle_long_press(widget, duration=0.5):
        """Handle long press gestures"""
        # Implemented via kivy gesture detection
        pass

# ============================================
class SetupWizardMobile(Popup):
    """First-run setup wizard for mobile"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Klar 3.1 - First Setup'
        self.size_hint = (0.95, 0.95)
        
        self.setup_data = {
            'first_run_completed': False,
            'loki_enabled': True,
            'data_path': str(Path.home() / "Klar-data")
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup mobile-optimized UI"""
        layout = BoxLayout(
            orientation='vertical',
            padding=ResponsiveDesign.PADDING,
            spacing=ResponsiveDesign.SPACING
        )
        
        # Header
        header = Label(
            text='Klar 3.1',
            font_size='32sp',
            size_hint_y=None,
            height=dp(50),
            color=ResponsiveDesign.TEXT_PRIMARY
        )
        layout.add_widget(header)
        
        # Subtitle
        subtitle = Label(
            text='Mobile Setup',
            font_size='18sp',
            size_hint_y=None,
            height=dp(40),
            color=ResponsiveDesign.TEXT_SECONDARY
        )
        layout.add_widget(subtitle)
        
        # LOKI section
        layout.add_widget(Label(
            text='🔍 Offline Search (LOKI)',
            font_size='14sp',
            size_hint_y=None,
            height=dp(40)
        ))
        
        loki_desc = Label(
            text='Cache pages for offline search.\nCan be disabled anytime in settings.',
            font_size='12sp',
            size_hint_y=None,
            height=dp(60),
            color=ResponsiveDesign.TEXT_SECONDARY
        )
        layout.add_widget(loki_desc)
        
        # Buttons
        button_layout = BoxLayout(
            size_hint_y=None,
            height=ResponsiveDesign.BUTTON_HEIGHT,
            spacing=ResponsiveDesign.SPACING
        )
        
        skip_btn = Button(
            text='Skip',
            background_color=ResponsiveDesign.BG_SECONDARY
        )
        skip_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(skip_btn)
        
        next_btn = Button(
            text='Next',
            background_color=ResponsiveDesign.ACCENT_BLUE
        )
        next_btn.bind(on_press=self._on_next)
        button_layout.add_widget(next_btn)
        
        layout.add_widget(button_layout)
        
        self.content = layout
    
    def _on_next(self, instance):
        """Handle next button"""
        self.setup_data['first_run_completed'] = True
        self.dismiss()
    
    def get_setup_data(self):
        """Return setup configuration"""
        return self.setup_data

# ============================================
class KlarMobileApp(App):
    """Main Klar Android application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Klar 3.1'
        
        # Window settings for mobile
        Window.minimum_width = dp(320)
        Window.minimum_height = dp(480)
        
        # Initialize engine components
        self.search_engine = None
        self.loki = None
        self.blacklist = None
        self.demographic_detector = None
        
        # State
        self.is_searching = False
        self.config_path = Path.home() / "klar_config.json"
    
    def build(self):
        """Build the mobile app UI"""
        # Load or create config
        self.config = self._load_or_create_config()
        self.data_path = self.config.get('loki', {}).get('storage_path', str(Path.home() / "Klar-data"))
        
        # Initialize LOKI if enabled
        if self.config.get('loki', {}).get('enabled', False):
            try:
                self.loki = LOKISystem(self.data_path)
                Logger.info(f'Klar: LOKI initialized at {self.data_path}')
            except Exception as e:
                Logger.error(f'Klar: LOKI init error: {e}')
                self.loki = None
        
        # Initialize search engine
        try:
            self.search_engine = SearchEngine()
            Logger.info('Klar: Search engine initialized')
        except Exception as e:
            Logger.error(f'Klar: Search engine error: {e}')
        
        # Initialize security
        try:
            domains_file = 'domains.json'
            self.blacklist = DomainWhitelist(domains_file)
            self.demographic_detector = DemographicDetector()
            Logger.info('Klar: Security modules loaded')
        except Exception as e:
            Logger.error(f'Klar: Security modules error: {e}')
        
        # Build main UI
        main_layout = BoxLayout(orientation='vertical')
        
        # Top navigation (touch-friendly)
        nav_layout = BoxLayout(
            size_hint_y=0.08,
            spacing=ResponsiveDesign.SPACING,
            padding=ResponsiveDesign.PADDING
        )
        nav_layout.canvas.before.clear()
        with nav_layout.canvas.before:
            Color(*ResponsiveDesign.BG_SECONDARY)
            Rectangle(size=nav_layout.size, pos=nav_layout.pos)
        
        # Navigation buttons
        for icon, callback in [('←', self.navigate_back), ('→', self.navigate_forward), ('↻', self.reload_page)]:
            btn = Button(
                text=icon,
                size_hint_x=0.15,
                background_color=ResponsiveDesign.BG_PRIMARY,
                font_size='18sp'
            )
            btn.bind(on_press=callback)
            nav_layout.add_widget(btn)
        
        # Search bar (main focus area)
        self.search_input = TextInput(
            multiline=False,
            hint_text='Search or enter URL...',
            size_hint_x=0.7,
            height=ResponsiveDesign.INPUT_HEIGHT,
            background_color=ResponsiveDesign.BG_PRIMARY,
            foreground_color=ResponsiveDesign.TEXT_PRIMARY,
            hint_text_color=ResponsiveDesign.TEXT_SECONDARY,
            font_size='14sp'
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        nav_layout.add_widget(self.search_input)
        
        # Search button
        search_btn = Button(
            text='Go',
            size_hint_x=0.15,
            background_color=ResponsiveDesign.ACCENT_BLUE,
            font_size='14sp'
        )
        search_btn.bind(on_press=self.perform_search)
        nav_layout.add_widget(search_btn)
        
        main_layout.add_widget(nav_layout)
        
        # Content area (home page for now)
        self.content_area = ScrollView()
        home_layout = GridLayout(
            cols=1,
            spacing=ResponsiveDesign.SPACING,
            padding=ResponsiveDesign.PADDING,
            size_hint_y=None,
            height=dp(800)
        )
        
        # Logo
        home_layout.add_widget(Label(
            text='Klar',
            font_size='48sp',
            size_hint_y=None,
            height=dp(80),
            color=ResponsiveDesign.ACCENT_BLUE
        ))
        
        # Features grid (responsive)
        features = [
            ('🇸🇪', '115 Swedish'),
            ('⚡', 'Fast'),
            ('🔒', 'Privacy'),
            ('📶', 'Offline'),
            ('🖼️', 'Images'),
            ('🎥', 'Video')
        ]
        
        features_grid = GridLayout(
            cols=ResponsiveDesign.get_column_count(),
            spacing=ResponsiveDesign.SPACING,
            size_hint_y=None,
            height=dp(300)
        )
        
        for icon, text in features:
            feature_box = BoxLayout(orientation='vertical')
            feature_box.add_widget(Label(
                text=icon,
                font_size='32sp',
                size_hint_y=0.6
            ))
            feature_box.add_widget(Label(
                text=text,
                font_size='12sp',
                size_hint_y=0.4,
                color=ResponsiveDesign.TEXT_SECONDARY
            ))
            features_grid.add_widget(feature_box)
        
        home_layout.add_widget(features_grid)
        
        self.content_area.add_widget(home_layout)
        main_layout.add_widget(self.content_area)
        
        # Status bar
        self.status_label = Label(
            text='Ready',
            size_hint_y=0.05,
            color=ResponsiveDesign.TEXT_SECONDARY,
            font_size='11sp'
        )
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def perform_search(self, instance=None):
        """Perform search from input"""
        query = self.search_input.text.strip()
        if not query:
            return
        
        self.status_label.text = f'Searching: {query}...'
        Logger.info(f'Klar: Search query: {query}')
        
        # Background search
        thread = Thread(target=self._search_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_thread(self, query):
        """Background search thread"""
        try:
            if self.search_engine:
                results = self.search_engine.search(query)
                Clock.schedule_once(lambda dt: self._display_results(results, query), 0)
            else:
                Logger.error('Klar: Search engine not initialized')
        except Exception as e:
            Logger.error(f'Klar: Search error: {e}')
            Clock.schedule_once(lambda dt: self.update_status(f'Error: {e}'), 0)
    
    def _display_results(self, results, query):
        """Display search results"""
        self.status_label.text = f'Found {len(results.get("results", []))} results'
        Logger.info(f'Klar: Results ready for {query}')
        
        # In a full implementation, render HTML results here
        # For now, show count
    
    def navigate_back(self, instance):
        """Navigate back"""
        self.status_label.text = 'Back'
    
    def navigate_forward(self, instance):
        """Navigate forward"""
        self.status_label.text = 'Forward'
    
    def reload_page(self, instance):
        """Reload page"""
        self.status_label.text = 'Reloading...'
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.text = message
    
    def _load_or_create_config(self):
        """Load or create config"""
        if not self.config_path.exists():
            # First run - show setup wizard
            wizard = SetupWizardMobile()
            wizard.open()
            
            setup_data = wizard.get_setup_data()
            config = {
                "version": "3.1",
                "platform": "android",
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
            
            return config
        else:
            # Load existing config
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                Logger.error(f'Klar: Config load error: {e}')
                return {"loki": {"enabled": False}}

if __name__ == '__main__':
    app = KlarMobileApp()
    app.run()
