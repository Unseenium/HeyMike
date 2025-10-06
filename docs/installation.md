# 🎤 Hey Mike! Installation Guide

## ⚡ Quick Start (5 Minutes)

### Method 1: DMG Installer (Recommended)
1. Download `HeyMike-v1.0.dmg`
2. Open the DMG
3. Double-click **`Install.command`**
4. Follow the on-screen instructions
5. Done! 🚀

### Method 2: Manual Installation
```bash
# Clone or download the repository
git clone https://github.com/Unseenium/HeyMike.git
cd HeyMike

# Run the installer
./scripts/install.sh

# Launch Hey Mike!
heymike
```

---

## 📋 Requirements

- **macOS:** 12.0 (Monterey) or later
- **Python:** 3.11 or later
- **Homebrew:** Recommended (for dependencies)
- **Disk Space:** ~2 GB (for ML models)
- **RAM:** 8 GB minimum, 16 GB recommended

---

## 🔧 What Gets Installed?

The installer will:
1. ✅ Check Python 3.11+ is available
2. ✅ Install PortAudio (for microphone access)
3. ✅ Create isolated virtual environment at `~/.heymike_venv`
4. ✅ Install all Python dependencies (MLX, PyQt6, etc.)
5. ✅ Create launcher script at `~/.local/bin/heymike`
6. ✅ Set up logging directory

**Total installation time:** 5-10 minutes (depending on internet speed)

---

## 🚀 Running Hey Mike!

After installation:

```bash
# Option 1: Use the launcher (if PATH is set)
heymike

# Option 2: Use full path
~/.local/bin/heymike

# Option 3: Run directly from source
cd /path/to/HeyMike
source ~/.heymike_venv/bin/activate
python main.py
```

**First Launch:**
- Grant **Microphone** permission when prompted
- Grant **Accessibility** permission (System Settings → Privacy & Security → Accessibility)
- The app will appear in your menu bar with a microphone icon 🎤

---

## ⌨️ Usage

### Recording:
- **Cmd+Shift+Space** - Start/stop recording
- **Esc** - Cancel recording

### Features:
- 🎤 **Visual overlay** - See waveform while recording
- ✨ **AI enhancement** - Automatic punctuation and formatting
- 📋 **Clipboard fallback** - Text never lost
- 🔄 **Transcription history** - Access last 10 transcriptions
- 🎯 **Menu bar only** - No Dock icon

---

## 🔄 Updating

### Method 1: Re-download and install
1. Download latest DMG
2. Run `Install.command` again
3. Choose to recreate virtual environment

### Method 2: Git update (if cloned)
```bash
cd HeyMike
git pull
source ~/.heymike_venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check logs
tail -f ~/.heymike_venv/logs/heymike.log

# OR (if running from source)
tail -f /path/to/HeyMike/logs/heymike.log
```

### Text doesn't insert
1. Check Accessibility permissions:
   - System Settings → Privacy & Security → Accessibility
   - Ensure Terminal (or your launcher) is checked
2. Try clipboard fallback (press Cmd+V after recording)

### Microphone not working
1. Check permissions:
   - System Settings → Privacy & Security → Microphone
   - Ensure Python/Terminal has permission
2. Check PortAudio is installed:
   ```bash
   brew list portaudio
   ```

### Poor transcription quality
1. Speak clearly and at normal pace
2. Reduce background noise
3. Download larger Whisper model:
   - Open Hey Mike! menu
   - Settings → Model → Select "large"

### "Python not found" error
```bash
# Install Python 3.11+
brew install python@3.11

# Verify installation
python3 --version  # Should show 3.11 or higher
```

### Virtual environment issues
```bash
# Recreate virtual environment
rm -rf ~/.heymike_venv
./scripts/install.sh
```

---

## 🗑️ Uninstalling

To completely remove Hey Mike!:

```bash
# Remove virtual environment
rm -rf ~/.heymike_venv

# Remove launcher
rm ~/.local/bin/heymike

# Remove settings
rm ~/.heymike_settings.json

# Remove application (if installed from DMG)
rm -rf /path/to/HeyMike

# Remove logs
rm -rf ~/Library/Logs/HeyMike  # If logs were moved there
```

---

## 📝 Adding to Login Items (Optional)

To start Hey Mike! automatically on login:

1. Open **System Settings**
2. Go to **General → Login Items**
3. Click the **+** button
4. Add: `/Users/YOUR_USERNAME/.local/bin/heymike`

**OR** create a Launch Agent:

```bash
# Create launch agent directory
mkdir -p ~/Library/LaunchAgents

# Create launch agent plist
cat > ~/Library/LaunchAgents/com.unseenium.heymike.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.unseenium.heymike</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/.local/bin/heymike</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

# Replace YOUR_USERNAME with your actual username
sed -i '' "s/YOUR_USERNAME/$USER/g" ~/Library/LaunchAgents/com.unseenium.heymike.plist

# Load the agent
launchctl load ~/Library/LaunchAgents/com.unseenium.heymike.plist
```

---

## 🆘 Getting Help

- **Documentation:** [README.md](README.md)
- **User Guide:** [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Issues:** [GitHub Issues](https://github.com/Unseenium/HeyMike/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Unseenium/HeyMike/discussions)

---

## 🎉 You're Ready!

Press **Cmd+Shift+Space** and start dictating! 🎤

The visual overlay will appear showing your voice waveform, and your transcribed text will be inserted right where you're typing.

**Enjoy Hey Mike!** ✨
