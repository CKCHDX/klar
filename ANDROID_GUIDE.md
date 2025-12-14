# Klar 3.1 Android Build Guide

## Overview

This guide explains how to build and deploy Klar as an Android APK.

**Branch:** `android`  
**Platform:** Android 7.0+ (API 24+)  
**Target Architecture:** ARM64 (primary), ARMv7 (fallback)  
**Framework:** Kivy (Python mobile framework)  
**Build Tool:** Buildozer (Python→APK compiler)  

---

## What Changed from Desktop Version?

### 1. **Framework Switch: PyQt6 → Kivy**

| Aspect | Desktop (PyQt6) | Mobile (Kivy) |
|--------|-----------------|---------------|
| **UI Toolkit** | PyQt6 (C++ backend) | Kivy (Python-based) |
| **Touch Support** | No native touch | Full touch gestures |
| **Responsive** | Fixed 1400x900 | Responsive, scales to device |
| **Mobile Features** | None | Camera, vibration, sensors |
| **File Size** | ~100MB exe | ~80-100MB APK |
| **Entry Point** | `klar_browser.py` | `klar_mobile.py` |

### 2. **Key Modifications for Mobile**

#### **Touch Support**
- Native Kivy touch handling (no modifications needed - built-in)
- Tap, drag, swipe gestures supported by default
- Long-press gestures via gesture detection
- Haptic feedback on button presses (Android vibration API)

#### **UI Scaling**
- Responsive design with `ResponsiveDesign` class
- Minimum button size: 48dp (Android Material Design standard)
- Font sizes scale based on device width
- Column layout adapts: 1 col (mobile) → 2 cols (tablet) → 3 cols (desktop)

#### **Mobile-Specific Features**
```python
# Detection for tablet vs phone
if ResponsiveDesign.is_tablet():  # width > 600dp
    # Tablet layout
else:
    # Phone layout
```

#### **Screen Orientation**
- **Portrait mode only** (optimized for phones)
- Can be changed in `buildozer.spec` if needed:
  ```
  android.orientation = portrait  # or landscape
  android.allow_landscape = 0     # set to 1 to allow
  ```

### 3. **Python Modules - What Works on Android**

✅ **Fully Compatible:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML parsing
- `json` - JSON handling
- `pathlib` - File paths
- `threading` - Background tasks
- `kivy` - All UI components
- `plyer` - Device features (vibration, notifications)
- `pyjnius` - Java/Android API access

⚠️ **Requires Adaptation:**
- Database operations (use SQLite, not file-based JSON heavily)
- File I/O (restricted to `/sdcard` or app-specific storage)
- Network (handle timeouts better on mobile networks)

❌ **NOT Compatible:**
- `PyQt6` / `PyQt5` - Requires C++ GUI
- `tkinter` - Requires X11 display
- `wx` - Requires native toolkit
- Any Qt-based library

### 4. **File Structure Changes**

```
android branch/
├── klar_mobile.py              ← NEW: Kivy version
├── klar_browser.py             ← OLD: Desktop version (kept for reference)
├── release-android.bat         ← NEW: Android build script
├── buildozer.spec              ← NEW: Buildozer config
├── ANDROID_GUIDE.md            ← NEW: This file
├── engine/                     ← REUSED: Search engine
├── keywords_db.json            ← REUSED: Search data
├── domains.json                ← REUSED: Security data
└── core/                       ← REUSED: Core modules
```

---

## Building for Android

### Prerequisites

1. **Python 3.9 or higher**
   ```bash
   python --version
   ```

2. **Java Development Kit (JDK) 11+**
   ```bash
   java -version
   ```
   - Download from: https://www.oracle.com/java/technologies/downloads/#java11
   - Add to PATH or set `JAVA_HOME` environment variable

3. **Android SDK** (recommended minimum)
   - API 31 or higher
   - Download from Android Studio or: https://developer.android.com/studio

4. **Git** (for version control)

### Step 1: Clone and Switch Branch

```bash
git clone https://github.com/CKCHDX/klar.git
cd klar
git checkout android
```

### Step 2: Run Build Script

**Windows:**
```bash
release-android.bat
```

**macOS/Linux:**
```bash
bash release-android.sh
```

The script will:
1. Check Python and Java
2. Create virtual environment (`venv_android`)
3. Install dependencies (buildozer, kivy, etc.)
4. Validate files
5. Configure Buildozer
6. Compile APK (10-30 minutes)
7. Output: `bin/klar-release-3.1.0.apk`

### Step 3: Install on Device

**Option A: Using ADB (Android Debug Bridge)**
```bash
adb install bin/klar-release-3.1.0.apk
```

**Option B: Direct File Transfer**
1. Connect device to PC
2. Copy APK to device
3. Open file manager on Android
4. Tap APK → Install

**Option C: USB + Android Studio**
```bash
adb devices  # List connected devices
adb install -r bin/klar-release-3.1.0.apk  # -r = replace existing
```

