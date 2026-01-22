#!/usr/bin/env python3
"""
SBDB Index - Inverted Index Management and Search
Production-ready indexing and search operations
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class InvertedIndex:
    """Fast inverted index for full-text search"""
    
    def __init__(self, index_file: Path, pages_file: Path):
        self.index_file = index_file
        self.pages_file = pages_file
        
        # In-memory index: word -> [page_id, page_id, ...]
        self.index: Dict[str, List[int]] = {}
        
        # Document frequency cache: word -> count of documents containing it
        self.df_cache: Dict[str, int] = {}
        
        # Total document count
        self.total_docs = 0
        
        # Pages cache: page_id -> page_data
        self.pages: Dict[int, Dict] = {}
    
    def load(self) -> bool:
        """Load index and pages from disk into memory"""
        try:
            # Load index
            if self.index_file.exists():
                index_data = json.loads(self.index_file.read_text(encoding='utf-8'))
                # Convert string keys back to strings, but values stay as lists
                self.index = {word: page_ids for word, page_ids in index_data.items()}
                logger.info(f"✓ Loaded index with {len(self.index)} unique terms")
            
            # Load pages
            if self.pages_file.exists():
                pages_list = json.loads(self.pages_file.read_text(encoding='utf-8'))
                self.pages = {i: page for i, page in enumerate(pages_list)}
                self.total_docs = len(self.pages)
                logger.info(f"✓ Loaded {self.total_docs} pages")
            
            # Rebuild DF cache
            self._rebuild_df_cache()
            
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to load index: {e}")
            return False
    
    def _rebuild_df_cache(self):
        """Rebuild document frequency cache from index"""
        self.df_cache = {word: len(page_ids) for word, page_ids in self.index.items()}
        logger.debug(f"DF cache rebuilt with {len(self.df_cache)} terms")
    
    def add_page(self, page_id: int, page_data: Dict, tokens: List[str]):
        """Add or update a page in the index"""
        # Store page data
        self.pages[page_id] = page_data
        self.total_docs = len(self.pages)
        
        # Remove old entries for this page
        for word_list in self.index.values():
            if page_id in word_list:
                word_list.remove(page_id)
        
        # Add new entries
        seen_tokens = set()
        for token in tokens:
            if token not in seen_tokens:  # Count each term only once per doc
                if token not in self.index:
                    self.index[token] = []
                if page_id not in self.index[token]:
                    self.index[token].append(page_id)
                seen_tokens.add(token)
        
        # Update DF cache
        self._rebuild_df_cache()
    
    def remove_page(self, page_id: int):
        """Remove a page from the index"""
        if page_id in self.pages:
            del self.pages[page_id]
        
        # Remove from all postings
        for word_list in self.index.values():
            if page_id in word_list:
                word_list.remove(page_id)
        
        self.total_docs = len(self.pages)
        self._rebuild_df_cache()
    
    def search(self, query_tokens: List[str], top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for query tokens and return ranked results.
        Returns: [(page_id, relevance_score), ...]
        """
        if not query_tokens:
            return []
        
        # Find candidate pages (intersection of all query term postings)
        candidates = None
        
        for token in query_tokens:
            if token in self.index:
                posting = set(self.index[token])
                if candidates is None:
                    candidates = posting
                else:
                    candidates &= posting  # Intersection
        
        if candidates is None:
            candidates = set()
        
        # Score candidates
        scored_results = []
        for page_id in candidates:
            score = self._calculate_relevance(page_id, query_tokens)
            scored_results.append((page_id, score))
        
        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        return scored_results[:top_k]
    
    def _calculate_relevance(self, page_id: int, query_tokens: List[str]) -> float:
        """Calculate relevance score for a page given query tokens"""
        if page_id not in self.pages:
            return 0.0
        
        page = self.pages[page_id]
        page_tokens = page.get('tokens', [])
        
        score = 0.0
        for token in query_tokens:
            # TF-IDF
            tf = page_tokens.count(token) / len(page_tokens) if page_tokens else 0
            df = self.df_cache.get(token, 0)
            idf = math.log(self.total_docs / (df + 1)) if self.total_docs > 0 else 0
            tfidf = tf * idf
            
            # Title boost
            if token in page.get('title', '').lower().split():
                tfidf *= 2.0
            
            score += tfidf
        
        # Trust score boost
        trust_boost = 1.0 + (page.get('trust_score', 0.5) * 0.5)
        score *= trust_boost
        
        return score
    
    def save(self) -> bool:
        """Save index and pages to disk"""
        try:
            # Save index
            index_data = {word: page_ids for word, page_ids in self.index.items()}
            self.index_file.write_text(json.dumps(index_data, indent=2), encoding='utf-8')
            
            # Save pages
            pages_list = [self.pages[i] for i in sorted(self.pages.keys())]
            self.pages_file.write_text(json.dumps(pages_list, indent=2, ensure_ascii=False), encoding='utf-8')
            
            logger.info(f"✓ Saved index ({len(self.index)} terms) and pages ({len(self.pages)} docs)")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to save index: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get current index statistics"""
        index_size_bytes = sum(len(self.index_file.read_bytes()))
        
        return {
            'unique_terms': len(self.index),
            'total_pages': self.total_docs,
            'index_size_mb': round(index_size_bytes / (1024 * 1024), 2),
            'avg_terms_per_page': round(sum(len(page.get('tokens', [])) for page in self.pages.values()) / max(self.total_docs, 1)),
        }
    
    def get_index_info(self) -> Dict:
        """Get detailed index information"""
        return {
            'total_terms': len(self.index),
            'total_documents': self.total_docs,
            'avg_posting_list_length': round(sum(len(v) for v in self.index.values()) / max(len(self.index), 1), 2) if self.index else 0,
            'max_posting_list_length': max((len(v) for v in self.index.values()), default=0),
        }


class SearchEngine:
    """High-level search engine combining index, NLP, and ranking"""
    
    def __init__(self, inverted_index: InvertedIndex, nlp, ranking_engine):
        self.index = inverted_index
        self.nlp = nlp
        self.ranking = ranking_engine
        self.logger = logging.getLogger(__name__)
    
    def search(self, query: str, top_k: int = 10, query_region: Optional[str] = None) -> List[Dict]:
        """
        Execute a search query and return formatted results.
        
        Args:
            query: User's search query
            top_k: Number of results to return
            query_region: Optional region filter (e.g., 'Stockholm')
        
        Returns:
            List of result dictionaries with metadata
        """
        # Process query through NLP
        query_tokens, entities = self.nlp.process_text(query)
        
        if not query_tokens:
            return []
        
        # Search index
        ranked_results = self.index.search(query_tokens, top_k * 2)  # Get extra for reranking
        
        # Format results
        formatted_results = []
        for page_id, score in ranked_results:
            if page_id not in self.index.pages:
                continue
            
            page = self.index.pages[page_id]
            
            # Create result object
            result = {
                'page_id': page_id,
                'title': page.get('title', 'Untitled'),
                'url': page.get('url', ''),
                'snippet': self._generate_snippet(page, query_tokens),
                'trust_score': page.get('trust_score', 0.5),
                'region': page.get('region', 'Unknown'),
                'domain': page.get('domain', 'unknown.se'),
                'crawl_date': page.get('crawl_date'),
                'tfidf_score': score,
                'in_title': any(token in page.get('title', '').lower().split() for token in query_tokens),
            }
            
            formatted_results.append(result)
        
        # Apply final ranking with regional boost
        if entities.get('cities'):
            query_region = entities['cities'][0]
        
        final_ranked = self.ranking.rank_results(formatted_results, query_tokens, query_region)
        
        return final_ranked[:top_k]
    
    def _generate_snippet(self, page: Dict, query_tokens: List[str], snippet_length: int = 150) -> str:
        """
        Generate a search result snippet with query terms highlighted.
        """
        text = page.get('text', '')[:500]  # Use first 500 chars
        
        # Simple snippet: find first occurrence of query term and extract surrounding context
        text_lower = text.lower()
        for token in query_tokens:
            idx = text_lower.find(token)
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(text), idx + snippet_length)
                snippet = text[start:end].strip()
                if start > 0:
                    snippet = '...' + snippet
                if end < len(text):
                    snippet = snippet + '...'
                return snippet
        
        # Fallback: first snippet_length characters
        return text[:snippet_length].strip() + ('...' if len(text) > snippet_length else '')


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    index_file = Path('test_index.json')
    pages_file = Path('test_pages.json')
    
    idx = InvertedIndex(index_file, pages_file)
    
    # Add test pages
    idx.add_page(0, {'title': 'Best Restaurants in Stockholm', 'url': 'example.com/1'}, ['best', 'restaurants', 'stockholm'])
    idx.add_page(1, {'title': 'Göteborg Food Guide', 'url': 'example.com/2'}, ['goteborg', 'food', 'guide'])
    
    # Search
    results = idx.search(['restaurants', 'stockholm'])
    print(f"Found {len(results)} results")
    
    # Save
    idx.save()
