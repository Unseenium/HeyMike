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

### Standard Workflow
1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** following code standards
3. **Test thoroughly** using the test suite
4. **Update documentation** if needed
5. **Submit pull request** with detailed description

### Testing Changes

#### Option 1: Run from Source (Fastest for iterations)
```bash
source venv/bin/activate  # or your virtualenv
python main.py
```
**Pros:** Instant, no rebuild needed  
**Cons:** Doesn't test bundled app behavior

#### Option 2: Build DMG (Final testing)
```bash
# Build the .app bundle
pyinstaller heymike.spec

# Create DMG installer
./scripts/create_macos_dmg.sh

# Install and test
open HeyMike-v1.0.0.dmg
# Drag to Applications, then launch
```
**Pros:** Tests actual user experience  
**Cons:** Slower, requires permission reset (see below)

---

### ⚠️ **Important: macOS Accessibility Permissions**

**The Issue:**  
Every time you rebuild the `.app` with PyInstaller, macOS generates a new ad-hoc code signature. This causes macOS to treat it as a "different app," requiring you to **reset Accessibility permissions**.

**Why This Happens:**
- Unsigned apps get new signatures on each build
- macOS tracks permissions by: `Bundle ID + Code Signature`
- Changed signature = New app identity = Reset permissions

**Development Workflow:**
1. Install new DMG to `/Applications`
2. Open **System Settings** → **Privacy & Security** → **Accessibility**
3. Remove old "Hey Mike!" entry (if grayed out)
4. Click **"+"** and add the new **Hey Mike!** from Applications
5. Restart the app

**This is NORMAL for development!** End users who install once won't see this.

**Avoiding Resets:**
- For quick iterations, use `python main.py` (no rebuild needed)
- Only build DMG for final testing before commits
- Future: Sign with Apple Developer ID ($99/year) to prevent this

---

### 🏗️ Building for Distribution

#### Prerequisites
```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Verify models are downloaded
# Launch app and download Whisper + LLM models via menu
```

#### Build Steps
```bash
# 1. Clean previous builds
rm -rf build dist

# 2. Build the app bundle
pyinstaller heymike.spec

# 3. Create DMG
./scripts/create_macos_dmg.sh

# 4. Test the DMG
open HeyMike-v1.0.0.dmg
```

#### DMG Contents
- `Hey Mike!.app` - The bundled application (~473MB)
- `Applications` symlink - For drag-and-drop install
- Final DMG size: ~203MB (compressed)

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

## ✅ Pre-Push Checklist

Before pushing to GitHub or creating a release, ensure:

### Code Quality
- [ ] All code follows PEP 8 standards
- [ ] Type hints added for new functions
- [ ] Docstrings updated for changed functions
- [ ] No debug print statements or commented-out code
- [ ] All TODOs resolved or tracked in issues

### Testing
- [ ] App runs from source (`python main.py`)
- [ ] DMG builds successfully (`./scripts/create_macos_dmg.sh`)
- [ ] DMG installs and launches without errors
- [ ] Hotkey works (Cmd+Shift+Space)
- [ ] Text enhancement toggle works (ON/OFF)
- [ ] Audio device selection works
- [ ] Language selection works
- [ ] All menu items functional
- [ ] Accessibility permissions alert shows correctly on first launch

### Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md updated with changes
- [ ] CONTRIBUTING.md reflects current workflow
- [ ] All links in docs are valid (no dead links)
- [ ] Code comments are clear and accurate
- [ ] API.md updated if APIs changed
- [ ] ARCHITECTURE.md updated if structure changed

### Repository Cleanup
- [ ] No sensitive data (API keys, tokens, personal info)
- [ ] No large binary files committed (except assets)
- [ ] `.gitignore` is comprehensive
- [ ] Lock files removed (`/tmp/.heymike.lock`)
- [ ] Build artifacts excluded (`build/`, `dist/`, `*.dmg`)
- [ ] Python cache cleaned (`__pycache__/`, `*.pyc`)
- [ ] Log files excluded (`logs/*.log`)

### Dependencies
- [ ] `requirements.txt` is up to date
- [ ] All dependencies have version pins
- [ ] No unused dependencies listed
- [ ] System dependencies documented in README

### Files to Review
```bash
# Check for untracked files
git status

# Check for large files (> 1MB)
find . -type f -size +1M -not -path "./.git/*" -not -path "./dist/*"

# Check for sensitive patterns
grep -r "API_KEY\|SECRET\|PASSWORD" --exclude-dir=.git --exclude-dir=node_modules

# Verify .gitignore is working
git check-ignore -v <file>
```

### Git Status
- [ ] All intended changes staged
- [ ] No unintended files staged
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main/master
- [ ] No merge conflicts

### Release Specific (for version releases)
- [ ] Version number updated in:
  - [ ] `heymike.spec` (version string)
  - [ ] `scripts/create_macos_dmg.sh` (VERSION variable)
  - [ ] `README.md` (download links, version mentions)
  - [ ] `CHANGELOG.md` (new version header)
- [ ] DMG file named correctly: `HeyMike-vX.Y.Z.dmg`
- [ ] Release notes prepared
- [ ] Git tag created: `git tag -a vX.Y.Z -m "Version X.Y.Z"`

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.
