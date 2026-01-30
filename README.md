# Klar - Custom Render Engine Browser

A custom web browser with a built-from-scratch render engine to replace QT WebEngine.

## Features

- ✅ **Custom HTML Parser** - Built from scratch using BeautifulSoup and html5lib
- ✅ **Custom Rendering Pipeline** - No QT WebEngine dependency
- ✅ **CSS Support** - Basic CSS parsing and style computation
- ✅ **URL Navigation** - Enter domains in the address bar
- ✅ **HTTP/HTTPS Support** - Fetch content from the web
- ✅ **Browser Controls** - Back, forward, and refresh navigation
- ✅ **DOM Tree Construction** - Full HTML document object model
- ✅ **Text Rendering** - Headers, paragraphs, lists, and formatting
- ✅ **Image Loading** - Support for images from HTTP/HTTPS and data URIs
- ✅ **Video Support** - Video elements with visual placeholders
- ✅ **External Resources** - Loads external CSS and JavaScript files
- ✅ **Resource Caching** - In-memory caching of loaded resources

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Browser

```bash
python main.py
```

Enter a URL in the address bar (e.g., `example.com`) and press Enter to navigate.

## Screenshots

The browser successfully renders:
- HTML headings with proper sizing
- Paragraphs with spacing
- Bold and italic text
- Lists (ordered and unordered)
- Navigation controls
- Scrollable content viewport

## Architecture

### Core Components

- `main.py` - Application entry point
- `browser_window.py` - Main browser window UI
- `render_engine.py` - Core rendering engine and pipeline
- `html_parser.py` - HTML parsing and DOM tree construction
- `css_parser.py` - CSS parsing and style computation
- `http_client.py` - HTTP/HTTPS request handler
- `resource_loader.py` - External resource loading and caching

### How It Works

1. **Fetch** - HTTP client fetches HTML content from URLs
2. **Parse** - HTML parser builds a DOM tree structure
3. **Load Resources** - Resource loader fetches external images, videos, CSS, and JavaScript
4. **Style** - CSS parser computes styles for each node
5. **Render** - Render engine paints content to the viewport

## Testing

### Test the Render Engine

```bash
# Test with sample HTML
python test_render.py

# Test with a domain (requires network)
python test_domain.py
```

### Automated Testing

The test scripts will:
1. Load HTML content
2. Render to the viewport
3. Generate screenshots
4. Verify rendering functionality

## Documentation

For detailed usage instructions, see [USAGE.md](USAGE.md)

## Project Goal

This project demonstrates how to build a custom render engine from scratch, replacing QT WebEngine with a pure Python implementation. It's designed for:
- Learning how browsers work
- Understanding rendering pipelines
- Testing custom HTML rendering
- Educational purposes

## Limitations

- Basic CSS support (no complex layouts)
- No JavaScript execution
- Video elements show placeholders (no video playback)
- Best for simple HTML documents

## Contributing

This is a demonstration project showing render engine architecture and implementation.
