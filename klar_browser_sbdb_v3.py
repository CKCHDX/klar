#!/usr/bin/env python3
"""
KLAR Browser v3 - Complete Rewrite
Integrated with SBDB v3 Backend

This is a complete rewrite of klarbrowser.py to work with the new SBDB v3 
backend (run_v3.py) while maintaining the same UI design and user experience.

Key Changes:
- APIClient class for REST API communication to 127.0.0.1:8080
- SearchWorker thread for non-blocking searches
- ResultWidget for individual result display
- KlarBrowser main window with Google-like interface
- Real-time connection status bar
- Swedish language support throughout
- Graceful error handling and fallbacks

Installation:
    pip install PyQt6 requests

Usage:
    python klar_browser_v3.py

Requirements:
    - SBDB v3 server running on 127.0.0.1:8080
    - Python 3.8+
    - PyQt6, requests
"""

import sys
import json
import time
import requests
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class APIClient:
    """
    REST API client for SBDB v3 backend.
    All communication goes through 127.0.0.1:8080 (hidden from user).
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.base_url = f"http://{host}:{port}"
        self.timeout = 10
        self.session = requests.Session()
        self.last_response_time = 0.0
    
    def search(self, query: str, top_k: int = 10) -> Dict:
        """POST /api/search - Execute Swedish search query"""
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/api/search",
                json={"query": query, "top_k": top_k},
                timeout=self.timeout
            )
            
            self.last_response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return response.json()
            
            return {
                "status": "error",
                "message": f"Server error: {response.status_code}",
                "results": []
            }
        
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to SBDB server",
                "results": []
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Search timed out",
                "results": []
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "results": []
            }
    
    def get_status(self) -> Dict:
        """GET /api/status - Check server connection"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/status",
                timeout=5
            )
            return response.json() if response.status_code == 200 else {}
        except:
            return {}


class SearchWorker(QThread):
    """Background worker thread for non-blocking searches"""
    
    result_ready = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, query: str):
        super().__init__()
        self.api_client = api_client
        self.query = query
    
    def run(self):
        result = self.api_client.search(self.query)
        self.result_ready.emit(result)


class ResultWidget(QFrame):
    """Individual search result display widget"""
    
    def __init__(self, result: Dict):
        super().__init__()
        self.result = result
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 8px 0px;
                padding: 12px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Domain/URL
        domain_label = QLabel()
        domain = self.result.get('domain', 'Unknown')
        domain_label.setText(f"<b>{domain}</b>")
        domain_label.setStyleSheet("color: #0066cc; font-size: 14px;")
        layout.addWidget(domain_label)
        
        # Page Title
        if self.result.get('title'):
            title = QLabel(self.result['title'])
            title.setStyleSheet("color: #1a1a1a; font-size: 16px; font-weight: bold;")
            title.setWordWrap(True)
            layout.addWidget(title)
        
        # Snippet
        if self.result.get('snippet'):
            snippet = QLabel(self.result['snippet'])
            snippet.setStyleSheet("color: #545454; font-size: 13px;")
            snippet.setWordWrap(True)
            layout.addWidget(snippet)
        
        # Metadata row
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)
        
        # Trust score
        trust = self.result.get('trust_score', 0)
        trust_color = "#28a745" if trust > 0.8 else "#ffc107" if trust > 0.6 else "#dc3545"
        trust_label = QLabel(f"Pålitlighet: {trust:.0%}")
        trust_label.setStyleSheet(f"color: {trust_color}; font-size: 11px;")
        meta_layout.addWidget(trust_label)
        
        # Region
        if self.result.get('region'):
            region_label = QLabel(f"Region: {self.result['region']}")
            region_label.setStyleSheet("color: #666666; font-size: 11px;")
            meta_layout.addWidget(region_label)
        
        meta_layout.addStretch()
        layout.addLayout(meta_layout)
        
        self.setLayout(layout)


