[app]
# Application metadata
title = Klar 3.1
package.name = klar
package.domain = oscyra.solutions

# App version
version = 3.1.0
version.regex = __version__ = ['"]([^'"]+)['"]
version.filename = %(source.dir)s/__init__.py

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*,images/*

# Build requirements
requirements = python3,kivy,pillow,pyjnius,plyer,requests,beautifulsoup4,lxml

# Compile settings  
compile_dir = bin/compiledir
compile_targets = arm64-v8a
compile_py = yes
compile_pyo = yes

# Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,VIBRATE,INTERNET

# Features
android.features = android.hardware.touchscreen,android.hardware.internet

# Architecture
android.archs = arm64-v8a,armeabi-v7a
android.accepted_abis = arm64-v8a,armeabi-v7a

# Build info
android.gradle_dependencies = androidx.appcompat:appcompat:1.3.1,androidx.constraintlayout:constraintlayout:2.1.1
android.add_src = 
android.add_libs_armeabi_v7a = 
android.add_libs_arm64_v8a = 

# API levels
android.minapi = 24
android.targetapi = 31
android.ndk = 25b
android.sdk = 31

# Orientation
android.orientation = portrait
android.allow_landscape = 0

# App icon and presplash
icon.filename = klar.ico
presplash.filename = %(source.dir)s/data/presplash.png

# Permissions policy
android.request_permissions = 1

# Fullscreen settings
fullscreen = 0

# Android logging
android.logcat_filters = *:S python:D

# NetworkSecurityConfig for cleartext traffic
android.network_security_config = %(source.dir)s/network_security_config.xml

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1

# Build directory
build_dir = .buildozer
bindroid.bin_dir = bin

# Android SDK/NDK paths (auto-detected if not set)
# android_sdk_root = /path/to/android-sdk
# android_ndk_root = /path/to/android-ndk

# Java version
java_version = 11
