# MagikMike Architecture

## 🏗️ System Architecture

MagikMike follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ MenuBarController│  │  Settings UI    │              │
│  │    (rumps)      │  │   (dialogs)     │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Core Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ MLXWhisper  │ │AudioManager │ │HotkeyManager│       │
│  │  Manager    │ │  (PyAudio)  │ │  (pynput)   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                         │
│  ┌─────────────┐ ┌─────────────┐                       │
│  │TextInsertion│ │AppSettings  │                       │
│  │Manager(AX)  │ │  (JSON)     │                       │
│  └─────────────┘ └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                System Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   MLX       │ │   macOS     │ │  Hardware   │       │
│  │ Framework   │ │Accessibility│ │ (Mic, M1+)  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## 📦 Component Details

### UI Layer
- **MenuBarController**: Main application interface using rumps
- **Settings Dialogs**: Native macOS dialog boxes for configuration

### Core Layer
- **MLXWhisperManager**: Handles model loading and transcription
- **AudioManager**: Microphone input and recording management
- **HotkeyManager**: Global keyboard shortcut detection
- **TextInsertionManager**: Cursor detection and text insertion
- **AppSettings**: Configuration persistence and management

### System Layer
- **MLX Framework**: Apple Silicon optimized ML inference
- **macOS Accessibility**: System APIs for text insertion
- **Hardware**: Microphone input and Apple Silicon processing

## 🔄 Data Flow

1. **User triggers recording** (hotkey or menu)
2. **AudioManager captures** microphone input
3. **MLXWhisperManager processes** audio through Whisper model
4. **TextInsertionManager inserts** transcribed text at cursor
5. **MenuBarController provides** visual feedback

## 🔧 Configuration Management

Settings are stored in JSON format at `~/.magikmike_settings.json`:

```json
{
  "model": "medium",
  "language": null,
  "hotkey": "cmd+shift+space",
  "audio_device": null,
  "max_recording_duration": 30.0,
  "silence_duration": 2.0,
  "silence_threshold": 500,
  "insertion_method": "auto",
  "notifications": true
}
```

## 🧠 Model Management

- **Pre-download**: All models downloaded on first run
- **Instant switching**: Models cached for immediate access
- **Memory efficient**: Only active model kept in memory
- **MLX optimized**: All models use Apple Silicon acceleration

## 🔐 Security Architecture

- **Offline processing**: No network communication during transcription
- **Local storage**: All models and data stored locally
- **Permission based**: Requires explicit microphone/accessibility access
- **No telemetry**: Zero data collection or external communication

## ⚡ Performance Optimizations

- **Lazy loading**: Models loaded only when needed
- **Background processing**: Pre-download doesn't block UI
- **Apple Silicon**: MLX framework for maximum performance
- **Memory management**: Automatic cleanup and optimization

## 🚀 Future Architecture (Swift Migration)

```
┌─────────────────────────────────────────────────────────┐
│                 Swift UI Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │   NSStatusItem  │  │   SwiftUI       │              │
│  │  (Native Menu)  │  │  (Settings)     │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
                           │ IPC/XPC
┌─────────────────────────────────────────────────────────┐
│               Python Backend                            │
│  (Existing Core Layer - Unchanged)                     │
└─────────────────────────────────────────────────────────┘
```

This hybrid approach will provide:
- **Native macOS UI** with Swift/SwiftUI
- **Proven ML backend** with existing Python/MLX code
- **Best of both worlds** - Native UX + Python ML ecosystem
