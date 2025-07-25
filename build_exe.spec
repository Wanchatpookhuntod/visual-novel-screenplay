# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Visual Novel Node Editor
This file defines how to build the executable including all necessary files and fonts
"""

import os
import sys
from pathlib import Path

# Get current directory
current_dir = Path('.')

# Define data files to include
datas = []

# Add Thai fonts
font_dir = current_dir / 'font'
if font_dir.exists():
    for font_file in font_dir.glob('*.ttf'):
        datas.append((str(font_file), 'font'))

# Add any other data files if needed
# datas.append(('data', 'data'))  # Example for data folder

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'reportlab.lib.fonts',
    'reportlab.pdfbase.ttfonts',
    'reportlab.pdfbase.pdfmetrics',
    'reportlab.platypus',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'PIL.Image',
    'PIL.ImageFont',
]

# Analysis step
a = Analysis(
    ['main_clean.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Visual_Novel_Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico file path here if you have an icon
    version='version_info.txt'  # Optional version info file
)
