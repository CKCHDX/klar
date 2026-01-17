# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['klar_browser.py'],
    pathex=[],
    binaries=[],
    datas=[('keywords_db.json', '.'), ('domains.json', '.'), ('klar.ico', '.'), ('engine', 'engine')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.sip', 'requests', 'bs4', 'lxml', 'engine.domain_whitelist', 'engine.demographic_detector', 'engine.loki_system', 'engine.setup_wizard'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Klar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\akoj2\\Desktop\\klar\\3.1\\klar.ico'],
)
