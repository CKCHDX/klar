"""
KSE Main - Main entry point for Klar Search Engine
"""
import sys
from pathlib import Path
from typing import Optional
from kse.core.kse_config import KSEConfig, get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.core.kse_constants import (
    DEFAULT_CONFIG_FILE, DEFAULT_LOG_DIR, DOMAINS_FILE
)
from kse.storage.kse_storage_manager import StorageManager
from kse.storage.kse_domain_manager import DomainManager

logger = None  # Will be initialized after logging setup


class KSEApplication:
    """Main KSE application"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize KSE application
        
        Args:
            config_file: Optional path to configuration file
        """
        # Load configuration
        if config_file and config_file.exists():
            self.config = KSEConfig(config_file)
        else:
            self.config = get_config()
        
        # Setup logging
        log_dir = Path(self.config.get("log_dir"))
        log_level = self.config.get("log_level", "INFO")
        enable_console = self.config.get("enable_console_logging", True)
        KSELogger.setup(log_dir, log_level, enable_console)
        
        global logger
        logger = get_logger(__name__)
        
        logger.info("=" * 60)
        logger.info("KSE - Klar Search Engine")
        logger.info("Version 3.0.0")
        logger.info("=" * 60)
        
        # Initialize core components
        self.storage_manager = None
        self.domain_manager = None
        
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize core components"""
        try:
            # Initialize storage
            data_dir = Path(self.config.get("data_dir"))
            self.storage_manager = StorageManager(data_dir)
            logger.info("Storage manager initialized")
            
            # Initialize domain manager
            if DOMAINS_FILE.exists():
                self.domain_manager = DomainManager(DOMAINS_FILE)
                stats = self.domain_manager.get_stats()
                logger.info(f"Domain manager initialized: {stats['total_domains']} domains loaded")
            else:
                logger.warning(f"Domains file not found: {DOMAINS_FILE}")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def get_status(self) -> dict:
        """
        Get application status
        
        Returns:
            Dictionary with status information
        """
        status = {
            "version": "3.0.0",
            "status": "running",
            "components": {
                "storage": self.storage_manager is not None,
                "domains": self.domain_manager is not None,
            }
        }
        
        if self.storage_manager:
            status["storage_stats"] = self.storage_manager.get_storage_stats()
        
        if self.domain_manager:
            status["domain_stats"] = self.domain_manager.get_stats()
        
        return status
    
    def shutdown(self) -> None:
        """Shutdown application gracefully"""
        logger.info("Shutting down KSE...")
        logger.info("KSE shutdown complete")


def main():
    """Main entry point"""
    try:
        # Check for config file argument
        config_file = None
        if len(sys.argv) > 1:
            config_file = Path(sys.argv[1])
            if not config_file.exists():
                print(f"Error: Config file not found: {config_file}")
                sys.exit(1)
        
        # Create and run application
        app = KSEApplication(config_file)
        
        # Print status
        status = app.get_status()
        print("\n" + "=" * 60)
        print("KSE STATUS")
        print("=" * 60)
        print(f"Version: {status['version']}")
        print(f"Status: {status['status']}")
        print(f"\nComponents:")
        print(f"  Storage: {'✓' if status['components']['storage'] else '✗'}")
        print(f"  Domains: {'✓' if status['components']['domains'] else '✗'}")
        
        if "domain_stats" in status:
            print(f"\nDomain Statistics:")
            print(f"  Total domains: {status['domain_stats']['total_domains']}")
            print(f"  Categories: {', '.join(status['domain_stats']['categories'].keys())}")
        
        if "storage_stats" in status:
            print(f"\nStorage Statistics:")
            print(f"  Base path: {status['storage_stats']['base_path']}")
            print(f"  Total size: {status['storage_stats']['total_size_mb']} MB")
        
        print("=" * 60 + "\n")
        
        print("KSE core initialized successfully!")
        print("Next steps:")
        print("  - Implement crawler: kse/crawler/kse_crawler_core.py")
        print("  - Implement indexer: kse/indexing/kse_indexer_pipeline.py")
        print("  - Implement search: kse/search/kse_search_pipeline.py")
        print("  - Start server: python -m kse.server.kse_server")
        
        app.shutdown()
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if logger:
            logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
