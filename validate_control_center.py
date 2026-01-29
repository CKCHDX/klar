"""
Static validation test for Control Center components
Tests that don't require PyQt6 runtime
"""

import sys
import ast
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def validate_syntax(file_path: Path) -> bool:
    """Validate Python syntax"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path.name}: {e}")
        return False

def validate_imports(file_path: Path) -> list:
    """Extract imports from file"""
    imports = []
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        return imports
    except Exception as e:
        logger.error(f"Error parsing imports from {file_path.name}: {e}")
        return []

def validate_classes(file_path: Path) -> dict:
    """Extract class definitions"""
    classes = {}
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                classes[node.name] = {
                    'methods': methods,
                    'bases': [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
                }
        
        return classes
    except Exception as e:
        logger.error(f"Error parsing classes from {file_path.name}: {e}")
        return {}

def test_control_center_config():
    """Test control_center_config.py"""
    logger.info("\n" + "="*60)
    logger.info("Testing control_center_config.py")
    logger.info("="*60)
    
    file_path = Path('gui/control_center/control_center_config.py')
    
    # Syntax check
    if not validate_syntax(file_path):
        return False
    logger.info("✓ Syntax valid")
    
    # Check classes
    classes = validate_classes(file_path)
    assert 'ControlCenterConfig' in classes
    logger.info(f"✓ ControlCenterConfig class found")
    
    # Check methods
    config_class = classes['ControlCenterConfig']
    expected_methods = [
        'get_module_config', 'get_module_list', 'get_api_endpoint',
        'get_update_interval', 'load_config', 'save_config'
    ]
    for method in expected_methods:
        assert method in config_class['methods'], f"Missing method: {method}"
    logger.info(f"✓ All required methods found: {len(expected_methods)}")
    
    # Import the config directly
    from gui.control_center.control_center_config import ControlCenterConfig
    
    # Test constants
    assert ControlCenterConfig.WINDOW_WIDTH == 1400
    assert ControlCenterConfig.WINDOW_HEIGHT == 900
    assert ControlCenterConfig.API_BASE_URL == "http://localhost:5000"
    logger.info("✓ Constants defined correctly")
    
    # Test modules
    modules = ControlCenterConfig.MODULES
    assert len(modules) == 5
    assert all(m in modules for m in ['pcc', 'mcs', 'scs', 'acc', 'scc'])
    logger.info(f"✓ All 5 modules defined: {list(modules.keys())}")
    
    # Test module structure
    for module_id, config in modules.items():
        assert 'name' in config
        assert 'title' in config
        assert 'description' in config
        assert 'shortcut' in config
    logger.info("✓ Module structure correct")
    
    # Test API endpoints
    endpoints = ControlCenterConfig.API_ENDPOINTS
    assert len(endpoints) >= 8
    assert 'health' in endpoints
    assert 'stats' in endpoints
    assert 'search' in endpoints
    logger.info(f"✓ API endpoints defined: {len(endpoints)}")
    
    return True

def test_control_center_api_client():
    """Test control_center_api_client.py"""
    logger.info("\n" + "="*60)
    logger.info("Testing control_center_api_client.py")
    logger.info("="*60)
    
    file_path = Path('gui/control_center/control_center_api_client.py')
    
    # Syntax check
    if not validate_syntax(file_path):
        return False
    logger.info("✓ Syntax valid")
    
    # Check classes
    classes = validate_classes(file_path)
    assert 'APIRequest' in classes
    assert 'ControlCenterAPIClient' in classes
    logger.info(f"✓ Classes found: {list(classes.keys())}")
    
    # Check API client methods
    api_class = classes['ControlCenterAPIClient']
    expected_methods = [
        'check_health', 'get_stats', 'search', 'get_history',
        'get_cache_stats', 'clear_cache', 'test_connection'
    ]
    for method in expected_methods:
        assert method in api_class['methods'], f"Missing method: {method}"
    logger.info(f"✓ All required API methods found: {len(expected_methods)}")
    
    # Check it extends QObject
    assert 'QObject' in api_class['bases']
    logger.info("✓ Inherits from QObject")
    
    return True

def test_control_center_navigation():
    """Test control_center_navigation.py"""
    logger.info("\n" + "="*60)
    logger.info("Testing control_center_navigation.py")
    logger.info("="*60)
    
    file_path = Path('gui/control_center/control_center_navigation.py')
    
    # Syntax check
    if not validate_syntax(file_path):
        return False
    logger.info("✓ Syntax valid")
    
    # Check classes
    classes = validate_classes(file_path)
    assert 'ControlCenterNavigation' in classes
    logger.info("✓ ControlCenterNavigation class found")
    
    # Check methods
    nav_class = classes['ControlCenterNavigation']
    expected_methods = [
        'add_module', 'remove_module', 'get_current_module_id',
        'set_active_module', 'get_module_count', 'get_module_list'
    ]
    for method in expected_methods:
        assert method in nav_class['methods'], f"Missing method: {method}"
    logger.info(f"✓ All required methods found: {len(expected_methods)}")
    
    # Check it extends QTabWidget
    assert 'QTabWidget' in nav_class['bases']
    logger.info("✓ Inherits from QTabWidget")
    
    return True

def test_control_center_main():
    """Test control_center_main.py"""
    logger.info("\n" + "="*60)
    logger.info("Testing control_center_main.py")
    logger.info("="*60)
    
    file_path = Path('gui/control_center/control_center_main.py')
    
    # Syntax check
    if not validate_syntax(file_path):
        return False
    logger.info("✓ Syntax valid")
    
    # Check classes
    classes = validate_classes(file_path)
    assert 'ControlCenterMain' in classes
    logger.info("✓ ControlCenterMain class found")
    
    # Check methods
    main_class = classes['ControlCenterMain']
    expected_methods = [
        '_setup_window', '_create_menu_bar', '_create_toolbar',
        '_create_status_bar', '_setup_navigation', '_load_modules',
        'closeEvent'
    ]
    for method in expected_methods:
        assert method in main_class['methods'], f"Missing method: {method}"
    logger.info(f"✓ Core window methods found: {len(expected_methods)}")
    
    # Check it extends QMainWindow
    assert 'QMainWindow' in main_class['bases']
    logger.info("✓ Inherits from QMainWindow")
    
    # Check for main function
    with open(file_path, 'r') as f:
        content = f.read()
    assert 'def main():' in content
    assert "if __name__ == '__main__':" in content
    logger.info("✓ Standalone execution support")
    
    return True

def test_file_structure():
    """Test overall file structure"""
    logger.info("\n" + "="*60)
    logger.info("Testing File Structure")
    logger.info("="*60)
    
    base_dir = Path('gui/control_center')
    
    # Check all required files exist
    required_files = [
        '__init__.py',
        'control_center_config.py',
        'control_center_api_client.py',
        'control_center_navigation.py',
        'control_center_main.py',
    ]
    
    for file_name in required_files:
        file_path = base_dir / file_name
        assert file_path.exists(), f"Missing file: {file_name}"
        assert file_path.stat().st_size > 0, f"Empty file: {file_name}"
    
    logger.info(f"✓ All {len(required_files)} required files present")
    
    # Check file sizes (should be substantial)
    sizes = {
        'control_center_config.py': 6000,
        'control_center_api_client.py': 9000,
        'control_center_navigation.py': 8000,
        'control_center_main.py': 16000,
    }
    
    for file_name, min_size in sizes.items():
        file_path = base_dir / file_name
        size = file_path.stat().st_size
        assert size >= min_size, f"{file_name} too small: {size} < {min_size}"
    
    logger.info("✓ All files have substantial content")
    
    return True

def main():
    """Run all validation tests"""
    logger.info("="*60)
    logger.info("Control Center Static Validation Tests")
    logger.info("="*60)
    
    results = {}
    
    try:
        results['File Structure'] = test_file_structure()
        results['Config Module'] = test_control_center_config()
        results['API Client'] = test_control_center_api_client()
        results['Navigation'] = test_control_center_navigation()
        results['Main Window'] = test_control_center_main()
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results[str(e)] = False
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("Test Results Summary")
    logger.info("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:25} {status}")
    
    logger.info("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if all(results.values()):
        logger.info("\n🎉 All validation tests passed!")
    
    return all(results.values())

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
