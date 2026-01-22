"""
Klar SBDB Index - Inverted Index Management
Handles building, searching, and updating the inverted index
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


class InvertedIndex:
    """
    Inverted Index for fast full-text search
    Structure: word → [page_id_1, page_id_2, page_id_3, ...]
    """
    
    def __init__(self, data_dir: str = "klar_sbdb_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.index: Dict[str, List[int]] = {}  # word → [page_ids]
        self.pages: Dict[int, Dict] = {}  # page_id → page_data
        self.word_to_tf: Dict[str, Dict[int, float]] = {}  # word → {page_id: tf}
        self.page_to_words: Dict[int, Set[str]] = {}  # page_id → {words}
        
        self.index_file = self.data_dir / "index.json"
        self.pages_file = self.data_dir / "pages.json"
        self.stats_file = self.data_dir / "stats.json"
        
        logger.info(f"InvertedIndex initialized with data_dir={data_dir}")
    
    def add_page(self, page_id: int, page_data: Dict) -> None:
        """
        Add a page to the index
        
        Args:
            page_id: Unique page identifier
            page_data: Dictionary with 'tokens', 'url', 'title', 'metadata'
        """
        tokens = page_data.get('tokens', [])
        self.pages[page_id] = page_data
        self.page_to_words[page_id] = set(tokens)
        
        # Calculate term frequency for each token
        total_tokens = len(tokens)
        word_counts = defaultdict(int)
        
        for token in tokens:
            word_counts[token] += 1
        
        # Add to inverted index
        for word, count in word_counts.items():
            if word not in self.index:
                self.index[word] = []
                self.word_to_tf[word] = {}
            
            self.index[word].append(page_id)
            
            # Calculate TF (term frequency)
            tf = count / total_tokens if total_tokens > 0 else 0
            self.word_to_tf[word][page_id] = tf
    
    def search(self, query_tokens: List[str], top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search using inverted index
        Returns top K results ranked by relevance
        
        Args:
            query_tokens: Processed query tokens
            top_k: Number of results to return
            
        Returns:
            List of (page_id, relevance_score) tuples
        """
        if not query_tokens:
            return []
        
        # Find pages that contain ANY query token
        matching_pages: Dict[int, float] = defaultdict(float)
        
        for token in query_tokens:
            if token in self.index:
                # Calculate IDF for this token
                idf = self._calculate_idf(token)
                
                # Add score to all pages containing this token
                for page_id in self.index[token]:
                    tf = self.word_to_tf[token].get(page_id, 0)
                    tf_idf = tf * idf
                    matching_pages[page_id] += tf_idf
        
        # Boost score based on metadata
        for page_id, score in matching_pages.items():
            page_data = self.pages.get(page_id, {})
            metadata = page_data.get('metadata', {})
            trust_score = metadata.get('trust_score', 0.5)
            
            # Apply trust multiplier
            matching_pages[page_id] = score * (1 + trust_score)
        
        # Sort by score (descending)
        ranked_results = sorted(
            matching_pages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top K
        return ranked_results[:top_k]
    
    def _calculate_idf(self, word: str) -> float:
        """
        Calculate Inverse Document Frequency
        IDF = log(total_pages / pages_with_word)
        
        Args:
            word: Word to calculate IDF for
            
        Returns:
            IDF score
        """
        if word not in self.index:
            return 0.0
        
        total_pages = len(self.pages)
        pages_with_word = len(self.index[word])
        
        if pages_with_word == 0 or total_pages == 0:
            return 0.0
        
        idf = math.log(total_pages / pages_with_word)
        return idf
    
    def get_page(self, page_id: int) -> Dict:
        """
        Get page data by ID
        
        Args:
            page_id: Page identifier
            
        Returns:
            Page data dictionary
        """
        return self.pages.get(page_id, {})
    
    def get_stats(self) -> Dict:
        """
        Get index statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'unique_words': len(self.index),
            'total_pages': len(self.pages),
            'index_size_bytes': self._estimate_size(),
            'timestamp': time.time()
        }
    
    def _estimate_size(self) -> int:
        """
        Estimate index size in bytes
        """
        size = 0
        for word, pages in self.index.items():
            size += len(word) + (len(pages) * 4)  # word + page_id pointers
        return size
    
    def save(self) -> None:
        """
        Save index to disk (JSON format)
        """
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
        """
        Load index from disk
        
        Returns:
            True if loaded successfully
        """
        if not self.index_file.exists():
            logger.warning(f"Index file not found: {self.index_file}")
            return False
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            self.index = index_data.get('index', {})
            
            # Convert string keys back to int for pages dict
            pages_data = index_data.get('pages', {})
            self.pages = {int(k): v for k, v in pages_data.items()}
            
            # Rebuild word_to_tf and page_to_words
            self._rebuild_metadata()
            
            logger.info(f"Index loaded from {self.index_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def _rebuild_metadata(self) -> None:
        """
        Rebuild internal metadata (word_to_tf, page_to_words)
        """
        self.word_to_tf = defaultdict(dict)
        self.page_to_words = defaultdict(set)
        
        for word, page_ids in self.index.items():
            for page_id in page_ids:
                # Add word to page
                self.page_to_words[page_id].add(word)
                
                # Calculate TF
                page_data = self.pages.get(page_id, {})
                tokens = page_data.get('tokens', [])
                
                if tokens:
                    count = tokens.count(word)
                    tf = count / len(tokens)
                    self.word_to_tf[word][page_id] = tf
    
    def clear(self) -> None:
        """
        Clear all index data
        """
        self.index = {}
        self.pages = {}
        self.word_to_tf = {}
        self.page_to_words = {}
        logger.info("Index cleared")


class SearchEngine:
    """
    High-level search engine combining index + ranking
    """
    
    def __init__(self, data_dir: str = "klar_sbdb_data"):
        self.index = InvertedIndex(data_dir)
        self.index.load()
    
    def search(self, query: str, processed_tokens: List[str], top_k: int = 10) -> List[Dict]:
        """
        Search and return formatted results
        
        Args:
            query: Original query string
            processed_tokens: Tokenized and processed query
            top_k: Number of results
            
        Returns:
            List of result dictionaries
        """
        start_time = time.time()
        
        # Search index
        ranked_results = self.index.search(processed_tokens, top_k)
        
        # Format results
        results = []
        for page_id, relevance_score in ranked_results:
            page_data = self.index.get_page(page_id)
            
            result = {
                'page_id': page_id,
                'url': page_data.get('url', ''),
                'title': page_data.get('title', ''),
                'snippet': self._generate_snippet(page_data.get('text', ''), processed_tokens),
                'relevance_score': round(relevance_score, 3),
                'trust_score': page_data.get('metadata', {}).get('trust_score', 0.5),
                'region': page_data.get('metadata', {}).get('regions', []),
                'domain': page_data.get('metadata', {}).get('domain', '')
            }
            results.append(result)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        return {
            'query': query,
            'results': results,
            'total_results': len(results),
            'response_time_ms': round(response_time_ms, 2)
        }
    
    def _generate_snippet(self, text: str, query_tokens: List[str], length: int = 150) -> str:
        """
        Generate snippet from text highlighting query terms
        
        Args:
            text: Full text
            query_tokens: Query tokens to highlight
            length: Snippet length
            
        Returns:
            Snippet string
        """
        # Find first occurrence of any query token
        text_lower = text.lower()
        
        start_idx = 0
        for token in query_tokens:
            idx = text_lower.find(token)
            if idx != -1:
                start_idx = max(0, idx - 50)  # Start 50 chars before
                break
        
        # Extract snippet
        snippet = text[start_idx:start_idx + length]
        
        # Add ellipsis if truncated
        if len(text) > start_idx + length:
            snippet += "..."
        
        return snippet


if __name__ == "__main__":
    # Test InvertedIndex
    idx = InvertedIndex()
    
    # Add test pages
    page1 = {
        'url': 'https://example.se/page1',
        'title': 'Stockholm Restaurants',
        'tokens': ['stockholm', 'restaurants', 'food', 'stockholm'],
        'text': 'Stockholm has great restaurants',
        'metadata': {'trust_score': 0.95, 'regions': ['stockholm']}
    }
    
    page2 = {
        'url': 'https://example.se/page2',
        'title': 'Göteborg Food Guide',
        'tokens': ['goteborg', 'food', 'restaurants', 'guide'],
        'text': 'Göteborg is known for great food',
        'metadata': {'trust_score': 0.90, 'regions': ['goteborg']}
    }
    
    idx.add_page(1, page1)
    idx.add_page(2, page2)
    
    # Search
    results = idx.search(['stockholm', 'restaurants'], top_k=5)
    print(f"Search results: {results}")
    
    # Get stats
    stats = idx.get_stats()
    print(f"Index stats: {json.dumps(stats, indent=2)}")
    
    # Test SearchEngine
    se = SearchEngine()
    search_results = se.search(
        query="Stockholm restaurants",
        processed_tokens=['stockholm', 'restaurants'],
        top_k=5
    )
    print(f"\nFormatted results: {json.dumps(search_results, indent=2, ensure_ascii=False)}")
