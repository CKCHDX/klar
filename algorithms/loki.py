"""
LOKI 1.0 - Local Offline Knowledge Index
Instant answers for common Swedish queries
"""
import json
from pathlib import Path
from typing import Optional, Dict

class LOKI:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.knowledge_base = self._load_knowledge_base()
        print(f"[LOKI] Loaded {len(self.knowledge_base)} instant answers")
    
    def _load_knowledge_base(self) -> Dict:
        """Load pre-computed instant answers"""
        kb_file = self.data_path / 'loki_kb.json'
        
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default knowledge base
        return {
            'vÃ¤der stockholm': {
                'answer': 'FÃ¶r aktuell vÃ¤derinformation i Stockholm, besÃ¶k SMHI.se',
                'source': 'smhi.se',
                'type': 'redirect'
            },
            'nyheter': {
                'answer': 'Senaste nyheterna frÃ¥n svenska kÃ¤llor',
                'source': 'multiple',
                'type': 'aggregated'
            },
            'skatteverket kontakt': {
                'answer': 'Skatteverket: 0771-567 567 (mÃ¥n-fre 8-16:30)',
                'source': 'skatteverket.se',
                'type': 'fact'
            },
            'polisen telefon': {
                'answer': 'Polisen: NÃ¶dnummer 112, Ej brÃ¥dskande 114 14',
                'source': 'polisen.se',
                'type': 'fact'
            }
        }
    
    def get_instant_answer(self, query: str) -> Optional[Dict]:
        """Get instant answer if available"""
        query_normalized = query.lower().strip()
        
        # Exact match
        if query_normalized in self.knowledge_base:
            return self.knowledge_base[query_normalized]
        
        # Partial match
        for key, value in self.knowledge_base.items():
            if key in query_normalized or query_normalized in key:
                return value
        
        return None
    
    def add_answer(self, query: str, answer: Dict):
        """Add new instant answer to knowledge base"""
        self.knowledge_base[query.lower()] = answer
        self._save_knowledge_base()
    
    def _save_knowledge_base(self):
        """Save knowledge base to disk"""
        kb_file = self.data_path / 'loki_kb.json'
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)