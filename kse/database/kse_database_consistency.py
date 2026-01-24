"""
Database Consistency Checker

Validates database integrity and identifies anomalies.
Used for diagnostics and repair operations.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 is required")

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """
    Validates database consistency and integrity.
    
    Checks for:
    - Orphaned records
    - Missing foreign keys
    - Data anomalies
    - Index integrity
    - Statistics accuracy
    """
    
    def __init__(self, connection):
        """Initialize consistency checker.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
        self.errors = []
        self.warnings = []
    
    def run_full_check(self) -> Dict:
        """Run complete consistency check.
        
        Returns:
            Dictionary with check results
        """
        logger.info("Starting database consistency check...")
        self.errors = []
        self.warnings = []
        
        results = {
            'timestamp': datetime.now(),
            'checks': {}
        }
        
        # Run all checks
        results['checks']['orphaned_pages'] = self._check_orphaned_pages()
        results['checks']['orphaned_terms'] = self._check_orphaned_terms()
        results['checks']['invalid_domains'] = self._check_invalid_domains()
        results['checks']['index_consistency'] = self._check_index_consistency()
        results['checks']['statistics'] = self._check_statistics()
        results['checks']['table_sizes'] = self._check_table_sizes()
        
        results['errors'] = self.errors
        results['warnings'] = self.warnings
        results['status'] = 'OK' if not self.errors else 'ISSUES_FOUND'
        
        logger.info(f"Consistency check complete. Status: {results['status']}")
        
        return results
    
    def _check_orphaned_pages(self) -> Dict:
        """Check for pages referencing non-existent domains.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM kse_pages p
                WHERE NOT EXISTS (SELECT 1 FROM kse_domains d WHERE d.domain_id = p.domain_id);
            """)
            count = cursor.fetchone()[0]
            
            if count > 0:
                error_msg = f"Found {count} orphaned pages (no matching domain)"
                self.errors.append(error_msg)
                logger.error(error_msg)
            
            return {
                'status': 'PASS' if count == 0 else 'FAIL',
                'orphaned_count': count
            }
        finally:
            cursor.close()
    
    def _check_orphaned_terms(self) -> Dict:
        """Check for page-term mappings with missing references.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            # Check orphaned page references
            cursor.execute("""
                SELECT COUNT(*) FROM kse_page_terms pt
                WHERE NOT EXISTS (SELECT 1 FROM kse_pages p WHERE p.page_id = pt.page_id)
                OR NOT EXISTS (SELECT 1 FROM kse_index_terms t WHERE t.term_id = pt.term_id);
            """)
            count = cursor.fetchone()[0]
            
            if count > 0:
                error_msg = f"Found {count} orphaned page-term mappings"
                self.errors.append(error_msg)
                logger.error(error_msg)
            
            return {
                'status': 'PASS' if count == 0 else 'FAIL',
                'orphaned_count': count
            }
        finally:
            cursor.close()
    
    def _check_invalid_domains(self) -> Dict:
        """Check for invalid domain configurations.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            issues = []
            
            # Check domains with empty URLs
            cursor.execute("SELECT COUNT(*) FROM kse_domains WHERE domain_url IS NULL OR domain_url = '';")
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append(f"Found {count} domains with empty URL")
            
            # Check domains with invalid trust scores
            cursor.execute("SELECT COUNT(*) FROM kse_domains WHERE trust_score < 0 OR trust_score > 1;")
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append(f"Found {count} domains with invalid trust score (not 0-1)")
            
            # Check active domains with zero page count and old crawl date
            cursor.execute("""
                SELECT COUNT(*) FROM kse_domains
                WHERE is_active = TRUE AND page_count = 0
                AND (last_crawled_at IS NULL OR last_crawled_at < NOW() - INTERVAL '30 days');
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append(f"Found {count} active domains with no recent crawl")
            
            for issue in issues:
                logger.warning(issue)
                self.warnings.append(issue)
            
            return {
                'status': 'PASS' if not issues else 'WARNING',
                'issues': issues
            }
        finally:
            cursor.close()
    
    def _check_index_consistency(self) -> Dict:
        """Check index consistency.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            issues = []
            
            # Check for missing indexes
            critical_indexes = [
                'idx_domains_domain_name',
                'idx_pages_domain_id',
                'idx_pages_is_indexed',
                'idx_page_terms_tf_idf',
            ]
            
            for idx_name in critical_indexes:
                cursor.execute("""
                    SELECT 1 FROM pg_indexes WHERE indexname = %s;
                """, (idx_name,))
                if not cursor.fetchone():
                    issues.append(f"Missing critical index: {idx_name}")
            
            for issue in issues:
                logger.error(issue)
                self.errors.append(issue)
            
            return {
                'status': 'PASS' if not issues else 'FAIL',
                'issues': issues
            }
        finally:
            cursor.close()
    
    def _check_statistics(self) -> Dict:
        """Check statistics accuracy.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            stats = {}
            
            # Count domains
            cursor.execute("SELECT COUNT(*) FROM kse_domains;")
            stats['total_domains'] = cursor.fetchone()[0]
            
            # Count pages
            cursor.execute("SELECT COUNT(*) FROM kse_pages;")
            stats['total_pages'] = cursor.fetchone()[0]
            
            # Count indexed pages
            cursor.execute("SELECT COUNT(*) FROM kse_pages WHERE is_indexed = TRUE;")
            stats['indexed_pages'] = cursor.fetchone()[0]
            
            # Count terms
            cursor.execute("SELECT COUNT(*) FROM kse_index_terms;")
            stats['total_terms'] = cursor.fetchone()[0]
            
            # Calculate indexing percentage
            if stats['total_pages'] > 0:
                stats['indexing_percentage'] = round(
                    (stats['indexed_pages'] / stats['total_pages']) * 100, 2
                )
            else:
                stats['indexing_percentage'] = 0.0
            
            logger.info(f"Statistics: {stats}")
            
            return {
                'status': 'OK',
                'statistics': stats
            }
        finally:
            cursor.close()
    
    def _check_table_sizes(self) -> Dict:
        """Check table sizes and growth.
        
        Returns:
            Check result dict
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables
                WHERE schemaname = 'public' AND tablename LIKE 'kse_%'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            table_sizes = {}
            total_size = 0
            
            for row in cursor.fetchall():
                table_name = row[1]
                size_str = row[2]
                size_bytes = row[3]
                table_sizes[table_name] = {
                    'size': size_str,
                    'bytes': size_bytes
                }
                total_size += size_bytes
            
            logger.info(f"Table sizes: Total {total_size / (1024**3):.2f} GB")
            
            return {
                'status': 'OK',
                'table_sizes': table_sizes,
                'total_size_gb': round(total_size / (1024**3), 2)
            }
        finally:
            cursor.close()
    
    def repair_orphaned_pages(self, confirm: bool = False) -> int:
        """Remove orphaned pages (delete pages with no domain).
        
        Args:
            confirm: Must be True to proceed
        
        Returns:
            Number of rows deleted
        """
        if not confirm:
            logger.warning("Repair not confirmed. Pass confirm=True.")
            return 0
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                DELETE FROM kse_pages
                WHERE domain_id NOT IN (SELECT domain_id FROM kse_domains);
            """)
            deleted = cursor.rowcount
            self.connection.commit()
            logger.info(f"Deleted {deleted} orphaned pages")
            return deleted
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error repairing orphaned pages: {e}")
            return 0
        finally:
            cursor.close()
    
    def repair_orphaned_terms(self, confirm: bool = False) -> int:
        """Remove orphaned term mappings.
        
        Args:
            confirm: Must be True to proceed
        
        Returns:
            Number of rows deleted
        """
        if not confirm:
            logger.warning("Repair not confirmed. Pass confirm=True.")
            return 0
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                DELETE FROM kse_page_terms
                WHERE page_id NOT IN (SELECT page_id FROM kse_pages)
                OR term_id NOT IN (SELECT term_id FROM kse_index_terms);
            """)
            deleted = cursor.rowcount
            self.connection.commit()
            logger.info(f"Deleted {deleted} orphaned term mappings")
            return deleted
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error repairing orphaned terms: {e}")
            return 0
        finally:
            cursor.close()
