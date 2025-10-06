#!/usr/bin/env python3
"""
Hey Mike! - macOS Application Setup (py2app - DEPRECATED)

⚠️  THIS FILE IS DEPRECATED - USE PYINSTALLER INSTEAD ⚠️

PyInstaller (heymike.spec) is now used for building the .app bundle.
py2app has recursion issues with MLX/PyQt6 dependencies.

To build:
    pyinstaller heymike.spec --clean
    ./scripts/create_macos_dmg.sh

See: dev-docs/build-process.md

---

Package Python application as native macOS .app bundle using py2app
"""

import sys
sys.setrecursionlimit(10000)  # Increase recursion limit BEFORE any imports

from setuptools import setup
import os

# Read version
with open('VERSION', 'r') as f:
    version = f.read().strip()

APP = ['main.py']
DATA_FILES = [
    ('assets', ['assets/icon.icns']),
    # Assets are now handled by PyInstaller (heymike.spec)
    # This py2app setup.py is deprecated
    ('assets', ['assets/menubar_icon_hey_mike.png']),
    ('', ['VERSION']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icon.icns',
    
    # Use includes instead of packages for better control
    'includes': [
        # Core dependencies
        'rumps',
        'pyaudio',
        'numpy',
        'pynput',
        'yaml',
        
        # PyQt6 for overlay
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        
        # Flask for VS Code bridge
        'flask',
        'flask_socketio',
        'flask_cors',
        'eventlet',
        
        # Our modules
        'Core',
        'UI',
        'Models',
    ],
    
    # Explicitly exclude problematic packages
    'excludes': [
        'torch',
        'torchvision', 
        'torchaudio',
        'tensorflow',
        'tkinter',
        'unittest',
        'test',
        'tests',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
        'PIL',
        'Pillow',
    ],
    
    # Don't bundle everything (use semi-standalone)
    'semi_standalone': False,
    'site_packages': True,
    
    # Optimize
    'optimize': 0,
    'compressed': True,
    
    # App metadata
    'plist': {
        'CFBundleName': 'Hey Mike!',
        'CFBundleDisplayName': 'Hey Mike!',
        'CFBundleIdentifier': 'com.unseenium.heymike',
        'CFBundleVersion': version,
        'CFBundleShortVersionString': version,
        'LSMinimumSystemVersion': '12.0',
        'LSUIElement': True,  # Menu bar only
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'Hey Mike! needs microphone access for voice dictation and transcription.',
        'NSAppleEventsUsageDescription': 'Hey Mike! needs permission to insert text into applications.',
        'NSRequiresAquaSystemAppearance': False,
    },
}

setup(
    name='Hey Mike!',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    version=version,
    description='AI-powered voice dictation for Mac',
    author='Unseenium',
    author_email='hello@unseenium.com',
    url='https://github.com/Unseenium/HeyMike',
    license='MIT',
)