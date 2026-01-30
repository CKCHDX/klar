#!/usr/bin/env python3
"""
Demonstration of resource loading with screenshots
"""
import sys
import os

# Set offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtCore import QSize
from render_engine import RenderEngine

def create_demo_page_with_resources():
    """Create a demo page showcasing all resource types"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Klar Browser Resource Loading Demo</title>
    <link rel="stylesheet" href="https://example.com/styles.css">
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: #0066cc; }
        .highlight { background-color: #ffffcc; padding: 10px; }
    </style>
</head>
<body>
    <h1>Klar Browser - Resource Loading Demo</h1>
    
    <div class="highlight">
        <p><strong>This page demonstrates loading of:</strong></p>
        <ul>
            <li>Images from data URIs</li>
            <li>External images (when online)</li>
            <li>Video elements with placeholders</li>
            <li>External CSS stylesheets</li>
            <li>External JavaScript files</li>
        </ul>
    </div>
    
    <h2>1. Data URI Image</h2>
    <p>This is a small red dot loaded from a data URI:</p>
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot (5x5)" width="50" height="50">
    
    <h2>2. Video Element</h2>
    <p>Video elements are rendered with a play button placeholder:</p>
    <video width="400" height="300" src="https://example.com/sample-video.mp4" controls>
        Your browser does not support the video tag.
    </video>
    
    <h2>3. Multiple Video Sources</h2>
    <p>Videos can have multiple source formats:</p>
    <video width="400" height="300" controls>
        <source src="https://example.com/video.mp4" type="video/mp4">
        <source src="https://example.com/video.webm" type="video/webm">
        <source src="https://example.com/video.ogg" type="video/ogg">
        Your browser does not support the video tag.
    </video>
    
    <h2>4. External Resources</h2>
    <p>This page also attempts to load:</p>
    <ul>
        <li><strong>CSS:</strong> External stylesheet (https://example.com/styles.css)</li>
        <li><strong>JavaScript:</strong> External script file (see script tag below)</li>
    </ul>
    
    <h3>Image Placeholder Example</h3>
    <p>When an image fails to load, a placeholder is shown:</p>
    <img src="https://example.com/missing-image.jpg" alt="This image doesn't exist" width="200">
    
    <h2>5. Supported Protocols</h2>
    <p>The browser supports:</p>
    <ul>
        <li><strong>HTTP:</strong> http:// URLs</li>
        <li><strong>HTTPS:</strong> https:// URLs (secure)</li>
        <li><strong>Data URIs:</strong> data:image/... for embedded images</li>
    </ul>
    
    <h2>Summary</h2>
    <p><em>All resource types are now loaded and rendered by Klar Browser!</em></p>
    
    <script src="https://example.com/app.js"></script>
</body>
</html>
"""

def render_to_image(html_content, url, output_file, width=800, height=1200):
    """Render HTML to an image file"""
    engine = RenderEngine()
    engine.load_html(html_content, url)
    
    # Create image
    image = QImage(QSize(width, height), QImage.Format.Format_ARGB32)
    image.fill(0xffffffff)  # White background
    
    # Create painter
    painter = QPainter(image)
    
    # Render
    engine.render(painter, width, height)
    
    painter.end()
    
    # Save image
    image.save(output_file)
    print(f"✓ Saved screenshot to {output_file}")

def main():
    """Main demo function"""
    print("\n" + "="*60)
    print("KLAR BROWSER - RESOURCE LOADING DEMONSTRATION")
    print("="*60 + "\n")
    
    # Create QApplication (required for rendering)
    app = QApplication(sys.argv)
    
    print("Creating demo page with various resources...")
    html = create_demo_page_with_resources()
    
    print("Rendering demo page...")
    render_to_image(
        html, 
        "http://localhost/demo.html",
        "resource_loading_demo.png",
        width=800,
        height=2400
    )
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nScreenshot saved: resource_loading_demo.png")
    print("\nThe browser now supports:")
    print("  ✓ Images (HTTP, HTTPS, data URIs)")
    print("  ✓ Videos (placeholder rendering)")
    print("  ✓ External CSS loading")
    print("  ✓ External JavaScript loading")
    print("  ✓ Resource caching")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
