"""
KSE Search Engine

Full-text search engine with query processing and result ranking.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from kse.core import KSELogger
from .kse_indexer import KSEIndexer
from .kse_tokenizer import Tokenizer
from .kse_ranker import TFIDFRanker, HybridRanker

logger = KSELogger.get_logger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    page_id: int
    url: str
    title: str
    description: str
    score: float
    matched_terms: List[str]
    rank: int = 0  # Position in results
    
    def __repr__(self):
        return f"Result(id={self.page_id}, title='{self.title[:50]}...', score={self.score:.4f})"


class SearchEngine:
    """Full-text search engine."""
    
    def __init__(self, db_connection, use_hybrid_ranking: bool = True):
        """
        Initialize search engine.
        
        Args:
            db_connection: Database connection
            use_hybrid_ranking: Use hybrid ranking or just TF-IDF
        """
        self.db = db_connection
        self.indexer = KSEIndexer(db_connection)
        self.tokenizer = Tokenizer(remove_stopwords=True, use_stemming=True)
        self.use_hybrid_ranking = use_hybrid_ranking
        
        if use_hybrid_ranking:
            self.ranker = HybridRanker()
        else:
            self.ranker = TFIDFRanker()
        
        logger.info("SearchEngine initialized")
    
    def index_all_pages(self, limit: int = None) -> Dict:
        """
        Build index from all pages in database.
        
        Args:
            limit: Maximum pages to index
            
        Returns:
            Statistics dictionary
        """
        logger.info(f"Starting indexing (limit={limit})...")
        stats = self.indexer.build_from_database(limit=limit)
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def search(self, query: str, limit: int = 10, explain: bool = False) -> Tuple[List[SearchResult], Dict]:
        """
        Execute search query.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            explain: Return scoring explanation
            
        Returns:
            Tuple of (results, stats)
        """
        stats = {
            'query': query,
            'query_terms': [],
            'results_count': 0,
            'search_time_ms': 0,
            'explanation': {},
        }
        
        # Tokenize query
        query_terms = self.tokenizer.tokenize(query)
        stats['query_terms'] = query_terms
        
        if not query_terms:
            logger.warning(f"Query produced no terms: '{query}'")
            return [], stats
        
        # Score documents
        doc_scores: Dict[int, float] = {}
        term_hits: Dict[int, List[str]] = {}  # Track which terms matched
        
        for term in query_terms:
            postings = self.indexer.get_postings(term)
            idf = self.indexer.get_idf(term)
            
            for posting in postings:
                doc_id = posting.doc_id
                term_freq = posting.term_freq
                
                # Calculate score
                if isinstance(self.ranker, HybridRanker):
                    score = self.ranker.rank(doc_id, term_freq, idf)
                else:
                    score = self.ranker.rank(doc_id, term, term_freq, idf)
                
                doc_scores[doc_id] = doc_scores.get(doc_id, 0) + score
                
                if doc_id not in term_hits:
                    term_hits[doc_id] = []
                if term not in term_hits[doc_id]:
                    term_hits[doc_id].append(term)
        
        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Fetch page data and build results
        results = []
        for rank, (doc_id, score) in enumerate(sorted_docs[:limit], 1):
            try:
                page_data = self._fetch_page(doc_id)
                if page_data:
                    result = SearchResult(
                        page_id=doc_id,
                        url=page_data['url'],
                        title=page_data['title'],
                        description=page_data['description'],
                        score=score,
                        matched_terms=term_hits.get(doc_id, []),
                        rank=rank,
                    )
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching page {doc_id}: {e}")
                continue
        
        stats['results_count'] = len(results)
        
        if explain and results:
            stats['explanation'] = self._explain_results(results[:3], query_terms)
        
        return results, stats
    
    def search_phrase(self, phrase: str, limit: int = 10) -> Tuple[List[SearchResult], Dict]:
        """
        Search for exact phrase.
        
        Args:
            phrase: Exact phrase to search
            limit: Maximum results
            
        Returns:
            Tuple of (results, stats)
        """
        # For now, treat as regular search
        # TODO: Implement true phrase search using positions
        return self.search(phrase, limit)
    
    def search_with_filters(self,
                           query: str,
                           domain: str = None,
                           min_score: float = 0.0,
                           limit: int = 10) -> Tuple[List[SearchResult], Dict]:
        """
        Search with filters.
        
        Args:
            query: Search query
            domain: Filter by domain
            min_score: Minimum relevance score
            limit: Maximum results
            
        Returns:
            Tuple of (results, stats)
        """
        results, stats = self.search(query, limit=limit*2)  # Get more for filtering
        
        # Apply filters
        filtered = []
        for result in results:
            if result.score < min_score:
                continue
            
            if domain and domain not in result.url:
                continue
            
            filtered.append(result)
        
        # Rerank and limit
        filtered = filtered[:limit]
        for i, result in enumerate(filtered, 1):
            result.rank = i
        
        stats['filters'] = {
            'domain': domain,
            'min_score': min_score,
            'pre_filter_count': len(results),
            'post_filter_count': len(filtered),
        }
        
        return filtered, stats
    
    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions starting with prefix.
        
        Args:
            prefix: Prefix to search
            limit: Maximum suggestions
            
        Returns:
            List of suggested terms
        """
        prefix_lower = prefix.lower()
        suggestions = []
        
        for term in self.indexer.inverted_index.keys():
            if term.startswith(prefix_lower):
                suggestions.append(term)
        
        # Sort by document frequency (most common first)
        suggestions.sort(
            key=lambda t: self.indexer.inverted_index[t].document_frequency,
            reverse=True
        )
        
        return suggestions[:limit]
    
    def get_statistics(self) -> Dict:
        """
        Get search engine statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.indexer.get_statistics()
    
    def _fetch_page(self, page_id: int) -> Optional[Dict]:
        """
        Fetch page data from database.
        
        Args:
            page_id: Page ID
            
        Returns:
            Page data or None
        """
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                "SELECT url, title, description FROM pages WHERE id = %s",
                (page_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'url': row[0],
                    'title': row[1],
                    'description': row[2],
                }
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
        
        return None
    
    def _explain_results(self, results: List[SearchResult], terms: List[str]) -> Dict:
        """
        Generate explanation for top results.
        
        Args:
            results: Top search results
            terms: Query terms
            
        Returns:
            Explanation dictionary
        """
        explanation = {}
        
        for result in results:
            doc_explanation = {
                'title': result.title,
                'score': result.score,
                'matched_terms': result.matched_terms,
                'term_details': {},
            }
            
            for term in result.matched_terms:
                idf = self.indexer.get_idf(term)
                postings = self.indexer.get_postings(term)
                
                doc_explanation['term_details'][term] = {
                    'idf': idf,
                    'document_frequency': len(postings),
                }
            
            explanation[result.page_id] = doc_explanation
        
        return explanation
