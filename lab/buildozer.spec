[app]
title = Klar
package.name = klar
package.domain = se.oscyra

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,ico

version = 3.0.0

requirements = python3,kivy,requests,beautifulsoup4,lxml,pillow,pycryptodome

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION
android.api = 34
android.minapi = 21
android.ndk = 26b
android.private_storage = True
android.logcat_filters = *:S python:D
android.copy_libs = 1
android.archs = arm64-v8a,armeabi-v7a

android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1,com.google.android.material:material:1.9.0
android.add_src = 

[buildozer]
log_level = 2
warn_on_root = 1
