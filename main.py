#!/usr/bin/env python3
"""
Klar Browser - Mobile version for Android
Simple Kivy-based mobile app for KSE Search Engine
"""

import os
import sys

# Default server URL - can be overridden with environment variable
DEFAULT_SERVER_URL = os.environ.get('KSE_SERVER_URL', 'http://localhost:5000')

# Check if running on Android
try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
    request_permissions([Permission.INTERNET])
except ImportError:
    ANDROID = False

# Check if Kivy is available (for mobile), otherwise use PyQt6 (for desktop)
KIVY_AVAILABLE = False
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.gridlayout import GridLayout
    from kivy.core.window import Window
    from kivy.clock import Clock
    import requests
    KIVY_AVAILABLE = True
except ImportError:
    pass


class KlarBrowserApp(App):
    """Kivy-based mobile browser app"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = DEFAULT_SERVER_URL
    
    def build(self):
        """Build the app UI"""
        self.title = "Klar Browser"
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Search bar
        search_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.search_input = TextInput(
            hint_text='Search KSE...',
            multiline=False,
            size_hint_x=0.8
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        
        search_button = Button(
            text='Search',
            size_hint_x=0.2,
            on_press=self.perform_search
        )
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_button)
        
        # Results area
        self.results_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.results_layout)
        
        # Status label
        self.status_label = Label(
            text='Ready to search',
            size_hint_y=None,
            height=30
        )
        
        # Add to main layout
        layout.add_widget(search_layout)
        layout.add_widget(scroll_view)
        layout.add_widget(self.status_label)
        
        return layout
    
    def perform_search(self, *args):
        """Perform search query"""
        query = self.search_input.text.strip()
        if not query:
            return
        
        self.status_label.text = f'Searching for: {query}...'
        self.results_layout.clear_widgets()
        
        # Perform search in background
        Clock.schedule_once(lambda dt: self.do_search(query), 0.1)
    
    def do_search(self, query):
        """Execute search request"""
        try:
            url = f"{self.server_url}/api/search"
            params = {'q': query}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.display_results(data)
            
        except requests.exceptions.ConnectionError:
            self.status_label.text = "Unable to connect to KSE server"
        except requests.exceptions.Timeout:
            self.status_label.text = "Search request timed out"
        except requests.exceptions.HTTPError as e:
            self.status_label.text = f"Server error: {e.response.status_code}"
        except (requests.exceptions.JSONDecodeError, ValueError):
            self.status_label.text = "Invalid response from server"
        except Exception as e:
            # Log detailed error but show generic message to user
            print(f"Search error: {e}")
            self.status_label.text = "An error occurred during search"
    
    def display_results(self, data):
        """Display search results"""
        results = data.get('results', [])
        
        if not results:
            self.status_label.text = 'No results found'
            return
        
        self.status_label.text = f'Found {len(results)} results'
        
        for result in results:
            result_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=120,
                padding=10
            )
            
            title_label = Label(
                text=result.get('title', 'No title'),
                bold=True,
                size_hint_y=None,
                height=30,
                halign='left',
                valign='top'
            )
            title_label.bind(size=title_label.setter('text_size'))
            
            url_label = Label(
                text=result.get('url', ''),
                size_hint_y=None,
                height=20,
                color=(0.3, 0.5, 1, 1),
                halign='left',
                valign='top'
            )
            url_label.bind(size=url_label.setter('text_size'))
            
            snippet_label = Label(
                text=result.get('snippet', ''),
                size_hint_y=None,
                height=50,
                halign='left',
                valign='top'
            )
            snippet_label.bind(size=snippet_label.setter('text_size'))
            
            result_box.add_widget(title_label)
            result_box.add_widget(url_label)
            result_box.add_widget(snippet_label)
            
            self.results_layout.add_widget(result_box)


def main():
    """Main entry point - runs appropriate app based on available framework"""
    if KIVY_AVAILABLE:
        # Run Kivy mobile app
        KlarBrowserApp().run()
    else:
        # Fall back to PyQt6 for desktop
        try:
            import klar_browser
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            window = klar_browser.KlarBrowser()
            window.show()
            sys.exit(app.exec())
        except ImportError as e:
            print("Error: Neither Kivy nor PyQt6 is available.")
            print("Please install the required dependencies:")
            print("  For desktop: pip install PyQt6")
            print("  For mobile: pip install kivy")
            print(f"Import error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
