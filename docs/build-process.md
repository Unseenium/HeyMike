# Build Process - Hey Mike!

**How to build the production-ready .app bundle and DMG installer**

---

## 🛠️ Tools Used

### PyInstaller (NOT py2app)

**Why PyInstaller?**
- ✅ Handles complex ML dependencies (MLX, PyQt6)
- ✅ No recursion errors with deep nesting
- ✅ Built-in hooks for modern frameworks
- ✅ Industry standard (2024)
- ✅ Actively maintained

**Why NOT py2app?**
- ❌ RecursionError with MLX/PyQt6
- ❌ Poor support for modern ML frameworks
- ❌ Module scanner gets stuck on deep dependencies
- ❌ Less actively maintained

See: `PYINSTALLER_SUCCESS.md` for the full story.

---

## 📦 Build Steps

### 1. Install Dependencies

```bash
cd /Users/arraman/Projects/Unseenium/HeyMike
source ~/.virtualenvs/MagikMike/bin/activate
pip install pyinstaller
```

### 2. Build .app Bundle

```bash
pyinstaller heymike.spec --clean
```

**Output:** `dist/Hey Mike!.app` (327 MB)

**What it includes:**
- Python 3.11 runtime
- MLX + mlx_whisper + mlx_lm
- PyQt6 framework
- Flask + SocketIO
- rumps, pynput, PyAudio
- All Core/, UI/, Models/ modules
- Assets (icon.icns, menubar icon)

**Build time:** 2-3 minutes

### 3. Create DMG Installer

```bash
./scripts/create_macos_dmg.sh
```

**Output:** `HeyMike-v1.0.0.dmg` (146 MB compressed)

**What it contains:**
```
/Volumes/Install Hey Mike! v1.0.0/
├── Hey Mike!.app (the standalone bundle)
└── Applications (symlink to /Applications)
```

**DMG type:** Traditional drag-and-drop (like Slack, Dropbox, VS Code)

---

## 📋 Configuration Files

### `heymike.spec`

**PyInstaller spec file** - Defines:
- Entry point: `main.py`
- Hidden imports (all Core/UI/Models modules)
- Data files (icons, VERSION)
- Exclusions (torch, tensorflow, matplotlib)
- Bundle metadata (`Info.plist` settings)
- Icon (`assets/icon.icns`)

**Key settings:**
```python
exe = EXE(
    console=False,  # No terminal window
    icon='assets/icon.icns',
)

app = BUNDLE(
    name='Hey Mike!.app',
    bundle_identifier='com.unseenium.heymike',
    info_plist={
        'LSUIElement': True,  # Menu bar only
        'NSMicrophoneUsageDescription': '...',
        'NSAppleEventsUsageDescription': '...',
    },
)
```

### `scripts/create_macos_dmg.sh`

**DMG creation script** - Uses `hdiutil`:
1. Creates temp directory
2. Copies `Hey Mike!.app`
3. Creates Applications symlink
4. Packages into compressed DMG
5. Cleans up temp files

---

## 🧪 Testing the Build

### Verify .app Structure

```bash
ls -lh "dist/Hey Mike!.app"
file "dist/Hey Mike!.app/Contents/MacOS/Hey Mike!"
codesign -dv "dist/Hey Mike!.app"  # Check signing status
```

### Test .app Locally

```bash
open "dist/Hey Mike!.app"
```

**Check:**
- [ ] Appears in menu bar (no Dock icon)
- [ ] Microphone permission prompt
- [ ] Accessibility permission prompt
- [ ] Cmd+Shift+Space starts recording
- [ ] Visual overlay appears
- [ ] Text inserts correctly

### Verify DMG

```bash
hdiutil attach HeyMike-v1.0.0.dmg -readonly
ls -la "/Volumes/Install Hey Mike! v1.0.0/"
hdiutil detach "/Volumes/Install Hey Mike! v1.0.0/"
```

**Check:**
- [ ] DMG mounts without errors
- [ ] Contains `Hey Mike!.app`
- [ ] Contains Applications symlink
- [ ] Drag-and-drop works

### Test on Clean System

**Ideal test:**
1. Copy DMG to another Mac (without Python/dev environment)
2. Open DMG
3. Drag to Applications
4. Launch and verify all features work

---

## 🚨 Common Issues

