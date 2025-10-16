# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Hey Mike!

block_cipher = None

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect ALL MLX packages
mlx_datas, mlx_binaries, mlx_hiddenimports = collect_all('mlx')
mlx_whisper_datas, mlx_whisper_binaries, mlx_whisper_hiddenimports = collect_all('mlx_whisper')
mlx_lm_datas, mlx_lm_binaries, mlx_lm_hiddenimports = collect_all('mlx_lm')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=mlx_binaries + mlx_whisper_binaries + mlx_lm_binaries,
    datas=[
        ('assets/icon.icns', 'assets'),
        ('VERSION', '.'),
    ] + mlx_datas + mlx_whisper_datas + mlx_lm_datas,
    hiddenimports=mlx_hiddenimports + mlx_whisper_hiddenimports + mlx_lm_hiddenimports + [
        # Core modules
        'Core.AudioManager',
        'Core.MLXWhisperManager',
        'Core.MLXLLMManager',
        'Core.TextEnhancer',
        'Core.AmplitudeAnalyzer',
        'Core.HotkeyManager',
        'Core.TextInsertionManager',
        'Core.VSCodeBridge',
        # Note: NoteClassifier excluded - Phase 2 feature, not needed in Phase 1 Mac app
        
        # UI modules
        'UI.MenuBarController',
        'UI.OverlayWindow',
        'UI.OverlayManager',
        'UI.WaveformRenderer',
        
        # Models
        'Models.AppSettings',
        'Models.RecognitionResult',
        'Models.TranscriptionHistory',
        
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        
        # MLX - explicit imports
        'mlx',
        'mlx.core',
        'mlx.nn',
        'mlx.optimizers',
        'mlx_whisper',
        'mlx_whisper.whisper',
        'mlx_whisper.audio',
        'mlx_whisper.decoding',
        'mlx_whisper.model',
        'mlx_whisper.transcribe',
        'mlx_lm',
        'mlx_lm.utils',
        'mlx_lm.models',
        
        # Other dependencies
        'rumps',
        'pyaudio',
        'numpy',
        'pynput',
        'yaml',
        'flask',
        'flask_socketio',
        'flask_cors',
        'eventlet',
        'eventlet.hubs',
        'eventlet.green',
        'eventlet.greenthread',
        'dns',
        'dns.resolver',
        'pyobjc',
        'Cocoa',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'torchvision',
        'torchaudio',
        'tensorflow',
        'matplotlib',
        'pandas',
        'tkinter',
    ],
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
    name='Hey Mike!',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Hey Mike!',
)

app = BUNDLE(
    coll,
    name='Hey Mike!.app',
    icon='assets/icon.icns',
    bundle_identifier='com.unseenium.heymike',
    info_plist={
        'CFBundleName': 'Hey Mike!',
        'CFBundleDisplayName': 'Hey Mike!',
        'CFBundleIdentifier': 'com.unseenium.heymike',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '12.0',
        'LSUIElement': True,  # Menu bar only
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'Hey Mike! needs microphone access for voice dictation and transcription.',
        'NSAppleEventsUsageDescription': 'Hey Mike! needs permission to insert text into applications.',
        'NSRequiresAquaSystemAppearance': False,
    },
)
