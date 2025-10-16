# Hey Mike! User Guide

> **Version**: 1.0 | **Phase**: Production  
> **Last Updated**: October 2025

Welcome to Hey Mike! - an AI-powered voice dictation tool for macOS. This guide will help you get started and make the most of your voice dictation experience.

---

## 🚀 Quick Start

### 1. Installation

1. Download `Hey Mike!.dmg` from [GitHub Releases](https://github.com/Unseenium/HeyMike/releases)
2. Open the DMG and drag **Hey Mike!** to your Applications folder
3. Launch **Hey Mike!** from Applications or Spotlight

### 2. Grant Permissions

On first launch, you'll need to grant two permissions:

#### Microphone Access
- **When**: First recording attempt
- **Why**: To capture your voice
- **Where**: System Preferences → Privacy & Security → Microphone
- Enable checkbox next to "Hey Mike!"

#### Accessibility Access
- **When**: First hotkey press or text insertion
- **Why**: For global hotkeys and typing text
- **Where**: System Preferences → Privacy & Security → Accessibility
- Enable checkbox next to "Hey Mike!"

### 3. First Recording

1. Click anywhere in a text field (Notes, TextEdit, Chrome, etc.)
2. Press **Cmd+Shift+Space** to start recording
3. Speak naturally
4. Press **Cmd+Shift+Space** again to stop
5. Your text appears automatically! ✨

---

## 🎤 Using Hey Mike!

### Recording Voice

#### Push-to-Talk

Hey Mike! uses a **push-to-talk** model:

1. **Press hotkey** → Recording starts (overlay appears)
2. **Speak** → Waveform shows your voice
3. **Press hotkey again** → Recording stops, processing begins
4. **Text inserted** → Overlay fades out

#### What You'll See

**Recording**:
- 🔴 Pulsing dot in overlay
- Animated waveform (cyan → purple)
- Menu bar icon: 🔴

**Processing**:
- Spinning arc animation
- Menu bar icon: ⏳

**Complete**:
- Green checkmark (500ms)
- Text appears at cursor (if focused)
- Menu bar icon: ✅ (brief)
- 📋 **Always in clipboard** (can paste anytime!)

**Clipboard Only** (no text field focused):
- 📋 "Copied to Clipboard" notification
- Press Cmd+V to paste manually
- Text never lost!

**Cancelled**:
- Red X icon (500ms)
- No text inserted
- Returns to idle state

#### Canceling a Recording

If you accidentally start recording or change your mind:

1. **Press Esc** at any time
2. **Works during**:
   - ✅ Recording (while speaking)
   - ✅ Processing (during transcription)
   - ✅ Enhancement (during AI cleanup)
3. **Result**:
   - ❌ Red X appears in overlay (500ms)
   - 🚫 No text will be inserted
   - 🎤 Returns to idle immediately
   - 🗑️ Audio discarded

**Use cases:**
- Accidentally triggered hotkey
- Background noise captured
- Changed your mind mid-sentence
- Want to rephrase before recording

### 📋 Clipboard & History (Never Lose Text!)

Hey Mike! uses a **hybrid approach** to ensure you never lose transcribed text:

#### Always in Clipboard
- **Every transcription** is automatically copied to clipboard
- ✅ **Text field focused?** → Auto-inserts AND in clipboard
- ❌ **No text field?** → Notification: "Press Cmd+V to paste"
- 🎯 **Wrong place?** → Undo (Cmd+Z), click correct spot, paste (Cmd+V)

#### Recent Transcriptions
Access your last 10 transcriptions:
1. Click **🎤** menu bar icon
2. Select **📋 Recent Transcriptions**
3. Click any item to copy & paste it again
4. Items show:
   - ✨ indicator for AI-enhanced text
   - Timestamp (HH:MM)
   - First 60 characters

**Features:**
- 📝 **Last 10 items** stored
- ⏰ **Timestamps** for context
- ✨ **Enhancement indicator** shows AI-cleaned text
- 🗑️ **Clear History** option
- 🔄 **Reuse** old transcriptions anytime

**Example workflow:**
```
1. Record: "Send the report today"
2. No text field focused → "📋 Copied to Clipboard"
3. Click in email → Cmd+V → Text pasted!

OR

1. Record: "Important meeting notes..."
2. Text auto-inserted ✅ (also in clipboard)
3. Later: Menu → Recent → Click item → Reuse it!
```

---

## ⚙️ Settings

Click the **🎤** icon in menu bar to access settings:

### Speech Recognition

#### Whisper Model
Choose your transcription model:

- **Tiny** (39MB) - Fastest, basic accuracy
- **Base** (74MB) - ⭐ Recommended for most users
- **Small** (244MB) - Better accuracy, slower
- **Medium** (769MB) - Very good, requires more RAM
- **Large** (1.5GB) - Best accuracy, slowest

💡 **Tip**: Start with Base. Upgrade to Small/Medium if accuracy is critical.

#### Language
- **Auto-detect** (default) - Works for most languages
- **Specific language** - Select if auto-detect fails

### AI Enhancement

#### Enable Text Enhancement
When enabled, Hey Mike! uses AI to:
- ✅ Add punctuation
- ✅ Fix grammar
- ✅ Remove filler words ("um", "uh")
- ✅ Improve flow

#### Enhancement Style

- **Standard** ⭐ - Natural, clean text
- **Professional** - Formal business tone
- **Casual** - Friendly, conversational
- **Technical** - For technical writing

**Example:**
```
Raw:        "um so yeah i think we should uh fix the bug"
Standard:   "I think we should fix the bug."
Professional: "I believe we should address the bug."
Casual:     "Yeah, we should probably fix that bug."
Technical:  "The bug requires remediation."
```

💡 **Tip**: Standard works for 90% of use cases.

#### LLM Model

Choose your enhancement model:
- **Llama 3.2 1B** ⭐ - Fast, good quality
- **Llama 3.2 3B** - Better quality, slower
- **Qwen 2.5 0.5B** - Fastest, basic quality

### Hotkeys

#### Recording Hotkey
- **Default**: Cmd+Shift+Space
- **Custom**: Click to set your own

💡 **Tip**: Avoid hotkeys used by other apps (e.g., Spotlight, Alfred).

### Text Insertion

#### Method
- **Auto** ⭐ - Tries paste, falls back to typing
- **Paste** - Fast, uses clipboard (overwrites it temporarily)
- **Type** - Character-by-character (slower, more universal)

#### Options
- **Add space after text**: Useful for continuous dictation
- **Add space before text**: For mid-sentence insertion

### Visual Overlay

#### Enable Overlay
- ✅ Show animated waveform during recording (recommended)
- ❌ Disable for distraction-free mode

#### Overlay Position
- Bottom-center of screen (60px from bottom)
- Follows your active display

---

## 💡 Tips & Best Practices

### For Best Accuracy

1. **Speak naturally** - Don't slow down or over-enunciate
2. **Use a quiet environment** - Background noise affects quality
3. **Get close to mic** - 6-12 inches from built-in mic
4. **Use external mic** - USB or AirPods for better quality
5. **Pause between thoughts** - Helps AI understand context

### What to Say

**Good**:
- "Let's schedule a meeting for tomorrow at 3 PM"
- "The quick brown fox jumps over the lazy dog"
- "I need to buy milk, eggs, and bread"

**Avoid**:
- Speaking too fast without pauses
- Mumbling or trailing off
- Eating/drinking while speaking
- Saying "period", "comma" (AI adds these automatically)

### Common Scenarios

#### Writing Emails
1. Enable **Professional** style
2. Record your message naturally
3. AI will format it professionally

#### Taking Notes
1. Use **Standard** style
2. Record in chunks (one thought at a time)
3. Press hotkey between thoughts for better accuracy

#### Code Comments
1. Use **Technical** style
2. Speak technical terms clearly
3. AI will maintain technical vocabulary

#### Chat Messages
1. Use **Casual** style
2. Speak naturally like you're talking to a friend
3. AI keeps it conversational

---

## 🎯 Supported Applications

Hey Mike! works with **any text field** on macOS:

### Productivity
- ✅ Notes
- ✅ TextEdit
- ✅ Microsoft Word
- ✅ Pages
- ✅ Notion
- ✅ Obsidian
- ✅ Bear
- ✅ Evernote

### Communication
- ✅ Slack
- ✅ Discord
- ✅ WhatsApp
- ✅ Telegram
- ✅ iMessage
- ✅ Mail

### Browsers
- ✅ Safari
- ✅ Chrome
- ✅ Firefox
- ✅ Edge
- ✅ Arc

### Code Editors
- ✅ VS Code
- ✅ Xcode
- ✅ Sublime Text
- ✅ Atom
- ✅ IntelliJ IDEA

### Forms & Fields
- ✅ Google Docs
- ✅ Web forms
- ✅ Search bars
- ✅ Terminal (with caution!)

💡 **Tip**: If text doesn't insert, check Accessibility permissions.

---

## 🔧 Troubleshooting

### Audio Issues

#### "No audio recorded"
- Check Microphone permission (Privacy & Security)
- Test mic in System Preferences → Sound → Input
- Try different audio device in Hey Mike! settings

#### "Audio quality is poor"
- Use external microphone or AirPods
- Move to quieter environment
- Speak closer to mic (6-12 inches)

#### "Overlay doesn't show waveform"
- Enable "Visual Overlay" in settings
- Restart Hey Mike!
- Check Console.app for PyQt6 errors

### Transcription Issues

#### "Transcription is blank"
- Speak louder or closer to mic
- Check if mic is muted (hardware mute switch)
- Try a larger model (Small or Medium)

#### "Wrong words transcribed"
- Switch to larger model (Small → Medium → Large)
- Speak more clearly
- Enable language-specific mode (disable auto-detect)
- Use external microphone

#### "Processing takes too long"
- Switch to smaller model (Medium → Base → Tiny)
- Close other apps to free up RAM
- Wait for model to fully load (first use)

### Text Insertion Issues

#### "Text doesn't insert"
- **New in v1.0**: Text is always in clipboard! Press Cmd+V to paste
- Check notification: "📋 Copied to Clipboard"
- Click in text field, then press Cmd+V
- Check Accessibility permission if Cmd+V doesn't work
- Try changing insertion method in Settings (Paste → Type)
- Access from **Recent Transcriptions** menu

#### "Cursor moves away"
- This is a known macOS behavior with some apps
- Try **Type** method instead of Paste
- Click back to original position

#### "Text is duplicated"
- Don't paste manually after recording (it's automatic)
- Check if "Add space after" is enabled unnecessarily