---

## Android-Specific Considerations

### Storage Permissions

**App Storage Locations:**
```python
from kivy.app import App
app = App.get_running_app()
app_storage = app.user_data_dir  # App-specific directory
```

**File Access:**
- App data: `/data/data/com.example.klar/` (private)
- Cache: App cache directory (auto-cleared)
- External storage: `/sdcard/` (requires permissions)

Permissions are declared in `buildozer.spec`:
```
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
```

### Network Handling

Mobile networks are less reliable. Implement timeouts:

```python
# In search_engine.py or network code
import requests

response = requests.get(
    url,
    timeout=10,  # 10 second timeout
    retries=3    # Retry 3 times
)
```

### Battery Optimization

✅ **Good Practices:**
- Use `threading` for background tasks (not CPU-blocking)
- Close connections properly
- Cache results aggressively
- Stop searches on pause/minimize

❌ **Bad Practices:**
- Continuous polling
- Large data transfers without batching
- Running at full CPU constantly

### Back Button Handling

Kivy automatically handles Android back button to exit or go back in navigation.

### Offline Support (LOKI)

LOKI caching works perfectly on Android! Data stored in app's private directory.

---

## Python Code Modifications Needed

### ✅ Already Handled in `klar_mobile.py`

1. **Responsive Layout**
   ```python
   from ResponsiveDesign import ResponsiveDesign
   cols = ResponsiveDesign.get_column_count()  # Adapts to screen
   ```

2. **Touch Events**
   - Kivy handles automatically via `Button`, `TextInput` widgets
   - All widgets are touch-responsive by default

3. **Mobile Screen Sizes**
   - Minimum window: 320x480dp
   - Scales to any device automatically

4. **Background Tasks**
   ```python
   from threading import Thread
   thread = Thread(target=search_function)
   thread.daemon = True
   thread.start()
   ```

5. **Status Updates**
   - Using `Clock.schedule_once()` for thread-safe UI updates

### ⚠️ Modules Needing Updates for Full Feature Parity

If you want to use Android-specific features:

```python
# Camera access
from plyer import camera
camera.take_picture(
    filename='/sdcard/photo.jpg',
    on_complete=callback
)

# Vibration/Haptics
from plyer import vibrator
vibrator.vibrate(duration=0.5)  # 500ms buzz

# Notifications
from plyer import notification
notification.notify(
    title='Search Complete',
    message='Found 42 results',
    timeout=5
)

# Sensors (GPS, accelerometer, etc.)
from plyer import gps
gps.start()  # Get location
```

---

## Troubleshooting

### Build Fails: "JDK Not Found"
```
Solution: Set JAVA_HOME environment variable
Windows: set JAVA_HOME=C:\Program Files\Java\jdk-11
Linux/Mac: export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
```

### Build Fails: "Android SDK Not Found"
```
Solution: Set ANDROID_SDK_ROOT
Windows: set ANDROID_SDK_ROOT=C:\Users\Username\AppData\Local\Android\Sdk
Linux: export ANDROID_SDK_ROOT=~/Android/Sdk
```

### APK Too Large (>200MB)
```
Solutions:
1. Reduce number of architectures (remove armeabi-v7a if not needed)
2. Compress JSON files
3. Remove unused dependencies from buildozer.spec
```

### App Crashes on Startup
```
Check logcat for errors:
adb logcat | grep python
```

### Touch Not Responsive
```
Verify in buildozer.spec:
android.features = android.hardware.touchscreen
```

---

## Performance Tips

1. **Lazy Load Search Results** - Don't render all 1000 results at once
2. **Compress Images** - Resize before displaying
3. **Batch Network Requests** - Combine multiple requests
4. **Use SQLite for Large Data** - Not JSON files
5. **Profile with Kivy Metrics** - `Clock.schedule_interval(print_metrics, 5)`

---

## Distribution

### Google Play Store

1. Create Google Play account ($25 one-time fee)
2. Sign APK with keystore:
   ```bash
   keytool -genkey -v -keystore klar.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias klar_key
   ```
3. Upload signed APK to Google Play Console

### F-Droid (Open Source Alternative)

- Free app store
- Source code must be public
- Community-managed

### Direct Distribution

- Host APK on your website
- Users enable "Unknown Sources" to install

---

## Version Info

- **Klar Version:** 3.1
- **Android Min:** API 24 (Android 7.0)
- **Android Target:** API 31 (Android 12)
- **Buildozer:** Latest
- **Kivy:** Latest 2.x
- **Python:** 3.9+

---

## Related Files

- `release-android.bat` - Build script
- `buildozer.spec` - Build configuration
- `klar_mobile.py` - Kivy app entry point
- `engine/search_engine.py` - Search logic (reused)
- `.github/workflows/build-release.yml` - CI/CD automation

---

**Questions?** Check the main README.md or create an issue on GitHub.
