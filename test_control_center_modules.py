#!/usr/bin/env python3
"""
Test script to verify Control Center modules
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        from gui.control_center.modules import (
            PCCPrimaryControl,
            MCSMainControlServer,
            SCSSystemStatus,
            ACCAuxiliaryControl,
            SCCSecondaryControl
        )
        logger.info("✓ All modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False

def test_module_instantiation():
    """Test that modules can be instantiated"""
    logger.info("Testing module instantiation...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.control_center.control_center_api_client import ControlCenterAPIClient
        from gui.control_center.modules import (
            PCCPrimaryControl,
            MCSMainControlServer,
            SCSSystemStatus,
            ACCAuxiliaryControl,
            SCCSecondaryControl
        )
        
        # Create QApplication (required for Qt widgets)
        app = QApplication(sys.argv)
        
        # Create API client
        api_client = ControlCenterAPIClient()
        
        # Test instantiation of each module
        modules = {
            'PCC Primary Control': PCCPrimaryControl,
            'MCS Main Control Server': MCSMainControlServer,
            'SCS System Status': SCSSystemStatus,
            'ACC Auxiliary Control': ACCAuxiliaryControl,
            'SCC Secondary Control': SCCSecondaryControl,
        }
        
        for name, module_class in modules.items():
            try:
                module = module_class(api_client)
                logger.info(f"✓ {name} instantiated successfully")
                
                # Check that module has required methods
                required_methods = ['showEvent', 'hideEvent', 'refresh_data']
                for method in required_methods:
                    if not hasattr(module, method):
                        logger.warning(f"  ⚠ {name} missing method: {method}")
                
            except Exception as e:
                logger.error(f"✗ Failed to instantiate {name}: {e}")
                return False
        
        logger.info("✓ All modules instantiated successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Instantiation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_structure():
    """Test module structure and components"""
    logger.info("Testing module structure...")
    
    try:
        from gui.control_center.modules import pcc_primary_control
        from gui.control_center.modules import mcs_main_control_server
        from gui.control_center.modules import scs_system_status
        from gui.control_center.modules import acc_auxiliary_control
        from gui.control_center.modules import scc_secondary_control
        
        modules = [
            ('pcc_primary_control', pcc_primary_control),
            ('mcs_main_control_server', mcs_main_control_server),
            ('scs_system_status', scs_system_status),
            ('acc_auxiliary_control', acc_auxiliary_control),
            ('scc_secondary_control', scc_secondary_control),
        ]
        
        for name, module in modules:
            logger.info(f"Checking {name}...")
            # Check for main widget class
            class_names = [attr for attr in dir(module) if not attr.startswith('_')]
            logger.info(f"  Classes: {', '.join(class_names[:5])}...")
        
        logger.info("✓ Module structure check complete")
        return True
        
    except Exception as e:
        logger.error(f"✗ Structure test error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("KSE Control Center Modules Test Suite")
    logger.info("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Structure Test", test_module_structure),
        ("Instantiation Test", test_module_instantiation),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n✓ All tests passed!")
        return 0
    else:
        logger.error("\n✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
