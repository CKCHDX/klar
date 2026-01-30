# Klar Browser: Desktop vs Android Comparison

This document explains the differences between the desktop and Android versions of Klar Browser.

## Overview

| Aspect | Desktop Version | Android Version |
|--------|----------------|-----------------|
| **File** | `klar_browser.py` | `klar_browser_android.py` |
| **Framework** | PyQt6 + QWebEngine | Kivy |
| **Platform** | Windows, macOS, Linux | Android (API 21-34) |
| **UI Technology** | HTML/CSS/JavaScript | Native Python Widgets |
| **Build Tool** | Direct Python execution | Buildozer + Python-for-Android |
| **Size** | ~29 MB (with dependencies) | ~15-20 MB APK |

## Why Two Versions?

**PyQt6 is incompatible with Android**. The Qt framework's WebEngine component doesn't support Android packaging. Therefore, we created a separate Android version using Kivy, a framework specifically designed for mobile development.

## Feature Comparison

### Included in Both Versions ✅

- Search functionality via KSE API
- Server URL configuration
- Settings dialog
- Results display
- Error handling
- Configuration persistence
- Network status checking

### Desktop-Only Features 🖥️

- Web-based UI with HTML/CSS/JavaScript
- Animated compass logo
- Particle field background effects
- CSS-based dark/light theme toggle
- Nordic-styled animations
- Web browser navigation
- QWebChannel JS-Python bridge
- Rich text formatting

### Android-Only Features 📱

- Native Android UI widgets
- Touch-optimized interface
- Mobile-specific storage paths
- Android permissions handling
- Optimized for portrait orientation
- Smaller package size
- Better battery efficiency

## Technical Architecture

### Desktop Version

```
User → HTML UI → JavaScript → QWebChannel → Python Bridge → KSE API
                    ↓
              WebEngine (Chromium)
```

**Key Components:**
- `QMainWindow`: Application window
- `QWebEngineView`: Renders HTML/CSS/JS
- `QWebChannel`: Bidirectional JS-Python communication
- `KlarBridge`: Python backend for API calls
- External HTML file with full UI

### Android Version

```
User → Kivy Widgets → Python App Logic → KSE API
```

**Key Components:**
- `KlarApp`: Main Kivy application
- `KlarBrowserAndroid`: BoxLayout container
- `SearchResult`: Custom widget for results
- Direct Python-to-API communication
- No separate UI files (widgets defined in code)

## Code Comparison

### Desktop: Rendering UI
```python
# Uses HTML file
self.web_view = QWebEngineView()
self.web_view.setHtml(html_content)
```

### Android: Building UI
```python
# Uses native widgets
self.search_input = TextInput(hint_text='Enter search query...')
search_btn = Button(text='Search')
```

### Desktop: Search Implementation
```python
# Bridge method exposed to JavaScript
@pyqtSlot(str)
def performSearch(self, query: str):
    response = requests.get(url, params=params)
    self.search_completed.emit(json.dumps(data))
```

### Android: Search Implementation
```python
# Direct method call
def perform_search(self, instance):
    query = self.search_input.text.strip()
    Clock.schedule_once(lambda dt: self._execute_search(query))
```

## User Experience

### Desktop Version

**Pros:**
- Beautiful, polished interface
- Smooth animations
- Web-familiar experience
- Easy to customize (edit HTML/CSS)

**Cons:**
- Larger download size
- Requires system WebEngine
- Higher resource usage

### Android Version

**Pros:**
- Native mobile feel
- Smaller APK size
- Better performance on low-end devices
- No external dependencies beyond Python

**Cons:**
- Simpler interface
- No web animations
- Limited styling options

## Configuration Storage

### Desktop
```
~/.kse/klar_browser_config.json
```
Unix-style home directory

### Android
```
/data/data/org.kse.klarbrowser/files/klar_browser_config.json
```
Android app storage (auto-detected via Kivy)

## API Communication

Both versions use identical API calls:

```python
# Search endpoint
GET http://localhost:5000/api/search?q=query

# Health check
GET http://localhost:5000/api/health
```

The difference is only in how results are displayed.

## Build Process

### Desktop
```bash
# No build required
pip install -r requirements.txt
python3 klar_browser.py
```

### Android
```bash
# Build required
pip install buildozer
buildozer android debug
# Produces: bin/klarbrowser-1.0.0-debug.apk
```

## Dependencies

### Desktop
- PyQt6 (60+ MB)
- PyQt6-WebEngine (100+ MB)
- requests (500 KB)

**Total:** ~160 MB installed

### Android
- Kivy (bundled in APK)
- requests (bundled in APK)
- certifi (bundled in APK)

**Total:** ~15-20 MB APK

## Development Workflow

### Desktop Development
1. Edit `klar_browser.py` or `klar_browser.html`
2. Run `python3 klar_browser.py`
3. See changes immediately

### Android Development
1. Edit `klar_browser_android.py`
2. Run `buildozer android debug`
3. Install APK on device/emulator
4. Test (2-5 minutes per iteration after first build)

## Performance

### Desktop
- **Startup:** 2-3 seconds
- **Memory:** 100-150 MB
- **CPU:** Moderate (WebEngine rendering)

### Android
- **Startup:** 1-2 seconds
- **Memory:** 30-50 MB
- **CPU:** Low (native widgets)

## Maintenance

Both versions:
- Share the same API contract
- Use identical configuration format
- Have similar error handling
- Follow the same search logic

Changes to the KSE API only need to be updated once in terms of the request/response format, but implementations differ.

## Future Considerations

### Potential Unification
It's theoretically possible to use Kivy for both desktop and Android, which would unify the codebase. However, this would sacrifice the rich web UI of the desktop version.

**Trade-off:**
- ✅ Single codebase
- ✅ Easier maintenance
- ❌ Loss of HTML/CSS/JS flexibility
- ❌ Less polished desktop experience

**Current approach:** Maintain both versions to provide the best experience on each platform.

## When to Use Each

### Use Desktop Version When:
- Running on Windows/macOS/Linux
- Want the most polished UI
- Have good hardware resources
- Prefer web technologies

### Use Android Version When:
- Running on Android devices/tablets
- Need mobile compatibility
- Want smaller app size
- Prefer native mobile feel

## Summary

Both versions accomplish the same goal—providing a search interface to KSE—but are optimized for their respective platforms. The desktop version prioritizes visual polish and web technologies, while the Android version prioritizes compatibility, size, and mobile-native experience.

---

**Recommendation:** Users should use the version appropriate for their platform. The Android version is not a "lesser" version—it's purpose-built for mobile devices with Android-specific optimizations.
