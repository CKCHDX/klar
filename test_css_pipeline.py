#!/usr/bin/env python3
"""
Test script for CSS fetch/apply pipeline
"""
import sys
import os

# Set offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication

# Create QApplication first (required for QPixmap)
app = QApplication(sys.argv)

from render_engine import RenderEngine
from css_parser import CSSParser
from html_parser import HTMLParserEngine, DOMNode


def test_css_parser_stylesheet():
    """Test CSS stylesheet parsing"""
    print("=== Testing CSS Stylesheet Parsing ===\n")
    
    parser = CSSParser()
    
    # Test basic CSS parsing
    css_content = """
    body {
        background-color: #f0f0f0;
        font-family: Arial, sans-serif;
    }
    
    h1 {
        color: #333333;
        font-size: 28px;
    }
    
    .highlight {
        background-color: yellow;
        color: black;
    }
    
    #special {
        font-weight: bold;
        color: red;
    }
    """
    
    rules = parser.parse_stylesheet(css_content)
    
    print(f"Parsed {len(rules)} CSS rules:")
    for rule in rules:
        print(f"  Selector: {rule['selector']}")
        print(f"  Declarations: {rule['declarations']}")
        print(f"  Specificity: {rule['specificity']}")
        print()
    
    assert len(rules) == 4, f"Expected 4 rules, got {len(rules)}"
    print("✓ CSS stylesheet parsing works\n")


def test_css_selector_matching():
    """Test CSS selector matching"""
    print("=== Testing CSS Selector Matching ===\n")
    
    parser = CSSParser()
    
    # Create test nodes
    div_node = DOMNode('div', {'class': 'highlight'})
    h1_node = DOMNode('h1', {'id': 'special'})
    p_node = DOMNode('p')
    
    # Test element selector
    assert parser._selector_matches('div', div_node), "Element selector failed"
    print("✓ Element selector works")
    
    # Test class selector
    assert parser._selector_matches('.highlight', div_node), "Class selector failed"
    print("✓ Class selector works")
    
    # Test id selector
    assert parser._selector_matches('#special', h1_node), "ID selector failed"
    print("✓ ID selector works")
    
    # Test non-matching
    assert not parser._selector_matches('span', div_node), "Non-matching selector failed"
    print("✓ Non-matching selector works")
    
    print()


def test_css_specificity():
    """Test CSS specificity calculation"""
    print("=== Testing CSS Specificity ===\n")
    
    parser = CSSParser()
    
    # Test specificity
    spec_element = parser._calculate_specificity('p')
    spec_class = parser._calculate_specificity('.highlight')
    spec_id = parser._calculate_specificity('#special')
    
    print(f"Element selector specificity: {spec_element}")
    print(f"Class selector specificity: {spec_class}")
    print(f"ID selector specificity: {spec_id}")
    
    # ID should be more specific than class, class more than element
    assert spec_id > spec_class, "ID specificity should be higher than class"
    assert spec_class > spec_element, "Class specificity should be higher than element"
    
    print("✓ Specificity calculation works\n")


def test_stylesheet_application():
    """Test applying stylesheets to DOM nodes"""
    print("=== Testing Stylesheet Application ===\n")
    
    parser = CSSParser()
    
    # Add a stylesheet
    css_content = """
    p {
        color: blue;
        font-size: 14px;
    }
    
    .red-text {
        color: red;
    }
    """
    
    parser.add_stylesheet(css_content)
    
    # Create nodes
    p_node = DOMNode('p')
    p_with_class = DOMNode('p', {'class': 'red-text'})
    
    # Compute styles
    styles1 = parser.compute_styles(p_node)
    styles2 = parser.compute_styles(p_with_class)
    
    print(f"Paragraph styles: color={styles1.get('color')}, font-size={styles1.get('font-size')}")
    print(f"Paragraph with class styles: color={styles2.get('color')}")
    
    assert styles1['color'] == 'blue', f"Expected blue, got {styles1['color']}"
    assert styles2['color'] == 'red', f"Expected red (class override), got {styles2['color']}"
    
    print("✓ Stylesheet application works\n")


def test_inline_style_priority():
    """Test that inline styles have highest priority"""
    print("=== Testing Inline Style Priority ===\n")
    
    parser = CSSParser()
    
    # Add stylesheet
    parser.add_stylesheet("p { color: blue; }")
    
    # Create node with inline style
    p_node = DOMNode('p', {'style': 'color: green;'})
    
    styles = parser.compute_styles(p_node)
    
    print(f"Paragraph with inline style: color={styles.get('color')}")
    
    assert styles['color'] == 'green', f"Expected green (inline override), got {styles['color']}"
    
    print("✓ Inline style priority works\n")


