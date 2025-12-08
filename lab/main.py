#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klar 3.0 - Android Mobile Version
Swedish Search Browser with Responsive Touch UI
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from engine.search_engine import SearchEngine
except ImportError:
    # Fallback for basic search functionality
    class SearchEngine:
        def __init__(self, keywords_file, domains_file):
            self.keywords = {}
            self.domains = []
            try:
                if os.path.exists(keywords_file):
                    with open(keywords_file, 'r', encoding='utf-8') as f:
                        self.keywords = json.load(f)
                if os.path.exists(domains_file):
                    with open(domains_file, 'r', encoding='utf-8') as f:
                        self.domains = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
        
        def search(self, query):
            results = []
            query_lower = query.lower()
            for domain in self.domains[:10]:
                if query_lower in domain.get('name', '').lower() or query_lower in domain.get('url', '').lower():
                    results.append({
                        'title': domain.get('name', 'Unknown'),
                        'url': domain.get('url', ''),
                        'snippet': domain.get('description', 'Swedish website')
                    })
            return results


class TouchableSearchResultCard(MDCard):
    """Responsive search result card with touch feedback"""
    
    def __init__(self, title, url, snippet, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.url = url
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = self.calculate_height()
        self.md_bg_color = (0.15, 0.15, 0.15, 1)
        self.radius = [dp(10)]
        self.elevation = 2
        
        # Bind to window size changes for responsive scaling
        Window.bind(on_resize=self._on_window_resize)
        
        # Title
        title_label = MDLabel(
            text=title,
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=self.calculate_title_height(),
            bold=True,
            markup=True
        )
        
        # URL
        url_label = MDLabel(
            text=url,
            font_style='Caption',
            theme_text_color='Custom',
            text_color=(0.3, 0.7, 1, 1),
            size_hint_y=None,
            height=self.calculate_url_height(),
            shorten=True
        )
        
        # Snippet
        snippet_label = MDLabel(
            text=snippet,
            font_style='Body2',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=self.calculate_snippet_height(),
            markup=True
        )
        
        self.add_widget(title_label)
        self.add_widget(url_label)
        self.add_widget(snippet_label)
    
    def calculate_height(self):
        """Calculate card height based on window size"""
        if Window.height < 1000:  # Mobile
            return dp(120)
        else:  # Tablet
            return dp(150)
    
    def calculate_title_height(self):
        return dp(35) if Window.height < 1000 else dp(45)
    
    def calculate_url_height(self):
        return dp(20) if Window.height < 1000 else dp(28)
    
    def calculate_snippet_height(self):
        return dp(55) if Window.height < 1000 else dp(70)
    
    def _on_window_resize(self, window, width, height):
        """Handle window resize for responsive scaling"""
        self.height = self.calculate_height()
    
    def on_touch_down(self, touch):
        """Handle touch down with visual feedback"""
        if self.collide_point(*touch.pos):
            self.elevation = 5
            self.md_bg_color = (0.2, 0.2, 0.2, 1)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up"""
        if self.collide_point(*touch.pos):
            self.elevation = 2
            self.md_bg_color = (0.15, 0.15, 0.15, 1)
            return True
        return super().on_touch_up(touch)


class KlarApp(MDApp):
    """Klar Android Application with responsive design"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = '500'
        
        # Window size hint for mobile
        Window.size = (400, 800)
        
        # Initialize search engine
        base_path = Path(__file__).parent
        keywords_file = base_path / 'keywords_db.json'
        domains_file = base_path / 'domains.json'
        
        self.search_engine = SearchEngine(str(keywords_file), str(domains_file))
        
        # Bind window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
    
    def build(self):
        """Build responsive UI"""
        # Main layout
        main_layout = MDBoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Top app bar
        toolbar = MDTopAppBar(
            title='Klar',
            elevation=4,
            md_bg_color=(0.05, 0.1, 0.2, 1),
            specific_text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=self.calculate_toolbar_height()
        )
        
        # Search container
        search_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=self.calculate_search_height(),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0.1, 0.1, 0.1, 1)
        )
        
        # Search input
        self.search_input = MDTextField(
            hint_text='Sök svenska webbplatser',
            mode='rectangle',
            size_hint_x=0.85,
            multiline=False,
            font_size=sp(14)
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        
        # Search button
        search_btn = MDRaisedButton(
            text='Sök',
            size_hint_x=0.15,
            on_release=self.perform_search,
            font_size=sp(12)
        )
        
        search_container.add_widget(self.search_input)
        search_container.add_widget(search_btn)
        
        # Results scroll view
        self.results_scroll = ScrollView(size_hint=(1, 1))
        
        # Results container with responsive grid
        self.results_container = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        
        self.results_scroll.add_widget(self.results_container)
        
        # Welcome message
        welcome_text = 'Välkommen till Klar!\n\nSök på 111 svenska webbplatser\nmed 700+ svenska sökord'
        welcome = MDLabel(
            text=welcome_text,
            halign='center',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=self.calculate_welcome_height(),
            font_size=sp(14)
        )
        self.results_container.add_widget(welcome)
        
        # Build layout
        main_layout.add_widget(toolbar)
        main_layout.add_widget(search_container)
        main_layout.add_widget(self.results_scroll)
        
        return main_layout
    
    def calculate_toolbar_height(self):
        """Calculate toolbar height based on screen"""
        return dp(56) if Window.height < 1000 else dp(64)
    
    def calculate_search_height(self):
        """Calculate search container height"""
        return dp(70) if Window.height < 1000 else dp(80)
    
    def calculate_welcome_height(self):
        """Calculate welcome message height"""
        return dp(100) if Window.height < 1000 else dp(130)
    
    def _on_window_resize(self, window, width, height):
        """Handle window resize for responsive updates"""
        # Update root widget if it exists
        if self.root:
            # Update toolbar
            toolbar = self.root.children[-1]
            toolbar.height = self.calculate_toolbar_height()
            
            # Update search container
            search_container = self.root.children[-2]
            search_container.height = self.calculate_search_height()
    
    def perform_search(self, *args):
        """Execute search with responsive feedback"""
        query = self.search_input.text.strip()
        if not query:
            return
        
        # Clear previous results
        self.results_container.clear_widgets()
        
        # Show searching message
        searching_label = MDLabel(
            text=f'Söker efter "{query}"...',
            halign='center',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60),
            font_size=sp(14)
        )
        self.results_container.add_widget(searching_label)
        
        try:
            # Perform search
            results = self.search_engine.search(query)
            
            # Clear searching message
            self.results_container.clear_widgets()
            
            if not results:
                no_results = MDLabel(
                    text=f'Inga resultat för "{query}"',
                    halign='center',
                    theme_text_color='Custom',
                    text_color=(0.8, 0.3, 0.3, 1),
                    size_hint_y=None,
                    height=dp(60),
                    font_size=sp(14)
                )
                self.results_container.add_widget(no_results)
                return
            
            # Results header
            header = MDLabel(
                text=f'{len(results)} resultat för "{query}"',
                halign='center',
                font_style='H6',
                theme_text_color='Custom',
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(50),
                font_size=sp(16),
                bold=True
            )
            self.results_container.add_widget(header)
            
            # Add result cards
            for result in results:
                card = TouchableSearchResultCard(
                    title=result.get('title', 'Untitled'),
                    url=result.get('url', ''),
                    snippet=result.get('snippet', 'No description'),
                    app_ref=self
                )
                self.results_container.add_widget(card)
        
        except Exception as e:
            self.results_container.clear_widgets()
            error_label = MDLabel(
                text=f'Error: {str(e)}',
                halign='center',
                theme_text_color='Custom',
                text_color=(1, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(60),
                font_size=sp(14)
            )
            self.results_container.add_widget(error_label)


if __name__ == '__main__':
    KlarApp().run()
