# Klar 3.1 - Build Instructions & Artifact Guide

**Last Updated:** December 10, 2025
**Status:** ✅ Fully Automated with GitHub Actions

---

## Quick Start

### Option 1: Download Pre-Built Executables (Recommended)

1. Go to: https://github.com/CKCHDX/klar/actions
2. Click latest successful build (green checkmark)
3. Scroll to "Artifacts" section
4. Download your platform:
   - **Windows:** `Klar-3.1-Windows-ZIP`
   - **Linux:** `Klar-3.1-Linux-TAR`
5. Extract and run!

### Option 2: Build Locally

See "Building Locally" section below

---

## Artifact Overview

### What Gets Generated Automatically

Every push to `main` branch triggers a complete build:

```
✅ Build Verification
  └─ Syntax check (all Python files)
  └─ JSON validation (keywords_db.json, domains.json)
  └─ Dependency verification

✅ Windows Build
  └─ PyInstaller compile
  └─ Klar.exe (~100MB standalone executable)
  └─ README.txt (installation guide)
  └─ Klar.SHA256.txt (checksum)
  └─ Klar-3.1-Windows-ZIP (archive)

✅ Linux Build
  └─ PyInstaller compile
  └─ Klar (~110MB standalone executable)
  └─ README.md (installation guide)
  └─ Klar.SHA256.txt (checksum)
  └─ Klar-3.1-Linux-TAR.gz (archive)

✅ Release Notes
  └─ RELEASE_NOTES_3.1.md (comprehensive changelog)
✅ Build Summary
  └─ Final status report
```

**Build Time:** ~20-25 minutes
**Artifact Retention:** 90 days

---

## Downloading Artifacts

### Step 1: Navigate to Actions

```
GitHub.com → Your Fork
  → Actions Tab (top navigation)
  → "Build Klar 3.1 Release" (left sidebar)
```

### Step 2: Select Latest Build

```
Click the most recent workflow run
(Green checkmark = Success, Red X = Failed)
```

### Step 3: Download Artifacts

```
Scroll Down → "Artifacts" Section

Available Downloads:
✓ Klar-3.1-Windows-Standalone (EXE + README + SHA256)
✓ Klar-3.1-Windows-ZIP (Complete package)
✓ Klar-3.1-Linux-Standalone (ELF + README + SHA256)
✓ Klar-3.1-Linux-TAR (Complete package)
✓ Release-Notes (RELEASE_NOTES_3.1.md)
```

---

## Using Downloaded Artifacts

### Windows

**Extract:**
```cmd
# Right-click ZIP file
# Select "Extract All"
# Or use command line:
Expand-Archive -Path Klar-3.1-Windows-ZIP.zip -DestinationPath C:\Klar
```

**Run:**
```cmd
C:\Klar\Klar.exe
```

**Verify Checksum:**
```cmd
cd C:\Klar
certutil -hashfile Klar.exe SHA256
# Compare output with: Klar.SHA256.txt
```

### Linux

**Extract:**
```bash
tar -xzf Klar-3.1-Linux-Standalone.tar.gz
cd Klar-3.1-Linux-Standalone
```

**Run:**
```bash
chmod +x Klar
./Klar
```

**Verify Checksum:**
```bash
sha256sum Klar
# Compare output with: Klar.SHA256.txt
```

---

## Building Locally

If you want to build Klar yourself without GitHub Actions:

### Prerequisites

**Windows:**
```cmd
# Install Python 3.11+
winget install Python.Python.3.11

# Or download from: https://www.python.org/downloads/
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Or use your distribution's package manager
```

### Step 1: Clone Repository

```bash
git clone https://github.com/CKCHDX/klar.git
cd klar
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux
python3.11 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml pyinstaller pillow
```

### Step 4: Verify Build Requirements

```bash
# Check JSON files
python -c "import json; print('Keywords:', len(json.load(open('keywords_db.json'))['mappings']))"
python -c "import json; print('Domains:', len(json.load(open('domains.json'))))"

# Check Python syntax
python -m py_compile klar_browser.py engine/search_engine.py engine/domain_whitelist.py

# Test imports
python -c "import PyQt6; import requests; import bs4; print('OK')"
```

### Step 5: Build with PyInstaller

**Windows:**
```cmd
pyinstaller --onefile --windowed --name Klar --icon klar.ico `
  --add-data "keywords_db.json;." `
  --add-data "domains.json;." `
  --add-data "engine;engine" `
  --add-data "algorithms;algorithms" `
  --add-data "core;core" `
  --hidden-import PyQt6.QtCore `
  --hidden-import PyQt6.QtGui `
  --hidden-import PyQt6.QtWidgets `
  --hidden-import PyQt6.QtWebEngineWidgets `
  --hidden-import PyQt6.QtWebEngineCore `
  --hidden-import requests `
  --hidden-import bs4 `
  --hidden-import lxml `
  klar_browser.py
```

**Linux:**
```bash
pyinstaller --onefile --windowed --name Klar \
  --add-data "keywords_db.json:." \
  --add-data "domains.json:." \
  --add-data "engine:engine" \
  --add-data "algorithms:algorithms" \
  --add-data "core:core" \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtGui \
  --hidden-import PyQt6.QtWidgets \
  --hidden-import PyQt6.QtWebEngineWidgets \
  --hidden-import PyQt6.QtWebEngineCore \
  --hidden-import requests \
  --hidden-import bs4 \
  --hidden-import lxml \
  klar_browser.py
```

