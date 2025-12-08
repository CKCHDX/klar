"""
LOKI - Local Offline Knowledge Index
Offline search system for Klar with automatic page caching and SQLite indexing
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
    """Offline search and caching system"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.cache_dir = self.storage_path / "loki" / "cache"
        self.db_path = self.storage_path / "loki" / "search_index.db"
        self.settings_path = self.storage_path / "loki" / "settings.json"
        self.sync_log_path = self.storage_path / "loki" / "sync_log.json"
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load/create settings
        self.settings = self._load_settings()
        
        # Initialize database
        self._init_database()
        
        # Load sync log
        self.sync_log = self._load_sync_log()
    
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
    
    def _init_database(self):
        """Initialize SQLite database for offline search"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                domain TEXT,
                content_hash TEXT,
                timestamp DATETIME,
                cached_size INTEGER,
                last_accessed DATETIME
            )
        ''')
        
        # Create keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY,
                page_id INTEGER,
                keyword TEXT,
                frequency INTEGER,
                FOREIGN KEY(page_id) REFERENCES pages(id)
            )
        ''')
        
        # Create search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY,
                query TEXT,
                timestamp DATETIME,
                results_count INTEGER,
                online INTEGER DEFAULT 1
            )
        ''')
        
        # Create indices for fast searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON pages(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON pages(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _load_sync_log(self) -> Dict:
        """Load synchronization log"""
        if self.sync_log_path.exists():
            with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'entries': [], 'last_sync': None, 'offline_queries': []}
    
    def _save_sync_log(self):
        """Save synchronization log"""
        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.sync_log, f, indent=2, ensure_ascii=False)
    
    def cache_page(self, page_data: Dict) -> bool:
        """Cache a page for offline access"""
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
                (url, title, domain, content_hash, timestamp, cached_size, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, domain, content_hash, timestamp, cached_size, timestamp))
            
            page_id = cursor.lastrowid
            
            # Extract and index keywords
            keywords = self._extract_keywords(content, title)
            for keyword, frequency in keywords.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO keywords (page_id, keyword, frequency)
                    VALUES (?, ?, ?)
                ''', (page_id, keyword, frequency))
            
            # Save page cache as JSON
            cache_file = self.cache_dir / domain / f"page_{page_id}.json"
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'url': url,
                'title': title,
                'domain': domain,
                'content': content[:5000],  # Store first 5000 chars
                'timestamp': timestamp,
                'size_bytes': cached_size
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # Log sync
            self.sync_log['entries'].append({
                'url': url,
                'timestamp': timestamp,
                'action': 'cached',
                'size': cached_size
            })
            self._save_sync_log()
            
            conn.commit()
            conn.close()
            
            # Manage storage
            self._manage_storage()
            
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
    
    def offline_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search offline cache"""
        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Search for pages containing query keywords
            results = {}
            for word in query_words:
                if len(word) > 2:
                    cursor.execute('''
                        SELECT p.id, p.url, p.title, p.domain, p.timestamp, k.frequency
                        FROM pages p
                        JOIN keywords k ON p.id = k.page_id
                        WHERE k.keyword LIKE ?
                        ORDER BY k.frequency DESC
                    ''', (f'%{word}%',))
                    
                    for row in cursor.fetchall():
                        page_id = row[0]
                        if page_id not in results:
                            results[page_id] = {
                                'url': row[1],
                                'title': row[2],
                                'domain': row[3],
                                'timestamp': row[4],
                                'relevance_score': 0,
                                'source': 'offline_cache'
                            }
                        results[page_id]['relevance_score'] += row[5]
            
            # Sort by relevance
            sorted_results = sorted(
                results.values(),
                key=lambda x: x['relevance_score'],
                reverse=True
            )[:limit]
            
            # Update search history
            cursor.execute('''
                INSERT INTO search_history (query, timestamp, results_count, online)
                VALUES (?, ?, ?, ?)
            ''', (query, datetime.now().isoformat(), len(sorted_results), 0))
            
            conn.commit()
            conn.close()
            
            return sorted_results
        
        except Exception as e:
            print(f"[LOKI] Offline search error: {e}")
            return []
    
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
            
            conn.close()
            
            return {
                'enabled': self.settings.get('enabled', False),
                'page_count': page_count,
                'domain_count': domain_count,
                'cache_size_mb': total_size / 1024 / 1024,
                'storage_path': str(self.storage_path)
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
