# Klar 3.1 - Build Instructions

This document explains how to build Klar into a standalone executable program.

## Overview

Klar is a Swedish browser application built with Python and PyQt6. The build process uses PyInstaller to create a single-file executable that includes all dependencies.

## Prerequisites

- **Python**: Version 3.8 or higher (Python 3.12+ recommended)
- **pip**: Python package installer
- **Git**: For cloning the repository (optional)
- **Operating System**: 
  - Windows 10/11 (for Windows builds)
  - Linux (Ubuntu, Debian, etc. for Linux builds)
  - macOS (for macOS builds)

## Required Files

The following files must be present in the project directory:

- `klar_browser.py` - Main application file
- `keywords_db.json` - Keyword database
- `domains.json` - Domain configuration
- `klar.ico` - Application icon
- `engine/` - Engine modules directory

## Build Instructions

### Windows

1. **Open Command Prompt or PowerShell**
   ```cmd
   cd path\to\klar
   ```

2. **Run the build script**
   ```cmd
   release.bat
   ```

3. **Wait for completion** (3-7 minutes)
   - The script will:
     - Check Python installation
     - Create a virtual environment
     - Install dependencies
     - Validate all files
     - Build the executable
     - Create the release package

4. **Find the executable**
   - Location: `release\windows\Klar.exe`
   - Size: ~200-250 MB
   - Type: Standalone single-file executable

### Linux/macOS

1. **Open Terminal**
   ```bash
   cd /path/to/klar
   ```

2. **Run the build script**
   ```bash
   ./build.sh
   ```
   
   Or if the script is not executable:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. **Wait for completion** (3-7 minutes)
   - The script will:
     - Check Python installation
     - Create a virtual environment
     - Install dependencies
     - Validate all files
     - Build the executable
     - Create the release package

4. **Find the executable**
   - Location: `release/linux/Klar`
   - Size: ~200-250 MB
   - Type: Standalone single-file executable

## Manual Build (Advanced)

If you prefer to build manually or need more control:

### 1. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller
```

### 3. Clean old builds

```bash
# Linux/macOS
rm -rf dist build release
# Keep Klar.spec for reproducible builds

# Windows
rmdir /s /q dist build release
# Keep Klar.spec for reproducible builds
```

### 4. Build with PyInstaller

**Linux/macOS:**
```bash
python -m PyInstaller \
    --onefile \
    --windowed \
    --icon=klar.ico \
    --add-data "keywords_db.json:." \
    --add-data "domains.json:." \
    --add-data "klar.ico:." \
    --add-data "engine:engine" \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtWebEngineWidgets \
    --hidden-import=PyQt6.QtWebEngineCore \
    --hidden-import=PyQt6.sip \
    --hidden-import=requests \
    --hidden-import=bs4 \
    --hidden-import=lxml \
    --hidden-import=engine.domain_whitelist \
    --hidden-import=engine.demographic_detector \
    --hidden-import=engine.loki_system \
    --hidden-import=engine.setup_wizard \
    --exclude-module PySide6 \
    --name=Klar \
    klar_browser.py
```

**Windows:**
```cmd
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=klar.ico ^
    --add-data "keywords_db.json;." ^
    --add-data "domains.json;." ^
    --add-data "klar.ico;." ^
    --add-data "engine;engine" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtWebEngineWidgets ^
    --hidden-import=PyQt6.QtWebEngineCore ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=lxml ^
    --hidden-import=engine.domain_whitelist ^
    --hidden-import=engine.demographic_detector ^
    --hidden-import=engine.loki_system ^
    --hidden-import=engine.setup_wizard ^
    --exclude-module PySide6 ^
    --name=Klar ^
    klar_browser.py
```

### 5. Create release structure

**Linux/macOS:**
```bash
mkdir -p release/linux
cp dist/Klar release/linux/
```

**Windows:**
```cmd
mkdir release\windows
copy dist\Klar.exe release\windows\
```

## PyInstaller Configuration

The build uses the following PyInstaller options:

- `--onefile`: Create a single executable file
- `--windowed`: No console window (GUI only)
- `--icon=klar.ico`: Application icon
- `--add-data`: Include data files (JSON, icons, engine modules)
- `--hidden-import`: Explicitly include Python modules
- `--exclude-module`: Exclude unnecessary modules (PySide6)
- `--name=Klar`: Name of the executable

## Build Output

After a successful build, you'll find:

```
project/
├── build/          # Temporary build files (can be deleted)
├── dist/           # Main executable output
│   └── Klar        # or Klar.exe on Windows
├── release/        # Final release package
│   ├── linux/      # Linux build
│   │   └── Klar
│   └── windows/    # Windows build
│       └── Klar.exe
├── Klar.spec       # PyInstaller specification file
└── venv/           # Virtual environment (can be deleted)
```

## Troubleshooting

### Build Fails

1. **Missing dependencies**: Ensure all required Python packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **File not found errors**: Verify all required files exist in the project directory

3. **Python version issues**: Use Python 3.8 or higher
   ```bash
   python --version
   ```

### Executable Doesn't Run

1. **Linux/macOS**: Ensure the file is executable
   ```bash
   chmod +x release/linux/Klar
   ```

2. **Missing system libraries**: Install required Qt/GUI libraries
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libxcb-xkb1 libxcb-icccm4 libxcb-image0 libxcb-render-util0 libxcb-randr0 libxcb-keysyms1 libxcb-shape0
   ```

3. **First launch is slow**: This is normal - the executable unpacks on first run (5-10 seconds)

### Large File Size

- The executable size (~200-250 MB) is normal
- It includes Python runtime, PyQt6, WebEngine, and all dependencies
- This is a trade-off for having a single-file, no-install distribution

## Distribution

The built executable is completely standalone:

- **No Python installation required** on target system
- **No dependencies required** on target system
- **Single file distribution** - just send the executable
- **No installation needed** - users can run it directly

### Windows Distribution
- File: `release\windows\Klar.exe`
- Users can double-click to run

### Linux/macOS Distribution
- File: `release/linux/Klar`
- Users need to make it executable first: `chmod +x Klar`
- Then run: `./Klar`

## Continuous Integration

For automated builds, you can integrate the build script into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Build Klar
  run: |
    python -m venv venv
    source venv/bin/activate
    pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller
    python -m PyInstaller Klar.spec
```

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- Project repository: https://github.com/CKCHDX/klar

## Support

If you encounter issues during the build process:

1. Check the error messages in the terminal/command prompt
2. Verify all prerequisites are met
3. Try cleaning and rebuilding: delete `build`, `dist`, `venv` folders
4. Open an issue on the project repository with detailed error logs