### Issue 1: "Hey Mike! is damaged"
**Cause:** macOS quarantine flag on downloaded apps  
**Fix:** Right-click → Open (first launch)  
**Proper Fix:** Code signing + notarization (Phase 2)

### Issue 2: Missing dependencies
**Cause:** PyInstaller didn't include a module  
**Fix:** Add to `hiddenimports` in `heymike.spec`

### Issue 3: Crash on launch
**Cause:** Missing data files (icons, configs)  
**Fix:** Add to `datas` in `heymike.spec`

### Issue 4: Qt errors
**Cause:** Qt plugins not bundled  
**Fix:** PyInstaller usually handles this, check logs

---

## 📊 Build Artifacts

| File | Size | Purpose |
|------|------|---------|
| `dist/Hey Mike!.app` | 327 MB | Standalone app bundle |
| `dist/Hey Mike!/` | - | PyInstaller temp files |
| `build/heymike/` | - | Build cache |
| `HeyMike-v1.0.0.dmg` | 146 MB | Compressed DMG installer |
| `pyinstaller_build.log` | - | Build log |

**For distribution:** Only upload `HeyMike-v1.0.0.dmg` (146 MB)

---

## 🔐 Code Signing (Phase 2)

**Not yet implemented, but planned:**

### Requirements:
- Apple Developer ID ($99/year)
- Developer ID Application certificate

### Commands:
```bash
# Sign the .app
codesign --deep --force --verify --verbose \
         --sign "Developer ID Application: Your Name (TeamID)" \
         "dist/Hey Mike!.app"

# Verify signature
codesign -dv "dist/Hey Mike!.app"
spctl -a -v "dist/Hey Mike!.app"

# Notarize with Apple
xcrun notarytool submit HeyMike-v1.0.0.dmg \
                        --apple-id "your@email.com" \
                        --password "app-specific-password" \
                        --team-id "TEAMID" \
                        --wait

# Staple notarization ticket
xcrun stapler staple "dist/Hey Mike!.app"
xcrun stapler staple HeyMike-v1.0.0.dmg
```

**Benefit:** No "unverified developer" warnings

---

## 🎯 Complete Build Script

```bash
#!/bin/bash
# Complete build process

set -e

echo "🎤 Building Hey Mike! v1.0.0"
echo ""

# 1. Activate venv
source ~/.virtualenvs/MagikMike/bin/activate

# 2. Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf build dist *.dmg

# 3. Build .app with PyInstaller
echo "📦 Building .app bundle..."
pyinstaller heymike.spec --clean

# 4. Create DMG
echo "💿 Creating DMG..."
./scripts/create_macos_dmg.sh

# 5. Done
echo ""
echo "✅ Build complete!"
echo "📍 DMG: HeyMike-v1.0.0.dmg (146 MB)"
echo ""
echo "🧪 Test: open HeyMike-v1.0.0.dmg"
```

---

## 📝 Build Checklist

Before each release:

- [ ] Update `VERSION` file
- [ ] Update `CHANGELOG.md`
- [ ] Clean old builds: `rm -rf build dist *.dmg`
- [ ] Run: `pyinstaller heymike.spec --clean`
- [ ] Test .app: `open "dist/Hey Mike!.app"`
- [ ] Create DMG: `./scripts/create_macos_dmg.sh`
- [ ] Test DMG on clean system
- [ ] Upload to GitHub Releases
- [ ] Update README with download link

---

## 🎊 Success Metrics

**Build is ready when:**
- ✅ .app launches without terminal
- ✅ No Dock icon (menu bar only)
- ✅ All permissions prompt correctly
- ✅ Recording works (Cmd+Shift+Space)
- ✅ Visual overlay appears
- ✅ Text insertion works
- ✅ Works on Mac WITHOUT dev environment
- ✅ DMG < 200 MB
- ✅ Install time < 30 seconds

**Current stats:**
- Build time: ~3 minutes
- .app size: 327 MB (reasonable for bundled Python + ML)
- DMG size: 146 MB (good compression)
- Install time: ~10 seconds (drag and drop)

---

## 📚 References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller macOS Guide](https://pyinstaller.org/en/stable/usage.html#macos-specific-options)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [hdiutil man page](https://ss64.com/osx/hdiutil.html)

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Status:** ✅ Production-ready
