# Hey Mike! - VS Code Extension

> **AI-Powered Voice Coding Assistant with Local MLX**

Transform your coding with voice! Hey Mike! brings intelligent voice transcription and AI-powered code assistance directly into VS Code.

---

## ✨ Features

### 🎙️ **Smart Mode**
- Voice-to-text with AI enhancement
- Auto-detects English and enhances punctuation, grammar, and formatting
- Direct paste for non-English languages
- Lightning-fast MLX-optimized Whisper

### ⚡ **Action Mode** (v2.0)
- Voice commands for code navigation
- "Explain this function"
- "Search for error handling"
- "Open settings file"
- Voice note capture (bugs, TODOs, questions)

### 🧠 **Local AI Models**
- **Whisper**: 5 models (39MB - 1.5GB)
- **Text LLM**: 3 models for enhancement (800MB - 2.4GB)
- **Code LLM**: 4 models for code understanding (1.3GB - 7GB)
- 100% offline and private

### 🎯 **Rich VS Code Integration**
- Status bar with live recording/processing indicators
- Quick Pick menu for common actions
- Hotkey support (Cmd+Shift+Space, Cmd+Opt+1/2)
- Synchronized with macOS menu bar app

---

## 🚀 Quick Start

### Prerequisites
1. **macOS with Apple Silicon** (M1/M2/M3)
2. **Python 3.10+**
3. **VS Code 1.80+**

### Installation

**Step 1: Install Backend**
```bash
# Clone Hey Mike! backend
git clone https://github.com/Unseenium/HeyMike
cd HeyMike

# Create virtual environment
python3 -m venv MagikMike
source MagikMike/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python main.py
```

**Step 2: Install Extension**
1. Open VS Code
2. Press `Cmd+Shift+P`
3. Search "Extensions: Install from VSIX"
4. Select `heymike-2.0.0.vsix`
5. Reload VS Code

**Step 3: Configure**
1. Open Settings (`Cmd+,`)
2. Search "Hey Mike"
3. Set models and preferences
4. Click status bar to test connection

---

## 🎯 How to Use

### Recording
- **Global Hotkey**: `Cmd+Shift+Space` (works anywhere in macOS)
- **Status Bar**: Click "Hey Mike!" icon → "Start Recording"

### Modes
- **Smart Mode** (`Cmd+Opt+1`): AI text enhancement
- **Action Mode** (`Cmd+Opt+2`): Voice commands

### Quick Actions
Click the Hey Mike! status bar icon to access:
- 🎙️ Start Recording
- 📝 Smart Mode
- ⚡ Action Mode
- ❓ Explain Code
- 🔍 Search Code
- ⚙️ Settings

---

## ⚙️ Settings

### Connection
- `heymike.backendPort`: Backend server port (default: 8765)
- `heymike.autoReconnect`: Auto-reconnect if disconnected

### Models
- `heymike.whisperModel`: Transcription model (tiny/base/small/medium/large)
- `heymike.textLLM`: Text enhancement LLM
- `heymike.codeLLM`: Code understanding LLM (v2.0)

### Behavior
- `heymike.currentMode`: Active mode (smart/action)
- `heymike.enhancementStyle`: Text style (standard/professional/casual/technical)
- `heymike.alwaysRaw`: Disable AI enhancement
- `heymike.showOverlays`: Show explanation overlays (v2.0)

### UI
- `heymike.showStatusBar`: Show/hide status bar item

---

## 🎨 Status Bar Icons

| Icon | Meaning |
|------|---------|
| `$(mic) Hey Mike (Smart)` | Ready - Smart Mode |
| `$(mic) Hey Mike (Action)` | Ready - Action Mode |
| `$(record) Recording...` | Recording audio (pulsing) |
| `⠋ Transcribing...` | Processing (spinning) |
| `$(debug-disconnect) Hey Mike` | Backend disconnected |
| `$(error) Error` | Connection error |

---

## 🔧 Troubleshooting

### "Backend is not connected"
1. Make sure Python backend is running: `python main.py`
2. Check port in settings matches backend
3. Try manual reconnect from Quick Pick menu

### "Models not loading"
1. Models download on first use
2. Check internet connection
3. See logs: `Developer: Show Logs` → "Hey Mike!"

### "Hotkeys not working"
- Hotkeys are managed by the macOS backend
- Check System Preferences → Security & Privacy → Accessibility
- Make sure "Terminal" or your Python app has permission

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│      VS Code Extension (TS)         │
│  ┌────────────────────────────────┐ │
│  │ Status Bar   │   Quick Pick    │ │
│  ├────────────────────────────────┤ │
│  │ Action Router │ Settings Sync  │ │
│  └────────────┬───────────────────┘ │
└───────────────┼─────────────────────┘
                │ WebSocket (8765)
┌───────────────┼─────────────────────┐
│      Python Backend (MLX)           │
│  ┌────────────▼───────────────────┐ │
│  │       VSCodeBridge             │ │
│  ├────────────────────────────────┤ │
│  │  Whisper │ Text LLM │ Code LLM │ │
│  ├────────────────────────────────┤ │
│  │  Audio Manager │ Hotkey Mgr   │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 🗺️ Roadmap

### v2.0 (Q4 2025) - Current Development
- ✅ Hybrid architecture (Python + VS Code)
- ✅ Dual UI (macOS menu + VS Code status bar)
- ⏳ Code LLM integration
- ⏳ Explain code feature
- ⏳ Voice note capture
- ⏳ Smart navigation

### v2.1 (Q1 2026)
- Overlay panels for explanations
- Multi-cursor voice editing
- Code generation
- Inline suggestions

### v3.0 (Q2 2026)
- AI Pair Programmer
- Context-aware suggestions
- Refactoring commands
- Git integration

---

## 🙏 Support

- **Issues**: [GitHub Issues](https://github.com/Unseenium/HeyMike/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Unseenium/HeyMike/discussions)
- **Email**: hello@unseenium.com

---

## 📄 License

MIT License - See [LICENSE](../LICENSE)

---

## 🎉 Acknowledgments

- Built with ❤️ by [Unseenium](https://unseenium.com)
- Powered by [MLX](https://github.com/ml-explore/mlx) (Apple Silicon optimization)
- Uses [Whisper](https://github.com/openai/whisper) (OpenAI)
- Inspired by [Cursorless](https://github.com/cursorless-dev/cursorless)

---

**Made with 🎙️ for developers who code faster by voice!**