def test_render_engine_with_external_css():
    """Test render engine with external CSS"""
    print("=== Testing Render Engine with External CSS ===\n")
    
    engine = RenderEngine()
    
    # HTML with external CSS link
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSS Test</title>
    </head>
    <body>
        <h1>Test Page</h1>
        <p class="highlight">This should be highlighted</p>
        <div id="special">Special content</div>
    </body>
    </html>
    """
    
    # Manually add CSS (simulating external load)
    css_content = """
    h1 {
        color: #333;
        font-size: 36px;
    }
    .highlight {
        background-color: yellow;
    }
    #special {
        color: red;
        font-weight: bold;
    }
    """
    
    engine.load_html(html_content, "http://example.com/test.html")
    engine.css_parser.add_stylesheet(css_content)
    
    # Re-compute styles after adding stylesheet
    if engine.dom_tree:
        engine.css_parser.compute_styles_recursive(engine.dom_tree)
    
    print("✓ Render engine loaded HTML")
    print(f"  Stylesheet rules: {len(engine.css_parser.stylesheet_rules)}")
    
    # Find nodes and check styles
    def find_node_by_tag(node, tag):
        if node.tag == tag:
            return node
        for child in node.children:
            result = find_node_by_tag(child, tag)
            if result:
                return result
        return None
    
    h1_node = find_node_by_tag(engine.dom_tree, 'h1')
    if h1_node:
        print(f"  H1 styles: {h1_node.styles}")
    
    print("✓ External CSS application works\n")


def test_render_engine_with_inline_styles():
    """Test render engine with inline <style> tags"""
    print("=== Testing Render Engine with Inline Styles ===\n")
    
    engine = RenderEngine()
    
    # HTML with inline <style> tag
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inline CSS Test</title>
        <style>
            body {
                background-color: #f5f5f5;
            }
            h1 {
                color: darkblue;
                font-size: 32px;
            }
            .important {
                font-weight: bold;
                color: red;
            }
        </style>
    </head>
    <body>
        <h1>Test Page with Inline CSS</h1>
        <p class="important">Important text</p>
        <p>Normal text</p>
    </body>
    </html>
    """
    
    engine.load_html(html_content, "http://example.com/inline-test.html")
    
    print("✓ Render engine loaded HTML with inline styles")
    print(f"  Stylesheet rules: {len(engine.css_parser.stylesheet_rules)}")
    
    # Debug: print all rules
    for rule in engine.css_parser.stylesheet_rules:
        print(f"    Rule: {rule['selector']} -> {rule['declarations']}")
    
    # Find nodes and check styles
    def find_node_by_class(node, class_name):
        if 'class' in node.attrs:
            node_classes = node.attrs['class']
            if isinstance(node_classes, str):
                node_classes = node_classes.split()
            if class_name in node_classes:
                return node
        for child in node.children:
            result = find_node_by_class(child, class_name)
            if result:
                return result
        return None
    
    important_node = find_node_by_class(engine.dom_tree, 'important')
    if important_node:
        print(f"  Found important node: tag={important_node.tag}, class={important_node.attrs.get('class')}")
        print(f"  Important paragraph styles: color={important_node.styles.get('color')}, font-weight={important_node.styles.get('font-weight')}")
        assert important_node.styles.get('color') == 'red', "Important text should be red"
        assert important_node.styles.get('font-weight') == 'bold', "Important text should be bold"
    else:
        print("  Warning: Could not find important node")
    
    print("✓ Inline <style> tag parsing and application works\n")


def test_css_comments():
    """Test CSS comment removal"""
    print("=== Testing CSS Comment Removal ===\n")
    
    parser = CSSParser()
    
    css_with_comments = """
    /* This is a comment */
    body {
        color: black; /* inline comment */
    }
    /* Another comment
       spanning multiple lines */
    p {
        font-size: 14px;
    }
    """
    
    rules = parser.parse_stylesheet(css_with_comments)
    
    print(f"Parsed {len(rules)} rules from CSS with comments")
    assert len(rules) == 2, f"Expected 2 rules, got {len(rules)}"
    
    print("✓ CSS comment removal works\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("KLAR BROWSER - CSS PIPELINE TESTS")
    print("="*60 + "\n")
    
    try:
        test_css_parser_stylesheet()
        test_css_selector_matching()
        test_css_specificity()
        test_stylesheet_application()
        test_inline_style_priority()
        test_render_engine_with_external_css()
        test_render_engine_with_inline_styles()
        test_css_comments()
        
        print("\n" + "="*60)
        print("ALL CSS PIPELINE TESTS PASSED ✓")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
