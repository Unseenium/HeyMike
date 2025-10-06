# Documentation

Complete documentation for Hey Mike! - for users, developers, and contributors.

---

## 👥 For Users

### [user-guide.md](user-guide.md)
Complete guide to using Hey Mike!:
- Installation and setup
- Basic usage and keyboard shortcuts
- Settings and customization
- Troubleshooting
- Tips and tricks

### [installation.md](installation.md)
Detailed installation instructions:
- DMG installer (recommended)
- Building from source
- System requirements
- Permissions setup

---

## 🔧 For Developers

### [api.md](api.md)
API reference for developers:
- Core modules (AudioManager, MLXWhisperManager, etc.)
- UI components (MenuBarController, OverlayWindow)
- Models and data structures
- Event system
- Configuration

### [architecture.md](architecture.md)
Technical design and architecture:
- System overview
- Component interaction
- Thread-safe UI with PyQt6 + rumps
- MLX integration
- Performance considerations

### [build-process.md](build-process.md)
Building Hey Mike! from source:
- Build .app bundle with PyInstaller
- Create DMG installer
- Development workflow
- Troubleshooting builds

---

## 🤝 Contributing

Want to contribute? Here's how:

1. **Fork and clone the repository**
2. **Set up development environment:**
   ```bash
   brew install portaudio ffmpeg
   pip install -r requirements.txt
   python main.py
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## 📁 Project Structure

```
HeyMike/
├── Core/           # Audio, ML, text processing
│   ├── AudioManager.py
│   ├── MLXWhisperManager.py
│   ├── MLXLLMManager.py
│   ├── TextEnhancer.py
│   └── ...
├── UI/             # Menu bar, visual overlay
│   ├── MenuBarController.py
│   ├── OverlayWindow.py
│   ├── OverlayManager.py
│   └── WaveformRenderer.py
├── Models/         # Settings, history
│   ├── AppSettings.py
│   └── TranscriptionHistory.py
├── docs/           # Documentation (you are here)
└── main.py         # Entry point
```

---

## 🐛 Debugging

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Common Issues

**PyQt6 not found:**
```bash
pip install PyQt6>=6.5.0
```

**MLX models not downloading:**
- Check internet connection
- Requires ~1.2GB free space
- Models cache to `~/.cache/huggingface/`

**Build issues:**
See [build-process.md](build-process.md#troubleshooting)

---

## 📚 Additional Resources

- [GitHub Repository](https://github.com/Unseenium/HeyMike)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)

---

## 📧 Need Help?

- 📖 Check the [User Guide](user-guide.md)
- 🐛 [Report a bug](https://github.com/Unseenium/HeyMike/issues)
- 💡 [Request a feature](https://github.com/Unseenium/HeyMike/issues)
- 💬 [Ask a question](https://github.com/Unseenium/HeyMike/discussions)