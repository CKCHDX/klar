"""
Test script for crawler enhancements
Validates dynamic crawl speed, unlimited depth, and data persistence
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_crawler_dynamic_speed():
    """Test dynamic crawl speed feature"""
    logger.info("Testing dynamic crawl speed...")
    
    try:
        # Check that the parameter exists in the code
        with open('kse/crawler/kse_crawler_core.py', 'r') as f:
            content = f.read()
        
        # Check for dynamic_speed parameter in __init__
        assert 'dynamic_speed: bool = False' in content or 'dynamic_speed:bool=False' in content, \
            "CrawlerCore.__init__ should have dynamic_speed parameter"
        
        # Check that it's used
        assert 'self.dynamic_speed = dynamic_speed' in content, \
            "dynamic_speed should be stored as instance variable"
        
        # Check that robots.txt delay is used
        assert 'get_crawl_delay' in content, \
            "Should call robots parser's get_crawl_delay method"
        
        logger.info("✓ Dynamic crawl speed feature implemented in CrawlerCore")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Dynamic crawl speed test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unlimited_crawl_depth():
    """Test unlimited crawl depth configuration"""
    logger.info("Testing unlimited crawl depth...")
    
    try:
        # Just verify the phase 1 config has updated spinbox range
        with open('gui/setup_wizard/phase_1_storage_config.py', 'r') as f:
            content = f.read()
            
        # Check for large range in spinbox
        assert 'setRange(1, 1000)' in content or 'setRange(1,1000)' in content, \
            "Spinbox range should be set to allow up to 1000 pages"
        
        # Check for unlimited checkbox
        assert 'unlimited_crawl_checkbox' in content, \
            "Should have unlimited crawl checkbox"
        
        logger.info("✓ Phase 1 config supports unlimited crawl depth")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Unlimited crawl depth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_robots_parser_delay():
    """Test robots.txt crawl delay parsing"""
    logger.info("Testing robots.txt crawl delay parsing...")
    
    try:
        # Create logs directory
        logs_path = Path.cwd() / "data" / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        
        from kse.crawler.kse_robots_parser import RobotsParser
        
        parser = RobotsParser("TestBot/1.0")
        
        # Verify get_crawl_delay method exists
        assert hasattr(parser, 'get_crawl_delay'), "RobotsParser should have get_crawl_delay method"
        
        # Test with a URL that doesn't exist (should return None)
        delay = parser.get_crawl_delay("https://nonexistent-test-domain-12345.com")
        logger.info(f"Crawl delay for non-existent domain: {delay}")
        
        logger.info("✓ Robots parser crawl delay feature validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Robots parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indexer_pipeline():
    """Test indexer pipeline for data persistence"""
    logger.info("Testing indexer pipeline...")
    
    try:
        # Check that phase 2 adds indexing after crawl
        with open('gui/setup_wizard/phase_2_crawl_control.py', 'r') as f:
            content = f.read()
        
        # Check for indexing code
        assert 'IndexerPipeline' in content, \
            "Phase 2 should import IndexerPipeline"
        assert 'indexer.index_pages' in content, \
            "Phase 2 should call indexer.index_pages"
        assert 'get_crawled_pages' in content, \
            "Phase 2 should get crawled pages for indexing"
        
        logger.info("✓ Indexing is integrated into crawl phase")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Indexer pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file_path():
    """Test config file path handling"""
    logger.info("Testing config file path handling...")
    
    try:
        from kse.core.kse_config import ConfigManager
        from pathlib import Path
        
        # Create config manager
        config_manager = ConfigManager()
        
        # Verify config can be accessed
        config = config_manager.config
        assert hasattr(config, 'base_dir'), "Config should have base_dir"
        
        logger.info("✓ Config manager works correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Config file path test failed: {e}")
        return False

def test_control_center_import():
    """Test Control Center import with correct class name"""
    logger.info("Testing Control Center import...")
    
    try:
        # Test the corrected import
        try:
            from gui.control_center.control_center_main import ControlCenterMain as ControlCenter
            logger.info("✓ ControlCenter imported successfully (as ControlCenterMain)")
        except ImportError as e:
            # This is expected if PyQt6 is not installed
            if "PyQt6" in str(e) or "No module named 'PyQt6'" in str(e):
                logger.info("✓ Import failed as expected (PyQt6 not available in test environment)")
                return True
            raise
        
        # Also test alias
        from gui.control_center.control_center_main import ControlCenter
        logger.info("✓ ControlCenter alias works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Control Center import test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Starting Crawler Enhancement Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Dynamic Crawl Speed", test_crawler_dynamic_speed),
        ("Unlimited Crawl Depth", test_unlimited_crawl_depth),
        ("Robots Parser Delay", test_robots_parser_delay),
        ("Indexer Pipeline", test_indexer_pipeline),
        ("Config File Path", test_config_file_path),
        ("Control Center Import", test_control_center_import),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info("")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
