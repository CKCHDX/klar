"""
Klar SBDB Index - Inverted Index Management (with Advanced Semantic Ranking)
Handles building, searching, and updating the inverted index
Now integrates AdvancedSwedishNLP + SemanticSearchEnhancer for Google-grade Swedish relevance
"""

import json
import logging
import math
from typing import List, Dict, Set, Tuple
from pathlib import Path
from collections import defaultdict
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from sbdb_core_advanced import AdvancedSwedishNLP, SemanticSearchEnhancer


class InvertedIndex:
    """Inverted Index for fast full-text search"""
    
    def __init__(self, data_dir: str = "klar_sbdb_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.index: Dict[str, List[int]] = {}  # word → [page_ids]
        self.pages: Dict[int, Dict] = {}       # page_id → page_data
        self.word_to_tf: Dict[str, Dict[int, float]] = {}  # word → {page_id: tf}
        self.page_to_words: Dict[int, Set[str]] = {}       # page_id → {words}
        
        self.index_file = self.data_dir / "index.json"
        
        logger.info(f"InvertedIndex initialized with data_dir={data_dir}")
    
    def add_page(self, page_id: int, page_data: Dict) -> None:
        tokens = page_data.get('tokens', [])
        self.pages[page_id] = page_data
        self.page_to_words[page_id] = set(tokens)
        
        total_tokens = len(tokens)
        word_counts = defaultdict(int)
        for token in tokens:
            word_counts[token] += 1
        
        for word, count in word_counts.items():
            if word not in self.index:
                self.index[word] = []
                self.word_to_tf[word] = {}
            self.index[word].append(page_id)
            tf = count / total_tokens if total_tokens > 0 else 0
            self.word_to_tf[word][page_id] = tf
    
    def search(self, query_tokens: List[str], top_k: int = 10) -> List[Tuple[int, float]]:
        if not query_tokens:
            return []
        
        matching_pages: Dict[int, float] = defaultdict(float)
        for token in query_tokens:
            if token in self.index:
                idf = self._calculate_idf(token)
                for page_id in self.index[token]:
                    tf = self.word_to_tf[token].get(page_id, 0)
                    tf_idf = tf * idf
                    matching_pages[page_id] += tf_idf
        
        # Trust score boost
        for page_id, score in matching_pages.items():
            page_data = self.pages.get(page_id, {})
            metadata = page_data.get('metadata', {})
            trust_score = metadata.get('trust_score', 0.5)
            matching_pages[page_id] = score * (1 + trust_score)
        
        ranked_results = sorted(matching_pages.items(), key=lambda x: x[1], reverse=True)
        return ranked_results[:top_k]
    
    def _calculate_idf(self, word: str) -> float:
        if word not in self.index:
            return 0.0
        total_pages = len(self.pages)
        pages_with_word = len(self.index[word])
        if pages_with_word == 0 or total_pages == 0:
            return 0.0
        return math.log(total_pages / pages_with_word)
    
    def get_page(self, page_id: int) -> Dict:
        return self.pages.get(page_id, {})
    
    def get_stats(self) -> Dict:
        return {
            'unique_words': len(self.index),
            'total_pages': len(self.pages),
            'index_size_bytes': self._estimate_size(),
            'timestamp': time.time()
        }
    
    def _estimate_size(self) -> int:
        size = 0
        for word, pages in self.index.items():
            size += len(word) + (len(pages) * 4)
        return size
    
    def save(self) -> None:
        index_data = {
            'index': {k: v for k, v in self.index.items()},
            'pages': {str(k): v for k, v in self.pages.items()},
            'stats': self.get_stats()
        }
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Index saved to {self.index_file}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load(self) -> bool:
        if not self.index_file.exists():
            logger.warning(f"Index file not found: {self.index_file}")
            return False
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            self.index = index_data.get('index', {})
            pages_data = index_data.get('pages', {})
            self.pages = {int(k): v for k, v in pages_data.items()}
            self._rebuild_metadata()
            logger.info(f"Index loaded from {self.index_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def _rebuild_metadata(self) -> None:
        self.word_to_tf = defaultdict(dict)
        self.page_to_words = defaultdict(set)
        for word, page_ids in self.index.items():
            for page_id in page_ids:
                self.page_to_words[page_id].add(word)
                page_data = self.pages.get(page_id, {})
                tokens = page_data.get('tokens', [])
                if tokens:
                    count = tokens.count(word)
                    tf = count / len(tokens)
                    self.word_to_tf[word][page_id] = tf
    
    def clear(self) -> None:
        self.index = {}
        self.pages = {}
        self.word_to_tf = {}
        self.page_to_words = {}
        logger.info("Index cleared")


class SearchEngine:
    """High-level search engine combining index + advanced semantic ranking"""
    
    def __init__(self, data_dir: str = "klar_sbdb_data"):
        self.index = InvertedIndex(data_dir)
        self.index.load()
        self.advanced_nlp = AdvancedSwedishNLP()
        self.semantic_enhancer = SemanticSearchEnhancer()
    
    def search(self, query: str, processed_tokens: List[str], top_k: int = 10) -> Dict:
        start_time = time.time()
        
        # Base search (TF-IDF + trust)
        ranked_results = self.index.search(processed_tokens, top_k * 3)
        
        results = []
        advanced_query_tokens = self.advanced_nlp.tokenize_advanced(query)
        
        for page_id, base_score in ranked_results:
            page_data = self.index.get_page(page_id)
            result = {
                'page_id': page_id,
                'url': page_data.get('url', ''),
                'title': page_data.get('title', ''),
                'text': page_data.get('text', ''),
                'snippet': self._generate_snippet(page_data.get('text', ''), processed_tokens),
                'base_score': round(base_score, 4),
                'trust_score': page_data.get('metadata', {}).get('trust_score', 0.5),
                'region': page_data.get('metadata', {}).get('regions', []),
                'domain': page_data.get('metadata', {}).get('domain', '')
            }
            # Enrich with advanced semantics
            enriched = self.semantic_enhancer.enrich_search_result(result, advanced_query_tokens)
            results.append(enriched)
        
        # Re-rank by enriched_score (fallback to base_score)
        results.sort(key=lambda r: r.get('enriched_score', r.get('base_score', 0.0)), reverse=True)
        results = results[:top_k]
        
        response_time_ms = (time.time() - start_time) * 1000
        
        return {
            'query': query,
            'results': [
                {
                    'page_id': r['page_id'],
                    'url': r['url'],
                    'title': r['title'],
                    'snippet': r['snippet'],
                    'relevance_score': round(r.get('enriched_score', r['base_score']), 3),
                    'base_score': r['base_score'],
                    'trust_score': r['trust_score'],
                    'region': r['region'],
                    'domain': r['domain'],
                    'semantic_similarity': round(r.get('semantic_similarity', 0.0), 3),
                    'entities': r.get('entities', {}),
                }
                for r in results
            ],
            'total_results': len(results),
            'response_time_ms': round(response_time_ms, 2)
        }
    
    def _generate_snippet(self, text: str, query_tokens: List[str], length: int = 150) -> str:
        text_lower = text.lower()
        start_idx = 0
        for token in query_tokens:
            idx = text_lower.find(token)
            if idx != -1:
                start_idx = max(0, idx - 50)
                break
        snippet = text[start_idx:start_idx + length]
        if len(text) > start_idx + length:
            snippet += "..."
        return snippet


if __name__ == "__main__":
    idx = InvertedIndex()
    page1 = {
        'url': 'https://example.se/page1',
        'title': 'Stockholm Restaurants',
        'tokens': ['stockholm', 'restauranger', 'mat', 'stockholm'],
        'text': 'Stockholm har många fantastiska restauranger med god mat.',
        'metadata': {'trust_score': 0.95, 'regions': ['stockholm'], 'domain': 'example.se'}
    }
    page2 = {
        'url': 'https://example.se/page2',
        'title': 'Göteborg Food Guide',
        'tokens': ['göteborg', 'mat', 'restauranger', 'guide'],
        'text': 'Göteborg är känt för bra mat och restauranger.',
        'metadata': {'trust_score': 0.90, 'regions': ['göteborg'], 'domain': 'example.se'}
    }
    idx.add_page(1, page1)
    idx.add_page(2, page2)
    se = SearchEngine()
    se.index = idx
    query = "Stockholm restauranger"
    processed = ['stockholm', 'restauranger']
    res = se.search(query=query, processed_tokens=processed, top_k=5)
    print(json.dumps(res, indent=2, ensure_ascii=False))