### Hotkey Issues

#### "Hotkey doesn't work"
- Check Accessibility permission
- Hotkey might conflict with another app
- Try different hotkey combination
- Restart Hey Mike!

#### "Hotkey triggers other app"
- Change hotkey in settings
- Close conflicting app (Alfred, Spotlight shortcuts)

### Performance Issues

#### "App is slow"
- Close unused apps to free RAM
- Use smaller models (Tiny/Base)
- Disable AI enhancement temporarily
- Restart Mac (free up memory)

#### "High memory usage"
- Normal: 1.5-2GB with models loaded
- Try smaller LLM (Qwen 0.5B instead of Llama 3B)
- Restart Hey Mike! to clear memory

### Other Issues

#### "App crashes on launch"
- Check Console.app for error logs
- Delete settings: `~/.heymike_settings.json`
- Reinstall Hey Mike!
- Report bug on GitHub

#### "Models won't download"
- Check internet connection
- Check disk space (need ~3GB free)
- Try again (downloads resume automatically)
- Check firewall settings

---

## 🎨 Customization

### Audio Device

**Change microphone:**
1. Click 🎤 → Settings → Audio
2. Select device from dropdown
3. Test with recording

**Recommended devices:**
- Built-in Microphone (good)
- AirPods Pro (better)
- USB microphone (best)

