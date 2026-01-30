# Klar Browser

A modern web-based search browser for the KSE (Klar Search Engine) with a beautiful Nordic-inspired UI.

## Features

- 🎨 **Modern Web UI** - Beautiful dark/light theme with animations
- 🔍 **Integrated Search** - Direct connection to KSE Search Engine API
- 🌍 **Swedish Interface** - Nordic-focused design and language
- ⚡ **Fast & Lightweight** - Built with PyQt6 WebEngine
- 🎭 **Animated Interface** - Smooth transitions and particle effects
- 🌓 **Theme Toggle** - Dark and light modes with persistence

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** On Linux, you may need additional system packages:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6.qtwebengine libxcb-cursor0

# Fedora
sudo dnf install python3-pyqt6-webengine
```

## Usage

Run the browser:
```bash
python3 klar_browser.py
```

## Configuration

### Server URL

The browser connects to a KSE server. Configure the server URL in one of three ways:

1. **Environment variable** (highest priority):
```bash
export KSE_SERVER_URL="http://localhost:5000"
python3 klar_browser.py
```

2. **Settings dialog** - Click the ⚙ button in the footer

3. **Config file** - Automatically saved to `~/.kse/klar_browser_config.json`

### Default Settings

- Server URL: `http://localhost:5000`
- Theme: Dark mode
- Language: Swedish

## UI Elements

### Main Interface
- **Search Bar** - Enter search queries (press Enter to search)
- **Quick Actions** - Three action buttons:
  - "Sök" - Perform search
  - "Känslan Säger" - I'm feeling lucky
  - "Privat läge" - Private mode

### Footer Controls
- **Theme Toggle** - Switch between dark/light modes
- **Stats** - Display search statistics
- **Settings (⚙)** - Configure server connection
- **About (?)** - Application information

### Keyboard Shortcuts
- `Enter` - Execute search
- `Escape` - Clear results and focus search bar

## Visual Design

The UI features:
- Animated compass logo with rotating ring
- Grid background with particle field animation
- Smooth cubic-bezier transitions
- Nordic color palette (cyan, indigo, orange accents)
- Responsive design for mobile and desktop

## Technical Details

### Architecture
- **Frontend:** HTML/CSS/JavaScript (loaded in QWebEngineView)
- **Backend:** Python with PyQt6
- **Communication:** QWebChannel bridge between JS and Python
- **API:** RESTful communication with KSE server

### Files
- `klar_browser.py` - Main Python application
- `klar_browser.html` - Complete UI design
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.8+
- PyQt6 >= 6.4.0
- PyQt6-WebEngine >= 6.4.0
- requests >= 2.28.0
- KSE Search Engine server (running separately)

## Development

### Testing
Run integration tests:
```bash
python3 test_integration.py
```

### Logs
Application logs are written to stdout with INFO level by default.

## License

Part of the Klar Search Engine Project

---

**Note:** This is the production-ready version of Klar Browser with a modern web-based UI. The experimental PyQt6 widgets version has been replaced.
