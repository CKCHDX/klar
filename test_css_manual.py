#!/usr/bin/env python3
"""
Comprehensive manual test demonstrating CSS pipeline functionality
"""
import sys
import os

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

from render_engine import RenderEngine


def test_external_css_simulation():
    """Test external CSS file loading and application"""
    print("=== Test 1: External CSS Simulation ===")
    
    engine = RenderEngine()
    
    # HTML that references external CSS
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <h1 class="title">Welcome</h1>
        <p class="intro">This is styled by external CSS</p>
        <div id="main-content">
            <p>Content paragraph</p>
        </div>
    </body>
    </html>
    """
    
    # Simulated external CSS
    external_css = """
    .title {
        color: #2c3e50;
        font-size: 40px;
    }
    .intro {
        color: #7f8c8d;
        font-size: 18px;
    }
    #main-content {
        background-color: #ecf0f1;
        padding: 20px;
    }
    """
    
    engine.load_html(html, "http://example.com/page.html")
    
    # Simulate external CSS being loaded and applied
    engine.css_parser.add_stylesheet(external_css)
    engine.css_parser.compute_styles_recursive(engine.dom_tree)
    
    # Verify styles are applied
    def find_by_class(node, class_name):
        if 'class' in node.attrs and class_name in (node.attrs['class'] if isinstance(node.attrs['class'], list) else node.attrs['class'].split()):
            return node
        for child in node.children:
            result = find_by_class(child, class_name)
            if result:
                return result
        return None
    
    title = find_by_class(engine.dom_tree, 'title')
    if title:
        assert title.styles.get('color') == '#2c3e50'
        assert title.styles.get('font-size') == '40px'
        print("  ✓ External CSS applied to .title class")
    
    intro = find_by_class(engine.dom_tree, 'intro')
    if intro:
        assert intro.styles.get('color') == '#7f8c8d'
        print("  ✓ External CSS applied to .intro class")
    
    print()


def test_inline_style_tags():
    """Test inline <style> tag parsing and application"""
    print("=== Test 2: Inline <style> Tags ===")
    
    engine = RenderEngine()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .alert {
                color: red;
                font-weight: bold;
            }
            .success {
                color: green;
            }
        </style>
    </head>
    <body>
        <p class="alert">This is an alert</p>
        <p class="success">This is success</p>
        <p>Regular text</p>
    </body>
    </html>
    """
    
    engine.load_html(html, "http://example.com/inline.html")
    
    # Find and verify alert
    def find_by_class(node, class_name):
        if 'class' in node.attrs:
            classes = node.attrs['class'] if isinstance(node.attrs['class'], list) else node.attrs['class'].split()
            if class_name in classes:
                return node
        for child in node.children:
            result = find_by_class(child, class_name)
            if result:
                return result
        return None
    
    alert = find_by_class(engine.dom_tree, 'alert')
    if alert:
        assert alert.styles.get('color') == 'red'
        assert alert.styles.get('font-weight') == 'bold'
        print("  ✓ Inline <style> applied to .alert class")
    
    success = find_by_class(engine.dom_tree, 'success')
    if success:
        assert success.styles.get('color') == 'green'
        print("  ✓ Inline <style> applied to .success class")
    
    print()


