"""
CSS Parser for styling support
"""
import re


class CSSParser:
    """Basic CSS parser for style computation"""
    
    def __init__(self):
        self.default_styles = {
            'font-size': '16px',
            'color': '#000000',
            'background-color': '#ffffff',
            'margin': '0px',
            'padding': '0px',
            'display': 'block',
            'font-family': 'Arial, sans-serif',
            'font-weight': 'normal',
        }
        
        # Default styles for common elements
        self.element_defaults = {
            'h1': {'font-size': '32px', 'font-weight': 'bold', 'margin': '10px 0'},
            'h2': {'font-size': '24px', 'font-weight': 'bold', 'margin': '8px 0'},
            'h3': {'font-size': '20px', 'font-weight': 'bold', 'margin': '6px 0'},
            'p': {'margin': '10px 0'},
            'a': {'color': '#0000ff', 'text-decoration': 'underline'},
            'strong': {'font-weight': 'bold'},
            'b': {'font-weight': 'bold'},
            'em': {'font-style': 'italic'},
            'i': {'font-style': 'italic'},
            'ul': {'margin': '10px 0', 'padding-left': '40px'},
            'ol': {'margin': '10px 0', 'padding-left': '40px'},
            'li': {'display': 'list-item'},
            'div': {'display': 'block'},
            'span': {'display': 'inline'},
            'body': {'margin': '8px'},
        }
        
    def parse_inline_style(self, style_string):
        """
        Parse inline CSS style string
        
        Args:
            style_string: CSS style string (e.g., "color: red; font-size: 12px")
            
        Returns:
            dict: Parsed styles
        """
        styles = {}
        if not style_string:
            return styles
            
        declarations = style_string.split(';')
        for decl in declarations:
            if ':' in decl:
                prop, value = decl.split(':', 1)
                styles[prop.strip().lower()] = value.strip()
        
        return styles
    
    def compute_styles(self, node):
        """
        Compute final styles for a DOM node
        
        Args:
            node: DOMNode instance
            
        Returns:
            dict: Computed styles
        """
        # Start with default styles
        styles = self.default_styles.copy()
        
        # Apply element-specific defaults
        if node.tag in self.element_defaults:
            styles.update(self.element_defaults[node.tag])
        
        # Apply inline styles
        if 'style' in node.attrs:
            inline_styles = self.parse_inline_style(node.attrs['style'])
            styles.update(inline_styles)
        
        # Store computed styles on the node
        node.styles = styles
        
        return styles
    
    def compute_styles_recursive(self, node):
        """
        Recursively compute styles for all nodes in the tree
        
        Args:
            node: Root DOMNode
        """
        self.compute_styles(node)
        for child in node.children:
            self.compute_styles_recursive(child)
    
    def parse_size(self, size_string, default=0):
        """
        Parse a size value (e.g., "10px", "1em")
        
        Args:
            size_string: Size string
            default: Default value if parsing fails
            
        Returns:
            float: Parsed size in pixels
        """
        if not size_string:
            return default
            
        # Extract numeric value
        match = re.match(r'([-\d.]+)(px|em|%)?', str(size_string))
        if match:
            value = float(match.group(1))
            unit = match.group(2) or 'px'
            
            if unit == 'px':
                return value
            elif unit == 'em':
                return value * 16  # Assume 16px base font size
            elif unit == '%':
                return value  # Return percentage as-is
        
        return default
