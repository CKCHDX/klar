"""
Klar 3.1+ Production GUI
Updated to use file-based storage instead of PostgreSQL
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import logging
from pathlib import Path
import sys
import json
from datetime import datetime

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from crawler import Crawler
from storage import FileStorage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)d %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H%M%S'
)
logger = logging.getLogger('GUI')


class KlarGUI:
    """Klar 3.1+ Production GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Klar 3.1+ Search Engine - Production")
        self.root.geometry("1200x700")
        
        # Data path
        self.data_path = Path(__file__).parent.parent / 'data'
        self.data_path.mkdir(exist_ok=True)
        
        # Initialize storage (FILE-BASED, no database needed)
        logger.info(f"📁 Initializing file-based storage at {self.data_path}")
        self.storage = FileStorage(self.data_path)
        logger.info("✅ File-based storage ready")
        
        # Load domains
        domains_file = Path(__file__).parent.parent / 'domains.json'
        self.domains = []
        if domains_file.exists():
            with open(domains_file, 'r') as f:
                data = json.load(f)
                self.domains = data.get('domains', [])
            logger.info(f"📍 Loaded {len(self.domains)} domains")
        
        # Initialize crawler
        logger.info("🌐 Initializing crawler...")
        self.crawler = Crawler(self.domains, self.data_path)
        logger.info("✅ Crawler ready")
        
        # Create UI
        self._create_ui()
        
        logger.info("🎨 GUI COMPONENTS INITIALIZED")
    
    def _create_ui(self):
        """Create GUI components"""
        # Main frames
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search section
        ttk.Label(left_frame, text="🔍 Search Query", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.query_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.query_var, width=50).pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="🔎 Search", command=self._search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Storage Info", command=self._show_storage_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Stats", command=self._show_stats).pack(side=tk.LEFT, padx=5)
        
        # Results section
        ttk.Label(left_frame, text="📄 Results", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Results listbox
        scrollbar = ttk.Scrollbar(left_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar.set, height=20)
        self.results_listbox.pack(fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self._on_result_select)
        scrollbar.config(command=self.results_listbox.yview)
        
        # Preview section (right)
        ttk.Label(right_frame, text="👁️ Preview", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.preview_text = scrolledtext.ScrolledText(
            right_frame,
            height=30,
            width=60,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Storage info label
        self.storage_info_label = ttk.Label(right_frame, text="💾 Storage: Ready", foreground="green")
        self.storage_info_label.pack(anchor=tk.W, pady=5)
        
        # Log section (bottom)
        ttk.Label(self.root, text="📋 Activity Log", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5)
        
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar_log = ttk.Scrollbar(log_frame)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=6, yscrollcommand=scrollbar_log.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar_log.config(command=self.log_text.yview)
        
        # Redirect logging to GUI
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging to GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.update()
                # Keep last 1000 lines
                if self.text_widget.index(tk.END).split('.')[0] > '1000':
                    self.text_widget.delete('1.0', '2.0')
        
        handler = GUILogHandler(self.log_text)
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logging.getLogger().addHandler(handler)
    
    def _search(self):
        """Execute search"""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        logger.info(f"🔍 Searching for: '{query}'")
        
        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._search_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_thread(self, query):
        """Search thread"""
        try:
            # Search in storage first
            logger.info(f"📂 Checking local storage...")
            storage_results = self.storage.search_pages(query)
            
            if storage_results:
                logger.info(f"✅ Found {len(storage_results)} pages in storage")
                self._display_results(storage_results)
                return
            
            # If not in storage, crawl
            logger.info(f"🌐 Crawling for new results...")
            results = self.crawler.crawl_for_query(query, limit=20)
            
            if results:
                logger.info(f"💾 Saving {len(results)} results to storage...")
                saved = self.storage.save_batch(results)
                logger.info(f"✅ Saved {saved} pages")
            
            self._display_results(results)
        
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
    
    def _display_results(self, results):
        """Display search results"""
        self.results_listbox.delete(0, tk.END)
        self.current_results = results
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')[:50]
            domain = result.get('domain', 'unknown')
            item_text = f"{i}. {title} ({domain})"
            self.results_listbox.insert(tk.END, item_text)
        
        logger.info(f"📊 Displayed {len(results)} results")
    
    def _on_result_select(self, event):
        """Handle result selection"""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx < len(self.current_results):
            result = self.current_results[idx]
            
            # Display preview
            preview = f"""TITLE: {result.get('title', 'N/A')}
DOMAIN: {result.get('domain', 'N/A')}
URL: {result.get('url', 'N/A')}
\n--- DESCRIPTION ---\n{result.get('description', 'N/A')}\n\n--- CONTENT (First 1000 chars) ---\n{result.get('content', 'N/A')[:1000]}
"""
            
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert(tk.END, preview)
            self.preview_text.config(state=tk.DISABLED)
    
    def _show_storage_info(self):
        """Show storage information"""
        info = self.storage.get_storage_info()
        
        msg = f"""📊 STORAGE INFORMATION:

Location: {info.get('storage_path')}
Total Pages: {info.get('total_pages')}
Storage Size: {info.get('total_size_mb')} MB
Domains: {info.get('domains')}

✅ File-based storage (no database required)
"""
        
        messagebox.showinfo("Storage Info", msg)
        logger.info(f"📂 Storage: {info['total_pages']} pages, {info['total_size_mb']} MB")
    
    def _show_stats(self):
        """Show statistics"""
        domains = self.storage.get_all_domains()
        
        stats_text = "📈 DOMAIN STATISTICS:\n\n"
        total_size = 0
        
        for domain in domains:
            stats = self.storage.get_domain_stats(domain)
            stats_text += f"{domain}: {stats['pages']} pages ({stats['size_mb']} MB)\n"
            total_size += stats['size_bytes']
        
        stats_text += f"\nTotal: {len(domains)} domains, {total_size / (1024*1024):.2f} MB"
        
        messagebox.showinfo("Statistics", stats_text)
        logger.info(f"📊 Stats: {len(domains)} domains")


def main():
    root = tk.Tk()
    app = KlarGUI(root)
    logger.info("🚀 Klar GUI started")
    root.mainloop()


if __name__ == '__main__':
    main()
