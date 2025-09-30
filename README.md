# Hey Mike!

[![GitHub](https://img.shields.io/badge/GitHub-Unseenium%2FHeyMike-blue.svg)](https://github.com/Unseenium/HeyMike)
[![Version](https://img.shields.io/badge/Version-2.0-brightgreen.svg)](CHANGELOG.md)
[![macOS](https://img.shields.io/badge/macOS-12.0+-blue.svg)](https://developer.apple.com/macos/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-M1%2FM2%2FM3-orange.svg)](https://en.wikipedia.org/wiki/Apple_silicon)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://openai.com/research/whisper)
[![Unseenium](https://img.shields.io/badge/Made%20by-Unseenium-red.svg)](https://github.com/Unseenium)

🎤 **Voice dictation that actually makes sense.** Multi-mode AI transcription that's completely private, lightning fast, and works in 99+ languages.

> **🚀 v2.0 Released (Sept 2025)**: VS Code Integration + Hybrid Architecture! Auto-start backend, live status bar, and seamless voice coding in VS Code. See [CHANGELOG](CHANGELOG.md).

## ✨ What Makes Hey Mike! Amazing

- **🎯 Two Powerful Modes**: Smart (auto-enhances English), or Action (voice commands)
- **⌨️ Instant Mode Switching**: `⌥⌘1/2` hotkeys to switch modes on the fly
- **🌍 True Multilingual**: Supports 99+ languages - Tamil, Japanese, Spanish, you name it
- **✨ Smart AI Enhancement**: Automatically cleans up English text with punctuation, grammar, and removes filler words
- **🔒 Completely Private**: Your voice never leaves your Mac - 100% offline processing (even the AI!)
- **⚡ Lightning Fast**: Optimized for Apple Silicon with near-instant transcription
- **🎨 Beautiful Interface**: Clean menu bar app with mode indicators
- **🧠 Smart Models**: Choose from 5 Whisper models + 3 LLM models + 4 enhancement styles
- **📱 Native macOS**: Works with any app - TextEdit, Slack, Email, IDE, Terminal
- **🎯 Precision**: >98% accuracy that gets better the more you use it

## 🚀 What's New in v2.0 (Sept 2025)

### 🔌 VS Code Integration
- **Full VS Code Extension** - Deep integration with VS Code for seamless voice coding
- **Auto-Start Backend** - Extension automatically starts Python backend if not running
- **Live Status Bar** - See recording/processing status with animations (🔴 Recording, ⠋ Processing)
- **Quick Pick Menu** - Fast access to commands and settings (click status bar icon)
- **Settings Sync** - Configure models and settings directly in VS Code

### 🌉 Hybrid Architecture
- **Dual UI System** - macOS menu bar + VS Code status bar (synchronized!)
- **Standalone Mode** - Backend still works independently without VS Code
- **WebSocket Bridge** - Real-time communication on port 8765
- **Process Monitoring** - Backend logs visible in VS Code Debug Console
- **Smart Reconnection** - Handles backend crashes and restarts gracefully

### 🎯 Enhanced Features
- **7 VS Code Commands** - Start recording, explain code, search, switch modes, settings
- **12 Configuration Options** - Full control over backend, models, and behavior
- **Backend API** - HTTP REST API for settings and LLM requests
- **State Synchronization** - Recording, processing, and mode changes broadcast everywhere

### 📦 Installation (VS Code)
```bash
# 1. Install Python backend dependencies
cd HeyMike
pip install -r requirements.txt

# 2. Open VS Code extension folder
cd vscode-extension
code .

# 3. Press F5 to test (auto-starts backend!)
# Or: Install from VSIX (coming soon)
```

**[See full v2.0 docs →](vscode-extension/README.md)**

---

## 🆕 What's New in v1.5 (Sept 2025)

### ✨ Smart Mode with AI Enhancement
- **Auto-detects English** and enhances with AI (punctuation, grammar, filler word removal)
- **Direct paste for non-English** - works seamlessly with 99+ languages
- **4 enhancement styles**: Standard, Professional, Casual, Technical
- **Powered by local LLM** (Llama 3.2 1B) - completely private!

### 🐛 Critical Bug Fixes
- **5-minute recordings**: Increased from 30s limit (no more crashes!)
- **4-8x less memory**: Efficient buffer management
- **100MB safety limit**: Prevents out-of-memory crashes
- **Warning at 4 minutes**: Get notified before auto-stop
- **Complete cleanup**: No more memory leaks

### 🎯 Simplified UX
- **Two modes** (was 3): Smart + Action
- **Better hotkeys**: `⌥⌘1` (Smart) / `⌥⌘2` (Action)
- **Mode indicators**: 📝 (Smart) / ⚡ (Action) in menu bar
- **Auto-detection**: No manual language switching needed

[See full changelog →](CHANGELOG.md)

---

## 🖥️ What You Need

- **macOS 12.0+** with **Apple Silicon** (M1/M2/M3) - The magic happens here
- **Python 3.8+** - Don't worry, setup is automatic
- **200MB - 2GB RAM** - Depending on which AI model you choose
- **Microphone permission** - So Hey Mike! can hear you
- **Accessibility permission** - So it can type for you

## 🚀 Get Started in 3 Minutes

**1. Install Dependencies**
```bash
# Install system requirements
brew install portaudio ffmpeg
```

**2. Get Hey Mike!**
```bash
git clone https://github.com/Unseenium/HeyMike.git
cd HeyMike

# Install Python dependencies
pip install -r requirements.txt
```

**3. Grant Permissions**
- Open **System Preferences → Security & Privacy → Privacy**
- Add **Terminal** to both **Microphone** and **Accessibility**

**4. Launch Hey Mike!**
```bash
python main.py
```

**That's it!** 🎉 Look for the 🎤 icon in your menu bar.

**Note:** On first run, Hey Mike! will download:
- Whisper model (~39MB-1.5GB depending on model)
- LLM for text enhancement (~800MB)
This only happens once!

## 🎯 How to Use Hey Mike!

### Choose Your Mode First

Hey Mike! has **two modes** for different use cases:

**📝 Smart Mode** (`⌥⌘1`) - **Default**
- **Automatically enhances English** with AI cleanup (punctuation, grammar, removes filler words)
- **Direct paste for non-English** (Tamil, Japanese, Spanish, etc.)
- **Auto-detects language** - no manual switching needed!
- Perfect for: Emails, documents, multilingual notes, professional writing
- **Optional**: Disable AI enhancement in Settings → "Always use raw transcription"

**⚡ Action Mode** (`⌥⌘2`) - *Coming Soon*
- Voice commands to control your Mac
- "Open README", "Search for bug", etc.
- Perfect for: Hands-free coding, automation

**The menu bar icon shows your current mode:** 📝 (Smart) / ⚡ (Action)

### Recording is Simple

1. **Choose your mode** (press `⌥⌘1` for Smart, `⌥⌘2` for Action)
2. **Position your cursor** where you want text
3. **Press ⌘⇧Space** to start recording (icon turns 🔴)
4. **Speak naturally** - don't worry about filler words!
5. **Press ⌘⇧Space again** to stop
6. **Watch the magic** - text appears instantly!

### First Time Setup
- Hey Mike! downloads AI models on first launch (~2GB total)
- The menu bar shows ✅ when ready
- Start in **Smart Mode** (📝) - it automatically handles any language!

### ✨ See Smart Mode in Action

**Smart Mode - Non-English** (auto-detected):
```
You say: "வேண்டாம் சரி, சரி, சரி"
Result:  "வேண்டாம் சரி, சரி, சரி"  ✅ Perfect Tamil! (direct paste)
```

**Smart Mode - English** (auto-enhanced):
```
You say: "hey um send that file like the one from yesterday you know"
Result:  "Hey, send that file, the one from yesterday."  ✨ AI cleaned!
```

**Why it matters:** This is what makes Hey Mike! better than macOS dictation - ONE mode that handles everything!

## ⚙️ Customize Hey Mike!

### Menu Bar Controls
Click the icon (📝/⚡) to access:
- **🎯 Transcription Mode**: Switch between Smart or Action modes
- **🧠 Models**: Choose your Whisper model (5 options from lightning-fast to ultra-accurate)
- **✨ Text Enhancement**: 
  - Choose AI style (standard/professional/casual/technical)
  - Toggle "Always use raw transcription" to disable AI enhancement
- **⌨️ Hotkey**: Change your recording shortcut  
- **🎙️ Audio**: Select your microphone
- **🌍 Language**: Set your preferred language (or leave on auto-detect)

### Hotkey Reference
- **⌥⌘1**: Switch to Smart Mode (📝)
- **⌥⌘2**: Switch to Action Mode (⚡)
- **⌘⇧Space**: Start/Stop recording (default, customizable)
- **Esc**: Cancel recording

### Pro Tips for Perfect Results

**Smart Mode Handles Everything:**
- **Just speak naturally** - AI automatically cleans up English ("um", "uh", filler words)
- **Multilingual? No problem** - Smart mode detects non-English and pastes directly
- **Want raw text?** Toggle "Always use raw transcription" in Text Enhancement settings

**Speak Naturally:**
- **Don't overthink it** - AI handles messy speech for English
- **Quiet environment** helps, but Hey Mike! handles background noise well
- **Switch languages freely** - Smart mode adapts automatically

**Choose Your Whisper Model:**
  - **Tiny**: Lightning fast (~1s, 39MB) - great for quick notes
  - **Base**: Balanced (~2s, 74MB) - perfect for most use
  - **Large**: Ultra accurate (~5s, 1.5GB) - for important documents

**Choose Your Enhancement Style** (Smart mode for English only):
  - **Standard**: Clean and natural (default)
  - **Professional**: Formal business tone
  - **Casual**: Friendly, conversational
  - **Technical**: Technical writing style

**Other Tips:**
- **📍 Position matters** - click where you want text before recording
- **🌐 Language detection** - Smart mode auto-detects English vs non-English

## 🔒 Your Privacy is Sacred

**Hey Mike! keeps your voice completely private:**

- **🏠 Everything stays local** - your voice never leaves your Mac
- **🚫 Zero data collection** - we don't store, track, or transmit anything  
- **✈️ Works offline** - no internet needed after setup
- **🧠 Memory only** - audio processed and immediately forgotten
- **👁️ Open source** - see exactly what the code does
- **🛡️ No telemetry** - no usage tracking, no analytics, no spying

**Your thoughts, your voice, your business. Period.**

## Architecture

The app is built using:
- **Python + MLX Framework**: Optimized performance on Apple Silicon
- **MLX Whisper**: OpenAI's Whisper models optimized for Apple Silicon  
- **MLX LM**: Local Large Language Models for text enhancement
- **rumps**: Lightweight menu bar interface framework
- **PyAudio**: Professional audio capture and processing
- **pynput**: Global hotkey detection for mode switching
- **Accessibility APIs**: Universal text insertion across macOS
- **Threading**: Async processing for responsive UI

## Project Structure

```
HeyMike/
├── Core/
│   ├── MLXWhisperManager.py      # MLX Whisper model integration
│   ├── MLXLLMManager.py          # MLX LLM for text enhancement
│   ├── TextEnhancer.py           # AI text cleanup and enhancement
│   ├── HotkeyManager.py          # Global hotkey + mode switching
│   ├── TextInsertionManager.py   # Text insertion via Accessibility APIs
│   └── AudioManager.py           # Audio capture and processing
├── UI/
│   └── MenuBarController.py      # rumps-based menu bar interface
├── Models/
│   ├── WhisperModels/           # Downloaded Whisper model files
│   ├── LLMModels/               # Downloaded LLM model files
│   ├── RecognitionResult.py     # Transcription result handling
│   └── AppSettings.py           # User configuration + mode persistence
└── Resources/
    ├── requirements.txt         # Python dependencies
    └── assets/                  # Icons and resources
```

## Development

### Building from Source
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### Key Components
- **MLXWhisperManager**: Handles MLX Whisper model loading and inference  
- **MLXLLMManager**: Manages local LLM for text enhancement
- **TextEnhancer**: AI-powered text cleanup with multiple styles
- **HotkeyManager**: Global keyboard shortcuts + multi-mode switching
- **TextInsertionManager**: Universal text insertion via Accessibility APIs
- **MenuBarController**: Coordinates UI, modes, and user interactions

### Development Dependencies
- `mlx-whisper`: MLX-optimized Whisper models
- `mlx-lm`: MLX-optimized Large Language Models
- `rumps`: Menu bar application framework
- `pyaudio`: Audio input/output
- `pynput`: Global hotkey detection
- `pyobjc`: macOS system integration

## Troubleshooting

### Permissions Issues
If the app isn't working properly, check that you've granted the required permissions:

1. **System Preferences → Security & Privacy → Privacy**
2. **Microphone**: Ensure Terminal/Python is listed and enabled ✓
3. **Accessibility**: Ensure Terminal/Python is listed and enabled ✓
4. **Restart Hey Mike!** after granting permissions

### Model Loading Issues
- **Internet connection**: Required for first-time model download
- **Disk space**: Ensure sufficient space (39MB for tiny, 1.5GB for large)
- **Apple Silicon**: MLX requires M1/M2/M3 chips

### Audio Issues
- **Test microphone**: Verify it works in other applications
- **Check logs**: Look for "PyAudio initialized successfully"
- **PortAudio**: Ensure installed with `brew install portaudio`

### Text Not Appearing
- **Accessibility permissions**: Most common issue - check Terminal is enabled
- **Cursor position**: Click in a text field before recording
- **Try manual paste**: After recording, try Cmd+V manually
- **Check logs**: Look for "Successfully inserted X characters"

### Performance Issues
- **Model selection**: Use `tiny` for speed, `large` for accuracy
- **Memory**: Close other applications if using large models
- **Thermal throttling**: Ensure your Mac isn't overheating

## License

MIT License - Copyright © 2025 [Unseenium Inc.](https://github.com/Unseenium)

See [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/Unseenium/HeyMike/issues)
- 💡 **Have a feature request?** [Start a discussion](https://github.com/Unseenium/HeyMike/discussions)
- 📖 **Need help?** Check the troubleshooting section above
- 🔧 **Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

## Links

- 🏢 **Organization**: [Unseenium](https://github.com/Unseenium)
- 🌐 **Website**: [unseenium.com](https://unseenium.com)
- 📦 **Repository**: [github.com/Unseenium/HeyMike](https://github.com/Unseenium/HeyMike)
