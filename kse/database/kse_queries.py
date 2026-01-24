"""
KSE Database Query Repository

Common database queries and operations for the search engine.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

from .kse_database_init import KSEDatabase
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class KSEQueries:
    """Repository for common database queries."""
    
    def __init__(self, db: KSEDatabase):
        """
        Initialize query repository.
        
        Args:
            db: KSEDatabase instance
        """
        self.db = db
    
    # ========================================================================
    # DOMAIN QUERIES
    # ========================================================================
    
    def get_pending_domains(self, limit: int = 100) -> List[Dict]:
        """
        Get pending domains for crawling.
        
        Args:
            limit: Maximum number of domains
            
        Returns:
            List of domain dictionaries
        """
        results = self.db.fetch_all(
            """
            SELECT id, url, domain_name, trust_score, error_count
            FROM domains
            WHERE status = 'pending' OR (status = 'active' AND next_crawl < NOW())
            ORDER BY trust_score DESC, error_count ASC
            LIMIT %s;
            """,
            (limit,)
        )
        return [
            {
                "id": r[0],
                "url": r[1],
                "domain_name": r[2],
                "trust_score": r[3],
                "error_count": r[4],
            }
            for r in results
        ]
    
    def update_domain_crawl_time(self, domain_id: int, status: str = "active") -> bool:
        """
        Update domain crawl timestamp.
        
        Args:
            domain_id: Domain ID
            status: New status
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                UPDATE domains
                SET last_crawled = NOW(),
                    next_crawl = NOW() + INTERVAL '24 hours',
                    status = %s,
                    error_count = 0
                WHERE id = %s;
                """,
                (status, domain_id)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update domain crawl time: {e}")
            return False
    
    def increment_domain_error_count(self, domain_id: int) -> bool:
        """
        Increment error count for domain.
        
        Args:
            domain_id: Domain ID
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                UPDATE domains
                SET error_count = error_count + 1
                WHERE id = %s;
                """,
                (domain_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to increment error count: {e}")
            return False
    
    # ========================================================================
    # PAGE QUERIES
    # ========================================================================
    
    def insert_page(
        self,
        domain_id: int,
        url: str,
        title: str,
        description: str,
        content: str,
        content_hash: str,
        status_code: int,
        content_type: str,
        size_bytes: int,
    ) -> Optional[int]:
        """
        Insert a crawled page into database.
        
        Args:
            domain_id: Domain ID
            url: Page URL
            title: Page title
            description: Meta description
            content: Page content
            content_hash: SHA256 hash of content
            status_code: HTTP status code
            content_type: Content-Type header
            size_bytes: Page size in bytes
            
        Returns:
            Page ID if successful, None otherwise
        """
        try:
            query = """
                INSERT INTO pages (
                    domain_id, url, title, description, content,
                    content_hash, status_code, crawl_time, content_type, size_bytes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    content = EXCLUDED.content,
                    content_hash = EXCLUDED.content_hash,
                    status_code = EXCLUDED.status_code,
                    crawl_time = NOW()
                RETURNING id;
            """
            
            result = self.db.fetch_one(
                query,
                (
                    domain_id,
                    url,
                    title,
                    description,
                    content,
                    content_hash,
                    status_code,
                    content_type,
                    size_bytes,
                )
            )
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to insert page: {e}")
            return None
    
    def get_unindexed_pages(self, limit: int = 100) -> List[Dict]:
        """
        Get pages waiting to be indexed.
        
        Args:
            limit: Maximum number of pages
            
        Returns:
            List of page dictionaries
        """
        results = self.db.fetch_all(
            """
            SELECT id, url, title, content
            FROM pages
            WHERE indexed = false AND status_code = 200
            ORDER BY crawl_time DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return [
            {
                "id": r[0],
                "url": r[1],
                "title": r[2],
                "content": r[3],
            }
            for r in results
        ]
    
    def mark_page_indexed(self, page_id: int) -> bool:
        """
        Mark page as indexed.
        
        Args:
            page_id: Page ID
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                "UPDATE pages SET indexed = true WHERE id = %s;",
                (page_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark page indexed: {e}")
            return False
    
    # ========================================================================
    # TERM/INDEX QUERIES
    # ========================================================================
    
    def insert_or_get_term(self, term: str, language: str = "sv") -> Optional[int]:
        """
        Insert term if not exists, return term ID.
        
        Args:
            term: Search term
            language: Language code
            
        Returns:
            Term ID if successful, None otherwise
        """
        try:
            result = self.db.fetch_one(
                "SELECT id FROM terms WHERE term = %s AND language = %s;",
                (term, language)
            )
            
            if result:
                return result[0]
            
            result = self.db.fetch_one(
                """
                INSERT INTO terms (term, language, frequency)
                VALUES (%s, %s, 1)
                RETURNING id;
                """,
                (term, language)
            )
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to insert term: {e}")
            return None
    
    def insert_inverted_index(
        self,
        term_id: int,
        page_id: int,
        position: int,
        field: str = "content",
        tf_idf_score: float = 0.0,
    ) -> bool:
        """
        Insert entry into inverted index.
        
        Args:
            term_id: Term ID
            page_id: Page ID
            position: Word position in page
            field: Field name (title, description, content)
            tf_idf_score: Precomputed TF-IDF score
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                INSERT INTO inverted_index (term_id, page_id, position, field, tf_idf_score, frequency)
                VALUES (%s, %s, %s, %s, %s, 1)
                ON CONFLICT DO NOTHING;
                """,
                (term_id, page_id, position, field, tf_idf_score)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert inverted index: {e}")
            return False
    
    def search_inverted_index(self, term_id: int, limit: int = 100) -> List[Dict]:
        """
        Search inverted index for pages containing term.
        
        Args:
            term_id: Term ID
            limit: Maximum results
            
        Returns:
            List of search result dictionaries
        """
        results = self.db.fetch_all(
            """
            SELECT ii.page_id, p.url, p.title, ii.tf_idf_score
            FROM inverted_index ii
            JOIN pages p ON ii.page_id = p.id
            WHERE ii.term_id = %s
            ORDER BY ii.tf_idf_score DESC
            LIMIT %s;
            """,
            (term_id, limit)
        )
        return [
            {
                "page_id": r[0],
                "url": r[1],
                "title": r[2],
                "score": r[3],
            }
            for r in results
        ]
    
    # ========================================================================
    # LINK QUERIES
    # ========================================================================
    
    def insert_link(
        self,
        source_page_id: int,
        target_page_id: Optional[int],
        target_url: str,
        anchor_text: Optional[str],
        link_type: str = "internal",
    ) -> bool:
        """
        Insert link into database.
        
        Args:
            source_page_id: Source page ID
            target_page_id: Target page ID (if found)
            target_url: Target URL
            anchor_text: Link anchor text
            link_type: Type of link (internal, external, broken)
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                INSERT INTO links (
                    source_page_id, target_page_id, target_url, anchor_text, link_type
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (source_page_id, target_page_id, target_url, anchor_text, link_type)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert link: {e}")
            return False
    
    # ========================================================================
    # CRAWL QUEUE QUERIES
    # ========================================================================
    
    def add_to_crawl_queue(
        self,
        url: str,
        domain_id: Optional[int] = None,
        priority: int = 5,
    ) -> bool:
        """
        Add URL to crawl queue.
        
        Args:
            url: URL to crawl
            domain_id: Domain ID
            priority: Crawl priority (1-10)
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                INSERT INTO crawl_queue (url, domain_id, priority, status)
                VALUES (%s, %s, %s, 'pending')
                ON CONFLICT (url) DO NOTHING;
                """,
                (url, domain_id, priority)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add to crawl queue: {e}")
            return False
    
    def get_next_url_to_crawl(self) -> Optional[Dict]:
        """
        Get next URL from crawl queue.
        
        Returns:
            URL dictionary or None
        """
        result = self.db.fetch_one(
            """
            SELECT id, url, domain_id, priority
            FROM crawl_queue
            WHERE status = 'pending'
            ORDER BY priority DESC, added_at ASC
            LIMIT 1;
            """
        )
        
        if result:
            return {
                "id": result[0],
                "url": result[1],
                "domain_id": result[2],
                "priority": result[3],
            }
        return None
    
    def mark_url_crawled(self, queue_id: int, success: bool = True) -> bool:
        """
        Mark URL as crawled.
        
        Args:
            queue_id: Crawl queue ID
            success: Whether crawl was successful
            
        Returns:
            True if successful
        """
        try:
            status = "done" if success else "failed"
            self.db.execute(
                """
                UPDATE crawl_queue
                SET status = %s, processed_at = NOW()
                WHERE id = %s;
                """,
                (status, queue_id)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark URL crawled: {e}")
            return False
    
    # ========================================================================
    # STATISTICS QUERIES
    # ========================================================================
    
    def log_crawl_event(
        self,
        event_type: str,
        domain_id: Optional[int] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Log a crawl event.
        
        Args:
            event_type: Type of event
            domain_id: Domain ID
            url: URL
            status_code: HTTP status code
            duration_ms: Duration in milliseconds
            message: Log message
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                """
                INSERT INTO crawl_logs (
                    domain_id, url, event_type, status_code, duration_ms, message
                )
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (domain_id, url, event_type, status_code, duration_ms, message)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to log crawl event: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {}
        try:
            stats["total_domains"] = self.db.fetch_one("SELECT COUNT(*) FROM domains;")[0]
            stats["total_pages"] = self.db.fetch_one("SELECT COUNT(*) FROM pages;")[0]
            stats["indexed_pages"] = self.db.fetch_one("SELECT COUNT(*) FROM pages WHERE indexed = true;")[0]
            stats["total_terms"] = self.db.fetch_one("SELECT COUNT(*) FROM terms;")[0]
            stats["pending_crawls"] = self.db.fetch_one(
                "SELECT COUNT(*) FROM crawl_queue WHERE status = 'pending';"
            )[0]
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
        
        return stats
