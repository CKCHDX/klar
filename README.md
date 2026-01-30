# Klar Browser

Simple Web Browser for KSE Search Engine with modern visual design system.

## Features

- Modern PyQt6-based interface for desktop (Windows, Linux, macOS)
- Kivy-based mobile interface for Android
- KSE search engine integration
- Cross-platform support

## Installation

### Desktop (PyQt6)
```bash
pip install -r requirements.txt
python klar_browser.py
```

### Mobile (Kivy)
```bash
pip install kivy requests
python main.py
```

## Building Executables

This project uses GitHub Actions to automatically build executables for multiple platforms.

### Automated Builds

The workflow automatically builds executables on push to main/master branch:

- **Linux Executable**: Built on Ubuntu, creates a standalone binary using PyInstaller
- **Windows Executable**: Built on Windows, creates a `.exe` file using PyInstaller
- **Android APK**: Built using Buildozer with Kivy framework. The mobile version (`main.py`) provides a simplified interface for Android devices.

### Manual Build

You can manually trigger builds:

1. Go to the "Actions" tab in GitHub
2. Select "Build Executables" workflow
3. Click "Run workflow"
4. Select the branch and run

All three builds (Linux, Windows, Android) will run automatically.

### Download Built Artifacts

After a successful build:

1. Go to the "Actions" tab
2. Click on the latest workflow run
3. Download the artifacts:
   - `klar-browser-linux` - Linux executable
   - `klar-browser-windows` - Windows .exe file
   - `klar-browser-android` - APK file for Android

### Local Build with PyInstaller (Desktop)

To build locally for desktop:

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your platform
pyinstaller --onefile --windowed --name klar_browser klar_browser.py

# The executable will be in the dist/ folder
```

### Local Build with Buildozer (Android)

To build locally for Android:

```bash
# Install Buildozer (Linux only)
pip install buildozer

# Create buildozer.spec if not present
buildozer init

# Build APK
buildozer android debug

# The APK will be in the bin/ folder
```

## Project Structure

- `klar_browser.py` - Main desktop application using PyQt6
- `main.py` - Cross-platform entry point with Kivy support for mobile
- `requirements.txt` - Desktop dependencies (PyQt6, requests)

## Requirements

### Desktop
- Python 3.11+
- PyQt6==6.6.1
- requests==2.31.0

### Android
- Python 3.11+
- Kivy
- requests==2.31.0

**Note**: The desktop version uses PyQt6 which only supports desktop platforms (Windows, macOS, Linux). The mobile version uses Kivy which supports Android and iOS.

## License

See LICENSE file for details.
