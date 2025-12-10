# Klar 3.1 CI/CD Workflow Guide

**Updated:** December 10, 2025
**Status:** ✅ Active and Automated

---

## Overview

The Klar build workflow automatically:

1. ✅ **Verifies** all Python files and dependencies
2. ✅ **Builds** Windows executable (PyInstaller)
3. ✅ **Builds** Linux executable (PyInstaller)
4. ✅ **Generates** release notes
5. ✅ **Creates** artifacts for download
6. ✅ **Publishes** checksums (SHA256)

---

## Workflow Triggers

The workflow runs automatically on:

### Push Events
```yaml
Trigger: Any push to 'main' branch
Except: Changes to 'lab/', 'docs/', or '*.md' files
```

### Pull Requests
```yaml
Trigger: PR to 'main' branch
Except: Changes to 'lab/', 'docs/', or '*.md' files
```

### Manual Trigger
```
Go to: GitHub → Actions → "Build Klar 3.1 Release" → "Run workflow"
```

---

## Workflow Jobs

### 1. **verify** (Ubuntu Latest)
Verifies build requirements before compilation.

**Steps:**
- ✅ Check out code
- ✅ Setup Python 3.11
- ✅ Validate `keywords_db.json` (categories count)
- ✅ Validate `domains.json` (domain count)
- ✅ Check Python syntax for all modules:
  - `klar_browser.py`
  - `engine/search_engine.py`
  - `engine/domain_whitelist.py`
  - `core/crawler.py`
  - `algorithms/sven.py`
  - `algorithms/thor.py`
- ✅ Test dependencies (all imports work)

**Output:** Pass/Fail status before compilation starts

---

### 2. **build-windows** (Windows Latest) [Needs: verify]
Builds standalone Windows executable.

**Steps:**
- ✅ Check out code
- ✅ Setup Python 3.11
- ✅ Install dependencies (PyInstaller, PyQt6, etc.)
- ✅ Build with PyInstaller:
  ```bash
  pyinstaller --onefile --windowed --name Klar \
    --add-data "keywords_db.json;." \
    --add-data "domains.json;." \
    --add-data "engine;engine" \
    --add-data "algorithms;algorithms" \
    --add-data "core;core" \
    [hidden imports...] \
    klar_browser.py
  ```
- ✅ Verify executable created
- ✅ Create release package with README
- ✅ Generate SHA256 checksum
- ✅ Create ZIP archive

**Artifacts Generated:**
1. `Klar-3.1-Windows-Standalone` (folder)
   - `Klar.exe` (~100MB)
   - `README.txt` (Installation guide)
   - `Klar.SHA256.txt` (Checksum)

2. `Klar-3.1-Windows-ZIP` (archive)
   - Complete package compressed

**Retention:** 90 days

---

### 3. **build-linux** (Ubuntu Latest) [Needs: verify]
Builds standalone Linux executable.

**Steps:**
- ✅ Check out code
- ✅ Setup Python 3.11
- ✅ Install system dependencies:
  - libxcb-xinerama0
  - libxcb-cursor0
  - libxkbcommon-x11-0
  - libgl1-mesa-dev
  - libfontconfig1
- ✅ Install Python dependencies
- ✅ Build with PyInstaller
- ✅ Verify executable
- ✅ Create release package with README
- ✅ Generate SHA256 checksum
- ✅ Create TAR.GZ archive

**Artifacts Generated:**
1. `Klar-3.1-Linux-Standalone` (folder)
   - `Klar` (~110MB, executable)
   - `README.md` (Installation guide)
   - `Klar.SHA256.txt` (Checksum)

2. `Klar-3.1-Linux-TAR` (archive)
   - Complete package compressed

**Retention:** 90 days

---

### 4. **create-release-notes** (Ubuntu Latest) [Needs: build-windows, build-linux]
Generates comprehensive release notes.

**Output File:** `RELEASE_NOTES_3.1.md`

**Contains:**
- Release date and status
- What's new in 3.1
- Bug fixes
- Testing checklist
- Known limitations
- System requirements
- Security notes
- Download links
- Roadmap for 1.0 official

**Artifact:** `Release-Notes`

---

### 5. **summary** (Ubuntu Latest) [Needs: all jobs]
Final build summary and status.

**Output:**
```
🎉 Klar 3.1 Build Complete!

📦 Artifacts Generated:
  ✓ Klar-3.1-Windows-Standalone (EXE + README + SHA256)
  ✓ Klar-3.1-Windows-ZIP (Compressed archive)
  ✓ Klar-3.1-Linux-Standalone (ELF + README + SHA256)
  ✓ Klar-3.1-Linux-TAR (Compressed archive)
  ✓ Release-Notes (RELEASE_NOTES_3.1.md)

📊 Build Status: [success/failure]

🔗 Download from: Actions tab → Artifacts
```

---

## File Structure

```
.github/
└── workflows/
    └── build-release.yml          # This workflow file
    
.github/
└── WORKFLOW_GUIDE.md              # This file

# Generated during build:
release/
├── windows/
│   ├── Klar.exe                   # Windows executable
│   ├── README.txt                 # Installation guide
│   └── Klar.SHA256.txt            # Checksum
└── linux/
    ├── Klar                       # Linux executable
    ├── README.md                  # Installation guide
    └── Klar.SHA256.txt            # Checksum
```

---

