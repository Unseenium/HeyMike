# Changelog

All notable changes to Hey Mike! will be documented in this file.

## [2.0.0] - 2025-09-30

### 🚀 Major Release: VS Code Integration + Hybrid Architecture

This is a **major release** that transforms Hey Mike! from a standalone macOS dictation tool into a hybrid system with deep VS Code integration!

### Added - VS Code Extension 🎉

#### Core Features
- 🔌 **VS Code Extension** - Full-featured TypeScript extension for VS Code
- 🌉 **WebSocket Bridge** - Real-time bidirectional communication (Python ↔ VS Code)
- 🤖 **Auto-Start Backend** - Extension automatically starts Python backend if not running
- 🔄 **Hybrid Architecture** - Backend runs standalone OR managed by VS Code
- 📊 **Status Bar Integration** - Live recording/processing indicators with animations
- 🎯 **Quick Pick Menu** - Fast access to commands and settings
- ⚙️ **Settings Sync** - Bidirectional sync between VS Code and Python backend

#### Backend Enhancements
- 🌐 **Flask-SocketIO Server** - WebSocket server on port 8765
- 📡 **HTTP REST API** - `/health`, `/api/settings`, `/api/explain` endpoints
- 🔔 **State Notifications** - Recording, processing, and mode changes broadcast to VS Code
- 🎨 **Dual UI System** - macOS menu bar + VS Code status bar (synchronized)

#### Smart Features
- ✨ **Smart Mode** - Auto-detects English for AI enhancement, direct paste for other languages
- ⚡ **Action Mode** - Voice command infrastructure with intelligent fallback
- 🧠 **LLM Model Selection** - Choose from 3 text enhancement models via UI
- 🔍 **Process Monitoring** - Backend logs visible in VS Code Debug Console
- 🔁 **Auto-Reconnect** - Handles backend crashes and restarts gracefully

### VS Code Extension Details

#### Commands (7 total)
- `heymike.startRecording` - Start voice recording
- `heymike.explainCode` - Explain selected code (v2.0 foundation)
- `heymike.searchCode` - Search codebase
- `heymike.switchToSmartMode` - Switch to Smart Mode (Cmd+Opt+1)
- `heymike.switchToActionMode` - Switch to Action Mode (Cmd+Opt+2)
- `heymike.showQuickPick` - Show quick actions menu
- `heymike.openSettings` - Open extension settings

#### Configuration Settings (12 total)
- `heymike.backendPort` - Backend server port (default: 8765)
- `heymike.autoReconnect` - Auto-reconnect if disconnected (default: true)
- `heymike.autoStartBackend` - Auto-start backend if not running (default: true)
- `heymike.stopBackendOnExit` - Stop backend when extension exits (default: false)
- `heymike.whisperModel` - Whisper model selection (5 options)
- `heymike.textLLM` - Text enhancement LLM (3 options)
- `heymike.codeLLM` - Code understanding LLM (4 options, future use)
- `heymike.enhancementStyle` - Text style (4 options)
- `heymike.currentMode` - Active mode (smart/action)
- `heymike.alwaysRaw` - Disable AI enhancement (default: false)
- `heymike.showOverlays` - Show explanation overlays (default: true)
- `heymike.showStatusBar` - Show status bar item (default: true)

#### Architecture Components
- **BackendClient** - WebSocket connection management
- **StatusBarManager** - Animated status bar (recording, processing, modes)
- **QuickPickMenu** - Command palette integration
- **ActionRouter** - Route transcriptions to Smart/Action mode handlers
- **SettingsSync** - Bidirectional settings synchronization

### Changed
- **Transcription Routing** - Now sends to VS Code if connected, falls back to local insertion
- **Mode System** - Simplified from 3 modes → 2 modes (Smart, Action)
- **Settings** - Added `always_raw` option to disable AI enhancement
- **Logging** - Backend output now visible in VS Code Debug Console

### Enhanced
- **LLM Integration** - Added UI for model selection (Llama 3.2 1B, Phi-3 Mini, Qwen 2.5 1.5B)
- **Error Handling** - Better error messages and retry logic
- **User Experience** - No manual terminal management needed
- **Documentation** - Added comprehensive PRDs, roadmap, and feature specs

### Dependencies Added
- `Flask>=3.0.0` - Web framework for WebSocket bridge
- `Flask-SocketIO>=5.3.0` - WebSocket support
- `Flask-CORS>=4.0.0` - Cross-origin resource sharing
- `python-socketio>=5.10.0` - Python Socket.IO client
- `eventlet>=0.33.0` - Async networking library

### Fixed
- Long recording crash bug (see v1.5.0 fixes - still applies)
- Action Mode fallback - Now silently inserts text if command not recognized
- Process cleanup - Backend gracefully stops on extension deactivation (if configured)

### Documentation
- Added `design_docs/PRD-v2.0.md` - VS Code integration PRD
- Added `design_docs/action-mode-features.md` - Future features roadmap
- Added `vscode-extension/README.md` - Extension user guide
- Updated `PROJECT_STRUCTURE.md` - Added vscode-extension/ structure

### Technical Notes
- **Backward Compatible** - Backend still works standalone without VS Code
- **Standalone Mode** - Auto-started backend continues running after extension exit
- **Port** - WebSocket server runs on port 8765 (configurable)
- **Process Management** - Smart Python venv detection and process spawning

### Breaking Changes
None - v1.5 standalone mode fully supported!

### Migration Guide
**From v1.5 to v2.0:**
1. Install Flask dependencies: `pip install -r requirements.txt`
2. (Optional) Install VS Code extension from `vscode-extension/`
3. Backend continues to work exactly as before
4. VS Code integration is additive, not required

---

## [1.5.0] - 2025-09-29

### Added
- **Smart Mode** - Auto-enhances English, direct paste for other languages
- **AI Text Enhancement** - LLM integration for punctuation, grammar, filler word removal
- **LLM Model Selection** - Choose from 3 models via menu bar
- **2-Mode System** - Simplified from 3 modes to 2 (Smart, Action)
- **Mode Switching** - Hotkeys Cmd+Opt+1/2 for Smart/Action modes

### Fixed - CRITICAL
- **Long Recording Crash Bug** - Fixed 5 critical issues:
  1. Increased max recording duration from 30s → 300s (5 minutes)
  2. Changed audio buffer from Queue → numpy list (4-8x more memory efficient)
  3. Added 100MB safety limit to prevent unbounded memory growth
  4. Implemented proper buffer cleanup (prevents memory leaks)
  5. Added warnings when approaching max duration

### Changed
- Audio buffer implementation (Queue → list of numpy arrays)
- Max recording duration (30s → 300s)
- Buffer size monitoring (added 100MB limit)
- Enhanced logging (duration, memory stats on recording stop)
- Thread safety (added buffer_lock)

### Technical Details
See `CHANGELOG.md` v1.5.0 for complete bugfix details.

---

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
