# ShareToMac.spec
#
# PyInstaller spec file for macOS .app bundle.
# Handles PyQt6 correctly by collecting all its dylibs and plugins.
#
# Usage:
#   pyinstaller ShareToMac.spec

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect PyQt6 Qt plugins (required for macOS rendering)
pyqt6_datas = collect_data_files("PyQt6", includes=["Qt/plugins/**/*"])
pyqt6_libs = collect_dynamic_libs("PyQt6")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=pyqt6_libs,
    datas=pyqt6_datas,
    hiddenimports=[
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ShareToMac",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ShareToMac",
)

app = BUNDLE(
    coll,
    name="ShareToMac.app",
    icon=None,
    bundle_identifier="com.sharetomac.app",
    # Embed the Python shared library inside the .app bundle using @executable_path
    # so it resolves correctly regardless of where the .app is installed.
    info_plist={
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "13.0",
    },
)
