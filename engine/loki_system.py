"""
LOKI - Local Offline Knowledge Index
Offline search system for Klar with automatic page caching and SQLite indexing
NOW with support for specialized handlers (Wikipedia, etc.)
INCLUDES: Database migration for backward compatibility
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import hashlib
from urllib.parse import urlparse


class LOKISystem:
    """Offline search and caching system with specialized handler support"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.cache_dir = self.storage_path / "loki" / "cache"
        self.db_path = self.storage_path / "loki" / "search_index.db"
        self.settings_path = self.storage_path / "loki" / "settings.json"
        self.sync_log_path = self.storage_path / "loki" / "sync_log.json"
        self.handlers_config_path = self.storage_path / "loki" / "handlers_config.json"
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load/create settings
        self.settings = self._load_settings()
        
        # Initialize database (includes migration)
        self._init_database()
        
        # Load sync log
        self.sync_log = self._load_sync_log()
        
        # Load handlers configuration
        self.handlers_config = self._load_handlers_config()
        
        print("[LOKI] Initialized with specialized handler support")
    
    def _load_settings(self) -> Dict:
        """Load LOKI settings"""
        if self.settings_path.exists():
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default settings
        defaults = {
            'enabled': False,
            'max_cache_size_mb': 500,
            'max_pages_per_domain': 1000,
            'retention_days': 90,
            'encryption': False,
            'auto_cleanup': True,
            'cache_images': False,
            'compression': True,
            'created_date': datetime.now().isoformat()
        }
        
        self._save_settings(defaults)
        return defaults
    
    def _save_settings(self, settings: Dict):
        """Save LOKI settings"""
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    
    def _load_handlers_config(self) -> Dict:
        """Load specialized handlers configuration"""
        if self.handlers_config_path.exists():
            with open(self.handlers_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default handlers configuration
        defaults = {
            'wikipedia': {
                'enabled': True,
                'cache_articles': True,
                'languages': ['sv', 'en'],
                'timeout': 5.0,
                'retry_attempts': 2,
            },
            'custom_handlers': {}
        }
        
        self._save_handlers_config(defaults)
        return defaults
    
    def _save_handlers_config(self, config: Dict):
        """Save handlers configuration"""
        with open(self.handlers_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _init_database(self):
        """Initialize SQLite database for offline search with automatic migration"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 1. Create tables (IF NOT EXISTS)
        # Note: If you have an old DB, this skips creating the table, so 'handler_type' is still missing!
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            title TEXT,
            domain TEXT,
            handler_type TEXT DEFAULT 'regular',
            content_hash TEXT,
            timestamp DATETIME,
            cached_size INTEGER,
            last_accessed DATETIME
        )
        ''')
        
        # ... (create other tables: keywords, search_history) ...
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY,
            page_id INTEGER,
            keyword TEXT,
            frequency INTEGER,
            FOREIGN KEY(page_id) REFERENCES pages(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY,
            query TEXT,
            timestamp DATETIME,
            results_count INTEGER,
            online INTEGER DEFAULT 1,
            handler_used TEXT
        )
        ''')

        # 2. RUN MIGRATION NOW (Before creating indices!)
        # This ensures the 'handler_type' column exists before we try to index it
        self._migrate_database_schema(cursor)
        conn.commit()

        # 3. Create indices for fast searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON pages(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON pages(timestamp)')
        
        # Now this is safe because migration has guaranteed the column exists
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_handler ON pages(handler_type)')
        
        conn.commit()
        conn.close()

    def _migrate_database_schema(self, cursor: sqlite3.Cursor):
        """Handle database schema migration for handler_type column"""
        try:
            # Check if handler_type column exists
            cursor.execute("PRAGMA table_info(pages)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'handler_type' not in columns:
                print("[LOKI] MIGRATION: Adding handler_type column to pages table")
                cursor.execute('''
                    ALTER TABLE pages ADD COLUMN handler_type TEXT DEFAULT 'regular'
                ''')
                print("[LOKI] MIGRATION: handler_type column added successfully")
            
            # Check search_history table for handler_used column
            cursor.execute("PRAGMA table_info(search_history)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'handler_used' not in columns:
                print("[LOKI] MIGRATION: Adding handler_used column to search_history table")
                cursor.execute('''
                    ALTER TABLE search_history ADD COLUMN handler_used TEXT
                ''')
                print("[LOKI] MIGRATION: handler_used column added successfully")
        
        except Exception as e:
            print(f"[LOKI] MIGRATION: Warning - could not migrate schema: {e}")
            print("[LOKI] MIGRATION: This is non-critical, continuing...")
    
    def _load_sync_log(self) -> Dict:
        """Load synchronization log"""
        if self.sync_log_path.exists():
            with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'entries': [], 'last_sync': None, 'offline_queries': [], 'handler_requests': []}
    
    def _save_sync_log(self):
        """Save synchronization log"""
        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.sync_log, f, indent=2, ensure_ascii=False)
    
    def cache_page(self, page_data: Dict, handler_type: str = 'regular') -> bool:
        """Cache a page for offline access
        
        Args:
            page_data: Dictionary with 'url', 'title', 'content'
            handler_type: 'regular', 'wikipedia', or custom handler name
        """
        if not self.settings.get('enabled', False):
            return False
        
        try:
            url = page_data.get('url')
            domain = urlparse(url).netloc.replace('www.', '')
            title = page_data.get('title', 'Untitled')
            content = page_data.get('content', '')
            
            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Insert into database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            cached_size = len(content.encode())
            
            cursor.execute('''
                INSERT OR REPLACE INTO pages 
                (url, title, domain, handler_type, content_hash, timestamp, cached_size, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, domain, handler_type, content_hash, timestamp, cached_size, timestamp))
            
            page_id = cursor.lastrowid
            
            # Extract and index keywords
            keywords = self._extract_keywords(content, title)
            for keyword, frequency in keywords.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO keywords (page_id, keyword, frequency)
                    VALUES (?, ?, ?)
                ''', (page_id, keyword, frequency))
            
            # Save page cache as JSON
            cache_dir_handler = self.cache_dir / handler_type / domain
            cache_file = cache_dir_handler / f"page_{page_id}.json"
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'url': url,
                'title': title,
                'domain': domain,
                'handler_type': handler_type,
                'content': content[:5000],  # Store first 5000 chars
                'timestamp': timestamp,
                'size_bytes': cached_size
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # Log sync
            self.sync_log['entries'].append({
                'url': url,
                'handler_type': handler_type,
                'timestamp': timestamp,
                'action': 'cached',
                'size': cached_size
            })
            self._save_sync_log()
            
            conn.commit()
            conn.close()
            
            # Manage storage
            self._manage_storage()
            
            print(f"[LOKI] Cached page via {handler_type}: {title}")
            return True
        
        except Exception as e:
            print(f"[LOKI] Error caching page: {e}")
            return False
    
    def _extract_keywords(self, content: str, title: str, max_keywords: int = 50) -> Dict[str, int]:
        """Extract keywords from content"""
        text = (title + " " + content).lower()
        
        # Simple word frequency analysis
        words = {}
        for word in text.split():
            word = word.strip('.,!?;:\'"()[]{}').lower()
            if len(word) > 3:  # Only words longer than 3 chars
                words[word] = words.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(words.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_words[:max_keywords])
    
    def offline_search(self, query: str, limit: int = 10, handler_filter: str = None) -> List[Dict]:
        """Search offline cache
        
        Args:
            query: Search query
            limit: Maximum results
            handler_filter: Filter by handler type (e.g., 'wikipedia', 'regular')
        """
        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Search for pages containing query keywords
            results = {}
            for word in query_words:
                if len(word) > 2:
                    sql = '''
                        SELECT p.id, p.url, p.title, p.domain, p.timestamp, p.handler_type, k.frequency
                        FROM pages p
                        JOIN keywords k ON p.id = k.page_id
                        WHERE k.keyword LIKE ?
                    '''
                    params = [f'%{word}%']
                    
                    if handler_filter:
                        sql += ' AND p.handler_type = ?'
                        params.append(handler_filter)
                    
                    sql += ' ORDER BY k.frequency DESC'
                    
                    cursor.execute(sql, params)
                    
                    for row in cursor.fetchall():
                        page_id = row[0]
                        if page_id not in results:
                            results[page_id] = {
                                'url': row[1],
                                'title': row[2],
                                'domain': row[3],
                                'timestamp': row[4],
                                'handler_type': row[5],
                                'relevance_score': 0,
                                'source': 'offline_cache'
                            }
                        results[page_id]['relevance_score'] += row[6]
            
            # Sort by relevance
            sorted_results = sorted(
                results.values(),
                key=lambda x: x['relevance_score'],
                reverse=True
            )[:limit]
            
            # Update search history
            handler_used = handler_filter or 'offline'
            cursor.execute('''
                INSERT INTO search_history (query, timestamp, results_count, online, handler_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (query, datetime.now().isoformat(), len(sorted_results), 0, handler_used))
            
            conn.commit()
            conn.close()
            
            return sorted_results
        
        except Exception as e:
            print(f"[LOKI] Offline search error: {e}")
            return []
    
    def get_handler_config(self, handler_name: str) -> Dict:
        """Get configuration for a specific handler"""
        return self.handlers_config.get(handler_name, {})
    
    def enable_handler(self, handler_name: str) -> bool:
        """Enable a specialized handler"""
        if handler_name in self.handlers_config:
            self.handlers_config[handler_name]['enabled'] = True
            self._save_handlers_config(self.handlers_config)
            print(f"[LOKI] Handler '{handler_name}' enabled")
            return True
        return False
    
    def disable_handler(self, handler_name: str) -> bool:
        """Disable a specialized handler"""
        if handler_name in self.handlers_config:
            self.handlers_config[handler_name]['enabled'] = False
            self._save_handlers_config(self.handlers_config)
            print(f"[LOKI] Handler '{handler_name}' disabled")
            return True
        return False
    
    def _manage_storage(self):
        """Manage cache storage size"""
        try:
            max_size = self.settings.get('max_cache_size_mb', 500) * 1024 * 1024
            current_size = self._get_cache_size()
            
            if current_size > max_size:
                print(f"[LOKI] Cache size {current_size / 1024 / 1024:.1f}MB exceeds limit")
                self._remove_oldest_pages()
        except Exception as e:
            print(f"[LOKI] Storage management error: {e}")
    
    def _get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                total += os.path.getsize(os.path.join(root, file))
        return total
    
    def _remove_oldest_pages(self, count: int = 10):
        """Remove oldest pages from cache"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get oldest pages
            cursor.execute('''
                SELECT id FROM pages
                ORDER BY last_accessed ASC
                LIMIT ?
            ''', (count,))
            
            oldest = cursor.fetchall()
            
            for page_id, in oldest:
                # Delete from database
                cursor.execute('DELETE FROM keywords WHERE page_id = ?', (page_id,))
                cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
            
            conn.commit()
            conn.close()
            
            print(f"[LOKI] Removed {len(oldest)} oldest pages")
        
        except Exception as e:
            print(f"[LOKI] Error removing pages: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count cached pages
            cursor.execute('SELECT COUNT(*) FROM pages')
            page_count = cursor.fetchone()[0]
            
            # Count domains
            cursor.execute('SELECT COUNT(DISTINCT domain) FROM pages')
            domain_count = cursor.fetchone()[0]
            
            # Get cache size
            cursor.execute('SELECT SUM(cached_size) FROM pages')
            total_size = cursor.fetchone()[0] or 0
            
            # Count by handler
            cursor.execute('''
                SELECT handler_type, COUNT(*) FROM pages
                GROUP BY handler_type
            ''')
            handler_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'enabled': self.settings.get('enabled', False),
                'page_count': page_count,
                'domain_count': domain_count,
                'cache_size_mb': total_size / 1024 / 1024,
                'handler_stats': handler_stats,
                'storage_path': str(self.storage_path),
                'handlers_enabled': [h for h, cfg in self.handlers_config.items() if cfg.get('enabled', False)]
            }
        
        except Exception as e:
            print(f"[LOKI] Error getting stats: {e}")
            return {}
    
    def clear_all_cache(self) -> bool:
        """Clear entire cache"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM keywords')
            cursor.execute('DELETE FROM pages')
            
            conn.commit()
            conn.close()
            
            # Delete cache files
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            print("[LOKI] Cache cleared")
            return True
        
        except Exception as e:
            print(f"[LOKI] Error clearing cache: {e}")
            return False
    
    def clear_handler_cache(self, handler_type: str) -> bool:
        """Clear cache for a specific handler"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get all page IDs for this handler
            cursor.execute('SELECT id FROM pages WHERE handler_type = ?', (handler_type,))
            page_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete keywords
            for page_id in page_ids:
                cursor.execute('DELETE FROM keywords WHERE page_id = ?', (page_id,))
            
            # Delete pages
            cursor.execute('DELETE FROM pages WHERE handler_type = ?', (handler_type,))
            
            conn.commit()
            conn.close()
            
            # Delete cache directory
            import shutil
            handler_cache_dir = self.cache_dir / handler_type
            if handler_cache_dir.exists():
                shutil.rmtree(handler_cache_dir)
            
            print(f"[LOKI] Cache cleared for handler: {handler_type}")
            return True
        
        except Exception as e:
            print(f"[LOKI] Error clearing handler cache: {e}")
            return False
