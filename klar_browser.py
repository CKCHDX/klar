"""
KLAR 3.0 - Swedish Search Engine Browser
PyQt6-based browser with integrated search, LOKI setup, and domain validation
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QComboBox, QDialog,
    QFileDialog, QMessageBox, QProgressBar, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

from engine.search_engine import SearchEngine
from algorithms.sven import SVEN
from core.crawler import Crawler
from core.parser import Parser
from engine.results_page import ResultsPageGenerator
from algorithms.loki import LOKI
from algorithms.thor import THOR


class LOKISetupDialog(QDialog):
    """First-run LOKI setup dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loki_path = None
        self.setup_ui()
        self.check_first_run()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("KLAR 3.0 - LOKI Setup")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #764ba2;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔍 KLAR Local Search Setup (LOKI)")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "LOKI enables fast local search indexing for instant answers.\n\n"
            "Would you like to enable local search?"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        skip_btn = QPushButton("Skip for Now")
        skip_btn.clicked.connect(self.skip_loki)
        button_layout.addWidget(skip_btn)
        
        install_btn = QPushButton("Install LOKI")
        install_btn.clicked.connect(self.install_loki)
        button_layout.addWidget(install_btn)
        
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def check_first_run(self):
        """Check if this is first run"""
        config_file = Path('klar_config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('loki_installed'):
                        self.accept()  # Skip dialog if LOKI already set
            except:
                pass
    
    def install_loki(self):
        """Install LOKI with folder selection"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select folder for LOKI data storage",
            str(Path.home())
        )
        
        if folder:
            self.loki_path = folder
            self.save_config(True, folder)
            QMessageBox.information(
                self,
                "LOKI Installed",
                f"LOKI has been installed at:\n{folder}"
            )
            self.accept()
    
    def skip_loki(self):
        """Skip LOKI installation"""
        self.save_config(False, None)
        self.accept()
    
    def save_config(self, installed: bool, path: str = None):
        """Save LOKI config to file"""
        config = {
            'loki_installed': installed,
            'loki_path': path,
            'first_run': False,
            'setup_date': datetime.now().isoformat()
        }
        
        with open('klar_config.json', 'w') as f:
            json.dump(config, f, indent=2)


class SearchWorker(QThread):
    """Background search worker thread"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, query: str, engine: SearchEngine):
        super().__init__()
        self.query = query
        self.engine = engine
    
    def run(self):
        """Execute search in background"""
        try:
            self.progress.emit("Searching...")
            results = self.engine.search(self.query)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class KLARBrowser(QMainWindow):
    """KLAR 3.0 Browser - Swedish Search Engine"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KLAR 3.0 - Swedish Search Engine")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.search_engine = SearchEngine()
        self.sven = SVEN()
        self.crawler = Crawler()
        self.parser = Parser()
        self.results_generator = ResultsPageGenerator()
        self.thor = THOR()
        
        # Load LOKI if available
        config_file = Path('klar_config.json')
        self.loki = None
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('loki_installed'):
                        self.loki = LOKI(config.get('loki_path'))
            except:
                pass
        
        self.setup_ui()
        self.show_loki_setup_if_needed()
    
    def setup_ui(self):
        """Setup main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🔍 KLAR 3.0")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter domain (e.g., svt.se) or search query...")
        self.url_input.returnPressed.connect(self.on_search)
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #667eea;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #764ba2;
                background: #f8f9ff;
            }
        """)
        search_layout.addWidget(self.url_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.on_search)
        search_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #764ba2;
            }
        """)
        search_btn.setMinimumWidth(100)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Category:")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(filter_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All", "News", "Weather", "Jobs", "Health", 
            "Food", "Sports", "Travel", "Entertainment"
        ])
        self.category_combo.setMaximumWidth(150)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #667eea;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: #667eea;
            }
        """)
        layout.addWidget(self.progress)
        
        # Results view
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        layout.addWidget(self.web_view)
        
        # Info label
        self.info_label = QLabel("Ready to search. Enter a domain or query above.")
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.info_label)
    
    def show_loki_setup_if_needed(self):
        """Show LOKI setup dialog on first run"""
        config_file = Path('klar_config.json')
        if not config_file.exists():
            dialog = LOKISetupDialog(self)
            dialog.exec()
    
    def on_search(self):
        """Handle search button click"""
        query = self.url_input.text().strip()
        
        if not query:
            self.info_label.setText("Please enter a search query or domain.")
            return
        
        # Check if it's a domain or search query
        is_domain = '.' in query and ' ' not in query
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.info_label.setText("Searching...")
        
        if is_domain:
            self.search_domain(query)
        else:
            self.search_query(query)
    
    def search_domain(self, domain: str):
        """Search a specific domain"""
        # Validate domain
        if not self.search_engine.is_valid_domain(domain):
            error_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial; background: #f5f5f5; padding: 40px; }}
                    .error {{ background: white; padding: 30px; border-radius: 8px; 
                             border-left: 4px solid #ff4444; }}
                    h2 {{ color: #ff4444; }}
                    p {{ color: #666; }}
                    .button {{ background: #667eea; color: white; padding: 10px 20px; 
                              border: none; border-radius: 4px; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Domain Not Trusted</h2>
                    <p>The domain '<strong>{domain}</strong>' is not in our database.</p>
                    <p>We only search 111 trusted Swedish and international domains for safety.</p>
                    <p><a href="mailto:domains@klar.se?subject=Add {domain}">Request this domain</a></p>
                </div>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
            self.progress.setVisible(False)
            self.info_label.setText(f"❌ Domain '{domain}' not in trusted database.")
            return
        
        # Fetch domain
        self.progress.setValue(50)
        try:
            content = self.crawler.fetch(f"https://{domain}")
            if content:
                parsed = self.parser.parse(content)
                html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
                        .result {{ background: white; padding: 20px; border-radius: 8px; 
                                 border-left: 4px solid #667eea; margin-bottom: 20px; }}
                        h2 {{ color: #667eea; }}
                        .meta {{ color: #999; font-size: 12px; margin-top: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="result">
                        <h2>{domain}</h2>
                        <p><strong>Title:</strong> {parsed.get('title', 'N/A')}</p>
                        <p><strong>Category:</strong> {parsed.get('category', 'General')}</p>
                        <p><strong>Words:</strong> {parsed.get('word_count', 0)}</p>
                        <div class="meta">Status: ✓ Loaded successfully</div>
                    </div>
                </body>
                </html>
                """
                self.web_view.setHtml(html)
                self.info_label.setText(f"✓ Loaded {domain} successfully")
            else:
                self.info_label.setText(f"Could not fetch {domain}")
        except Exception as e:
            self.info_label.setText(f"Error: {str(e)}")
        
        self.progress.setVisible(False)
    
    def search_query(self, query: str):
        """Search using KLAR search engine"""
        try:
            # Get category from combo
            category = self.category_combo.currentText()
            if category == "All":
                category = None
            
            # Process query with SVEN
            processed = self.sven.process_query(query)
            
            # Search
            self.progress.setValue(25)
            results = self.search_engine.search(query, category=category)
            
            # Rank results with THOR
            self.progress.setValue(75)
            if results.get('results'):
                results['results'] = self.thor.rank_results(
                    results['results'], 
                    query, 
                    category=category
                )
            
            # Generate results page
            self.progress.setValue(95)
            html = self.results_generator.generate(results, query)
            self.web_view.setHtml(html)
            
            self.progress.setValue(100)
            total = results.get('total_results', 0)
            self.info_label.setText(f"Found {total} results from {len(results.get('domains_used', []))} sources")
        
        except Exception as e:
            error_html = f"<html><body><h2>Error: {str(e)}</h2></body></html>"
            self.web_view.setHtml(error_html)
            self.info_label.setText(f"Error: {str(e)}")
        
        finally:
            self.progress.setVisible(False)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show browser
    browser = KLARBrowser()
    browser.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
