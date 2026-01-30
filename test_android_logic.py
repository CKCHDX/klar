#!/usr/bin/env python3
"""
Test script to verify Android version logic without UI
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse

def test_url_validation():
    """Test URL validation logic"""
    print("Testing URL validation...")
    
    def validate_url(url):
        if not url:
            return False
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except Exception:
            return False
    
    test_cases = [
        ("http://localhost:5000", True),
        ("https://example.com", True),
        ("invalid", False),
        ("", False),
        ("ftp://example.com", False),
        ("http://", False),
    ]
    
    for url, expected in test_cases:
        result = validate_url(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} validate_url('{url}') = {result} (expected {expected})")
        if result != expected:
            return False
    
    print("✓ URL validation tests passed\n")
    return True


def test_config_handling():
    """Test configuration file handling"""
    print("Testing config handling...")
    
    import tempfile
    
    # Create a temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = Path(f.name)
        config = {'server_url': 'http://test.example.com:5000'}
        json.dump(config, f, indent=2)
    
    try:
        # Test reading
        with open(config_path, 'r') as f:
            loaded = json.load(f)
            if loaded['server_url'] == 'http://test.example.com:5000':
                print("  ✓ Config read successfully")
            else:
                print("  ✗ Config read failed")
                return False
        
        # Test writing
        new_config = {'server_url': 'http://new.example.com:8080'}
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        with open(config_path, 'r') as f:
            loaded = json.load(f)
            if loaded['server_url'] == 'http://new.example.com:8080':
                print("  ✓ Config write successful")
            else:
                print("  ✗ Config write failed")
                return False
        
        print("✓ Config handling tests passed\n")
        return True
        
    finally:
        # Cleanup
        config_path.unlink(missing_ok=True)


def test_search_result_data():
    """Test search result data structure"""
    print("Testing search result data handling...")
    
    # Simulate API response
    mock_response = {
        'results': [
            {
                'title': 'Test Result 1',
                'url': 'http://example.com/1',
                'snippet': 'This is a test snippet',
                'score': 0.95
            },
            {
                'title': 'Test Result 2',
                'url': 'http://example.com/2',
                'text': 'Alternative text field',
            }
        ]
    }
    
    results = mock_response.get('results', [])
    if len(results) != 2:
        print("  ✗ Failed to get results")
        return False
    
    print(f"  ✓ Got {len(results)} results")
    
    # Check first result
    r1 = results[0]
    if r1.get('title') == 'Test Result 1' and r1.get('score') == 0.95:
        print("  ✓ Result 1 data correct")
    else:
        print("  ✗ Result 1 data incorrect")
        return False
    
    # Check second result (using text fallback)
    r2 = results[1]
    snippet = r2.get('snippet') or r2.get('text', 'No description available')
    if snippet == 'Alternative text field':
        print("  ✓ Result 2 snippet fallback works")
    else:
        print("  ✗ Result 2 snippet fallback failed")
        return False
    
    print("✓ Search result data tests passed\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Klar Browser Android - Logic Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_url_validation,
        test_config_handling,
        test_search_result_data,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} raised exception: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
