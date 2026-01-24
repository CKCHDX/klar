"""
Search Index Manager

Manages keyword indexing and retrieval from database.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from kse.nlp.kse_nlp_extractor import Keyword, KeywordExtractor
from kse.nlp.kse_nlp_tfidf import TFIDFComputer, TFIDFScore
from kse.database import Repository
from kse.core import KSELogger, KSEException

logger = KSELogger.get_logger(__name__)


@dataclass
class IndexedPage:
    """Indexed page with keywords."""
    page_id: int
    domain_id: int
    url: str
    keywords: List[Keyword] = field(default_factory=list)
    keyword_count: int = 0
    indexed_at: Optional[datetime] = None
    tfidf_computed: bool = False


@dataclass
class IndexStats:
    """Indexing statistics."""
    total_pages_indexed: int = 0
    total_keywords_extracted: int = 0
    total_unique_keywords: int = 0
    avg_keywords_per_page: float = 0.0
    tfidf_documents_processed: int = 0
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0


class SearchIndexer:
    """
    Search index manager.
    
    Responsibilities:
    - Extract keywords from pages
    - Compute TF-IDF scores
    - Store in database
    - Retrieve indexed keywords
    """
    
    def __init__(
        self,
        db_repository: Repository,
        keyword_extractor: Optional[KeywordExtractor] = None,
        tfidf_computer: Optional[TFIDFComputer] = None,
    ):
        """
        Initialize search indexer.
        
        Args:
            db_repository: Database repository
            keyword_extractor: Custom keyword extractor
            tfidf_computer: Custom TF-IDF computer
        """
        self.db = db_repository
        self.extractor = keyword_extractor or KeywordExtractor(max_keywords=50)
        self.tfidf = tfidf_computer or TFIDFComputer()
        
        self.stats = IndexStats()
    
    def index_page(
        self,
        page_id: int,
        domain_id: int,
        url: str,
        text_content: str,
        title: str = "",
        description: str = "",
    ) -> Tuple[IndexedPage, bool]:
        """
        Index a single page.
        
        Args:
            page_id: Page ID from database
            domain_id: Domain ID
            url: Page URL
            text_content: Page text content
            title: Page title
            description: Meta description
        
        Returns:
            Tuple of (IndexedPage, success_flag)
        """
        try:
            # Extract keywords
            keywords, kw_stats = self.extractor.extract_from_document(
                text=text_content,
                title=title,
                description=description,
            )
            
            # Create indexed page
            indexed_page = IndexedPage(
                page_id=page_id,
                domain_id=domain_id,
                url=url,
                keywords=keywords,
                keyword_count=len(keywords),
                indexed_at=datetime.now(),
            )
            
            # Store in database
            stored = self._store_keywords(
                page_id=page_id,
                keywords=keywords,
            )
            
            if stored:
                self.stats.total_pages_indexed += 1
                self.stats.total_keywords_extracted += len(keywords)
                logger.info(f"Indexed page {page_id}: {len(keywords)} keywords")
                return indexed_page, True
            else:
                self.stats.errors.append(f"Failed to store keywords for page {page_id}")
                return indexed_page, False
        
        except Exception as e:
            error_msg = f"Error indexing page {page_id}: {e}"
            self.stats.errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            return IndexedPage(page_id, domain_id, url), False
    
    def index_domain(
        self,
        domain_id: int,
        pages: List[Dict],
    ) -> Tuple[List[IndexedPage], IndexStats]:
        """
        Index all pages in a domain.
        
        Args:
            domain_id: Domain ID
            pages: List of page dicts with url, text_content, title, description
        
        Returns:
            Tuple of (indexed_pages, statistics)
        """
        self.stats.start_time = datetime.now()
        indexed_pages = []
        
        logger.info(f"Starting indexing for domain {domain_id} ({len(pages)} pages)")
        
        for page in pages:
            indexed_page, success = self.index_page(
                page_id=page.get('id'),
                domain_id=domain_id,
                url=page.get('url', ''),
                text_content=page.get('text_content', ''),
                title=page.get('title', ''),
                description=page.get('description', ''),
            )
            
            if success:
                indexed_pages.append(indexed_page)
        
        self.stats.end_time = datetime.now()
        self.stats.duration_seconds = (
            self.stats.end_time - self.stats.start_time
        ).total_seconds()
        
        logger.info(
            f"Indexed {len(indexed_pages)} pages in {self.stats.duration_seconds:.2f}s"
        )
        
        return indexed_pages, self.stats
    
    def _store_keywords(self, page_id: int, keywords: List[Keyword]) -> bool:
        """
        Store keywords in database.
        
        Args:
            page_id: Page ID
            keywords: List of keywords
        
        Returns:
            True if successful
        """
        try:
            # Get top keywords
            top_keywords = self.extractor.get_top_keywords(keywords, count=50)
            
            # Convert to storage format
            keyword_dicts = self.extractor.keywords_to_dict(top_keywords)
            
            # Store each keyword
            for kw_dict in keyword_dicts:
                # Get or create term
                term_id = self.db.get_or_create_term(
                    term=kw_dict['term'],
                    is_phrase=kw_dict['is_phrase'],
                )
                
                if term_id:
                    # Create page-term relationship
                    self.db.add_page_term(
                        page_id=page_id,
                        term_id=term_id,
                        frequency=kw_dict['frequency'],
                        tfidf_score=kw_dict['tfidf_score'],
                        score=kw_dict['combined_score'],
                    )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to store keywords: {e}", exc_info=True)
            return False
    
    def compute_tfidf_scores(
        self,
        domain_id: int,
        pages: List[Dict],
    ) -> Dict:
        """
        Compute TF-IDF scores for all pages in domain.
        
        Args:
            domain_id: Domain ID
            pages: List of page dicts
        
        Returns:
            Statistics dictionary
        """
        logger.info(f"Computing TF-IDF for domain {domain_id} ({len(pages)} pages)")
        
        # Reset TF-IDF computer
        self.tfidf.reset()
        
        # First pass: add all documents to corpus
        for page in pages:
            text = page.get('text_content', '')
            # Simple tokenization for TF-IDF
            terms = text.lower().split()
            self.tfidf.add_document(terms)
        
        logger.info(f"Corpus created: {self.tfidf.total_documents} docs")
        
        # Second pass: compute and update scores
        for page in pages:
            page_id = page.get('id')
            text = page.get('text_content', '')
            terms = text.lower().split()
            
            # Get TF-IDF scores
            scores = self.tfidf.compute_document_scores(terms, top_n=50)
            
            # Update database with TF-IDF scores
            for score in scores:
                try:
                    self.db.update_page_term_tfidf(
                        page_id=page_id,
                        term=score.term,
                        tfidf_score=score.tfidf,
                    )
                except Exception as e:
                    logger.warning(f"Failed to update TF-IDF for {score.term}: {e}")
        
        corpus_stats = self.tfidf.compute_corpus_stats()
        
        return {
            'domain_id': domain_id,
            'pages_processed': len(pages),
            'corpus_stats': corpus_stats,
            'tfidf_scores_updated': len(pages),
        }
    
    def search_keywords(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Search for pages by keyword query.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching pages with scores
        """
        try:
            results = self.db.search_by_keyword(
                query=query,
                limit=limit,
            )
            return results
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return []
    
    def get_page_keywords(
        self,
        page_id: int,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get all keywords for a page.
        
        Args:
            page_id: Page ID
            limit: Maximum keywords
        
        Returns:
            List of keywords with scores
        """
        try:
            keywords = self.db.get_page_keywords(
                page_id=page_id,
                limit=limit,
            )
            return keywords
        except Exception as e:
            logger.error(f"Failed to get page keywords: {e}", exc_info=True)
            return []
    
    def get_domain_keywords(
        self,
        domain_id: int,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get top keywords for a domain.
        
        Args:
            domain_id: Domain ID
            limit: Maximum keywords
        
        Returns:
            List of domain keywords sorted by score
        """
        try:
            keywords = self.db.get_domain_keywords(
                domain_id=domain_id,
                limit=limit,
            )
            return keywords
        except Exception as e:
            logger.error(f"Failed to get domain keywords: {e}", exc_info=True)
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get indexing statistics.
        
        Returns:
            Statistics dictionary
        """
        stats_dict = {
            'pages_indexed': self.stats.total_pages_indexed,
            'keywords_extracted': self.stats.total_keywords_extracted,
            'avg_keywords_per_page': (
                self.stats.total_keywords_extracted / self.stats.total_pages_indexed
                if self.stats.total_pages_indexed > 0 else 0
            ),
            'duration_seconds': self.stats.duration_seconds,
            'errors': len(self.stats.errors),
        }
        
        if self.stats.errors:
            stats_dict['error_messages'] = self.stats.errors[:10]
        
        return stats_dict
