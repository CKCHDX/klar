#!/usr/bin/env python3
"""
Test script to validate klar_browser.py structure and integration
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        import logging
        import requests
        import json
        from pathlib import Path
        print("✓ Standard library imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that HTML file exists"""
    print("\nTesting file structure...")
    html_path = Path(__file__).parent / "klar_browser.html"
    
    if not html_path.exists():
        print(f"✗ HTML file not found: {html_path}")
        return False
    
    print(f"✓ HTML file found: {html_path}")
    
    # Check HTML content
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify key elements are present
    required_elements = [
        'class="compass"',
        'class="logo-text">KLAR</div>',
        'class="search-bar"',
        'class="quick-actions"',
        'class="theme-toggle"',
        'function handleSearch()',
        'function displayResults(',
        'function toggleTheme()',
        'function showSettings()',
        '--primary:',
        '--accent:',
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        print(f"✗ Missing HTML elements: {missing}")
        return False
    
    print(f"✓ All required HTML elements present ({len(required_elements)} checked)")
    
    return True

def test_python_structure():
    """Test Python file structure"""
    print("\nTesting Python structure...")
    py_path = Path(__file__).parent / "klar_browser.py"
    
    if not py_path.exists():
        print(f"✗ Python file not found: {py_path}")
        return False
    
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    required_components = [
        'class KlarBridge',
        'class KlarBrowser',
        'def performSearch',
        'def _load_html_ui',
        'QWebEngineView',
        'QWebChannel',
        'search_completed = pyqtSignal',
        'bridge.performSearch(query)',
        'handleSearchResults(data)',
    ]
    
    missing = []
    for component in required_components:
        if component not in content:
            missing.append(component)
    
    if missing:
        print(f"✗ Missing Python components: {missing}")
        return False
    
    print(f"✓ All required Python components present ({len(required_components)} checked)")
    
    return True

def test_integration():
    """Test that bridge injection is correct"""
    print("\nTesting integration...")
    py_path = Path(__file__).parent / "klar_browser.py"
    
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for proper bridge integration
    checks = [
        ('QWebChannel initialization', 'new QWebChannel(qt.webChannelTransport'),
        ('Bridge object registration', 'channel.objects.bridge'),
        ('Search override', 'const originalHandleSearch = handleSearch'),
        ('Result handler', 'function handleSearchResults(data)'),
        ('Settings integration', 'const originalShowSettings = showSettings'),
        ('HTML injection', "html_content.replace('</body>', injection_script)"),
    ]
    
    failed = []
    for name, check in checks:
        if check not in content:
            failed.append(name)
    
    if failed:
        print(f"✗ Failed integration checks: {failed}")
        return False
    
    print(f"✓ All integration checks passed ({len(checks)} checked)")
    
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("Klar Browser Integration Test Suite")
    print("="*60)
    
    tests = [
        test_imports,
        test_file_structure,
        test_python_structure,
        test_integration,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test failed with exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✓ ALL TESTS PASSED - UI integration is correct!")
        return 0
    else:
        print("✗ Some tests failed - please review")
        return 1

if __name__ == '__main__':
    sys.exit(main())
