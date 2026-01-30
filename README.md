# Klar - Custom Render Engine Browser

A custom web browser with a built-from-scratch render engine to replace QT WebEngine.

## Features

- Custom HTML parser and renderer
- Basic CSS support
- URL navigation
- HTTP/HTTPS request handling
- Custom rendering pipeline (no WebEngine dependency)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Enter a URL in the address bar and press Enter to navigate to the website.

## Architecture

- `main.py` - Main application entry point
- `render_engine.py` - Core rendering engine
- `html_parser.py` - HTML parsing and DOM construction
- `css_parser.py` - CSS parsing and style computation
- `http_client.py` - HTTP request handler
- `browser_window.py` - Main browser window UI

## Testing

To test the render engine, simply run the application and navigate to any URL (e.g., http://example.com).