## How to Use Artifacts

### 1. **Find Artifacts**
```
GitHub → Your Fork of Klar
  → Actions Tab
  → Select Latest Build
  → Scroll Down → "Artifacts" Section
```

### 2. **Download Executable**

**Windows Users:**
- Download: `Klar-3.1-Windows-ZIP`
- Extract: Right-click → "Extract All"
- Run: Double-click `Klar.exe`

**Linux Users:**
```bash
# Download: Klar-3.1-Linux-TAR
tar -xzf Klar-3.1-Linux-Standalone.tar.gz
chmod +x Klar
./Klar
```

### 3. **Verify Checksum**

**Windows:**
```cmd
certutil -hashfile Klar.exe SHA256
# Compare with: Klar.SHA256.txt
```

**Linux:**
```bash
sha256sum Klar
# Compare with: Klar.SHA256.txt
```

---

## Build Specifications

### Windows Build
- **Runner:** Windows Latest (windows-latest)
- **Python:** 3.11.x
- **Output:** Klar.exe (standalone executable)
- **Size:** ~100MB
- **Time:** ~10-15 minutes
- **Dependencies:** PyQt6, PyInstaller, requests, BeautifulSoup4

### Linux Build
- **Runner:** Ubuntu Latest (ubuntu-latest)
- **Python:** 3.11.x
- **Output:** Klar (standalone executable)
- **Size:** ~110MB
- **Time:** ~10-15 minutes
- **System Deps:** libxcb-*, libgl1-mesa-dev, libfontconfig1

---

## Environment Variables

The workflow uses only standard environment variables. No secrets required.

**Note:** Klar doesn't collect data or contact external services during build.

---

## Error Handling

### If Build Fails

1. **Check Error Message:**
   - Click job name → Scroll to error
   - Common: Python import error, missing dependency

2. **Common Fixes:**
   ```yaml
   # If Python syntax error:
   - Push fix to Python file
   - Workflow auto-retriggers
   
   # If JSON error:
   - Validate keywords_db.json
   - Validate domains.json
   - Push fixed files
   
   # If dependency error:
   - Check PyInstaller hidden-import list
   - Add missing import
   - Push fix
   ```

3. **Manual Trigger:**
   - Actions → "Build Klar 3.1 Release" → "Run workflow"

---

## Supported Configurations

### Windows
- ✅ Windows 10
- ✅ Windows 11
- ✅ Windows Server 2019+

### Linux
- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ Fedora 35+
- ✅ Any X11/Wayland system

---

## Performance Notes

**Build Times:**
- Verify job: ~2-3 minutes
- Windows build: ~8-10 minutes
- Linux build: ~8-10 minutes
- Release notes: ~1 minute
- **Total:** ~20-25 minutes per workflow run

**Parallel Jobs:**
- Windows and Linux build in parallel
- Release notes job waits for both to complete
- Summary job is final step

---

## Security

### Code Verification
- ✅ All Python files syntax-checked before build
- ✅ JSON files validated
- ✅ Dependencies verified
- ✅ No secrets in workflow
- ✅ No external APIs called

### Artifact Integrity
- ✅ SHA256 checksums provided
- ✅ 90-day artifact retention
- ✅ No automatic deletion

---

## Future Improvements

### Planned for 1.0 Release
1. **Code Signing**
   - Sign Windows executable (Authenticode)
   - Sign Linux executable (GPG)

2. **Automated Testing**
   - Run test suite before build
   - Performance benchmarks
   - Integration tests

3. **Release Publishing**
   - Auto-create GitHub Release
   - Upload to release page
   - Generate changelog from commits

4. **Quality Gates**
   - Code coverage reporting
   - Lint checks (pylint, flake8)
   - Type checking (mypy)

5. **Multi-Platform**
   - macOS build (darwin)
   - Arm64 Linux support
   - Alpine Linux support

---

## Troubleshooting

### Build Won't Trigger
```
Possible Causes:
1. Changes only in 'lab/' or 'docs/'
2. Changes only to '*.md' files
3. Push to branch other than 'main'

Solution:
- Make changes to Python/JSON files
- Or manually trigger from Actions tab
```

### Executable Won't Run
```
Windows:
- Right-click → Run as Administrator
- Check .NET Framework / Visual C++ installed
- Try: Klar.exe --verbose

Linux:
- chmod +x Klar
- Check: ldd ./Klar
- Try: ./Klar --verbose
```

### Checksum Doesn't Match
```
1. Download file again (partial download?)
2. Verify network didn't corrupt file
3. Check you're comparing correct hashes
4. Report issue on GitHub
```

---

## Questions?

For workflow issues:
1. Check this guide first
2. Review workflow logs (Actions tab)
3. Open GitHub Issue with:
   - Workflow run number
   - Error message
   - Steps to reproduce

---

## Quick Links

- 📁 **Workflow File:** `.github/workflows/build-release.yml`
- 🎯 **Actions Page:** https://github.com/CKCHDX/klar/actions
- 📦 **Artifacts:** https://github.com/CKCHDX/klar/actions (select workflow run)
- 📝 **Release Notes:** `RELEASE_NOTES_3.1.md` (in artifacts)
- 🐛 **Issues:** https://github.com/CKCHDX/klar/issues

---

**Last Updated:** December 10, 2025  
**Workflow Version:** 3.1  
**Status:** ✅ Active
