# Contributing to Hey Mike!

Thank you for your interest in contributing to Hey Mike! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/yourusername/HeyMike.git`
3. **Add upstream remote**: `git remote add upstream https://github.com/Unseenium/HeyMike.git`
4. **Set up development environment**: 
   ```bash
   cd HeyMike
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Install system dependencies**:
   ```bash
   brew install portaudio ffmpeg
   ```

## 🏗️ Development Setup

### Prerequisites
- macOS 12.0+ with Apple Silicon (M1/M2/M3)
- Python 3.8+
- Homebrew
- Xcode Command Line Tools

### Running Tests
```bash
# Run comprehensive test suite
python test_magikmike_complete.py

# Manual testing checklist provided in output
```

## 📋 Code Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Include error handling for all external calls

### Logging
- Use structured logging with appropriate levels
- Include context in error messages
- Log user actions for debugging

### Error Handling
- Graceful degradation for missing permissions
- User-friendly error messages
- Recovery mechanisms where possible

## 🧪 Testing Guidelines

### Manual Testing Required
- All menu bar functionality
- Recording and transcription accuracy
- Settings persistence
- Permission handling
- Error scenarios

### Test Categories
1. **Model Switching** - All 5 models work correctly
2. **Recording** - Audio capture and transcription
3. **Settings** - All dialogs and persistence
4. **Help/Utilities** - All support functions
5. **Error Handling** - Edge cases and failures
6. **Performance** - Speed and responsiveness

## 🔄 Development Workflow

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** following code standards
3. **Test thoroughly** using the test suite
4. **Update documentation** if needed
5. **Submit pull request** with detailed description

## 📝 Commit Messages

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements

## 🐛 Bug Reports

Include:
- macOS version and hardware
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Log output if relevant

## 💡 Feature Requests

Consider:
- User benefit and use cases
- Implementation complexity
- Compatibility with existing features
- Performance impact

## 🚀 Future Roadmap

### Phase 1: Swift Migration
- Native Swift menu bar app
- Python backend communication
- Modern SwiftUI interfaces

### Phase 2: Enhanced Features
- Custom model training
- Advanced language detection
- Voice activity detection
- Cloud sync (optional)

### Phase 3: Distribution
- App Store preparation
- Code signing and notarization
- Installer creation
- Auto-update system

## 📞 Contact

- Create issues for bugs and features
- Discussions for questions and ideas
- Email for security issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.
