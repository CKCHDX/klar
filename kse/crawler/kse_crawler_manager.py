"""
KSE Crawler Manager

Orchestrates crawling: coordinates frontier, crawler, and database.
"""

from typing import Optional, Dict, List
import time
import logging
from datetime import datetime, timedelta

from kse.core import KSELogger
from kse.database.kse_database_init import KSEDatabase
from kse.database.kse_queries import KSEQueries
from .kse_crawler import KSECrawler
from .kse_url_frontier import URLFrontier

logger = KSELogger.get_logger(__name__)


class KSECrawlerManager:
    """Manages the crawling process."""
    
    def __init__(
        self,
        db: KSEDatabase,
        frontier: URLFrontier = None,
        crawler: KSECrawler = None,
    ):
        """
        Initialize crawler manager.
        
        Args:
            db: Database connection
            frontier: URL frontier (created if not provided)
            crawler: Web crawler (created if not provided)
        """
        self.db = db
        self.queries = KSEQueries(db)
        self.frontier = frontier or URLFrontier(per_domain_delay=1.0)
        self.crawler = crawler or KSECrawler()
        
        self.stats = {
            'pages_crawled': 0,
            'pages_indexed': 0,
            'errors': 0,
            'links_extracted': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def initialize_from_domains(self, limit: int = None) -> int:
        """
        Initialize frontier from database domains.
        
        Args:
            limit: Max domains to load (None = all)
            
        Returns:
            Number of URLs added
        """
        logger.info("Initializing frontier from database domains...")
        
        # Get all pending domains
        pending_domains = self.queries.get_pending_domains(limit=limit or 10000)
        logger.info(f"Found {len(pending_domains)} pending domains")
        
        # Add each domain as URL
        urls_added = 0
        for domain in pending_domains:
            domain_url = domain['url']
            priority = 10 - (domain['error_count'] or 0)  # Lower priority if errors
            
            if self.frontier.add_url(domain_url, priority=priority):
                urls_added += 1
        
        logger.info(f"✅ Added {urls_added} domain URLs to frontier")
        return urls_added
    
    def crawl_one(self) -> Optional[Dict]:
        """
        Crawl one URL from frontier.
        
        Returns:
            Crawl result or None if nothing to crawl
        """
        # Get next URL
        url = self.frontier.get_next_url()
        if not url:
            logger.debug("No URLs ready to crawl (waiting for domain delay)")
            return None
        
        # Crawl it
        result = self.crawler.crawl(url)
        
        # Mark in frontier
        if result.success:
            self.frontier.mark_visited(url)
        else:
            self.frontier.mark_failed(url)
        
        # Store in database
        self._store_crawl_result(result)
        
        # Add discovered links to frontier
        if result.success and result.links:
            self._process_links(result)
        
        return result
    
    def crawl_batch(self, count: int = 10, max_duration: int = None) -> Dict:
        """
        Crawl multiple URLs.
        
        Args:
            count: Number of URLs to crawl
            max_duration: Max duration in seconds (None = unlimited)
            
        Returns:
            Statistics dictionary
        """
        logger.info(f"Starting crawl of {count} URLs...")
        self.stats['start_time'] = datetime.now()
        
        batch_stats = {
            'successful': 0,
            'failed': 0,
            'total_duration_ms': 0,
            'total_size_bytes': 0,
            'total_links': 0,
        }
        
        start_time = time.time()
        
        for i in range(count):
            # Check duration limit
            if max_duration:
                elapsed = time.time() - start_time
                if elapsed > max_duration:
                    logger.info(f"Duration limit reached ({max_duration}s)")
                    break
            
            # Crawl one URL
            result = self.crawl_one()
            if result is None:
                # No URLs ready, wait a bit
                logger.debug("Waiting for URLs...")
                time.sleep(1)
                continue
            
            # Update stats
            if result.success:
                batch_stats['successful'] += 1
                batch_stats['total_size_bytes'] += result.size_bytes
                batch_stats['total_links'] += len(result.links)
            else:
                batch_stats['failed'] += 1
            
            batch_stats['total_duration_ms'] += result.duration_ms
            
            # Progress
            if (i + 1) % 10 == 0:
                logger.info(
                    f"Progress: {i + 1}/{count} "
                    f"({batch_stats['successful']} success, "
                    f"{batch_stats['failed']} failed)"
                )
        
        self.stats['end_time'] = datetime.now()
        self.stats['pages_crawled'] += batch_stats['successful']
        self.stats['errors'] += batch_stats['failed']
        self.stats['links_extracted'] += batch_stats['total_links']
        
        logger.info(f"✅ Crawl batch complete: {batch_stats}")
        return batch_stats
    
    def _store_crawl_result(self, result) -> None:
        """
        Store crawl result in database.
        
        Args:
            result: CrawlResult object
        """
        try:
            # Get domain ID
            domain_id = self._get_domain_id_for_url(result.url)
            
            if result.success:
                # Insert page
                page_id = self.queries.insert_page(
                    domain_id=domain_id,
                    url=result.url,
                    title=result.title,
                    description=result.description,
                    content=result.content,
                    content_hash=result.content_hash,
                    status_code=result.status_code,
                    content_type=result.content_type,
                    size_bytes=result.size_bytes,
                )
                
                # Update domain crawl time
                self.queries.update_domain_crawl_time(domain_id, status='active')
                
                # Log event
                self.queries.log_crawl_event(
                    event_type='fetched',
                    domain_id=domain_id,
                    url=result.url,
                    status_code=result.status_code,
                    duration_ms=int(result.duration_ms),
                    message=f"Crawled {result.size_bytes} bytes",
                )
            else:
                # Log failure
                self.queries.log_crawl_event(
                    event_type='error',
                    domain_id=domain_id,
                    url=result.url,
                    status_code=result.status_code,
                    duration_ms=int(result.duration_ms),
                    message=result.error_message,
                )
                
                # Increment error count
                self.queries.increment_domain_error_count(domain_id)
        
        except Exception as e:
            logger.error(f"Failed to store crawl result: {e}")
    
    def _get_domain_id_for_url(self, url: str) -> int:
        """
        Get domain ID from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain ID
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain_name = parsed.netloc
        
        # Try to find existing domain
        result = self.db.fetch_one(
            "SELECT id FROM domains WHERE domain_name = %s;",
            (domain_name,)
        )
        
        if result:
            return result[0]
        
        # Return 1 as default (should exist from initial load)
        return 1
    
    def _process_links(self, result) -> int:
        """
        Process discovered links and add to frontier.
        
        Args:
            result: CrawlResult object
            
        Returns:
            Number of links added to frontier
        """
        added = 0
        
        for link in result.links:
            url = link['url']
            
            # Skip external links for now
            from urllib.parse import urlparse
            source_parsed = urlparse(result.url)
            target_parsed = urlparse(url)
            
            if source_parsed.netloc != target_parsed.netloc:
                continue
            
            # Add to frontier with high priority
            if self.frontier.add_url(url, priority=8):
                added += 1
        
        self.stats['links_extracted'] += len(result.links)
        
        if added > 0:
            logger.debug(f"Added {added} internal links to frontier")
        
        return added
    
    def get_stats(self) -> Dict:
        """
        Get crawler statistics.
        
        Returns:
            Statistics dictionary
        """
        frontier_stats = self.frontier.get_stats()
        
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (
                self.stats['end_time'] - self.stats['start_time']
            ).total_seconds()
        
        return {
            'pages_crawled': self.stats['pages_crawled'],
            'errors': self.stats['errors'],
            'links_extracted': self.stats['links_extracted'],
            'duration_seconds': duration,
            'frontier': frontier_stats,
        }
    
    def close(self) -> None:
        """
        Close manager (cleanup).
        """
        self.crawler.close()
        logger.info("Crawler manager closed")
