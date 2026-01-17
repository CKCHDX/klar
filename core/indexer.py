"""
Advanced indexer with BM25 scoring
"""
import json
import math
from pathlib import Path
from typing import List, Dict
from collections import defaultdict, Counter

class Indexer:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.index_file = data_path / 'index.json'
        self.index = self._load_index()
        
        # BM25 parameters
        self.k1 = 1.5
        self.b = 0.75
        
        print(f"[Indexer] Loaded index with {len(self.index)} documents")
    
    def _load_index(self) -> Dict:
        """Load existing index"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'documents': {},
            'inverted_index': {},
            'doc_lengths': {},
            'avg_doc_length': 0,
            'total_docs': 0
        }
    
    def index_page(self, page_data: Dict):
        """Index a page"""
        url = page_data['url']
        doc_id = str(hash(url))
        
        # Combine text for indexing
        text = ' '.join([
            page_data.get('title', ''),
            page_data.get('description', ''),
            page_data.get('content', '')
        ])
        
        # Tokenize
        tokens = self._tokenize(text)
        term_freq = Counter(tokens)
        
        # Store document
        self.index['documents'][doc_id] = {
            'url': url,
            'title': page_data.get('title', ''),
            'description': page_data.get('description', ''),
            'images': page_data.get('images', []),
            'videos': page_data.get('videos', []),
            'timestamp': page_data.get('timestamp'),
            'term_freq': dict(term_freq)
        }
        
        # Update inverted index
        for term in set(tokens):
            if term not in self.index['inverted_index']:
                self.index['inverted_index'][term] = []
            if doc_id not in self.index['inverted_index'][term]:
                self.index['inverted_index'][term].append(doc_id)
        
        # Update doc length
        self.index['doc_lengths'][doc_id] = len(tokens)
        
        # Update stats
        self.index['total_docs'] = len(self.index['documents'])
        total_length = sum(self.index['doc_lengths'].values())
        self.index['avg_doc_length'] = total_length / self.index['total_docs']
        
        # Save periodically
        if self.index['total_docs'] % 10 == 0:
            self._save_index()
    
    def search(self, query: str, expanded_terms: List[str]) -> List[Dict]:
        """Search using BM25 algorithm"""
        query_terms = self._tokenize(query)
        query_terms.extend(expanded_terms)
        query_terms = list(set(query_terms))
        
        # Calculate BM25 scores
        scores = defaultdict(float)
        
        for term in query_terms:
            if term not in self.index['inverted_index']:
                continue
            
            doc_ids = self.index['inverted_index'][term]
            idf = self._calculate_idf(term)
            
            for doc_id in doc_ids:
                doc = self.index['documents'][doc_id]
                tf = doc['term_freq'].get(term, 0)
                doc_length = self.index['doc_lengths'][doc_id]
                
                score = self._bm25_score(tf, doc_length, idf)
                scores[doc_id] += score
        
        # Convert to results
        results = []
        for doc_id, score in scores.items():
            doc = self.index['documents'][doc_id]
            results.append({
                'url': doc['url'],
                'title': doc['title'],
                'description': doc['description'],
                'images': doc['images'],
                'videos': doc['videos'],
                'timestamp': doc.get('timestamp'),
                'relevance_score': score,
                'content': ''  # Not storing full content in results
            })
        
        return results
    
    def _bm25_score(self, tf: int, doc_length: int, idf: float) -> float:
        """Calculate BM25 score"""
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (
            1 - self.b + self.b * (doc_length / self.index['avg_doc_length'])
        )
        return idf * (numerator / denominator)
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate inverse document frequency"""
        N = self.index['total_docs']
        n = len(self.index['inverted_index'].get(term, []))
        
        if n == 0:
            return 0
        
        return math.log((N - n + 0.5) / (n + 0.5) + 1)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\sÃ¥Ã¤Ã¶]', ' ', text)
        tokens = [t for t in text.split() if len(t) > 2]
        return tokens
    
    def get_page_count(self) -> int:
        """Get total indexed pages"""
        return self.index['total_docs']
    
    def _save_index(self):
        """Save index to disk"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False)