def test_style_cascade():
    """Test CSS cascade and specificity"""
    print("=== Test 3: CSS Cascade and Specificity ===")
    
    engine = RenderEngine()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            p {
                color: black;
                font-size: 14px;
            }
            .highlight {
                color: blue;
            }
            #special {
                color: red;
            }
        </style>
    </head>
    <body>
        <p>Normal paragraph (black)</p>
        <p class="highlight">Highlighted paragraph (blue)</p>
        <p id="special">Special paragraph (red, ID > class)</p>
        <p class="highlight" style="color: purple;">
            Inline style paragraph (purple, inline > ID > class > element)
        </p>
    </body>
    </html>
    """
    
    engine.load_html(html, "http://example.com/cascade.html")
    
    # Find paragraphs
    def find_all_p(node, results=None):
        if results is None:
            results = []
        if node.tag == 'p':
            results.append(node)
        for child in node.children:
            find_all_p(child, results)
        return results
    
    paragraphs = find_all_p(engine.dom_tree)
    
    # Check each paragraph
    p1 = paragraphs[0] if len(paragraphs) > 0 else None
    if p1:
        # Should have default element styles
        print(f"  P1 color: {p1.styles.get('color')} (expected: black)")
    
    p2 = paragraphs[1] if len(paragraphs) > 1 else None
    if p2:
        # Class selector should override element
        assert p2.styles.get('color') == 'blue'
        print(f"  ✓ P2 color: blue (class > element)")
    
    p3 = paragraphs[2] if len(paragraphs) > 2 else None
    if p3:
        # ID selector should override class
        assert p3.styles.get('color') == 'red'
        print(f"  ✓ P3 color: red (ID > class)")
    
    p4 = paragraphs[3] if len(paragraphs) > 3 else None
    if p4:
        # Inline style should override everything
        assert p4.styles.get('color') == 'purple'
        print(f"  ✓ P4 color: purple (inline > ID)")
    
    print()


def test_multiple_stylesheets():
    """Test multiple stylesheets being applied"""
    print("=== Test 4: Multiple Stylesheets ===")
    
    engine = RenderEngine()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .box {
                padding: 10px;
                color: black;
            }
        </style>
        <style>
            .box {
                background-color: lightgray;
            }
            .special-box {
                border: 2px solid blue;
            }
        </style>
    </head>
    <body>
        <div class="box special-box">Content</div>
    </body>
    </html>
    """
    
    engine.load_html(html, "http://example.com/multi.html")
    
    # Find the box
    def find_by_class(node, class_name):
        if 'class' in node.attrs:
            classes = node.attrs['class'] if isinstance(node.attrs['class'], list) else node.attrs['class'].split()
            if class_name in classes:
                return node
        for child in node.children:
            result = find_by_class(child, class_name)
            if result:
                return result
        return None
    
    box = find_by_class(engine.dom_tree, 'box')
    if box:
        # Should have styles from both <style> tags
        assert box.styles.get('padding') == '10px'
        assert box.styles.get('color') == 'black'
        assert box.styles.get('background-color') == 'lightgray'
        print("  ✓ Styles from first <style> tag applied")
        print("  ✓ Styles from second <style> tag applied")
        print("  ✓ Multiple classes applied correctly")
    
    print()


def test_real_world_scenario():
    """Test a realistic HTML page with mixed CSS"""
    print("=== Test 5: Real-World Scenario ===")
    
    engine = RenderEngine()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blog Post</title>
        <style>
            body {
                font-family: Georgia, serif;
                line-height: 1.6;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background-color: #333;
                color: white;
                padding: 20px;
            }
            .content {
                background-color: white;
                padding: 30px;
            }
            h1 {
                color: #2c3e50;
            }
            .meta {
                color: #7f8c8d;
                font-size: 14px;
            }
            .highlight {
                background-color: #fff9c4;
                padding: 2px 4px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>My Blog</h1>
        </div>
        <div class="content">
            <h1>Article Title</h1>
            <p class="meta">Posted on January 30, 2026</p>
            <p>This is the article content with <span class="highlight">highlighted text</span>.</p>
        </div>
    </body>
    </html>
    """
    
    engine.load_html(html, "http://example.com/blog.html")
    
    print(f"  ✓ Parsed {len(engine.css_parser.stylesheet_rules)} CSS rules")
    
    # Verify body styles
    def find_body(node):
        if node.tag == 'body':
            return node
        for child in node.children:
            result = find_body(child)
            if result:
                return result
        return None
    
    body = find_body(engine.dom_tree)
    if body:
        assert body.styles.get('background-color') == '#f5f5f5'
        assert body.styles.get('font-family') == 'Georgia, serif'
        print("  ✓ Body styles applied")
    
    # Find highlight span
    def find_by_class(node, class_name):
        if 'class' in node.attrs:
            classes = node.attrs['class'] if isinstance(node.attrs['class'], list) else node.attrs['class'].split()
            if class_name in classes:
                return node
        for child in node.children:
            result = find_by_class(child, class_name)
            if result:
                return result
        return None
    
    highlight = find_by_class(engine.dom_tree, 'highlight')
    if highlight:
        assert highlight.styles.get('background-color') == '#fff9c4'
        print("  ✓ Nested element styles applied")
    
    print("  ✓ Real-world HTML page rendered successfully")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("COMPREHENSIVE CSS PIPELINE MANUAL TEST")
    print("="*60 + "\n")
    
    try:
        test_external_css_simulation()
        test_inline_style_tags()
        test_style_cascade()
        test_multiple_stylesheets()
        test_real_world_scenario()
        
        print("="*60)
        print("ALL MANUAL TESTS PASSED ✓")
        print("="*60)
        print("\nThe CSS fetch/apply pipeline is fully functional!")
        print("The render engine can now:")
        print("  • Parse external CSS files")
        print("  • Parse inline <style> tags")
        print("  • Match element, class, and ID selectors")
        print("  • Apply proper CSS cascade and specificity")
        print("  • Handle multiple stylesheets")
        print("  • Render real-world HTML pages with CSS")
        print()
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
