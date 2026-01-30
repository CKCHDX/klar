# Building Klar Browser for Android

This guide explains how to build the Klar Browser as an Android APK targeting Android 16 (API level 34).

## Overview

The Android version of Klar Browser is a separate implementation from the desktop version:
- **Desktop version** (`klar_browser.py`): Uses PyQt6 and QWebEngineView
- **Android version** (`klar_browser_android.py`): Uses Kivy framework for Android compatibility

## Why Two Versions?

PyQt6 is not compatible with Android. Therefore, we've created `klar_browser_android.py` which uses the Kivy framework, a Python framework specifically designed for cross-platform mobile development.

## Key Differences

### Desktop Version (klar_browser.py)
- Framework: PyQt6 + QWebEngineView
- UI: HTML/CSS/JavaScript rendered in WebEngine
- Platform: Windows, macOS, Linux
- Rich web-based interface with animations

### Android Version (klar_browser_android.py)
- Framework: Kivy
- UI: Native Kivy widgets
- Platform: Android (API 21+, targeting API 34)
- Optimized mobile interface

## Prerequisites

### On Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

# Install buildozer
pip3 install --upgrade buildozer

# Install Cython (required for building)
pip3 install --upgrade cython

# Install Android dependencies (buildozer will download these automatically)
# - Android SDK
# - Android NDK
# - Apache Ant
```

### On macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 git
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer

# Install buildozer
pip3 install --upgrade buildozer
pip3 install --upgrade cython
```

## Building the APK

### Step 1: Navigate to Repository

```bash
cd /path/to/klar
```

### Step 2: Install buildozer (if not already installed)

```bash
pip3 install --upgrade buildozer
```

### Step 3: Build Debug APK

```bash
# Build in debug mode (faster, for testing)
buildozer android debug

# The APK will be created in: bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Step 4: Build Release APK (for distribution)

```bash
# Build in release mode (optimized, requires signing)
buildozer android release

# The APK will be created in: bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk
```

### Step 5: Clean Build (if needed)

```bash
# Clean all build artifacts
buildozer android clean

# Then rebuild
buildozer android debug
```

## Configuration Details

The build is configured in `buildozer.spec`:

- **Target API**: 34 (Android 16)
- **Minimum API**: 21 (Android 5.0)
- **Architectures**: arm64-v8a, armeabi-v7a (64-bit and 32-bit ARM)
- **Permissions**: INTERNET, ACCESS_NETWORK_STATE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
- **Orientation**: Portrait
- **Package**: org.kse.klarbrowser

## Installing on Android Device

### Via ADB (Android Debug Bridge)

```bash
# Install the APK on connected device
adb install bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-debug.apk

# Or to reinstall (overwrite existing)
adb install -r bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Via File Transfer

1. Transfer the APK to your Android device
2. Open the APK file on your device
3. Enable "Install from Unknown Sources" if prompted
4. Follow the installation prompts

## Testing

### On Device
1. Enable USB debugging on your Android device
2. Connect via USB
3. Run: `buildozer android deploy run logcat`
4. This will build, install, run, and show logs

### View Logs
```bash
# View app logs in real-time
adb logcat | grep python
```

## Build Time

First build will take **20-45 minutes** as buildozer downloads:
- Android SDK (~1 GB)
- Android NDK (~1 GB)
- Build dependencies

Subsequent builds are much faster (2-5 minutes).

## Troubleshooting

### Build fails with "SDK not found"
```bash
# Accept all SDK licenses
buildozer android debug
# When prompted, type 'y' to accept licenses
```

### Out of space
- The `.buildozer` directory can be 3-5 GB
- Ensure you have at least 10 GB free space

### Build fails with "NDK not compatible"
Edit `buildozer.spec` and update:
```ini
android.ndk = 25b  # or latest compatible version
```

### Permission denied errors
```bash
# Ensure buildozer has execute permissions
chmod +x ~/.buildozer/android/platform/android-ndk-*/build/tools/make_standalone_toolchain.py
```

### App crashes on startup
Check logs:
```bash
adb logcat | grep -E "python|kivy|klarbrowser"
```

## Features in Android Version

- ✅ Search functionality
- ✅ Server URL configuration
- ✅ Settings dialog
- ✅ About dialog
- ✅ Result display with scrolling
- ✅ Dark theme optimized for mobile
- ✅ Error handling and user feedback
- ✅ Configuration persistence

## Limitations vs Desktop Version

- No web-based UI (HTML/CSS/JavaScript)
- Simplified interface using native Kivy widgets
- No browser navigation (opens external links in system browser)
- No theme toggle (dark theme only)
- No animated compass/particle effects

## Development

### Testing Changes

```bash
# Quick test on connected device
buildozer android debug deploy run

# View logs
adb logcat | grep python
```

### Modifying the App

Edit `klar_browser_android.py` and rebuild.

### Changing Configuration

Edit `buildozer.spec` to modify:
- Package name
- Version number
- Permissions
- Target API levels
- App icon and splash screen

## File Structure

```
klar/
├── klar_browser.py              # Desktop version (PyQt6)
├── klar_browser_android.py      # Android version (Kivy)
├── main.py                      # Android entry point
├── klar_browser.html            # Desktop UI (not used on Android)
├── buildozer.spec               # Android build configuration
├── requirements.txt             # Desktop dependencies
├── requirements_android.txt     # Android dependencies reference
├── BUILD_ANDROID.md            # This file
└── .buildozer/                 # Build artifacts (created by buildozer)
```

## Signing for Release

For Google Play Store distribution:

```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore my-release-key.keystore -alias klar -keyalg RSA -keysize 2048 -validity 10000

# Sign the APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore \
    bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk klar

# Align the APK
zipalign -v 4 bin/klarbrowser-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk \
    bin/klarbrowser-1.0.0-release.apk
```

## Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Python for Android](https://python-for-android.readthedocs.io/)
- [Android API Levels](https://apilevels.com/)

## Support

For issues specific to:
- **App functionality**: Check `klar_browser_android.py`
- **Build process**: Check `buildozer.spec` and buildozer logs in `.buildozer/`
- **Android compatibility**: Ensure target device runs Android 5.0+ (API 21+)

---

**Note**: The desktop version (`klar_browser.py`) continues to work unchanged. This Android version is an adaptation specifically for mobile platforms.