### Step 6: Find Your Executable

```
dist/
└─ Klar.exe (Windows)
└─ Klar (Linux)
```

### Step 7: Run It!

```cmd
# Windows
dist\Klar.exe

# Linux
./dist/Klar
```

---

## Build Specifications

### Windows Executable
- **Size:** ~100MB
- **Python:** 3.11.x
- **Framework:** PyQt6
- **Bundled:** All dependencies
- **Standalone:** No installation needed
- **First Run:** 5-10 seconds (unpacking)
- **After First Run:** Instant startup

### Linux Executable
- **Size:** ~110MB
- **Python:** 3.11.x
- **Framework:** PyQt6
- **Bundled:** All dependencies except system libs
- **Standalone:** No installation needed
- **First Run:** 5-10 seconds (unpacking)
- **After First Run:** Instant startup

---

## Troubleshooting

### Build Failed

**Check the error log:**
```
Actions Tab → Failed Workflow → Expand Job → See Error
```

**Common Issues:**

1. **JSON Syntax Error**
   ```
   Error: json.JSONDecodeError
   
   Solution: Fix keywords_db.json or domains.json
   - Check for trailing commas
   - Validate with: python -m json.tool file.json
   ```

2. **Python Import Error**
   ```
   Error: ModuleNotFoundError
   
   Solution: 
   - Check module exists
   - Check syntax with: python -m py_compile file.py
   - Add to PyInstaller: --hidden-import module_name
   ```

3. **Missing Icon**
   ```
   Error: klar.ico not found
   
   Solution: Check file exists in repo root
   - Or build without: --icon klar.ico
   ```

### Executable Won't Run

**Windows:**
```
Problem: "Windows cannot find the file"
Solution:
- Right-click → Run as Administrator
- Check .NET Framework / Visual C++ Redistributable
- Try: klar_browser.exe --verbose

Problem: "DLL not found"
Solution:
- Download and install Visual C++ Redistributable
- https://support.microsoft.com/en-us/help/2977003
```

**Linux:**
```
Problem: "Permission denied"
Solution: chmod +x Klar

Problem: "Command not found"
Solution: Use full path: ./Klar

Problem: "error while loading shared libraries"
Solution: 
- ldd ./Klar (to see missing libs)
- Install missing system libraries
- Example: sudo apt-get install libgl1-mesa-dev
```

### Checksum Doesn't Match

```
Problem: SHA256 hash mismatch

Cause 1: File corruption (partial download)
  Solution: Delete and re-download from Actions

Cause 2: Wrong file
  Solution: Check you're comparing correct executables

Cause 3: Different build
  Solution: Each build generates new hash
  - Check artifact date matches executable
  - Use hash from same artifact folder
```

---

## File Structure

```
klar/
├── .github/
│   ├── workflows/
│   │   └── build-release.yml         # ↩️ CI/CD Pipeline
│   └── WORKFLOW_GUIDE.md          # 📁 Workflow Documentation
├── engine/
│   ├── search_engine.py
│   ├── domain_whitelist.py
│   └── loki.py
├── core/
│   ├── crawler.py                # 🔍 Deep Crawling
│   └── indexer.py
├── algorithms/
│   ├── sven.py                  # 🧠 Swedish NLP
│   └── thor.py                  # 🎆 Ranking
├── klar_browser.py            # 🐦 Main Application
├── keywords_db.json           # 📂 Keywords Database
├── domains.json               # 📂 Whitelist (115 domains)
├── klar.ico                   # 🌿 Icon
├── BUILD_INSTRUCTIONS.md      # 📄 This File
├── KLAR_1.0_IMPROVEMENTS.md   # 📄 Release Notes
└── README.md                  # 📄 Project README

# Generated by GitHub Actions:
release/
├── windows/
│   ├── Klar.exe
│   ├── README.txt
│   └── Klar.SHA256.txt
└── linux/
    ├── Klar
    ├── README.md
    └── Klar.SHA256.txt
```

---

## What Gets Built Automatically

### Workflow: build-release.yml

```yaml
Trigger: Push to main branch
Except: Changes only to lab/, docs/, *.md

Jobs (Parallel):
1. verify            # ~2-3 min (checks all files)
2. build-windows     # ~8-10 min (creates .exe)
3. build-linux       # ~8-10 min (creates executable)
4. create-release    # ~1 min (generates changelog)
5. summary           # Final report

Total Time: ~20-25 minutes
```

---

## Version History

| Version | Date | What's New |
|---------|------|------------|
| 3.1 | Dec 10, 2025 | ✅ Deep crawling, domain whitelist fix |
| 3.0 | Earlier | Initial release |

---

## Next Steps

1. 📥 **Download** executable from Actions artifacts
2. 🌎 **Test** with different search queries
3. 📤 **Report** issues on GitHub Issues
4. 📄 **Read** RELEASE_NOTES_3.1.md for full details
5. 🙋 **Provide** feedback for Klar 1.0 official release

---

## Support

- 📁 **Documentation:** This file + WORKFLOW_GUIDE.md
- 🌐 **GitHub:** https://github.com/CKCDHX/klar
- 📧 **Email:** oscyra.solutions
- 🐛 **Issues:** https://github.com/CKCDHX/klar/issues

---

**Status:** ✅ Ready for Testing
**Last Build:** Check Actions Tab
**Next Build:** Triggered on next push to main
