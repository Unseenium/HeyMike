# Hey Mike!

[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)](CHANGELOG.md)
[![macOS](https://img.shields.io/badge/macOS-12.0+-blue.svg)](https://developer.apple.com/macos/)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-M1%2FM2%2FM3-orange.svg)](https://en.wikipedia.org/wiki/Apple_silicon)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered voice dictation for macOS.** Fast, private, and works in 99+ languages.

---

## ✨ Key Features

- **🎨 Visual Overlay** - Animated waveform shows your voice in real-time
- **✨ AI Enhancement** - Auto-adds punctuation, grammar, removes filler words
- **📋 Never Lose Text** - Always copied to clipboard + smart auto-insert
- **🌍 99+ Languages** - Tamil, Japanese, Spanish, English, and more
- **🔒 100% Private** - All processing on-device, nothing sent to cloud
- **⚡ Lightning Fast** - Apple Silicon optimized, near-instant transcription

---

## 🚀 Installation

### Option 1: DMG Installer (Recommended)

1. Download `HeyMike-v1.0.0.dmg` from [Releases](https://github.com/Unseenium/HeyMike/releases)
2. Open DMG and drag "Hey Mike!" to Applications
3. Launch from Spotlight (Cmd+Space → "Hey Mike")
4. Grant Microphone & Accessibility permissions

**That's it!** No Python, no terminal required.

### Option 2: Run from Source

```bash
# Install dependencies
brew install portaudio ffmpeg
pip install -r requirements.txt

# Launch
python main.py
```

**First run:** Downloads AI models (~1.2GB, one-time download)

---

## 🎯 Quick Start

### Basic Usage

1. Look for the microphone icon in your menu bar
2. Press **Cmd+Shift+Space** to start recording
3. Speak naturally
4. Press **Cmd+Shift+Space** to stop
5. Text appears instantly with perfect punctuation!

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Cmd+Shift+Space** | Start/stop recording |
| **Esc** | Cancel recording |

### Menu Features

- **📋 Recent Transcriptions** - Access last 10 recordings
- **⚙️ Settings** - Choose AI models, hotkeys, enhancement style
- **🌍 Language** - Switch between 99+ languages

---

## 💡 How It Works

**Recording:**
- Visual overlay appears with animated waveform
- Speak as long as you want (up to 5 minutes)
- Press Esc anytime to cancel

**Transcription:**
- Whisper AI transcribes your speech on-device
- Auto-detects English and enhances with local LLM
- Other languages paste directly without enhancement

**Insertion:**
- Text auto-inserts at cursor
- Always copied to clipboard as backup
- Access history from menu bar

---

## 🖥️ Requirements

- **macOS 12.0+** with **Apple Silicon** (M1/M2/M3/M4)
- **200MB - 2GB RAM** (depending on model size)
- **Microphone** and **Accessibility** permissions

---

## 📚 Documentation

- **[User Guide](docs/user-guide.md)** - Complete usage guide
- **[API Documentation](docs/api.md)** - For developers
- **[Architecture](docs/architecture.md)** - Technical design
- **[Installation Guide](docs/installation.md)** - Detailed setup
- **[Changelog](CHANGELOG.md)** - Version history

---

## 🛠️ Development

### Build from Source

```bash
# Build .app bundle
pyinstaller heymike.spec --clean

# Create DMG installer
./scripts/create_macos_dmg.sh
```

See [docs/build-process.md](docs/build-process.md) for details.

### Project Structure

```
HeyMike/
├── Core/           # Audio, ML, text processing
├── UI/             # Menu bar, visual overlay
├── Models/         # Settings, history
├── docs/           # Documentation (user + developer)
└── main.py         # Entry point
```

---

## 🐛 Troubleshooting

**Menu bar icon doesn't appear?**  
→ Check Microphone permission in System Settings

**Text doesn't insert?**  
→ Check Accessibility permission  
→ Text is always in clipboard - press Cmd+V

**Models won't download?**  
→ Check internet connection  
→ Requires ~1.2GB free space

**Full troubleshooting:** See [docs/user-guide.md](docs/user-guide.md#troubleshooting)

---

## 🗺️ Roadmap

- **Phase 1 (Q4 2025)**: ✅ Native app with visual overlay
- **Phase 2 (Q1 2026)**: VS Code extension + Action Mode
- **Phase 3 (Q2 2026)**: Code search, explanations, file navigation

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [MLX](https://github.com/ml-explore/mlx) - Apple's ML framework
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Visual overlay
- [rumps](https://github.com/jaredks/rumps) - Menu bar

---

**Made with ❤️ by [Unseenium](https://github.com/Unseenium)**