class KlarBrowser(QMainWindow):
    """Main Klar Browser window - Google-like search interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Klar - Swedish Search Engine")
        self.setGeometry(100, 100, 1000, 800)
        
        self.api_client = APIClient()
        self.search_worker = None
        
        self.setup_ui()
        
        # Connection check timer
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(5000)
        
        self.check_connection()
    
    def setup_ui(self):
        """Build main interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 40, 30, 20)
        main_layout.setSpacing(20)
        
        # === HEADER ===
        title_label = QLabel("Klar")
        title_font = QFont("Arial", 40, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #0066cc; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        tagline = QLabel("Swedish Search. Crystal Clear.")
        tagline_font = QFont("Arial", 13)
        tagline.setFont(tagline_font)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: #999999; margin-bottom: 20px;")
        main_layout.addWidget(tagline)
        
        # === SEARCH BOX ===
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Sök på svenska... (t.ex. 'restauranger Stockholm')")
        self.search_input.setFont(QFont("Arial", 14))
        self.search_input.setMinimumHeight(48)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 25px;
                padding: 12px 20px;
                background-color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Sök")
        search_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        search_btn.setMinimumHeight(48)
        search_btn.setMinimumWidth(90)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        main_layout.addLayout(search_layout)
        
        # === RESULTS AREA ===
        self.results_label = QLabel("")
        self.results_label.setStyleSheet("color: #666666; font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(self.results_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(0)
        
        scroll.setWidget(self.results_container)
        main_layout.addWidget(scroll)
        
        # === STATUS BAR ===
        self.statusBar().setStyleSheet("""
            QStatusBar {
                border-top: 1px solid #e0e0e0;
                background-color: #f8f9fa;
                padding: 6px;
                font-size: 11px;
            }
        """)
        
        self.status_label = QLabel("● Ansluter till servern...")
        self.status_label.setStyleSheet("color: #ff9800;")
        self.statusBar().addWidget(self.status_label)
        
        self.response_label = QLabel("")
        self.response_label.setStyleSheet("color: #666666;")
        self.statusBar().addPermanentWidget(self.response_label)
    
    def perform_search(self):
        """Execute search"""
        query = self.search_input.text().strip()
        
        if not query:
            self.results_label.setText("Ange en sökterm")
            return
        
        self.results_label.setText("Söker...")
        self.status_label.setText("⏳ Söker...")
        self.status_label.setStyleSheet("color: #ff9800;")
        
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.search_worker = SearchWorker(self.api_client, query)
        self.search_worker.result_ready.connect(self.display_results)
        self.search_worker.start()
    
    def display_results(self, result: Dict):
        """Display search results"""
        if result.get('status') == 'error':
            self.results_label.setText(f"Fel: {result.get('message', 'Okänt fel')}")
            self.status_label.setText("● Fel vid sökning")
            self.status_label.setStyleSheet("color: #dc3545;")
            return
        
        results = result.get('results', [])
        response_time = self.api_client.last_response_time
        
        if results:
            self.results_label.setText(
                f"Resultat för '{self.search_input.text()}' - "
                f"{len(results)} träffar ({response_time:.0f}ms)"
            )
        else:
            self.results_label.setText(f"Inga resultat för '{self.search_input.text()}'")
        
        for res in results:
            widget = ResultWidget(res)
            self.results_layout.addWidget(widget)
        
        self.results_layout.addStretch()
        
        self.status_label.setText(f"● Ansluten ({response_time:.0f}ms)")
        self.status_label.setStyleSheet("color: #28a745;")
    
    def check_connection(self):
        """Check server connection"""
        try:
            status = self.api_client.get_status()
            if status.get('status') == 'running':
                self.status_label.setText("● Ansluten")
                self.status_label.setStyleSheet("color: #28a745;")
            else:
                self.status_label.setText("● Ansluter...")
                self.status_label.setStyleSheet("color: #ff9800;")
        except:
            self.status_label.setText("● Ej ansluten - starta servern")
            self.status_label.setStyleSheet("color: #dc3545;")


def main():
    app = QApplication(sys.argv)
    browser = KlarBrowser()
    browser.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
