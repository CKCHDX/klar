"""
Resource Loader - Handles loading external resources (images, videos, CSS, JS)
"""
from urllib.parse import urljoin, urlparse
from http_client import HTTPClient
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray
import base64
import re


class ResourceLoader:
    """Manages loading and caching of external resources"""
    
    def __init__(self, http_client=None):
        self.http_client = http_client or HTTPClient()
        # Separate caches for different resource types to avoid collisions
        self.image_cache = {}
        self.css_cache = {}
        self.js_cache = {}
        self.video_cache = {}
        
    def load_image(self, url, base_url=None):
        """
        Load an image from a URL or data URI
        
        Args:
            url: Image URL or data URI
            base_url: Base URL for resolving relative URLs
            
        Returns:
            QPixmap or None if loading fails
        """
        # Handle data URIs
        if url.startswith('data:'):
            return self._load_data_uri_image(url)
        
        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)
        
        # Check cache
        if url in self.image_cache:
            return self.image_cache[url]
        
        # Fetch image
        response = self.http_client.fetch(url, binary=True)
        if response['success'] and response['content']:
            # Create QPixmap from binary data
            pixmap = self._bytes_to_pixmap(response['content'])
            if pixmap and not pixmap.isNull():
                self.image_cache[url] = pixmap
                return pixmap
        
        return None
    
    def load_css(self, url, base_url=None):
        """
        Load CSS from an external URL
        
        Args:
            url: CSS file URL
            base_url: Base URL for resolving relative URLs
            
        Returns:
            str: CSS content or None if loading fails
        """
        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)
        
        # Check cache
        if url in self.css_cache:
            return self.css_cache[url]
        
        # Fetch CSS
        response = self.http_client.fetch(url, binary=False)
        if response['success'] and response['content']:
            self.css_cache[url] = response['content']
            return response['content']
        
        return None
    
    def load_script(self, url, base_url=None):
        """
        Load JavaScript from an external URL
        
        Args:
            url: JavaScript file URL
            base_url: Base URL for resolving relative URLs
            
        Returns:
            str: JavaScript content or None if loading fails
        """
        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)
        
        # Check cache
        if url in self.js_cache:
            return self.js_cache[url]
        
        # Fetch JavaScript
        response = self.http_client.fetch(url, binary=False)
        if response['success'] and response['content']:
            self.js_cache[url] = response['content']
            return response['content']
        
        return None
    
    def load_video_metadata(self, url, base_url=None):
        """
        Load video metadata (we don't fully load videos, just metadata)
        
        Args:
            url: Video URL
            base_url: Base URL for resolving relative URLs
            
        Returns:
            dict: Video metadata (url, content_type, etc.)
        """
        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)
        
        # We'll just store the URL and basic info
        # Full video loading would require a video player widget
        return {
            'url': url,
            'type': self._get_video_type(url),
            'loaded': True
        }
    
    def _load_data_uri_image(self, data_uri):
        """
        Load an image from a data URI
        
        Args:
            data_uri: Data URI string (e.g., data:image/png;base64,...)
            
        Returns:
            QPixmap or None
        """
        try:
            # Parse data URI: data:[<mediatype>][;base64],<data>
            match = re.match(r'data:([^;,]+)?(;base64)?,(.+)', data_uri)
            if not match:
                return None
            
            media_type = match.group(1) or 'text/plain'
            is_base64 = match.group(2) is not None
            data = match.group(3)
            
            if is_base64:
                # Decode base64
                image_data = base64.b64decode(data)
                return self._bytes_to_pixmap(image_data)
            else:
                # URL-encoded data (less common for images)
                return None
                
        except Exception as e:
            print(f"Error loading data URI image: {e}")
            return None
    
    def _bytes_to_pixmap(self, image_bytes):
        """
        Convert bytes to QPixmap
        
        Args:
            image_bytes: Image binary data
            
        Returns:
            QPixmap or None
        """
        try:
            byte_array = QByteArray(image_bytes)
            image = QImage.fromData(byte_array)
            if not image.isNull():
                return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error converting bytes to pixmap: {e}")
        return None
    
    def _get_video_type(self, url):
        """
        Determine video type from URL
        
        Args:
            url: Video URL
            
        Returns:
            str: Video type (mp4, webm, ogg, etc.)
        """
        url_lower = url.lower()
        if url_lower.endswith('.mp4'):
            return 'video/mp4'
        elif url_lower.endswith('.webm'):
            return 'video/webm'
        elif url_lower.endswith('.ogg') or url_lower.endswith('.ogv'):
            return 'video/ogg'
        elif url_lower.endswith('.avi'):
            return 'video/x-msvideo'
        elif url_lower.endswith('.mov'):
            return 'video/quicktime'
        else:
            return 'video/unknown'
    
    def extract_resources_from_html(self, dom_tree, base_url=None):
        """
        Extract all resource URLs from a DOM tree
        
        Args:
            dom_tree: DOM tree root node
            base_url: Base URL for resolving relative URLs
            
        Returns:
            dict: Dictionary of resource lists by type (deduplicated)
        """
        resources = {
            'images': set(),
            'videos': set(),
            'css': set(),
            'scripts': set()
        }
        
        self._extract_resources_recursive(dom_tree, resources, base_url)
        
        # Convert sets back to lists
        return {
            'images': list(resources['images']),
            'videos': list(resources['videos']),
            'css': list(resources['css']),
            'scripts': list(resources['scripts'])
        }
    
    def _extract_resources_recursive(self, node, resources, base_url):
        """
        Recursively extract resources from DOM tree
        
        Args:
            node: DOM node
            resources: Resources dictionary to populate
            base_url: Base URL for resolving relative URLs
        """
        if not node:
            return
        
        # Extract based on tag type
        if node.tag == 'img':
            src = node.get_attr('src')
            if src:
                full_url = urljoin(base_url, src) if base_url else src
                resources['images'].add(full_url)
        
        elif node.tag == 'video':
            src = node.get_attr('src')
            if src:
                full_url = urljoin(base_url, src) if base_url else src
                resources['videos'].add(full_url)
            # Also check for <source> children
            for child in node.children:
                if child.tag == 'source':
                    src = child.get_attr('src')
                    if src:
                        full_url = urljoin(base_url, src) if base_url else src
                        resources['videos'].add(full_url)
        
        elif node.tag == 'link':
            rel = node.get_attr('rel')
            if rel and 'stylesheet' in rel:
                href = node.get_attr('href')
                if href:
                    full_url = urljoin(base_url, href) if base_url else href
                    resources['css'].add(full_url)
        
        elif node.tag == 'script':
            src = node.get_attr('src')
            if src:
                full_url = urljoin(base_url, src) if base_url else src
                resources['scripts'].add(full_url)
        
        # Process children
        for child in node.children:
            self._extract_resources_recursive(child, resources, base_url)
    
    def clear_cache(self):
        """Clear all resource caches"""
        self.image_cache.clear()
        self.css_cache.clear()
        self.js_cache.clear()
        self.video_cache.clear()
