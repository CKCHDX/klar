"""
Repository Pattern - Data Access Abstraction

Provides high-level data access methods for KSE.
Abstracts database operations from business logic.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 is required")

logger = logging.getLogger(__name__)


class Repository:
    """
    Data access repository for KSE.
    
    Provides clean interface for:
    - Domain operations
    - Page operations
    - Search operations
    - Statistics operations
    """
    
    def __init__(self, connection):
        """Initialize repository with database connection.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
    
    # ==================== DOMAIN OPERATIONS ====================
    
    def add_domain(self, name: str, url: str, category: str = "Other", trust: float = 0.5) -> Optional[int]:
        """Add a new domain to database.
        
        Args:
            name: Domain name
            url: Domain URL
            category: Domain category
            trust: Trust score (0-1)
        
        Returns:
            Domain ID if successful, None otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO kse_domains (domain_name, domain_url, category, trust_score)
                VALUES (%s, %s, %s, %s)
                RETURNING domain_id;
            """, (name, url, category, trust))
            domain_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return domain_id
        except psycopg2.IntegrityError:
            self.connection.rollback()
            logger.warning(f"Domain already exists: {url}")
            return None
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding domain: {e}")
            return None
    
    def get_domain(self, domain_id: int) -> Optional[Dict]:
        """Get domain by ID.
        
        Args:
            domain_id: Domain ID
        
        Returns:
            Domain dict or None
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT domain_id, domain_name, domain_url, category, trust_score, 
                   is_active, page_count, last_crawled_at
            FROM kse_domains WHERE domain_id = %s;
        """, (domain_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'category': row[3],
                'trust': row[4],
                'active': row[5],
                'page_count': row[6],
                'last_crawled': row[7]
            }
        return None
    
    def get_all_domains(self, active_only: bool = True) -> List[Dict]:
        """Get all domains.
        
        Args:
            active_only: If True, only return active domains
        
        Returns:
            List of domain dictionaries
        """
        cursor = self.connection.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT domain_id, domain_name, domain_url, category, trust_score
                FROM kse_domains WHERE is_active = TRUE ORDER BY trust_score DESC;
            """)
        else:
            cursor.execute("""
                SELECT domain_id, domain_name, domain_url, category, trust_score
                FROM kse_domains ORDER BY trust_score DESC;
            """)
        
        domains = []
        for row in cursor.fetchall():
            domains.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'category': row[3],
                'trust': row[4]
            })
        cursor.close()
        return domains
    
    def update_domain_crawl_status(self, domain_id: int, pages_crawled: int, 
                                  success: bool = True) -> bool:
        """Update domain after crawling.
        
        Args:
            domain_id: Domain ID
            pages_crawled: Number of pages crawled
            success: If True, set next crawl to 7 days from now
        
        Returns:
            bool: True if successful
        """
        try:
            cursor = self.connection.cursor()
            next_crawl = datetime.now() + timedelta(days=7 if success else hours=1)
            
            cursor.execute("""
                UPDATE kse_domains SET 
                    last_crawled_at = NOW(),
                    next_crawl_at = %s,
                    page_count = page_count + %s
                WHERE domain_id = %s;
            """, (next_crawl, pages_crawled, domain_id))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error updating domain: {e}")
            return False
    
    # ==================== PAGE OPERATIONS ====================
    
    def add_page(self, domain_id: int, url: str, title: str = None, 
                description: str = None, content_text: str = None,
                content_hash: str = None, status_code: int = 200) -> Optional[int]:
        """Add a crawled page to database.
        
        Args:
            domain_id: Domain ID
            url: Page URL
            title: Page title
            description: Page description
            content_text: Page text content
            content_hash: Hash of content (for change detection)
            status_code: HTTP status code
        
        Returns:
            Page ID if successful, None otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO kse_pages 
                (domain_id, url, title, description, content_text, 
                 content_hash, status_code, last_crawled_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING page_id;
            """, (domain_id, url, title, description, content_text, 
                  content_hash, status_code))
            
            page_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return page_id
        except psycopg2.IntegrityError:
            self.connection.rollback()
            logger.debug(f"Page already exists: {url}")
            return None
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding page: {e}")
            return None
    
    def get_pages_for_domain(self, domain_id: int, limit: int = 1000) -> List[Dict]:
        """Get all pages for a domain.
        
        Args:
            domain_id: Domain ID
            limit: Maximum pages to return
        
        Returns:
            List of page dictionaries
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT page_id, url, title, description, is_indexed, page_rank
            FROM kse_pages WHERE domain_id = %s LIMIT %s;
        """, (domain_id, limit))
        
        pages = []
        for row in cursor.fetchall():
            pages.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'description': row[3],
                'indexed': row[4],
                'rank': row[5]
            })
        cursor.close()
        return pages
    
    def get_page_count(self) -> int:
        """Get total number of pages in database.
        
        Returns:
            Number of pages
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM kse_pages;")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def get_indexed_page_count(self) -> int:
        """Get number of indexed pages.
        
        Returns:
            Number of indexed pages
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM kse_pages WHERE is_indexed = TRUE;")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    # ==================== INDEX TERM OPERATIONS ====================
    
    def add_term(self, term: str, term_type: str = "word") -> Optional[int]:
        """Add a term to the inverted index.
        
        Args:
            term: The term
            term_type: Type of term (word, entity, phrase)
        
        Returns:
            Term ID if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO kse_index_terms (term, term_type)
                VALUES (%s, %s)
                ON CONFLICT (term) DO UPDATE SET collection_frequency = collection_frequency + 1
                RETURNING term_id;
            """, (term, term_type))
            
            term_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return term_id
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding term: {e}")
            return None
    
    def add_page_term(self, page_id: int, term_id: int, tf: int = 1, 
                     tf_idf: float = 0.0, in_title: bool = False,
                     in_description: bool = False) -> bool:
        """Add term occurrence in page (for inverted index).
        
        Args:
            page_id: Page ID
            term_id: Term ID
            tf: Term frequency
            tf_idf: TF-IDF score
            in_title: True if term appears in title
            in_description: True if term appears in description
        
        Returns:
            bool: True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO kse_page_terms 
                (page_id, term_id, term_frequency, tf_idf, 
                 position_in_title, position_in_description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (page_id, term_id) DO UPDATE SET
                    term_frequency = term_frequency + 1
                RETURNING page_term_id;
            """, (page_id, term_id, tf, tf_idf, in_title, in_description))
            
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding page term: {e}")
            return False
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_statistics(self) -> Dict:
        """Get overall system statistics.
        
        Returns:
            Statistics dictionary
        """
        cursor = self.connection.cursor()
        
        # Total domains
        cursor.execute("SELECT COUNT(*) FROM kse_domains;")
        domain_count = cursor.fetchone()[0]
        
        # Active domains
        cursor.execute("SELECT COUNT(*) FROM kse_domains WHERE is_active = TRUE;")
        active_domains = cursor.fetchone()[0]
        
        # Total pages
        cursor.execute("SELECT COUNT(*) FROM kse_pages;")
        page_count = cursor.fetchone()[0]
        
        # Indexed pages
        cursor.execute("SELECT COUNT(*) FROM kse_pages WHERE is_indexed = TRUE;")
        indexed_pages = cursor.fetchone()[0]
        
        # Total terms
        cursor.execute("SELECT COUNT(*) FROM kse_index_terms;")
        term_count = cursor.fetchone()[0]
        
        cursor.close()
        
        return {
            'domains': domain_count,
            'active_domains': active_domains,
            'pages': page_count,
            'indexed_pages': indexed_pages,
            'terms': term_count,
            'indexing_percentage': round((indexed_pages / max(page_count, 1)) * 100, 2)
        }
