# Klar Browser

Simple Web Browser for KSE Search Engine with modern visual design system.

## Features

- Modern PyQt6-based interface
- KSE search engine integration
- Cross-platform support

## Installation

```bash
pip install -r requirements.txt
python klar_browser.py
```

## Building Executables

This project uses GitHub Actions to automatically build executables for multiple platforms.

### Automated Builds

The workflow automatically builds executables on push to main/master branch:

- **Linux Executable**: Built on Ubuntu, creates a standalone binary
- **Windows Executable**: Built on Windows, creates a `.exe` file
- **APK (Experimental)**: This will fail - PyQt6 does not support Android. A complete rewrite using Kivy or another mobile framework would be required for Android support.

### Manual Build

You can manually trigger builds:

1. Go to the "Actions" tab in GitHub
2. Select "Build Executables" workflow
3. Click "Run workflow"
4. Select the branch and run

The APK build is only triggered via manual workflow dispatch and will fail because PyQt6 does not support Android.

### Download Built Artifacts

After a successful build:

1. Go to the "Actions" tab
2. Click on the latest workflow run
3. Download the artifacts:
   - `klar-browser-linux` - Linux executable
   - `klar-browser-windows` - Windows .exe file
   - `klar-browser-android` - APK file (if available)

### Local Build with PyInstaller

To build locally:

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your platform
pyinstaller --onefile --windowed --name klar_browser klar_browser.py

# The executable will be in the dist/ folder
```

## Requirements

- Python 3.11+
- PyQt6==6.6.1
- requests==2.31.0

**Note**: PyQt6 only supports desktop platforms (Windows, macOS, Linux) and does not support Android or iOS.

## License

See LICENSE file for details.
