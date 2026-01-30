#!/usr/bin/env python3
"""
Klar Browser - Android Version
A lightweight browser client for Android with integrated search functionality
Built with Kivy for cross-platform compatibility targeting Android 16 (API 34)
"""

import json
import logging
from pathlib import Path
from urllib.parse import urlparse

import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchResult(BoxLayout):
    """Widget to display a single search result"""
    
    def __init__(self, title, url, snippet, score=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 150
        self.padding = 10
        self.spacing = 5
        
        # Title
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=30,
            font_size='16sp',
            bold=True,
            color=(0.2, 0.6, 0.9, 1),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
        
        # URL
        url_label = Label(
            text=url,
            size_hint_y=None,
            height=20,
            font_size='12sp',
            color=(0.4, 0.8, 0.4, 1),
            halign='left',
            valign='middle'
        )
        url_label.bind(size=url_label.setter('text_size'))
        self.add_widget(url_label)
        
        # Snippet
        snippet_label = Label(
            text=snippet,
            size_hint_y=None,
            height=60,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='left',
            valign='top'
        )
        snippet_label.bind(size=snippet_label.setter('text_size'))
        self.add_widget(snippet_label)
        
        # Score badge if available
        if score:
            score_label = Label(
                text=f"Score: {score:.2f}",
                size_hint_y=None,
                height=20,
                font_size='11sp',
                color=(0.9, 0.7, 0.3, 1),
                halign='left',
                valign='middle'
            )
            score_label.bind(size=score_label.setter('text_size'))
            self.add_widget(score_label)


class KlarBrowserAndroid(BoxLayout):
    """Main browser interface for Android"""
    
    server_url = StringProperty("http://localhost:5000")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Load configuration
        self.config_file = self._get_config_path()
        self._load_config()
        
        # Header with title
        header = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        title_label = Label(
            text='Klar Search',
            font_size='24sp',
            bold=True,
            size_hint_x=0.7,
            color=(0.2, 0.7, 1, 1)
        )
        header.add_widget(title_label)
        
        # Settings button
        settings_btn = Button(
            text='⚙',
            size_hint_x=0.15,
            font_size='24sp'
        )
        settings_btn.bind(on_press=self.show_settings)
        header.add_widget(settings_btn)
        
        # About button
        about_btn = Button(
            text='?',
            size_hint_x=0.15,
            font_size='24sp'
        )
        about_btn.bind(on_press=self.show_about)
        header.add_widget(about_btn)
        
        self.add_widget(header)
        
        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.search_input = TextInput(
            hint_text='Enter search query...',
            size_hint_x=0.75,
            multiline=False,
            font_size='16sp'
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        search_box.add_widget(self.search_input)
        
        search_btn = Button(
            text='Search',
            size_hint_x=0.25,
            font_size='16sp'
        )
        search_btn.bind(on_press=self.perform_search)
        search_box.add_widget(search_btn)
        
        self.add_widget(search_box)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=30,
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.status_label)
        
        # Results container with scroll view
        self.results_scroll = ScrollView(size_hint=(1, 1))
        self.results_container = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )
        self.results_container.bind(
            minimum_height=self.results_container.setter('height')
        )
        self.results_scroll.add_widget(self.results_container)
        self.add_widget(self.results_scroll)
        
        logger.info("Klar Browser Android initialized")
    
    def _get_config_path(self):
        """Get platform-specific config path"""
        if platform == 'android':
            from android.storage import app_storage_path
            config_dir = Path(app_storage_path())
        else:
            config_dir = Path.home() / '.kse'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'klar_browser_config.json'
    
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
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config = {'server_url': self.server_url}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Config saved: {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def show_settings(self, instance):
        """Show settings dialog"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text='Server URL Configuration',
            size_hint_y=None,
            height=30,
            font_size='18sp'
        ))
        
        url_input = TextInput(
            text=self.server_url,
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size='14sp'
        )
        content.add_widget(url_input)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        save_btn = Button(text='Save', font_size='16sp')
        cancel_btn = Button(text='Cancel', font_size='16sp')
        
        popup = Popup(
            title='Settings',
            content=content,
            size_hint=(0.9, 0.4),
            auto_dismiss=False
        )
        
        def save_settings(instance):
            new_url = url_input.text.strip()
            if self._validate_url(new_url):
                self.server_url = new_url
                self._save_config()
                self.status_label.text = f'Server URL updated: {new_url}'
                popup.dismiss()
            else:
                self.status_label.text = 'Invalid URL format'
        
        def cancel_settings(instance):
            popup.dismiss()
        
        save_btn.bind(on_press=save_settings)
        cancel_btn.bind(on_press=cancel_settings)
        
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        
        popup.open()
    
    def show_about(self, instance):
        """Show about dialog"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        about_text = """Klar Browser for Android

Version: 1.0.0
Target: Android 16 (API 34)

A lightweight search browser client for the Klar Search Engine.

Built with Kivy framework for Android compatibility.
"""
        
        content.add_widget(Label(
            text=about_text,
            font_size='14sp'
        ))
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=50,
            font_size='16sp'
        )
        
        popup = Popup(
            title='About Klar Browser',
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def _validate_url(self, url):
        """Validate URL format"""
        if not url:
            return False
        
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except Exception:
            return False
    
    def perform_search(self, instance):
        """Perform search query"""
        query = self.search_input.text.strip()
        
        if not query:
            self.status_label.text = 'Please enter a search query'
            return
        
        self.status_label.text = f'Searching for: {query}...'
        self.results_container.clear_widgets()
        
        # Perform search in background thread
        Clock.schedule_once(lambda dt: self._execute_search(query), 0.1)
    
    def _execute_search(self, query):
        """Execute search API call"""
        try:
            url = f"{self.server_url}/api/search"
            params = {'q': query}
            
            logger.info(f"Searching for: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            # Update UI with results
            Clock.schedule_once(
                lambda dt: self._display_results(results, query), 0
            )
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(
                    "Unable to connect to KSE server. "
                    "Please ensure the server is running."
                ), 0
            )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(
                    "Search request timed out. Please try again."
                ), 0
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(f"Search error: {str(e)}"), 0
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error("Invalid response from server."), 0
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            Clock.schedule_once(
                lambda dt: self._show_error(f"Unexpected error: {str(e)}"), 0
            )
    
    def _display_results(self, results, query):
        """Display search results in UI"""
        self.results_container.clear_widgets()
        
        if not results:
            self.status_label.text = f'No results found for: {query}'
            no_results = Label(
                text='No results found',
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1)
            )
            self.results_container.add_widget(no_results)
            return
        
        self.status_label.text = f'Found {len(results)} results for: {query}'
        
        for result in results:
            title = result.get('title', 'No Title')
            url = result.get('url', '')
            snippet = result.get('snippet') or result.get('text', 'No description available')
            score = result.get('score')
            
            result_widget = SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                score=score
            )
            self.results_container.add_widget(result_widget)
        
        logger.info(f"Displayed {len(results)} results")
    
    def _show_error(self, error_message):
        """Show error message in UI"""
        self.status_label.text = f'Error: {error_message}'
        self.results_container.clear_widgets()
        
        error_label = Label(
            text=error_message,
            font_size='14sp',
            color=(1, 0.3, 0.3, 1)
        )
        self.results_container.add_widget(error_label)


class KlarApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build the application"""
        self.title = 'Klar Browser'
        
        # Set window background color (dark theme)
        Window.clearcolor = (0.1, 0.1, 0.12, 1)
        
        return KlarBrowserAndroid()


def main():
    """Main entry point"""
    try:
        KlarApp().run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
