# Klar 3.1 - Swedish Browser

Klar is a standalone Swedish browser application with integrated search engine, featuring LOKI offline search, Wikipedia direct search, and a setup wizard..

## Features

- **Swedish Browser**: Full-featured web browser built with PyQt6
- **Integrated Search Engine**: Built-in search capabilities
- **LOKI Offline Search**: Search without internet connection
- **Wikipedia Direct Search**: Quick Wikipedia lookups
- **Setup Wizard**: Easy first-time configuration
- **Ad Blocking**: Built-in ad blocker
- **Domain Whitelist**: Customizable domain filtering
- **Cookie Banner Detection**: Automatic cookie banner handling

## Building the Executable

Klar can be compiled into a standalone executable program that includes all dependencies.

### Quick Start

**Windows:**
```cmd
release.bat
```

**Linux/macOS:**
```bash
./build.sh
```

The build process will create a single-file executable in the `release/` directory:
- Windows: `release/windows/Klar.exe`
- Linux/macOS: `release/linux/Klar`

### Detailed Build Instructions

See [BUILD.md](BUILD.md) for comprehensive build instructions, troubleshooting, and manual build options.

## Requirements

### For Building
- Python 3.8+ (3.12+ recommended)
- pip (Python package installer)
- PyQt6, PyQt6-WebEngine
- PyInstaller
- Other dependencies (see requirements.txt)

### For Running the Executable
- No requirements! The executable is completely standalone
- Just run it directly - no Python or dependencies needed

## Project Structure

```
klar/
├── klar_browser.py          # Main application
├── engine/                  # Browser engine modules
│   ├── search_engine.py     # Search functionality
│   ├── loki_system.py       # Offline search system
│   ├── adblock.py           # Ad blocking
│   └── ...
├── keywords_db.json         # Keyword database
├── domains.json             # Domain configuration
├── klar.ico                 # Application icon
├── release.bat              # Windows build script
├── build.sh                 # Linux/macOS build script
├── BUILD.md                 # Build documentation
└── requirements.txt         # Python dependencies
```

## Development

To run Klar in development mode:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate.bat  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python klar_browser.py
   ```

## Distribution

After building, you can distribute just the executable file:
- **Windows**: Send `Klar.exe` (~200-250 MB)
- **Linux/macOS**: Send `Klar` binary (~200-250 MB)

Users can run it directly without installing Python or any dependencies.

## Build Output

The build process creates:
- **Single-file executable**: All dependencies embedded
- **No external files needed**: Completely standalone
- **No installation required**: Just run it
- **First launch may be slow**: 5-10 seconds to unpack

## Version

Current version: **3.1**

## License

See project repository for license information.

## Support

For build issues or questions, see [BUILD.md](BUILD.md) or open an issue in the repository.
