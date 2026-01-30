# Klar Browser Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Klar Browser (Python)                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  QMainWindow (KlarBrowser)                │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │           QWebEngineView (Web Renderer)             │ │ │
│  │  │                                                     │ │ │
│  │  │  ┌───────────────────────────────────────────────┐ │ │ │
│  │  │  │       klar_browser.html (UI Layer)            │ │ │ │
│  │  │  │                                               │ │ │ │
│  │  │  │  • Animated compass logo                      │ │ │ │
│  │  │  │  • Search bar with indicators                 │ │ │ │
│  │  │  │  • Quick action buttons                       │ │ │ │
│  │  │  │  • Result cards with animations               │ │ │ │
│  │  │  │  • Theme toggle                               │ │ │ │
│  │  │  │  • Particle field background                  │ │ │ │
│  │  │  │                                               │ │ │ │
│  │  │  │  JavaScript:                                  │ │ │ │
│  │  │  │  ├─ handleSearch()                            │ │ │ │
│  │  │  │  ├─ displayResults()                          │ │ │ │
│  │  │  │  ├─ toggleTheme()                             │ │ │ │
│  │  │  │  └─ showSettings()                            │ │ │ │
│  │  │  └───────────────────────────────────────────────┘ │ │ │
│  │  │                         ↕                           │ │ │
│  │  │                  QWebChannel Bridge                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                            ↕                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │         KlarBridge (Python Object)                  │ │ │
│  │  │                                                     │ │ │
│  │  │  Methods exposed to JavaScript:                    │ │ │
│  │  │  • performSearch(query)                            │ │ │
│  │  │  • getServerUrl()                                  │ │ │
│  │  │  • setServerUrl(url)                               │ │ │
│  │  │  • checkServerHealth()                             │ │ │
│  │  │                                                     │ │ │
│  │  │  Signals to JavaScript:                            │ │ │
│  │  │  • search_completed(json_results)                  │ │ │
│  │  │  • search_error(error_message)                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                              ↕                                  │
│                     HTTP Requests                              │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                 ┌──────────────────────────┐
                 │  KSE Search Engine API   │
                 │                          │
                 │  Endpoints:              │
                 │  • /api/search           │
                 │  • /api/health           │
                 └──────────────────────────┘
```

## Communication Flow

### 1. User Performs Search

```
User types query → Enter key
         ↓
HTML: handleSearch() triggered
         ↓
JavaScript: bridge.performSearch(query)
         ↓
QWebChannel: Serialize and send to Python
         ↓
Python: KlarBridge.performSearch(query)
         ↓
Python: HTTP GET to KSE API /api/search
         ↓
Python: Receive JSON response
         ↓
Python: Emit search_completed signal
         ↓
QWebChannel: Send JSON back to JavaScript
         ↓
JavaScript: handleSearchResults(data)
         ↓
JavaScript: displayResults() renders cards
         ↓
User sees results with animations
```

### 2. Configuration Update

```
User clicks settings button
         ↓
HTML: showSettings() called
         ↓
JavaScript: bridge.getServerUrl()
         ↓
Python: Return current URL
         ↓
JavaScript: Show prompt with current URL
         ↓
User enters new URL
         ↓
JavaScript: bridge.setServerUrl(newUrl)
         ↓
Python: Validate URL format
         ↓
Python: Save to ~/.kse/klar_browser_config.json
         ↓
JavaScript: Show notification "URL updated"
```

## Component Details

### KlarBrowser (Main Window)
- **Type**: QMainWindow
- **Responsibility**: Application container
- **Components**:
  - QWebEngineView (renders HTML)
  - QWebChannel (JS-Python bridge)
  - KlarBridge (backend logic)

### KlarBridge (Backend)
- **Type**: QObject
- **Responsibility**: Backend logic and API communication
- **Methods**:
  - `performSearch(query)` - Execute search via KSE API
  - `getServerUrl()` - Get configured server URL
  - `setServerUrl(url)` - Update and validate server URL
  - `checkServerHealth()` - Ping server health endpoint
- **Configuration**: `~/.kse/klar_browser_config.json`

### HTML UI (Frontend)
- **File**: klar_browser.html
- **Responsibility**: User interface and interactions
- **Features**:
  - Complete visual design (CSS animations, themes)
  - User input handling
  - Result rendering
  - Theme persistence (localStorage)

### QWebChannel Bridge
- **Type**: Qt communication layer
- **Responsibility**: Bidirectional JS ↔ Python communication
- **Mechanism**:
  - Python signals → JavaScript callbacks
  - JavaScript function calls → Python slots
  - JSON serialization for data transfer

## Data Flow

### Search Request
```
Query String (JS) 
  → Bridge (serialize)
    → HTTP Request (Python)
      → KSE API
        → JSON Response
          → Bridge (deserialize)
            → Results Array (JS)
              → Rendered Cards (HTML)
```

### Configuration
```
User Input (HTML)
  → Validation (JS)
    → Bridge (QWebChannel)
      → URL Validation (Python)
        → File Write (JSON)
          → Confirmation (Python → JS)
            → Notification (HTML)
```

## File Structure

```
klar/
├── klar_browser.py          # Main Python application (397 lines)
├── klar_browser.html        # Complete UI design (972 lines)
├── requirements.txt         # Python dependencies
├── README.md               # User documentation
├── UI_INTEGRATION.md       # Visual element documentation
├── COMPLETION_SUMMARY.md   # Task completion details
├── ARCHITECTURE.md         # This file
└── test_integration.py     # Integration tests
```

## Technology Stack

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling, animations, themes
- **JavaScript ES6** - Interaction logic
- **CSS Variables** - Dynamic theming

### Backend
- **Python 3.8+** - Application logic
- **PyQt6** - GUI framework
- **PyQt6-WebEngine** - Web rendering
- **requests** - HTTP client

### Communication
- **QWebChannel** - JS-Python bridge
- **JSON** - Data serialization
- **Signals/Slots** - Event system

## Security Considerations

1. **URL Validation**: All server URLs are validated for protocol and format
2. **Error Handling**: Specific exception types with proper logging
3. **Input Sanitization**: Query parameters are properly escaped
4. **No Eval**: No dynamic code execution
5. **HTTPS Support**: Supports secure connections

## Performance

- **Async Operations**: Search runs without blocking UI
- **Efficient Rendering**: Web engine handles DOM updates
- **Minimal Bridge Calls**: Only essential JS-Python communication
- **Cached Config**: Configuration loaded once at startup

## Extensibility

### Adding New API Endpoints
1. Add method to `KlarBridge` with `@pyqtSlot` decorator
2. Add JavaScript function in injection_script
3. Call from HTML UI as needed

### Customizing UI
1. Edit `klar_browser.html` directly
2. Changes automatically reflected on restart
3. No Python code modification needed

### Adding Features
- **JavaScript-only**: Edit HTML file
- **Backend-only**: Edit KlarBridge class
- **Both**: Add bridge method + HTML function

---

**Architecture Type**: Hybrid Desktop/Web Application
**Pattern**: Model-View-Bridge (similar to MVC)
**Rendering**: WebEngine (Chromium-based)
**Communication**: Qt WebChannel Protocol
