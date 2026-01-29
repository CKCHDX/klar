"""
Test script for Control Center components
Validates imports, configuration, and basic functionality
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

def test_imports():
    """Test all imports"""
    logger.info("Testing imports...")
    
    try:
        from gui.control_center.control_center_config import ControlCenterConfig
        logger.info("✓ ControlCenterConfig imported")
        
        from gui.control_center.control_center_api_client import ControlCenterAPIClient
        logger.info("✓ ControlCenterAPIClient imported")
        
        from gui.control_center.control_center_navigation import ControlCenterNavigation
        logger.info("✓ ControlCenterNavigation imported")
        
        from gui.control_center.control_center_main import ControlCenterMain
        logger.info("✓ ControlCenterMain imported")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    logger.info("\nTesting configuration...")
    
    try:
        from gui.control_center.control_center_config import ControlCenterConfig
        
        # Test window settings
        assert ControlCenterConfig.WINDOW_WIDTH == 1400
        assert ControlCenterConfig.WINDOW_HEIGHT == 900
        logger.info("✓ Window settings correct")
        
        # Test API configuration
        assert ControlCenterConfig.API_BASE_URL == "http://localhost:5000"
        logger.info("✓ API configuration correct")
        
        # Test modules
        modules = ControlCenterConfig.get_module_list()
        assert len(modules) == 5
        assert 'pcc' in modules
        assert 'mcs' in modules
        assert 'scs' in modules
        assert 'acc' in modules
        assert 'scc' in modules
        logger.info(f"✓ All 5 modules defined: {modules}")
        
        # Test module config
        pcc_config = ControlCenterConfig.get_module_config('pcc')
        assert pcc_config['name'] == 'Performance & Control'
        assert pcc_config['shortcut'] == 'Ctrl+1'
        logger.info("✓ Module configurations correct")
        
        # Test API endpoints
        health_endpoint = ControlCenterConfig.get_api_endpoint('health')
        assert health_endpoint == "http://localhost:5000/api/health"
        logger.info("✓ API endpoints correct")
        
        # Test update intervals
        interval = ControlCenterConfig.get_update_interval('pcc')
        assert interval == 5000
        logger.info("✓ Update intervals correct")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

def test_api_client():
    """Test API client initialization"""
    logger.info("\nTesting API client...")
    
    try:
        from gui.control_center.control_center_api_client import ControlCenterAPIClient
        from PyQt6.QtWidgets import QApplication
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        client = ControlCenterAPIClient()
        assert client.base_url == "http://localhost:5000"
        assert client.connection_status == 'disconnected'
        logger.info("✓ API client initialized")
        
        # Test methods exist
        assert hasattr(client, 'check_health')
        assert hasattr(client, 'get_stats')
        assert hasattr(client, 'search')
        assert hasattr(client, 'clear_cache')
        logger.info("✓ API client methods exist")
        
        return True
    except Exception as e:
        logger.error(f"✗ API client test failed: {e}")
        return False

def test_navigation():
    """Test navigation widget"""
    logger.info("\nTesting navigation widget...")
    
    try:
        from gui.control_center.control_center_navigation import ControlCenterNavigation
        from PyQt6.QtWidgets import QApplication, QWidget
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        nav = ControlCenterNavigation()
        assert nav is not None
        logger.info("✓ Navigation widget created")
        
        # Test adding modules
        test_widget = QWidget()
        nav.add_module('pcc', test_widget)
        assert 'pcc' in nav.get_module_list()
        logger.info("✓ Module added successfully")
        
        # Test module count
        assert nav.get_module_count() >= 1
        logger.info("✓ Module count correct")
        
        return True
    except Exception as e:
        logger.error(f"✗ Navigation test failed: {e}")
        return False

def test_main_window():
    """Test main window initialization"""
    logger.info("\nTesting main window...")
    
    try:
        from gui.control_center.control_center_main import ControlCenterMain
        from PyQt6.QtWidgets import QApplication
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = ControlCenterMain()
        assert window is not None
        logger.info("✓ Main window created")
        
        # Test window properties
        assert window.windowTitle() == "KSE Control Center"
        assert window.width() == 1400
        assert window.height() == 900
        logger.info("✓ Window properties correct")
        
        # Test components exist
        assert hasattr(window, 'api_client')
        assert hasattr(window, 'navigation')
        assert hasattr(window, 'status_bar')
        logger.info("✓ Window components exist")
        
        # Test modules loaded
        assert len(window.modules) == 5
        logger.info("✓ All modules loaded")
        
        # Cleanup
        window.close()
        
        return True
    except Exception as e:
        logger.error(f"✗ Main window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Control Center Component Tests")
    logger.info("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'Configuration': test_configuration(),
        'API Client': test_api_client(),
        'Navigation': test_navigation(),
        'Main Window': test_main_window(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:20} {status}")
    
    logger.info("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
