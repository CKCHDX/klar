# Klar Browser

A modern web-based search browser for the KSE (Klar Search Engine) with a beautiful Nordic-inspired UI.

## Platform Support

- **Desktop** (Windows, macOS, Linux): Full-featured web-based UI with PyQt6
- **Android** (API 21+, targeting Android 16/API 34): Mobile-optimized Kivy version

See [BUILD_ANDROID.md](BUILD_ANDROID.md) for instructions on building the Android APK.

## Features

- 🎨 **Modern Web UI** - Beautiful dark/light theme with animations
- 🔍 **Integrated Search** - Direct connection to KSE Search Engine API
- 🌍 **Swedish Interface** - Nordic-focused design and language
- ⚡ **Fast & Lightweight** - Built with PyQt6 WebEngine
- 🎭 **Animated Interface** - Smooth transitions and particle effects
- 🌓 **Theme Toggle** - Dark and light modes with persistence

## Installation

### Desktop Version

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

### Android Version

See [BUILD_ANDROID.md](BUILD_ANDROID.md) for complete instructions on building the Android APK.

## Usage

### Desktop Version

Run the browser:
```bash
python3 klar_browser.py
```

### Android Version

After building the APK (see [BUILD_ANDROID.md](BUILD_ANDROID.md)), install it on your Android device and launch the app.

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

### Architecture (Desktop)
- **Frontend:** HTML/CSS/JavaScript (loaded in QWebEngineView)
- **Backend:** Python with PyQt6
- **Communication:** QWebChannel bridge between JS and Python
- **API:** RESTful communication with KSE server

### Architecture (Android)
- **Frontend:** Native Kivy widgets
- **Backend:** Python with Kivy framework
- **Communication:** Direct Python code
- **API:** RESTful communication with KSE server

### Files
- `klar_browser.py` - Desktop Python application (PyQt6)
- `klar_browser_android.py` - Android Python application (Kivy)
- `main.py` - Android entry point
- `klar_browser.html` - Desktop UI design
- `buildozer.spec` - Android build configuration
- `requirements.txt` - Desktop Python dependencies
- `requirements_android.txt` - Android Python dependencies
- `BUILD_ANDROID.md` - Android build instructions

## Requirements

### Desktop
- Python 3.8+
- PyQt6 >= 6.4.0
- PyQt6-WebEngine >= 6.4.0
- requests >= 2.28.0
- KSE Search Engine server (running separately)

### Android
- Python 3.8+
- Kivy == 2.2.1
- requests == 2.31.0
- Buildozer (for building APK)
- Android SDK/NDK (automatically downloaded by buildozer)
- Target: Android 16 (API 34), Minimum: Android 5.0 (API 21)

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
