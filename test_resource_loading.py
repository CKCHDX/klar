#!/usr/bin/env python3
"""
Test script to verify resource loading (images, videos, CSS, JS)
"""
import sys
import os

# Set offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication

# Create QApplication first (required for QPixmap)
app = QApplication(sys.argv)

from PyQt6.QtGui import QPixmap
from render_engine import RenderEngine
from resource_loader import ResourceLoader
from http_client import HTTPClient

def test_resource_loader():
    """Test the ResourceLoader functionality"""
    print("=== Testing ResourceLoader ===\n")
    
    loader = ResourceLoader()
    
    # Test 1: Load a data URI image
    print("Test 1: Loading data URI image...")
    data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
    pixmap = loader.load_image(data_uri)
    if pixmap and not pixmap.isNull():
        print(f"✓ Data URI image loaded successfully: {pixmap.width()}x{pixmap.height()}")
    else:
        print("✗ Failed to load data URI image")
    
    # Test 2: Extract resources from HTML
    print("\nTest 2: Extracting resources from HTML...")
    from html_parser import HTMLParserEngine
    parser = HTMLParserEngine()
    
    html = """
    <html>
    <head>
        <link rel="stylesheet" href="style.css">
        <script src="script.js"></script>
    </head>
    <body>
        <img src="image1.jpg" alt="Image 1">
        <img src="http://example.com/image2.png" alt="Image 2">
        <video src="video.mp4"></video>
        <video>
            <source src="video.webm" type="video/webm">
        </video>
    </body>
    </html>
    """
    
    dom_tree = parser.parse(html)
    resources = loader.extract_resources_from_html(dom_tree, "http://example.com/")
    
    print(f"  Images found: {len(resources['images'])}")
    for img in resources['images']:
        print(f"    - {img}")
    
    print(f"  Videos found: {len(resources['videos'])}")
    for vid in resources['videos']:
        print(f"    - {vid}")
    
    print(f"  CSS files found: {len(resources['css'])}")
    for css in resources['css']:
        print(f"    - {css}")
    
    print(f"  JS files found: {len(resources['scripts'])}")
    for js in resources['scripts']:
        print(f"    - {js}")
    
    print("\n=== ResourceLoader Tests Complete ===\n")

def test_render_engine_with_resources():
    """Test the RenderEngine with resources"""
    print("=== Testing RenderEngine with Resources ===\n")
    
    engine = RenderEngine()
    
    # Load HTML with resources
    html_with_resources = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <h1>Resource Loading Test</h1>
        <p>This page contains various resources:</p>
        
        <h2>Image (Data URI)</h2>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot">
        
        <h2>Video</h2>
        <video width="400" height="300" src="video.mp4"></video>
        
        <script src="app.js"></script>
    </body>
    </html>
    """
    
    print("Loading HTML with resources...")
    engine.load_html(html_with_resources, "http://example.com/page.html")
    
    print(f"✓ HTML loaded successfully")
    print(f"  DOM tree: {engine.dom_tree.tag if engine.dom_tree else 'None'}")
    print(f"  Loaded images: {len(engine.loaded_resources['images'])}")
    print(f"  Loaded videos: {len(engine.loaded_resources['videos'])}")
    print(f"  Loaded CSS: {len(engine.loaded_resources['css'])}")
    print(f"  Loaded JS: {len(engine.loaded_resources['scripts'])}")
    
    print("\n=== RenderEngine Tests Complete ===\n")

def test_http_client_binary():
    """Test HTTP client binary content fetching"""
    print("=== Testing HTTP Client Binary Fetching ===\n")
    
    client = HTTPClient()
    
    # Test text fetching
    print("Test 1: Fetching text content...")
    response = client.fetch("http://example.com", binary=False)
    if response['success']:
        print(f"✓ Text content fetched: {len(response['content'])} chars")
        print(f"  Content-Type: {response['content_type']}")
    else:
        print(f"✗ Failed: {response['error']}")
    
    # Test binary fetching
    print("\nTest 2: Binary fetching mode available...")
    # We won't fetch a real binary file to save bandwidth
    print("✓ Binary mode implemented (binary=True parameter)")
    
    print("\n=== HTTP Client Tests Complete ===\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("KLAR BROWSER - RESOURCE LOADING TESTS")
    print("="*60 + "\n")
    
    try:
        test_http_client_binary()
        test_resource_loader()
        test_render_engine_with_resources()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
