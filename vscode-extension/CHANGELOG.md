# Change Log

All notable changes to the "Hey Mike!" VS Code extension will be documented in this file.

## [2.0.0] - 2025-09-30

### Added - Initial Release 🎉
- **Hybrid Architecture**: Python backend + VS Code frontend
- **Dual UI System**: macOS menu bar + VS Code status bar
- **WebSocket Bridge**: Real-time communication with backend
- **Status Bar**: Live recording/processing indicators with animations
- **Quick Pick Menu**: Quick access to common actions
- **Smart Mode**: AI text enhancement with auto-language detection
- **Action Mode**: Voice command infrastructure (v2.0 Phase 1)
- **Settings Sync**: Bidirectional sync between VS Code and backend
- **Model Selection**: Configure Whisper, Text LLM, and Code LLM models
- **Commands**:
  - `heymike.startRecording`: Start voice recording
  - `heymike.explainCode`: Explain selected code (v2.0)
  - `heymike.searchCode`: Search codebase
  - `heymike.switchToSmartMode`: Switch to Smart Mode
  - `heymike.switchToActionMode`: Switch to Action Mode
  - `heymike.showQuickPick`: Show quick actions menu
  - `heymike.openSettings`: Open extension settings

### Features
- ✅ Transcription routing (Smart/Action modes)
- ✅ Text insertion at cursor
- ✅ Status bar animations (recording, processing)
- ✅ Auto-reconnect on disconnect
- ✅ Configuration UI in VS Code settings
- ✅ Welcome message on first install

### Backend Integration
- WebSocket connection on port 8765
- HTTP REST API for settings and explanations
- Real-time state synchronization
- Event-driven architecture

### Settings
- `heymike.backendPort`: Backend server port (default: 8765)
- `heymike.autoReconnect`: Auto-reconnect if disconnected (default: true)
- `heymike.whisperModel`: Whisper model selection
- `heymike.textLLM`: Text enhancement LLM selection
- `heymike.codeLLM`: Code understanding LLM selection
- `heymike.enhancementStyle`: Text enhancement style
- `heymike.currentMode`: Current mode (smart/action)
- `heymike.alwaysRaw`: Disable AI enhancement
- `heymike.showOverlays`: Show explanation overlays (v2.0)
- `heymike.showStatusBar`: Show/hide status bar item

---

## [Unreleased]

### Planned for v2.0.1
- Code explanation overlay panel
- Voice note capture UI
- Smart code navigation
- Context-aware command parsing

### Planned for v2.1
- Inline code suggestions
- Multi-cursor voice editing
- Code generation from voice
- Git voice commands

### Planned for v3.0
- AI Pair Programmer mode
- Context-aware refactoring
- Real-time collaboration
- Team voice workflows

---

## Version History

### Pre-release
- v1.5.0: Smart Mode (Python-only, macOS menu bar)
- v1.0.0: Basic transcription (Python-only)

---

**Note**: This is the first release of the VS Code extension. The Python backend (HeyMike v1.5) has been in production since September 2025.
