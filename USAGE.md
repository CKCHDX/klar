# Klar Browser - Usage Guide

## Overview

Klar is a custom web browser built from scratch with its own rendering engine, completely replacing QT WebEngine. It demonstrates how to build a browser with custom HTML parsing, CSS styling, and page rendering.

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt6
- Additional dependencies (see requirements.txt)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/CKCHDX/klar.git
cd klar
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Browser

### Start the Browser

```bash
python main.py
```

### Using the Browser

1. **Enter a URL**: Type a URL in the address bar (e.g., `example.com` or `http://example.com`)
2. **Navigate**: Press Enter or click the "Go" button
3. **Navigation Controls**:
   - **← (Back)**: Go back to the previous page
   - **→ (Forward)**: Go forward to the next page
   - **⟳ (Refresh)**: Reload the current page

### Testing the Render Engine

#### Test with Default Page
```bash
python test_render.py
```
This will create screenshots showing the default welcome page and a custom test page.

#### Test with HTML Content
The browser automatically loads a welcome page on startup that demonstrates:
- Heading rendering (h1, h2, h3)
- Paragraph formatting
- Bold and italic text
- Lists
- Basic layout

## Architecture

### Core Components

1. **`main.py`** - Application entry point
2. **`browser_window.py`** - Main browser window and UI
3. **`render_engine.py`** - Core rendering pipeline
4. **`html_parser.py`** - HTML parsing and DOM tree construction
5. **`css_parser.py`** - CSS parsing and style computation
6. **`http_client.py`** - HTTP/HTTPS request handling

### How the Render Engine Works

1. **HTML Parsing**: The HTML parser converts HTML text into a DOM tree structure
2. **Style Computation**: CSS parser computes styles for each DOM node
3. **Layout**: The render engine determines positioning and sizing
4. **Painting**: Content is painted to the viewport using PyQt6's QPainter

### Supported Features

✅ **HTML Elements**:
- Headers (h1, h2, h3, etc.)
- Paragraphs (p)
- Lists (ul, ol, li)
- Text formatting (strong, b, em, i)
- Divs and spans
- Links (a)

✅ **CSS Properties**:
- Font size
- Font family
- Font weight (bold)
- Font style (italic)
- Color
- Background color
- Margin
- Padding
- Display (block/inline)

✅ **Browser Features**:
- URL navigation
- History (back/forward)
- Page refresh
- Address bar
- Status bar
- Scrollable viewport

## Limitations

This is a demonstration render engine with some limitations:

- **Limited CSS Support**: Only basic CSS properties are supported
- **No JavaScript**: JavaScript execution is not implemented
- **Simple Layout**: Complex layouts may not render correctly
- **No Image Loading**: Images are not currently rendered
- **Text-Only**: Best suited for text-based content

## Testing URLs

Good websites to test with simple HTML:
- `example.com` - Very simple HTML page
- `info.cern.ch` - Historic first website
- Simple text-based websites

## Development

### Adding New Features

To extend the render engine:

1. **Add HTML Element Support**: Modify `html_parser.py` to handle new elements
2. **Add CSS Properties**: Extend `css_parser.py` with new style properties
3. **Enhance Rendering**: Update `render_engine.py` to render new features

### Testing

Run the test scripts to verify functionality:

```bash
# Test basic rendering
python test_render.py

# Test with a domain (requires network access)
python test_domain.py
```

## Troubleshooting

### "libEGL.so.1: cannot open shared object file"

Install required system libraries:
```bash
sudo apt-get install libegl1 libxkbcommon-x11-0 libxcb-cursor0
```

### "Could not load the Qt platform plugin"

Try setting the platform explicitly:
```bash
export QT_QPA_PLATFORM=offscreen
python main.py
```

## License

This project is a demonstration of a custom render engine architecture.
