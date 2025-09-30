# Changelog

All notable changes to Hey Mike! will be documented in this file.

## [1.0.0] - 2025-09-26

### Added
- 🎤 MLX Whisper-based speech recognition system
- 📱 Native macOS menu bar interface with rumps
- 🧠 Support for 5 Whisper model sizes (tiny, base, small, medium, large)
- ⚡ Pre-downloading of all models for instant switching
- 🎙️ Real-time audio recording and transcription
- ⌨️ Customizable global hotkeys (default: Cmd+Shift+Space)
- 🎯 Intelligent text insertion at cursor position
- 🌍 Multi-language support (99+ languages)
- ⚙️ Comprehensive settings system
- 🔐 Privacy-focused offline processing
- 📊 Visual feedback and status indicators
- 🧪 Comprehensive test suite (68 tests)

### Technical Features
- MLX-optimized Whisper models for Apple Silicon
- PyAudio integration for microphone access
- macOS Accessibility API for text insertion
- Global hotkey detection with pynput
- Settings persistence with JSON storage
- Error handling and graceful degradation
- Memory-efficient model management

### UI/UX Features
- 🎨 Modern emoji-based menu interface
- 📈 Real-time visual feedback
- 🔔 System notifications for all actions
- 📋 Detailed system status and diagnostics
- 🛠️ Easy permission management
- 🚀 One-click model downloading

### Performance
- ⚡ Startup time: < 3 seconds
- 🔄 Model switching: < 2 seconds  
- 🎙️ Recording latency: < 100ms
- 💾 Memory usage: < 500MB with all models
- 🔋 Optimized for Apple Silicon efficiency

### Security & Privacy
- 🔒 100% offline processing
- 🚫 No data sent to external servers
- 🏠 Local model storage only
- 🔐 Secure permission handling
- 🛡️ No telemetry or tracking

---

## [1.5.0] - 2025-09-29

### Added
- ✨ Smart Mode: AI-powered text enhancement
- 🧠 MLX LLM integration (Llama 3.2 1B)
- 🎯 Automatic language detection (English vs non-English)
- 📝 Enhancement styles: Standard, Professional, Casual, Technical
- 🔄 Two-mode system: Smart Mode (⌥⌘1) & Action Mode (⌥⌘2)
- ⌨️ Mode-switching hotkeys with visual feedback
- 🎨 Updated menu bar UI with mode indicators

### Fixed
- 🐛 **CRITICAL: Long recording crash bug**
  - Increased max recording duration: 30s → 5 minutes
  - Fixed memory leak: 4-8x more efficient buffer usage
  - Added 100MB safety limit (prevents OOM crashes)
  - Added warning at 80% of max duration
  - Proper cleanup on auto-stop and errors
  - Thread-safe buffer access with locks
- 🔧 Hotkey detection issue with modifier keys on macOS
- 🎯 Text enhancement LLM prompt improvements
- 🧹 Memory cleanup on app exit (LLM model unloading)

### Changed
- 📊 Audio buffer: Queue → List of numpy arrays (4-8x memory reduction)
- ⏱️ Max recording: 30s → 300s (5 minutes)
- 🛡️ Added buffer size limit: 100MB hard cap
- 📝 Enhanced logging with duration and memory stats
- 🔐 Thread-safe audio buffer access

### Technical Improvements
- Efficient numpy array handling (no list conversion)
- Real-time buffer size tracking
- Graceful shutdown on limits
- Complete cleanup on errors
- Better error messages and warnings

---

## [2.0.0] - Planned (Q4 2025)

### Planned Features
- 🚀 Hybrid Architecture: Python Backend + VS Code Extension
- 🎯 Action Mode: Voice-controlled code navigation
- 💬 Code explanations with local LLM
- 🔍 Semantic code search
- 📝 Voice note capture
- 🎨 Dual UI: Menu bar + VS Code status bar
- 🔗 WebSocket bridge for backend-frontend communication
- 🧠 LLM Orchestrator (2-model system: Text 1B + Code 3B)

See `design_docs/PRD-v2.0.md` for full specifications.
