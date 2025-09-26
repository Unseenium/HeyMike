# Hey Mike!

[![GitHub](https://img.shields.io/badge/GitHub-Unseenium%2FHeyMike-blue.svg)](https://github.com/Unseenium/HeyMike)
[![macOS](https://img.shields.io/badge/macOS-12.0+-blue.svg)](https://developer.apple.com/macos/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-M1%2FM2%2FM3-orange.svg)](https://en.wikipedia.org/wiki/Apple_silicon)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://openai.com/research/whisper)
[![Unseenium](https://img.shields.io/badge/Made%20by-Unseenium-red.svg)](https://github.com/Unseenium)

🎤 **Like Hey Siri, but actually useful for your Mac.** The voice assistant that gets things done. Completely private, lightning fast, works in 99+ languages.

## ✨ What Makes Hey Mike! Amazing

- **🎯 Just Works**: Press a hotkey, speak, and watch text appear exactly where you need it
- **🌍 Speaks Your Language**: Supports 99+ languages with automatic detection  
- **🔒 Completely Private**: Your voice never leaves your Mac - 100% offline processing
- **⚡ Lightning Fast**: Optimized for Apple Silicon with near-instant transcription
- **🎨 Beautiful Interface**: Clean menu bar app that stays out of your way
- **🧠 Smart Models**: Choose from 5 AI models - from ultra-fast to ultra-accurate
- **⌨️ Your Hotkey**: Customize keyboard shortcuts to fit your workflow (default: ⌘⇧Space)
- **📱 Native macOS**: Works with any app - TextEdit, Slack, Email, you name it
- **🎵 Audio Feedback**: Optional sound cues so you know when it's listening
- **🎯 Precision**: >98% accuracy that gets better the more you use it
- **🗣️ Voice Commands**: "Hey Mike, open Chrome and search for Python tutorials" - it just works!

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

# Auto-setup (handles Python environment and dependencies)
./scripts/setup.sh
```

**3. Grant Permissions**
- Open **System Preferences → Security & Privacy → Privacy**
- Add **Terminal** to both **Microphone** and **Accessibility**

**4. Launch Hey Mike!**
```bash
source venv/bin/activate
python main.py
```

**That's it!** 🎉 Look for the 🎤 icon in your menu bar.

## 🎯 How to Use Hey Mike!

**It's incredibly simple:**

1. **Position your cursor** anywhere you want text (TextEdit, Slack, Email, etc.)
2. **Press ⌘⇧Space** (or your custom hotkey)
3. **Speak naturally** - the 🎤 icon turns 🔴 while listening
4. **Press ⌘⇧Space again** to stop
5. **Watch the magic** - your words appear as text instantly!

### First Time Setup
- Hey Mike! downloads its AI brain on first launch (~39MB)
- Try saying "Hello, this is a test" to see it work
- Or try "Hey Mike, open Calculator" to test voice commands
- The menu bar shows ✅ when ready

## ⚙️ Customize Hey Mike!

### Menu Bar Controls
Click the 🎤 icon to access:
- **🧠 Models**: Choose your AI brain (5 options from lightning-fast to ultra-accurate)
- **⌨️ Hotkey**: Change your recording shortcut  
- **🎙️ Audio**: Select your microphone
- **🌍 Language**: Set your preferred language (or leave on auto-detect)

### Pro Tips for Perfect Results
- **🎯 Speak naturally** - no need to slow down or over-enunciate
- **🤫 Quiet environment** helps, but Hey Mike! handles background noise well
- **🧠 Choose your model**:
  - **Tiny**: Lightning fast (~1s, 39MB) - great for quick notes
  - **Base**: Balanced (~2s, 74MB) - perfect for most use
  - **Large**: Ultra accurate (~5s, 1.5GB) - for important documents
- **📍 Position matters** - click where you want text before recording
- **🌍 Multilingual magic** - just speak, Hey Mike! detects your language

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
- **rumps**: Lightweight menu bar interface framework
- **PyAudio**: Professional audio capture and processing
- **Accessibility APIs**: Universal text insertion across macOS
- **Threading**: Async processing for responsive UI

## Project Structure

```
HeyMike/
├── Core/
│   ├── MLXWhisperManager.py      # MLX Whisper model integration
│   ├── HotkeyManager.py          # Global hotkey handling
│   ├── TextInsertionManager.py   # Text insertion via Accessibility APIs
│   └── AudioManager.py           # Audio capture and processing
├── UI/
│   ├── MenuBarController.py      # rumps-based menu bar interface
│   ├── SettingsView.py          # Configuration interface
│   └── StatusIndicator.py        # Visual feedback system
├── Models/
│   ├── WhisperModels/           # Downloaded Whisper model files
│   ├── RecognitionResult.py     # Transcription result handling
│   └── AppSettings.py           # User configuration management
└── Resources/
    ├── requirements.txt         # Python dependencies
    └── Assets/                  # Icons and resources
```

## Development

### Building from Source
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### Key Components
- **MLXWhisperManager**: Handles MLX Whisper model loading and inference
- **HotkeyManager**: Manages global keyboard shortcuts using Python libraries
- **TextInsertionManager**: Inserts text using Accessibility APIs and system events
- **MenuBarController**: Coordinates the rumps-based menu bar interface and user interactions

### Development Dependencies
- `mlx-whisper`: MLX-optimized Whisper models
- `rumps`: Menu bar application framework
- `pyaudio`: Audio input/output
- `pynput`: Global hotkey detection
- `pyobjc`: macOS system integration

## Troubleshooting

### Permissions Issues
If the app isn't working properly, check that you've granted the required permissions:

1. **Microphone**: System Preferences → Security & Privacy → Privacy → Microphone
2. **Accessibility**: System Preferences → Security & Privacy → Privacy → Accessibility

### Permission Issues
If Hey Mike! isn't working:
1. **Check System Preferences → Security & Privacy → Privacy**
2. **Microphone**: Ensure Terminal is listed and enabled ✓
3. **Accessibility**: Ensure Terminal is listed and enabled ✓
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