### Recording Duration

**Max recording time:**
- Default: 300 seconds (5 minutes)
- Adjust in Settings → Advanced
- Longer = more memory usage

💡 **Tip**: Record in shorter chunks for better accuracy.

### Enhancement Customization

**Per-app styles** (coming soon):
- Email app → Professional
- Slack → Casual
- VS Code → Technical

---

## 🔒 Privacy & Security

### Your Data

- ✅ **100% on-device** - No cloud processing
- ✅ **No audio saved** - Audio buffers are memory-only
- ✅ **No telemetry** - We don't track usage
- ✅ **No internet required** - Works offline (after model download)
- ✅ **Open source** - Audit the code yourself

### What Gets Stored

- **Settings**: `~/.heymike_settings.json` (preferences only)
- **Models**: `~/Library/Application Support/HeyMike/Models/` (cached AI models)
- **Logs**: `~/Library/Logs/HeyMike/` (debug info, no audio)

### Permissions Explained

#### Microphone
- **What**: Access to your microphone
- **Why**: To record your voice
- **When**: Only when hotkey pressed
- **Data**: Never saved to disk

#### Accessibility
- **What**: Control keyboard and insert text
- **Why**: For global hotkeys and typing text
- **When**: Only when you use hotkeys
- **Data**: No keystroke logging

