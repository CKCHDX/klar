"""
LOKI - Local Knowledge Base for Instant Answers
Local search indexing and instant answer retrieval
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict


class LOKI:
    """Local knowledge base for instant answers"""
    
    def __init__(self, data_path: Optional[str] = None):
        if data_path:
            self.data_path = Path(data_path)
            self.enabled = self.data_path.exists()
        else:
            self.enabled = False
        
        self.knowledge_base = {}
        if self.enabled:
            self.load_kb()
    
    def load_kb(self):
        """Load knowledge base from disk"""
        try:
            kb_file = self.data_path / 'knowledge_base.json'
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            print(f"Error loading LOKI: {e}")
    
    def index_content(self, url: str, content: str, category: str):
        """Index content into knowledge base"""
        if not self.enabled:
            return False
        
        entry = {
            'url': url,
            'content': content,
            'category': category,
            'indexed_at': str(os.stat(__file__).st_mtime)
        }
        
        # Create entry key from URL
        key = url.replace('https://', '').replace('http://', '').replace('/', '_')
        self.knowledge_base[key] = entry
        
        return True
    
    def search(self, query: str) -> Optional[Dict]:
        """Search local knowledge base"""
        if not self.enabled:
            return None
        
        query_lower = query.lower()
        for key, value in self.knowledge_base.items():
            if query_lower in value.get('content', '').lower():
                return value
        return None
    
    def get_instant_answer(self, query: str, category: str) -> Optional[str]:
        """Get instant answer from knowledge base"""
        if not self.enabled:
            return None
        
        for entry in self.knowledge_base.values():
            if entry.get('category') == category:
                if query.lower() in entry.get('content', '').lower():
                    return entry.get('content')[:200]
        
        return None
    
    def is_enabled(self) -> bool:
        """Check if LOKI is enabled"""
        return self.enabled
    
    def save_kb(self):
        """Save knowledge base to disk"""
        if not self.enabled:
            return False
        
        try:
            kb_file = self.data_path / 'knowledge_base.json'
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving LOKI: {e}")
            return False
