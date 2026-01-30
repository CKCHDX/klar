"""
Custom Render Engine - Core rendering pipeline
"""
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QRect, QPoint
from html_parser import HTMLParserEngine
from css_parser import CSSParser


class RenderEngine:
    """
    Custom rendering engine that replaces QT WebEngine
    Handles the complete rendering pipeline from HTML to pixels
    """
    
    def __init__(self):
        self.html_parser = HTMLParserEngine()
        self.css_parser = CSSParser()
        self.dom_tree = None
        self.current_url = None
        
    def load_html(self, html_content, url=None):
        """
        Load and parse HTML content
        
        Args:
            html_content: HTML string
            url: Source URL (for reference)
        """
        self.current_url = url
        self.dom_tree = self.html_parser.parse(html_content)
        
        # Compute styles for all nodes
        if self.dom_tree:
            self.css_parser.compute_styles_recursive(self.dom_tree)
    
    def render(self, painter, viewport_width, viewport_height):
        """
        Render the DOM tree to the given painter
        
        Args:
            painter: QPainter instance
            viewport_width: Width of the viewport
            viewport_height: Height of the viewport
        """
        if not self.dom_tree:
            return
        
        # Find body element
        body = self.html_parser.find_body(self.dom_tree)
        if not body:
            # If no body, use root
            body = self.dom_tree
        
        # Start rendering from body
        context = RenderContext(
            painter=painter,
            x=0,
            y=0,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        )
        
        self._render_node(body, context)
    
    def _render_node(self, node, context):
        """
        Recursively render a DOM node and its children
        
        Args:
            node: DOMNode to render
            context: RenderContext with current rendering state
        """
        if node.tag == 'text':
            self._render_text(node, context)
            return
        
        # Skip certain elements
        if node.tag in ['head', 'script', 'style', 'meta', 'link']:
            return
        
        # Get computed styles
        styles = node.styles
        
        # Parse margin and padding
        margin = self.css_parser.parse_size(styles.get('margin', '0'), 0)
        padding = self.css_parser.parse_size(styles.get('padding', '0'), 0)
        
        # Apply margin
        context.y += margin
        
        # Render background if specified
        bg_color = styles.get('background-color', '#ffffff')
        if bg_color != '#ffffff' and bg_color != 'transparent':
            self._render_background(node, context, bg_color)
        
        # Save position before rendering children
        start_y = context.y
        
        # Apply padding
        context.y += padding
        context.x += padding
        
        # Render children
        for child in node.children:
            self._render_node(child, context)
        
        # Apply bottom margin
        context.y += margin
        
        # For block elements, move to next line
        display = styles.get('display', 'block')
        if display == 'block':
            context.x = 0
    
    def _render_text(self, node, context):
        """
        Render a text node
        
        Args:
            node: Text DOMNode
            context: RenderContext
        """
        if not node.text or not node.text.strip():
            return
        
        # Get styles from parent
        parent = node.parent
        if not parent:
            return
        
        styles = parent.styles
        
        # Set up font
        font_size = self.css_parser.parse_size(styles.get('font-size', '16px'), 16)
        font_family = styles.get('font-family', 'Arial')
        font_weight = styles.get('font-weight', 'normal')
        
        font = QFont(font_family.split(',')[0].strip(), int(font_size))
        if font_weight == 'bold':
            font.setBold(True)
        
        context.painter.setFont(font)
        
        # Set text color
        color = styles.get('color', '#000000')
        context.painter.setPen(QPen(QColor(color)))
        
        # Draw text
        text = node.text.strip()
        if text:
            # Simple text rendering (no word wrap for now)
            rect = QRect(context.x, context.y, context.viewport_width - context.x, 100)
            context.painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)
            
            # Move cursor down
            metrics = context.painter.fontMetrics()
            text_height = metrics.boundingRect(rect, Qt.TextFlag.TextWordWrap, text).height()
            context.y += text_height + 5
    
    def _render_background(self, node, context, bg_color):
        """
        Render background color for a node
        
        Args:
            node: DOMNode
            context: RenderContext
            bg_color: Background color
        """
        color = QColor(bg_color)
        context.painter.fillRect(
            QRect(context.x, context.y, context.viewport_width, 50),
            QBrush(color)
        )


class RenderContext:
    """
    Rendering context that tracks current position and state
    """
    
    def __init__(self, painter, x, y, viewport_width, viewport_height):
        self.painter = painter
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