---

## 🆘 Getting Help

### Resources

- **User Guide**: You're reading it! 📖
- **API Docs**: [api.md](./api.md)
- **Architecture**: [architecture.md](./architecture.md)
- **GitHub**: [github.com/Unseenium/HeyMike](https://github.com/Unseenium/HeyMike)

### Report Issues

Found a bug? Have a feature request?

1. Check [existing issues](https://github.com/Unseenium/HeyMike/issues)
2. Create new issue with:
   - macOS version
   - Hey Mike! version
   - Steps to reproduce
   - Expected vs actual behavior
   - Console logs (if crash)

### Community

- **Discussions**: [GitHub Discussions](https://github.com/Unseenium/HeyMike/discussions)
- **Feature Requests**: [GitHub Issues](https://github.com/Unseenium/HeyMike/issues)

---

## 🗺️ Roadmap

### Phase 1 (Current - v1.0)
- ✅ AI-enhanced transcription
- ✅ Visual Overlay (waveform animation)
- ✅ Menu bar app
- ✅ Multi-model support
- ✅ Grammar, punctuation, filler word removal

### Phase 2 (Q1 2026)
- 🔜 VS Code extension
- 🔜 Voice notes with context
- 🔜 Live status in IDE

### Phase 3 (Q2 2026)
- 🔜 Code explanations
- 🔜 Semantic search
- 🔜 File navigation by voice

---

## 📋 Keyboard Shortcuts

| Hotkey | Action |
|--------|--------|
| **Cmd+Shift+Space** | Start/stop recording |
| **Esc** | Cancel recording/processing |

**Note**: Esc works during recording, transcription, and AI enhancement.

---

## ❓ FAQ

### General

**Q: Does Hey Mike! work offline?**  
A: Yes! After models are downloaded, it works 100% offline.

**Q: What macOS version do I need?**  
A: macOS 12.0+ (Monterey or later)

**Q: Does it work on Intel Macs?**  
A: No, it requires Apple Silicon (M1, M2, M3, M4) for MLX framework.

**Q: How much disk space do I need?**  
A: ~3GB for all models (minimal: ~500MB for tiny model + 1B LLM)

**Q: Can I use it in multiple languages?**  
A: Yes! Whisper supports 99 languages. Set language in Settings or use auto-detect.

### Features

**Q: Can I use it for dictating punctuation?**  
A: No need! AI adds punctuation automatically. Just speak naturally.

**Q: Does it support continuous dictation?**  
A: Currently push-to-talk only. Voice-activated mode coming in future update.

**Q: Can I train it on my voice?**  
A: Not yet. Custom voice training planned for Phase 3.

**Q: Can I add custom vocabulary?**  
A: Not yet. Custom vocabulary planned for future update.

### Privacy

**Q: Is my audio sent to the cloud?**  
A: Never. 100% on-device processing.

**Q: Can you hear my recordings?**  
A: No. Audio is never saved or transmitted anywhere.

**Q: What do you collect?**  
A: Nothing. No analytics, no telemetry, no tracking.

### Technical

**Q: Why does it use 2GB RAM?**  
A: AI models are loaded into memory for fast inference. This is normal.

**Q: Can I use it with VPN?**  
A: Yes, but VPN not needed (no internet required after model download).

**Q: Does it work with multiple displays?**  
A: Yes, overlay appears on display with active cursor.

---

## 📝 Changelog

See [CHANGELOG.md](../CHANGELOG.md) for version history.

---

## 🙏 Credits

- **MLX Framework**: Apple's ML framework for Apple Silicon
- **Whisper**: OpenAI's speech recognition model
- **Llama**: Meta's large language model
- **PyQt6**: Cross-platform GUI framework
- **rumps**: Ridiculously Uncomplicated macOS Python Statusbar apps

---

**Version**: 1.0 | **Phase**: Production  
**Last Updated**: October 2025  
Made with ❤️ for macOS
