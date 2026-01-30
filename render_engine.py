"""
Custom Render Engine - Core rendering pipeline
"""
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPixmap
from PyQt6.QtCore import Qt, QRect, QPoint
from html_parser import HTMLParserEngine
from css_parser import CSSParser
from resource_loader import ResourceLoader

# Rendering constants
DEFAULT_LINE_SPACING = 5  # Vertical spacing between lines of text
DEFAULT_RECT_HEIGHT = 100  # Default height for text bounding rectangle
DEFAULT_BG_HEIGHT = 50  # Default background block height


class RenderEngine:
    """
    Custom rendering engine that replaces QT WebEngine
    Handles the complete rendering pipeline from HTML to pixels
    """
    
    def __init__(self):
        self.html_parser = HTMLParserEngine()
        self.css_parser = CSSParser()
        self.resource_loader = ResourceLoader()
        self.dom_tree = None
        self.current_url = None
        self.loaded_resources = {
            'images': {},
            'videos': {},
            'css': [],
            'scripts': []
        }
        
    def load_html(self, html_content, url=None):
        """
        Load and parse HTML content
        
        Args:
            html_content: HTML string
            url: Source URL (for reference)
        """
        self.current_url = url
        self.dom_tree = self.html_parser.parse(html_content)
        
        # Extract and load external resources
        if self.dom_tree and url:
            self._load_external_resources()
        
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
        
        # Handle special rendering for images and videos
        if node.tag == 'img':
            self._render_image(node, context)
            return
        
        if node.tag == 'video':
            self._render_video(node, context)
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
        saved_x = context.x
        context.x += padding
        
        # Render children
        for child in node.children:
            self._render_node(child, context)
        
        # Restore x position after rendering children
        context.x = saved_x
        
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
            rect = QRect(int(context.x), int(context.y), int(context.viewport_width - context.x), DEFAULT_RECT_HEIGHT)
            context.painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)
            
            # Move cursor down
            metrics = context.painter.fontMetrics()
            text_height = metrics.boundingRect(rect, Qt.TextFlag.TextWordWrap, text).height()
            context.y += text_height + DEFAULT_LINE_SPACING
    
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
            QRect(int(context.x), int(context.y), int(context.viewport_width), DEFAULT_BG_HEIGHT),
            QBrush(color)
        )
    
    def _load_external_resources(self):
        """Load external resources from the DOM tree"""
        if not self.dom_tree or not self.current_url:
            return
        
        # Extract resources from DOM
        resources = self.resource_loader.extract_resources_from_html(
            self.dom_tree, 
            self.current_url
        )
        
        # Load images
        for img_url in resources['images']:
            pixmap = self.resource_loader.load_image(img_url, self.current_url)
            if pixmap:
                self.loaded_resources['images'][img_url] = pixmap
        
        # Load CSS files
        for css_url in resources['css']:
            css_content = self.resource_loader.load_css(css_url, self.current_url)
            if css_content:
                self.loaded_resources['css'].append(css_content)
                # TODO: Parse and apply external CSS styles
        
        # Load JavaScript files (for completeness, not executed)
        for js_url in resources['scripts']:
            js_content = self.resource_loader.load_script(js_url, self.current_url)
            if js_content:
                self.loaded_resources['scripts'].append(js_content)
        
        # Load video metadata
        for video_url in resources['videos']:
            video_meta = self.resource_loader.load_video_metadata(video_url, self.current_url)
            if video_meta:
                self.loaded_resources['videos'][video_url] = video_meta
    
    def _render_image(self, node, context):
        """
        Render an image node
        
        Args:
            node: Image DOMNode
            context: RenderContext
        """
        src = node.get_attr('src')
        if not src:
            return
        
        # Resolve URL
        from urllib.parse import urljoin
        if self.current_url and not src.startswith('data:'):
            img_url = urljoin(self.current_url, src)
        else:
            img_url = src
        
        # Get pixmap from loaded resources or load it now
        pixmap = self.loaded_resources['images'].get(img_url)
        if not pixmap:
            pixmap = self.resource_loader.load_image(src, self.current_url)
            if pixmap:
                self.loaded_resources['images'][img_url] = pixmap
        
        if pixmap and not pixmap.isNull():
            # Get image dimensions
            width = node.get_attr('width')
            height = node.get_attr('height')
            
            # Calculate scaled dimensions
            img_width = int(width) if width and width.isdigit() else pixmap.width()
            img_height = int(height) if height and height.isdigit() else pixmap.height()
            
            # Limit maximum size
            max_width = int(context.viewport_width - context.x - 20)
            if img_width > max_width:
                # Scale proportionally
                scale = max_width / img_width
                img_width = max_width
                img_height = int(img_height * scale)
            
            # Draw the image
            target_rect = QRect(int(context.x), int(context.y), img_width, img_height)
            context.painter.drawPixmap(target_rect, pixmap)
            
            # Move cursor down
            context.y += img_height + DEFAULT_LINE_SPACING
            
            # Get alt text in case image fails to display
            alt_text = node.get_attr('alt')
            if alt_text:
                # Store for potential fallback
                pass
        else:
            # Render alt text or placeholder if image fails
            alt_text = node.get_attr('alt', '[Image]')
            self._render_image_placeholder(alt_text, context)
    
    def _render_image_placeholder(self, text, context):
        """
        Render a placeholder for failed images
        
        Args:
            text: Placeholder text (usually alt text)
            context: RenderContext
        """
        # Draw a simple rectangle with text
        placeholder_width = 200
        placeholder_height = 100
        
        # Draw border
        context.painter.setPen(QPen(QColor('#cccccc'), 2))
        context.painter.setBrush(QBrush(QColor('#f0f0f0')))
        rect = QRect(int(context.x), int(context.y), placeholder_width, placeholder_height)
        context.painter.drawRect(rect)
        
        # Draw text
        context.painter.setPen(QPen(QColor('#666666')))
        font = QFont('Arial', 10)
        context.painter.setFont(font)
        context.painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)
        
        # Move cursor down
        context.y += placeholder_height + DEFAULT_LINE_SPACING
    
    def _render_video(self, node, context):
        """
        Render a video node (as a placeholder with play icon)
        
        Args:
            node: Video DOMNode
            context: RenderContext
        """
        src = node.get_attr('src')
        
        # Check for source children if no src attribute
        if not src:
            for child in node.children:
                if child.tag == 'source':
                    src = child.get_attr('src')
                    if src:
                        break
        
        if not src:
            return
        
        # Resolve URL
        from urllib.parse import urljoin
        if self.current_url:
            video_url = urljoin(self.current_url, src)
        else:
            video_url = src
        
        # Get video dimensions
        width = node.get_attr('width')
        height = node.get_attr('height')
        
        video_width = int(width) if width and width.isdigit() else 400
        video_height = int(height) if height and height.isdigit() else 300
        
        # Limit maximum size
        max_width = int(context.viewport_width - context.x - 20)
        if video_width > max_width:
            scale = max_width / video_width
            video_width = max_width
            video_height = int(video_height * scale)
        
        # Draw video placeholder
        rect = QRect(int(context.x), int(context.y), video_width, video_height)
        
        # Draw background
        context.painter.setPen(QPen(QColor('#333333'), 2))
        context.painter.setBrush(QBrush(QColor('#000000')))
        context.painter.drawRect(rect)
        
        # Draw play icon (triangle)
        center_x = rect.center().x()
        center_y = rect.center().y()
        play_size = min(video_width, video_height) // 4
        
        from PyQt6.QtGui import QPolygon
        play_triangle = QPolygon([
            QPoint(center_x - play_size // 2, center_y - play_size // 2),
            QPoint(center_x - play_size // 2, center_y + play_size // 2),
            QPoint(center_x + play_size // 2, center_y)
        ])
        
        context.painter.setPen(QPen(QColor('#ffffff')))
        context.painter.setBrush(QBrush(QColor('#ffffff')))
        context.painter.drawPolygon(play_triangle)
        
        # Draw video URL below
        context.painter.setPen(QPen(QColor('#666666')))
        font = QFont('Arial', 9)
        context.painter.setFont(font)
        text_rect = QRect(int(context.x), int(context.y + video_height + 5), video_width, 20)
        context.painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, f"Video: {src}")
        
        # Move cursor down
        context.y += video_height + 30


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
