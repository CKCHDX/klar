"""
CSS Parser for styling support
"""
import re

# CSS constants
BASE_FONT_SIZE_PX = 16  # Base font size for em unit conversion


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
        
        # Parsed CSS rules from stylesheets
        self.stylesheet_rules = []
        
    def parse_stylesheet(self, css_content):
        """
        Parse CSS stylesheet and extract rules
        
        Args:
            css_content: CSS stylesheet string
            
        Returns:
            list: List of CSS rules (selector, declarations)
        """
        rules = []
        if not css_content:
            return rules
        
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Match CSS rules: selector { declarations }
        # This is a simple parser that handles basic cases
        rule_pattern = r'([^{]+)\{([^}]+)\}'
        matches = re.finditer(rule_pattern, css_content)
        
        for match in matches:
            selector = match.group(1).strip()
            declarations_str = match.group(2).strip()
            
            # Parse declarations
            declarations = self.parse_inline_style(declarations_str)
            
            if selector and declarations:
                rules.append({
                    'selector': selector,
                    'declarations': declarations,
                    'specificity': self._calculate_specificity(selector)
                })
        
        return rules
    
    def add_stylesheet(self, css_content):
        """
        Add a stylesheet to be applied to all nodes
        
        Args:
            css_content: CSS stylesheet string
        """
        rules = self.parse_stylesheet(css_content)
        self.stylesheet_rules.extend(rules)
    
    def clear_stylesheets(self):
        """Clear all loaded stylesheets"""
        self.stylesheet_rules = []
    
    def _calculate_specificity(self, selector):
        """
        Calculate CSS selector specificity
        Returns (id_count, class_count, element_count)
        
        Args:
            selector: CSS selector string
            
        Returns:
            tuple: (id_count, class_count, element_count)
            
        Note:
            This is a simplified specificity calculation for basic selectors.
            It works correctly for simple selectors (element, .class, #id)
            but may not handle complex compound selectors perfectly.
            For compound selectors like 'div.class', the element part may not be counted.
        """
        # Simple specificity calculation
        # More specific = higher priority
        id_count = selector.count('#')
        class_count = selector.count('.')
        # Count element selectors (parts that don't contain . or #)
        element_count = len([s for s in selector.split() if s and '.' not in s and '#' not in s])
        
        return (id_count, class_count, element_count)
    
    def _selector_matches(self, selector, node):
        """
        Check if a CSS selector matches a DOM node
        
        Args:
            selector: CSS selector string
            node: DOMNode instance
            
        Returns:
            bool: True if selector matches
        """
        # Handle simple selectors only for now
        selector = selector.strip()
        
        # Universal selector
        if selector == '*':
            return True
        
        # ID selector (#id)
        if selector.startswith('#'):
            node_id = node.get_attr('id', '')
            return node_id == selector[1:]
        
        # Class selector (.class)
        if selector.startswith('.'):
            node_classes = node.get_attr('class', '')
            # Handle both list and string formats
            if isinstance(node_classes, list):
                # BeautifulSoup returns a list for class attribute - use directly
                return selector[1:] in node_classes
            elif isinstance(node_classes, str):
                node_classes = node_classes.split()
                return selector[1:] in node_classes
            else:
                return False
        
        # Element selector
        return selector.lower() == node.tag.lower()
    
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
            
        Note:
            This method has O(M) complexity where M is the number of stylesheet rules.
            For very large stylesheets, consider pre-sorting rules by specificity
            or implementing selector indexing for better performance.
        """
        # Start with default styles
        styles = self.default_styles.copy()
        
        # Apply element-specific defaults
        if node.tag in self.element_defaults:
            styles.update(self.element_defaults[node.tag])
        
        # Apply stylesheet rules (in order, sorted by specificity)
        matching_rules = []
        for rule in self.stylesheet_rules:
            if self._selector_matches(rule['selector'], node):
                matching_rules.append(rule)
        
        # Sort by specificity (lower specificity first, so higher overrides)
        matching_rules.sort(key=lambda r: r['specificity'])
        
        # Apply each matching rule
        for rule in matching_rules:
            styles.update(rule['declarations'])
        
        # Apply inline styles (highest priority)
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
                return value * BASE_FONT_SIZE_PX
            elif unit == '%':
                return value  # Return percentage as-is
        
        return default
