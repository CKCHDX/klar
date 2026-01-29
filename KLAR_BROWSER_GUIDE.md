# Klar Browser - User Guide

## Overview
Klar Browser is a lightweight, feature-rich browser client for the KSE (Klar Search Engine). It provides a clean and intuitive interface for searching and browsing content indexed by the search engine.

## Features

### 🔍 Search Functionality
- **Fast Search**: Real-time search with loading indicators
- **Rich Results**: Display title, URL, snippet, and relevance score
- **Result Details**: Click any result to view full content
- **Search History**: Track and revisit previous searches

### 🎨 User Interface
- **Modern Design**: Clean and responsive interface
- **Keyboard Shortcuts**: Quick access to common functions
- **Status Monitoring**: Real-time connection status
- **Error Handling**: User-friendly error messages

### ⚙️ Configuration
- **Server Settings**: Configure KSE server URL
- **Connection Testing**: Test server connectivity
- **History Management**: View and clear search history

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6
- requests library

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyQt6 requests
```

## Usage

### Starting the Browser

#### Option 1: Direct Execution
```bash
python klar_browser.py
```

#### Option 2: Make it executable (Unix/Linux/Mac)
```bash
chmod +x klar_browser.py
./klar_browser.py
```

### Basic Workflow

1. **Start KSE Server**
   - Ensure the KSE server is running (default: http://localhost:5000)
   - You can start it using `python scripts/start_gui.py` or directly

2. **Open Klar Browser**
   - Launch the browser using one of the methods above
   - Check connection status in the bottom-right corner

3. **Configure Server** (if needed)
   - Click **Settings** in the toolbar or press `Ctrl+,`
   - Enter your KSE server URL
   - Click **Test Connection** to verify
   - Click **Save**

4. **Search**
   - Type your query in the search box
   - Press `Enter` or click the **Search** button
   - Results will appear below

5. **View Results**
   - Click any result card to view full details
   - URL links open in your default web browser

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Focus search box (New search) |
| `Ctrl+H` | View search history |
| `Ctrl+,` | Open settings |
| `Ctrl+Q` | Quit browser |
| `Enter` | Execute search |

## Interface Components

### Search Bar
- **Search Input**: Enter your query here
- **Search Button**: Execute the search
- **Clear Button**: Clear results and start fresh
- **Settings Button**: Configure browser settings

### Results Area
- **Header**: Shows result count and search time
- **Result Cards**: Each result displays:
  - Title (clickable, opens details)
  - URL (green text)
  - Snippet (preview of content)
  - Relevance score (if available)

### Status Bar
- **Connection Status**: Shows server connection state
  - 🟢 Connected (green)
  - ⚫ Disconnected (red)

## Configuration

### Server Settings
Default server URL: `http://localhost:5000`

To change:
1. Open Settings (`Ctrl+,`)
2. Enter new server URL
3. Test connection
4. Save

### Search History
- Automatically tracks up to 50 recent searches
- Access via `Ctrl+H` or **File > Search History**
- Clear history from the history dialog

## Troubleshooting

### Connection Issues

**Problem**: "Unable to connect to KSE server"
- **Solution**: Ensure KSE server is running
- Check server URL in settings
- Verify firewall settings

**Problem**: "Search request timed out"
- **Solution**: Check network connection
- Increase timeout in code if needed
- Restart KSE server

### Display Issues

**Problem**: Results not showing
- **Solution**: Check browser console for errors
- Verify search returned results
- Clear and search again

**Problem**: GUI not launching
- **Solution**: Ensure PyQt6 is installed
- Check system has GUI support (not headless)
- Verify Python version (3.8+)

## Advanced Usage

### Custom Server Configuration
You can run KSE server on a different port or host:

```python
# In settings, use:
http://192.168.1.100:8080  # Remote server
http://localhost:8000      # Different port
```

### Search Tips
1. **Use specific terms**: More specific queries yield better results
2. **Check spelling**: Ensure query is spelled correctly
3. **Try variations**: Use synonyms if initial search fails
4. **Use quotes**: For exact phrase matching (if supported by server)

## API Integration

Klar Browser uses the following KSE API endpoints:

### Health Check
```
GET /api/health
```
Returns server health status

### Search
```
GET /api/search?q={query}
```
Returns search results for the given query

Response format:
```json
{
  "query": "search term",
  "results": [
    {
      "title": "Page Title",
      "url": "http://example.com",
      "snippet": "Text preview...",
      "score": 0.95
    }
  ],
  "search_time": 0.045
}
```

## Development

### Code Structure
```
klar_browser.py
├── SearchWorker       # Background search thread
├── ResultCard         # Result display widget
├── SearchHistoryDialog # History viewer
├── SettingsDialog     # Configuration dialog
└── KlarBrowser       # Main window
```

### Customization
You can customize the browser by modifying:
- **Colors**: Edit stylesheet strings
- **Fonts**: Modify QFont settings
- **Layout**: Adjust widget arrangements
- **Features**: Add new dialogs or functionality

## Support

### Reporting Issues
If you encounter problems:
1. Check this guide first
2. Verify server is running
3. Check console logs
4. Report issues with:
   - Error message
   - Steps to reproduce
   - System information

### Contributing
Contributions are welcome! Areas for improvement:
- Additional search filters
- Result export functionality
- Bookmarking system
- Advanced search syntax
- Theming support

## License
This browser is part of the Klar Search Engine project.

---

**Version**: 1.0.0  
**Last Updated**: January 2024
