#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klar 3.0 - Android Mobile Version
Swedish Search Browser for Android
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
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
            for domain in self.domains[:10]:  # Limit to 10 results on mobile
                if query_lower in domain.get('name', '').lower() or query_lower in domain.get('url', '').lower():
                    results.append({
                        'title': domain.get('name', 'Unknown'),
                        'url': domain.get('url', ''),
                        'snippet': domain.get('description', 'Swedish website')
                    })
            return results


class SearchResultCard(MDCard):
    def __init__(self, title, url, snippet, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '10dp'
        self.spacing = '5dp'
        self.size_hint_y = None
        self.height = '120dp'
        self.md_bg_color = (0.15, 0.15, 0.15, 1)
        self.radius = [10]
        
        # Title
        title_label = MDLabel(
            text=title,
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height='30dp'
        )
        
        # URL
        url_label = MDLabel(
            text=url,
            font_style='Caption',
            theme_text_color='Custom',
            text_color=(0.3, 0.7, 1, 1),
            size_hint_y=None,
            height='20dp'
        )
        
        # Snippet
        snippet_label = MDLabel(
            text=snippet,
            font_style='Body2',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height='50dp'
        )
        
        self.add_widget(title_label)
        self.add_widget(url_label)
        self.add_widget(snippet_label)
        
        self.url = url


class KlarApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        
        # Initialize search engine
        base_path = Path(__file__).parent
        keywords_file = base_path / 'keywords_db.json'
        domains_file = base_path / 'domains.json'
        
        self.search_engine = SearchEngine(str(keywords_file), str(domains_file))
    
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Top app bar
        toolbar = MDTopAppBar(
            title='Klar - Swedish Search',
            md_bg_color=(0.1, 0.1, 0.1, 1),
            specific_text_color=(1, 1, 1, 1)
        )
        
        # Search box container
        search_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            padding='10dp',
            spacing='10dp'
        )
        
        # Search input
        self.search_input = MDTextField(
            hint_text='Sök på svenska webbplatser...',
            mode='rectangle',
            size_hint_x=0.75,
            multiline=False
        )
        self.search_input.bind(on_text_validate=self.perform_search)
        
        # Search button
        search_btn = MDRaisedButton(
            text='Sök',
            size_hint_x=0.25,
            on_release=self.perform_search
        )
        
        search_container.add_widget(self.search_input)
        search_container.add_widget(search_btn)
        
        # Results scroll view
        self.results_scroll = ScrollView(size_hint=(1, 1))
        
        # Results container
        self.results_container = GridLayout(
            cols=1,
            spacing='10dp',
            padding='10dp',
            size_hint_y=None
        )
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        
        self.results_scroll.add_widget(self.results_container)
        
        # Add welcome message
        welcome = MDLabel(
            text='Välkommen till Klar!\n\nSök på 111 svenska webbplatser\nmed 700+ svenska sökord',
            halign='center',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height='100dp'
        )
        self.results_container.add_widget(welcome)
        
        # Build layout
        layout.add_widget(toolbar)
        layout.add_widget(search_container)
        layout.add_widget(self.results_scroll)
        
        return layout
    
    def perform_search(self, *args):
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
            height='50dp'
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
                    height='50dp'
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
                height='40dp'
            )
            self.results_container.add_widget(header)
            
            # Add result cards
            for result in results:
                card = SearchResultCard(
                    title=result.get('title', 'Untitled'),
                    url=result.get('url', ''),
                    snippet=result.get('snippet', 'No description available')
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
                height='50dp'
            )
            self.results_container.add_widget(error_label)


if __name__ == '__main__':
    KlarApp().run()
