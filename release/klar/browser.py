#!/usr/bin/env python3
"""
Klar 2.0 - FIXED Result Display Issue
Backend finds results but frontend wasn't displaying them properly
"""

import sys
import os
import json
import asyncio
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QStatusBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, QThread, Qt
from PyQt5.QtGui import QIcon
from qasync import QEventLoop

# Import existing components with CORRECT class names
from crawler import EnhancedSwedishCrawler  # ✅ FIXED
from parser import parse_html
from indexer import SuperFastBM25Indexer  # ✅ Your enhanced indexer

# Try to import revolutionary algorithms
try:
    from dossna_2 import DOSSNA_2_Engine, SwedishSearchContext
    from asi_2 import ASI_2_Index
    REVOLUTIONARY_MODE = True
    print("🚀 Revolutionary algorithms loaded!")
except ImportError as e:
    REVOLUTIONARY_MODE = False
    print(f"⚡ Enhanced mode: {e}")

def resource_path(relative_path):
    """Get resource path for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_domain_metadata():
    """Load domain metadata with fallback"""
    
    domain_files = ["domains.json", "revolutionary-domains.json"]
    
    for domain_file in domain_files:
        try:
            path = resource_path(domain_file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ Loaded {domain_file}")
                
                # Handle revolutionary format
                if "revolutionary_swedish_domains" in data:
                    simplified = {}
                    for tier_name, tier_data in data["revolutionary_swedish_domains"].items():
                        if isinstance(tier_data, dict):
                            for category, category_data in tier_data.items():
                                if isinstance(category_data, dict):
                                    for domain, domain_info in category_data.items():
                                        if isinstance(domain_info, dict) and 'keywords' in domain_info:
                                            simplified[domain] = domain_info['keywords']
                    return simplified
                
                return data
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Could not load {domain_file}: {e}")
            continue
    
    # Fallback domains
    print("⚠️ Using fallback Swedish domains")
    return {
        "svt.se": ["nyheter", "politik", "sport", "kultur"],
        "skatteverket.se": ["skatt", "deklaration", "moms", "tjänster"], 
        "blocket.se": ["köp", "sälj", "bil", "bostad", "elektronik"],
        "stockholm.se": ["kommun", "tjänster", "invånare", "kontakt"],
        "dn.se": ["nyheter", "ekonomi", "politik", "analys"],
        "1177.se": ["hälsa", "sjukvård", "medicin", "råd"]
    }

class SwedishSearchWorker(QThread):
    """Search worker with FIXED result format"""
    
    search_completed = pyqtSignal(list)
    search_progress = pyqtSignal(str)
    search_error = pyqtSignal(str)
    
    def __init__(self, query, domain_metadata):
        super().__init__()
        self.query = query
        self.domain_metadata = domain_metadata
        
        # Initialize systems
        try:
            if REVOLUTIONARY_MODE:
                self.dossna = DOSSNA_2_Engine()
                self.asi = ASI_2_Index()
                print("✅ engines initialized")
            else:
                self.dossna = None
                self.asi = None
            
            self.crawler = EnhancedSwedishCrawler(domain_metadata)
            self.indexer = SuperFastBM25Indexer(
                trusted_domains=set(domain_metadata.keys()) if domain_metadata else set()
            )
            
        except Exception as e:
            print(f"⚠️ System init error: {e}")
            self.dossna = None
            self.asi = None
            self.crawler = EnhancedSwedishCrawler({})
            self.indexer = SuperFastBM25Indexer(set())
    
    def run(self):
        """Run search with FIXED result formatting"""
        
        try:
            start_time = time.time()
            
            # Step 1: Check for instant answers (LOKI-style)
            self.search_progress.emit("🧠 Checking Swedish instant answers...")
            instant_answer = self._get_instant_swedish_answer()
            if instant_answer:
                result = [{
                    'title': '🇸🇪 Klar Direktsvar',
                    'url': '#instant',
                    'snippet': instant_answer,
                    'score': 1.0,
                    'source': 'swedish_knowledge',
                    'domain': 'klar.se'
                }]
                self.search_completed.emit(result)
                return
            
            # Step 2: Try revolutionary search
            if REVOLUTIONARY_MODE and self.dossna and self.asi:
                try:
                    self.search_progress.emit("🚀 DOSSNA 2.0 analyzing query...")
                    context = self.dossna.analyze_swedish_query(self.query)
                    
                    results = self.asi.revolutionary_search(self.query, context, limit=10)
                    
                    if results and len(results) > 0:
                        # Ensure results have proper format for display
                        formatted_results = []
                        for result in results:
                            if isinstance(result, dict) and 'title' in result:
                                formatted_result = {
                                    'title': result.get('title', 'Untitled'),
                                    'url': result.get('url', '#'),
                                    'snippet': result.get('snippet', 'No description available'),
                                    'score': result.get('score', 0.5),
                                    'source': result.get('source', 'revolutionary'),
                                    'domain': self._extract_domain(result.get('url', ''))
                                }
                                formatted_results.append(formatted_result)
                        
                        if formatted_results:
                            search_time = time.time() - start_time
                            self.search_progress.emit(f"✅ Revolutionary search: {len(formatted_results)} results in {search_time:.2f}s")
                            self.search_completed.emit(formatted_results)
                            return
                        
                except Exception as e:
                    print(f"Revolutionary search error: {e}")
                    self.search_progress.emit("⚠️ Revolutionary search failed, using enhanced...")
            
            # Step 3: Enhanced search (MAIN PATH)
            self.search_progress.emit("⚡ Enhanced Swedish search starting...")
            
            # Find seed URLs
            seeds = asyncio.run(self.crawler.find_seeds(self.query))
            self.search_progress.emit(f"🔍 Found {len(seeds)} Swedish sources")
            
            if not seeds:
                # Create fallback results if no seeds found
                fallback_results = self._create_fallback_results()
                self.search_completed.emit(fallback_results)
                return
            
            # Crawl pages
            pages = asyncio.run(self.crawler.crawl(seeds))
            self.search_progress.emit(f"📄 Crawled {len(pages)} pages")
            
            if not pages:
                # Create fallback results if no pages crawled
                fallback_results = self._create_fallback_results()
                self.search_completed.emit(fallback_results)
                return
            
            # Index and search
            indexed_count = 0
            for url, html in pages.items():
                try:
                    title, snippet, text = parse_html(html)
                    if text and len(text.strip()) > 50:
                        self.indexer.add_document(url, title or "Untitled", snippet or "", text)
                        indexed_count += 1
                except Exception as e:
                    print(f"Parse error for {url}: {e}")
            
            self.search_progress.emit(f"📊 Indexed {indexed_count} documents")
            
            if indexed_count == 0:
                # No documents indexed, create fallback
                fallback_results = self._create_fallback_results()
                self.search_completed.emit(fallback_results)
                return
            
            # Get search results from your indexer
            indexer_results = self.indexer.enhanced_search(self.query, limit=10)
            
            # Convert indexer results to display format
            formatted_results = []
            for result in indexer_results:
                if isinstance(result, dict):
                    formatted_result = {
                        'title': result.get('title', result.get('Title', 'Untitled')),
                        'url': result.get('url', result.get('URL', '#')),
                        'snippet': result.get('snippet', result.get('Snippet', 'No description available')),
                        'score': result.get('score', result.get('Score', 0.5)),
                        'source': 'enhanced_search',
                        'domain': self._extract_domain(result.get('url', result.get('URL', '')))
                    }
                    formatted_results.append(formatted_result)
            
            # Add search metadata as first result for debugging
            search_time = time.time() - start_time
            
            if not formatted_results:
                # Still no results, create informative fallback
                formatted_results = self._create_fallback_results()
            
            self.search_progress.emit(f"✅ Found {len(formatted_results)} results in {search_time:.2f}s")
            self.search_completed.emit(formatted_results)
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(error_msg)
            self.search_error.emit(error_msg)
    
    def _create_fallback_results(self):
        """Create fallback results when search fails"""
        query_lower = self.query.lower()
        
        # Swedish fallback results based on query
        fallback_results = []
        
        if any(term in query_lower for term in ['nyheter', 'news']):
            fallback_results = [
                {
                    'title': 'SVT Nyheter - Sveriges Television',
                    'url': 'https://svt.se/nyheter',
                    'snippet': 'Svenska nyheter, sport och underhållning från Sveriges Television.',
                    'score': 0.9,
                    'source': 'fallback',
                    'domain': 'svt.se'
                },
                {
                    'title': 'Dagens Nyheter - DN.se',
                    'url': 'https://dn.se',
                    'snippet': 'Senaste nyheterna inom politik, ekonomi, sport och kultur.',
                    'score': 0.8,
                    'source': 'fallback',
                    'domain': 'dn.se'
                }
            ]
        elif any(term in query_lower for term in ['skatt', 'deklaration']):
            fallback_results = [
                {
                    'title': 'Skatteverket - Startsida',
                    'url': 'https://skatteverket.se',
                    'snippet': 'Information om skatter, deklaration och moms från Skatteverket.',
                    'score': 0.9,
                    'source': 'fallback', 
                    'domain': 'skatteverket.se'
                }
            ]
        elif any(term in query_lower for term in ['köp', 'sälj', 'bil']):
            fallback_results = [
                {
                    'title': 'Blocket - köp & sälj begagnat & second hand',
                    'url': 'https://blocket.se',
                    'snippet': 'Sveriges största marknadsplats för begagnade saker.',
                    'score': 0.9,
                    'source': 'fallback',
                    'domain': 'blocket.se'
                }
            ]
        else:
            # General Swedish results
            fallback_results = [
                {
                    'title': f'Sökresultat för "{self.query}"',
                    'url': f'https://google.com/search?q={self.query}+site:se',
                    'snippet': f'Inga specifika svenska resultat hittades för "{self.query}". Försök med en mer specifik sökning eller kolla stavningen.',
                    'score': 0.5,
                    'source': 'fallback',
                    'domain': 'google.com'
                },
                {
                    'title': 'SVT Play',
                    'url': 'https://svtplay.se',
                    'snippet': 'Sveriges Televisions streaming-tjänst med program och serier.',
                    'score': 0.4,
                    'source': 'fallback',
                    'domain': 'svtplay.se'
                }
            ]
        
        return fallback_results
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            if url and url != '#':
                domain = urlparse(url).netloc
                return domain.replace('www.', '') if domain else 'unknown'
            return 'unknown'
        except:
            return 'unknown'
    
    def _get_instant_swedish_answer(self):
        """Get instant answers for common Swedish queries"""
        
        query_lower = self.query.lower()
        
        # Emergency numbers
        if any(term in query_lower for term in ['112', 'nödnummer', 'emergency', 'akut']):
            return "🚨 **Nödnummer Sverige: 112**\\nPolis, Brandkår, Ambulans - Ring vid akuta situationer och livsfara"
        
        if any(term in query_lower for term in ['1177', 'sjukvårdsrådgivning']):
            return "🏥 **Sjukvårdsrådgivning: Ring 1177**\\nDygnet runt för medicinska råd och hälsofrågor"
        
        # Government contacts
        if any(term in query_lower for term in ['skatteverket', 'deklaration', 'skatt']):
            return "💰 **Skatteverket: 0771-567 567**\\nskatteverket.se | Deklaration, moms, skattefrågor"
        
        if any(term in query_lower for term in ['försäkringskassan', 'sjukpenning']):
            return "💼 **Försäkringskassan: 0771-524 524**\\nforsakringskassan.se | Sjukpenning, föräldrapenning, pension"
        
        # Cultural concepts
        if 'allemansrätt' in query_lower:
            return "🌲 **Allemansrätt**\\nRätten att fritt röra sig i svensk natur. Regel: 'Inte störa, inte förstöra'"
        
        if 'fika' in query_lower:
            return "☕ **Fika**\\nSvensk kaffekultur och viktig del av arbetsplatstraditionen"
        
        return None

class BackendBridge(QObject):
    """Backend bridge with FIXED result handling"""
    
    sendResults = pyqtSignal(str)
    sendStatus = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            self.domain_metadata = load_domain_metadata()
            self.search_worker = None
            
            mode = "Revolutionary" if REVOLUTIONARY_MODE else "Enhanced"
            domain_count = len(self.domain_metadata)
            
            self.sendStatus.emit(f"🇸🇪 Klar 2.0 {mode} Ready! | {domain_count} Swedish domains")
            
        except Exception as e:
            self.sendStatus.emit(f"⚠️ Init error: {e}")
            self.domain_metadata = {}
    
    @pyqtSlot(str)
    def search(self, query):
        """Main search with FIXED result handling"""
        
        if not query.strip():
            self.sendStatus.emit("❌ Ange en sökterm")
            return
        
        try:
            # Kill previous search
            if self.search_worker and self.search_worker.isRunning():
                self.search_worker.terminate()
                self.search_worker.wait(2000)
            
            self.sendStatus.emit(f"🔍 Söker: '{query}'...")
            
            # Start search
            self.search_worker = SwedishSearchWorker(query, self.domain_metadata)
            self.search_worker.search_completed.connect(self._on_results)
            self.search_worker.search_progress.connect(self._on_progress)
            self.search_worker.search_error.connect(self._on_error)
            self.search_worker.start()
            
        except Exception as e:
            self.sendStatus.emit(f"❌ Search error: {e}")
    
    def _on_results(self, results):
        """Handle results with FIXED formatting"""
        try:
            # Ensure results are properly formatted
            if not results:
                results = [{
                    'title': 'Inga resultat',
                    'url': '#',
                    'snippet': 'Inga resultat hittades för din sökning. Försök med andra sökord.',
                    'score': 0.0,
                    'source': 'no_results',
                    'domain': 'klar.se'
                }]
            
            # Send results as JSON
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            self.sendResults.emit(results_json)
            
            # Update status
            self.sendStatus.emit(f"✅ Hittade {len(results)} resultat")
            
            # Debug output
            print(f"🔍 Sending {len(results)} results to frontend")
            for i, result in enumerate(results[:3]):  # Show first 3 for debugging
                print(f"  {i+1}. {result.get('title', 'No title')[:50]}...")
                
        except Exception as e:
            error_msg = f"Result handling error: {e}"
            print(error_msg)
            self.sendStatus.emit(f"❌ {error_msg}")
    
    def _on_progress(self, message):
        """Handle progress updates"""
        self.sendStatus.emit(message)
        print(f"Progress: {message}")
    
    def _on_error(self, error):
        """Handle errors"""
        self.sendStatus.emit(f"❌ {error}")
        print(f"Search error: {error}")
    
    @pyqtSlot(str)
    def open_url(self, url):
        """Open URL in browser"""
        try:
            if hasattr(self.parent(), 'browser'):
                self.parent().browser.load(QUrl(url))
                self.sendStatus.emit(f"🌐 Öppnar: {url}")
        except Exception as e:
            self.sendStatus.emit(f"❌ URL error: {e}")

class KlarRevolutionaryBrowser(QMainWindow):
    """Klar 2.0 with FIXED result display"""
    
    def __init__(self):
        super().__init__()
        
        mode = "Revolution" if REVOLUTIONARY_MODE else "Enhanced"
        self.setWindowTitle(f"🇸🇪 Klar 2.0 - Swedish Search Engine")
        self.resize(1400, 900)
        
        # Load icon
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        # Apply styling
        self._apply_styling()
        
        # Setup interface
        self._setup_interface()
        
        # Setup WebChannel
        self._setup_webchannel()
        
        print(f"✅ Klar 2.0 {mode} Browser with FIXED result display!")
    
    def _apply_styling(self):
        """Apply Swedish styling"""
        
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1a1a1a, stop: 1 #2d2d2d);
            color: #ffffff;
        }
        
        QToolBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0066CC, stop: 1 #004499);
            border: none;
            color: #ffffff;
            font-weight: bold;
            padding: 12px;
        }
        
        QToolBar QAction {
            background-color: rgba(255, 204, 0, 0.2);
            border: 2px solid #FFCC00;
            border-radius: 8px;
            padding: 12px 20px;
            margin: 4px;
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
        }
        
        QToolBar QAction:hover {
            background-color: rgba(255, 204, 0, 0.4);
        }
        
        QStatusBar {
            background: #2d2d2d;
            color: #FFCC00;
            font-weight: bold;
            border-top: 3px solid #0066CC;
            padding: 10px;
            font-size: 14px;
        }
        
        QWebEngineView {
            border: 2px solid #0066CC;
            border-radius: 8px;
        }
        """)
    
    def _setup_interface(self):
        """Setup interface"""
        
        # Browser
        self.browser = QWebEngineView()
        page = self.browser.page()
        
        settings = page.settings()
        settings.setAttribute(settings.JavascriptEnabled, True)
        settings.setAttribute(settings.AutoLoadImages, True)
        settings.setAttribute(settings.LocalContentCanAccessFileUrls, True)
        
        profile = page.profile()
        profile.setHttpAcceptLanguage("sv-SE,sv;q=0.9,en;q=0.7")
        
        self.setCentralWidget(self.browser)
        
        # Toolbar
        self._create_toolbar()
        
        # Status bar
        self.status_bar = QStatusBar()
        mode = "Revolution" if REVOLUTIONARY_MODE else "Enhanced"
        self.status_bar.showMessage(f"🇸🇪 Klar 2.0 - Redo för svenska sökningar!")
        self.setStatusBar(self.status_bar)
        
        # Load home
        self._load_home()
    
    def _create_toolbar(self):
        """Create toolbar"""
        
        toolbar = QToolBar("Navigation")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Navigation
        back_action = QAction("⬅️ Tillbaka", self)
        back_action.triggered.connect(self.browser.back)
        toolbar.addAction(back_action)
        
        forward_action = QAction("➡️ Framåt", self)
        forward_action.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_action)
        
        reload_action = QAction("🔄 Ladda Om", self)
        reload_action.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_action)
        
        toolbar.addSeparator()
        
        # Swedish links
        home_action = QAction("🏠 Hem", self)
        home_action.triggered.connect(self._load_home)
        toolbar.addAction(home_action)
        
        svt_action = QAction("📰 SVT", self)
        svt_action.triggered.connect(lambda: self.browser.load(QUrl("https://svt.se/nyheter")))
        toolbar.addAction(svt_action)
        
        # Mode
        mode_text = "🚀 Revolution" if REVOLUTIONARY_MODE else "⚡ Enhanced"
        mode_action = QAction(mode_text, self)
        mode_action.triggered.connect(self._show_info)
        toolbar.addAction(mode_action)
        
        self.addToolBar(toolbar)
    
    def _setup_webchannel(self):
        """Setup WebChannel"""
        
        try:
            self.channel = QWebChannel()
            self.browser.page().setWebChannel(self.channel)
            
            self.bridge = BackendBridge(self)
            self.bridge.sendStatus.connect(self._update_status)
            self.channel.registerObject("backend", self.bridge)
            
            print("✅ WebChannel setup complete")
        except Exception as e:
            print(f"⚠️ WebChannel error: {e}")
    
    def _load_home(self):
        """Load home with FIXED result display"""
        
        # Check for existing template
        templates_path = os.path.join(os.path.dirname(__file__), "templates")
        index_file = os.path.join(templates_path, "index.html")
        
        if os.path.exists(index_file):
            self.browser.load(QUrl.fromLocalFile(index_file))
            print("✅ Using existing template")
        else:
            print("⚡ Using built-in template with FIXED result display")
            self._load_builtin_home()
    
    def _load_builtin_home(self):
        """Load home with PROPER result display"""
        
        mode = "Revolution" if REVOLUTIONARY_MODE else "Enhanced"
        
        home_html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <title>Klar 2.0 {mode}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0066CC 0%, #1a1a1a 50%, #FFCC00 100%);
            font-family: 'Segoe UI', Arial, sans-serif;
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
        }}
        .logo {{
            font-size: 3.5em;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        }}
        .mode {{
            display: inline-block;
            background: rgba(255,204,0,0.3);
            padding: 8px 20px;
            border-radius: 20px;
            border: 2px solid #FFCC00;
            margin: 15px 0;
            font-weight: bold;
        }}
        .search-section {{
            background: rgba(0,0,0,0.4);
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
        }}
        .search-box {{
            display: flex;
            background: rgba(255,255,255,0.95);
            border-radius: 50px;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        .search-input {{
            flex: 1;
            border: none;
            padding: 15px 25px;
            font-size: 18px;
            border-radius: 45px;
            outline: none;
            color: #333;
        }}
        .search-button {{
            background: linear-gradient(45deg, #0066CC, #FFCC00);
            border: none;
            padding: 15px 25px;
            border-radius: 45px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        }}
        .quick-links {{
            text-align: center;
            margin: 20px 0;
        }}
        .quick-link {{
            display: inline-block;
            background: rgba(0,102,204,0.3);
            color: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 15px;
            text-decoration: none;
            border: 1px solid #0066CC;
            cursor: pointer;
            font-size: 14px;
        }}
        .quick-link:hover {{
            background: rgba(0,102,204,0.5);
        }}
        
        /* FIXED: Result display styles */
        .results-container {{
            background: rgba(0,0,0,0.6);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            display: none; /* Hidden initially */
        }}
        .results-container.show {{
            display: block;
        }}
        .result-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #FFCC00;
        }}
        .result-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #FFCC00;
            text-decoration: none;
        }}
        .result-title:hover {{
            text-decoration: underline;
        }}
        .result-url {{
            font-size: 12px;
            color: #66CC66;
            margin-bottom: 8px;
        }}
        .result-snippet {{
            color: #DDDDDD;
            line-height: 1.4;
            font-size: 14px;
        }}
        .result-score {{
            font-size: 11px;
            color: #888;
            text-align: right;
        }}
        .loading {{
            text-align: center;
            padding: 20px;
            color: #FFCC00;
        }}
        .no-results {{
            text-align: center;
            padding: 20px;
            color: #FF6666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🇸🇪 KLAR 2.0</div>
            <div class="mode">{mode} MODE</div>
            <p style="font-size: 1.1em; margin: 15px 0;">
                Sveriges kraftfullaste sökmotorn med {'revolutionära algoritmer' if REVOLUTIONARY_MODE else 'förbättrade algoritmer'}
            </p>
        </div>
        
        <div class="search-section">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" 
                       placeholder="Sök på svenska webbplatser..."
                       onkeypress="if(event.key==='Enter') performSearch()">
                <button class="search-button" onclick="performSearch()">
                    🔍 Sök
                </button>
            </div>
            
            <div class="quick-links">
                <strong>Snabbsökning:</strong><br><br>
                <div class="quick-link" onclick="quickSearch('svenska nyheter')">📰 Nyheter</div>
                <div class="quick-link" onclick="quickSearch('skatteverket')">💰 Skatteverket</div>
                <div class="quick-link" onclick="quickSearch('112')">🚨 Nödnummer</div>
                <div class="quick-link" onclick="quickSearch('köpa bil')">🚗 Köpa bil</div>
                <div class="quick-link" onclick="quickSearch('1177')">🏥 Hälsa</div>
                <div class="quick-link" onclick="quickSearch('allemansrätt')">🌲 Allemansrätt</div>
            </div>
        </div>
        
        <!-- FIXED: Results container -->
        <div id="results-container" class="results-container">
            <h2>🔍 Sökresultat</h2>
            <div id="results-list"></div>
        </div>
        
        <div style="text-align: center; margin: 30px 0; font-size: 0.9em; opacity: 0.8;">
            {'🚀 DOSSNA 2.0 | ASI 2.0 | SVEN | THOR | LOKI' if REVOLUTIONARY_MODE else '⚡ SuperFast BM25 | Enhanced Swedish Crawler | Swedish Optimization'}
        </div>
    </div>
    
    <script>
        // FIXED: Proper search and result display
        function performSearch() {{
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {{
                alert('Ange en sökterm');
                return;
            }}
            
            if (window.backend) {{
                console.log('🔍 Searching for:', query);
                
                // Show loading
                showLoading();
                
                // Send search to backend
                window.backend.search(query);
            }} else {{
                console.log('❌ Backend not available');
                showError('Backend inte tillgänglig');
            }}
        }}
        
        function quickSearch(query) {{
            document.getElementById('searchInput').value = query;
            performSearch();
        }}
        
        function showLoading() {{
            const container = document.getElementById('results-container');
            const resultsList = document.getElementById('results-list');
            
            resultsList.innerHTML = '<div class="loading">🔍 Söker svenska webbplatser...</div>';
            container.classList.add('show');
        }}
        
        function showError(message) {{
            const container = document.getElementById('results-container');
            const resultsList = document.getElementById('results-list');
            
            resultsList.innerHTML = `<div class="no-results">❌ ${{message}}</div>`;
            container.classList.add('show');
        }}
        
        function displayResults(results) {{
            console.log('📊 Displaying results:', results);
            
            const container = document.getElementById('results-container');
            const resultsList = document.getElementById('results-list');
            
            if (!results || results.length === 0) {{
                resultsList.innerHTML = '<div class="no-results">❌ Inga resultat hittades</div>';
            }} else {{
                let html = '';
                results.forEach((result, index) => {{
                    html += `
                        <div class="result-item">
                            <a href="${{result.url}}" class="result-title" onclick="openResult('${{result.url}}'); return false;">
                                ${{result.title || 'Untitled'}}
                            </a>
                            <div class="result-url">${{result.domain || result.url}}</div>
                            <div class="result-snippet">${{result.snippet || 'No description available'}}</div>
                            <div class="result-score">Score: ${{(result.score || 0).toFixed(2)}} | Source: ${{result.source || 'unknown'}}</div>
                        </div>
                    `;
                }});
                resultsList.innerHTML = html;
            }}
            
            container.classList.add('show');
            
            // Scroll to results
            container.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        function openResult(url) {{
            console.log('🌐 Opening:', url);
            if (window.backend && url !== '#') {{
                window.backend.open_url(url);
            }}
        }}
        
        // WebChannel initialization
        if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                window.backend = channel.objects.backend;
                console.log('✅ Klar WebChannel connected!');
                
                // FIXED: Connect result handler
                if (window.backend.sendResults) {{
                    window.backend.sendResults.connect(function(resultsJson) {{
                        console.log('📥 Received results JSON:', resultsJson);
                        try {{
                            const results = JSON.parse(resultsJson);
                            displayResults(results);
                        }} catch (e) {{
                            console.error('❌ JSON parse error:', e);
                            showError('Fel vid parsning av resultat');
                        }}
                    }});
                }} else {{
                    console.log('⚠️ sendResults signal not found');
                }}
            }});
        }} else {{
            console.log('⚠️ Qt WebChannel not available');
        }}
    </script>
</body>
</html>'''
        
        self.browser.setHtml(home_html)
    
    def _show_info(self):
        """Show mode info"""
        info_html = "System information would go here..."
        self.browser.setHtml(f"<html><body style='background:#1a1a1a;color:white;padding:30px;'>{info_html}</body></html>")
    
    def _update_status(self, message):
        """Update status bar"""
        self.status_bar.showMessage(message)

def main():
    """Main entry with FIXED result display"""
    
    mode = "Revolution" if REVOLUTIONARY_MODE else "Enhanced"
    print(f"🇸🇪 Starting Klar 2.0 {mode} with FIXED result display...")
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(f"Klar 2.0 {mode}")
        
        # Swedish locale
        from PyQt5.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.Swedish, QLocale.Sweden))
        
        # Create browser
        browser = KlarRevolutionaryBrowser()
        browser.show()
        
        # Setup async loop
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        print(f"✅ Klar 2.0 {mode} ready with FIXED result display!")
        
        with loop:
            return loop.run_forever()
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())