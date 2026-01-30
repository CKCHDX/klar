"""
HTML Parser for building DOM structure
"""
from html.parser import HTMLParser
from bs4 import BeautifulSoup


class DOMNode:
    """Represents a node in the DOM tree"""
    
    def __init__(self, tag, attrs=None, text=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.text = text
        self.children = []
        self.parent = None
        self.styles = {}
        
    def add_child(self, child):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
        
    def get_attr(self, name, default=None):
        """Get an attribute value"""
        return self.attrs.get(name, default)
    
    def __repr__(self):
        return f"<DOMNode {self.tag}>"


class HTMLParserEngine:
    """Parses HTML and builds a DOM tree"""
    
    def __init__(self):
        self.root = None
        
    def parse(self, html_content):
        """
        Parse HTML content and build DOM tree
        
        Args:
            html_content: HTML string
            
        Returns:
            DOMNode: Root node of the DOM tree
        """
        soup = BeautifulSoup(html_content, 'html5lib')
        self.root = self._build_dom_tree(soup)
        return self.root
    
    def _build_dom_tree(self, element, parent=None):
        """
        Recursively build DOM tree from BeautifulSoup element
        
        Args:
            element: BeautifulSoup element
            parent: Parent DOMNode
            
        Returns:
            DOMNode: Created DOM node
        """
        # Handle text nodes
        if isinstance(element, str):
            text = element.strip()
            if text:
                return DOMNode('text', text=text)
            return None
        
        # Create DOM node for element
        tag_name = element.name if hasattr(element, 'name') else 'unknown'
        attrs = dict(element.attrs) if hasattr(element, 'attrs') else {}
        
        node = DOMNode(tag_name, attrs)
        
        # Process children
        if hasattr(element, 'children'):
            for child in element.children:
                child_node = self._build_dom_tree(child, node)
                if child_node:
                    node.add_child(child_node)
        
        return node
    
    def find_body(self, root):
        """Find the body element in the DOM tree"""
        if root.tag == 'body':
            return root
        for child in root.children:
            result = self.find_body(child)
            if result:
                return result
        return None
    
    def find_head(self, root):
        """Find the head element in the DOM tree"""
        if root.tag == 'head':
            return root
        for child in root.children:
            result = self.find_head(child)
            if result:
                return result
        return None
