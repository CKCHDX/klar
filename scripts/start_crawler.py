"""
Start Crawler - Script to start KSE crawler
"""
import sys
from pathlib import Path
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.storage.kse_domain_manager import DomainManager
from kse.crawler.kse_crawler_core import CrawlerCore
from kse.core.kse_constants import DOMAINS_FILE

logger = None


def main():
    """Start the crawler"""
    global logger
    
    try:
        # Load configuration
        config = get_config()
        
        # Setup logging
        log_dir = Path(config.get("log_dir"))
        KSELogger.setup(log_dir, config.get("log_level", "INFO"), True)
        logger = get_logger(__name__)
        
        logger.info("=" * 60)
        logger.info("KSE Crawler Starting")
        logger.info("=" * 60)
        
        # Initialize storage
        data_dir = Path(config.get("data_dir"))
        storage_manager = StorageManager(data_dir)
        
        # Load domains
        if not DOMAINS_FILE.exists():
            logger.error(f"Domains file not found: {DOMAINS_FILE}")
            return 1
        
        domain_manager = DomainManager(DOMAINS_FILE)
        
        # Get crawl configuration
        crawler_config = config.get("crawler")
        
        # Get list of domains to crawl
        # For testing, use only high-priority domains (priority 1)
        domains_to_crawl = [d["domain"] for d in domain_manager.get_high_priority_domains()]
        
        # Limit to 3 domains for initial test
        domains_to_crawl = domains_to_crawl[:3]
        
        logger.info(f"Will crawl {len(domains_to_crawl)} domains: {', '.join(domains_to_crawl)}")
        
        # Initialize crawler
        crawler = CrawlerCore(
            storage_manager=storage_manager,
            allowed_domains=domains_to_crawl,
            user_agent=crawler_config.get("user_agent"),
            crawl_delay=crawler_config.get("crawl_delay", 1.0),
            timeout=crawler_config.get("timeout", 10),
            max_retries=crawler_config.get("max_retries", 3),
            crawl_depth=5,  # Limit to 5 pages per domain for testing
            respect_robots=crawler_config.get("respect_robots_txt", True)
        )
        
        # Crawl domains
        print("\nStarting crawl...\n")
        results = crawler.crawl_all_domains()
        
        # Print results
        print("\n" + "=" * 60)
        print("CRAWL RESULTS")
        print("=" * 60)
        
        for domain, result in results.items():
            print(f"\nDomain: {domain}")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Pages crawled: {result.get('pages_crawled', 0)}")
            print(f"  Pages failed: {result.get('pages_failed', 0)}")
        
        # Get statistics
        stats = crawler.get_crawl_stats()
        print(f"\nTotal Statistics:")
        print(f"  Total pages crawled: {stats['total_pages_crawled']}")
        print(f"  Total URLs visited: {stats['total_urls_visited']}")
        print("=" * 60 + "\n")
        
        # Get crawled pages
        pages = crawler.get_crawled_pages()
        print(f"Sample crawled pages (first 5):")
        for i, page in enumerate(pages[:5]):
            print(f"\n{i+1}. {page['url']}")
            print(f"   Title: {page['title'][:80]}")
            print(f"   Content length: {len(page['content'])} chars")
            print(f"   Links found: {len(page['links'])}")
        
        # Shutdown
        crawler.shutdown()
        
        logger.info("Crawler completed successfully")
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if logger:
            logger.error(f"Crawler error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
