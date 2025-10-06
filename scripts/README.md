# Build Scripts

Utility scripts for building and running Hey Mike!

---

## 🚀 Development

### `heymike.sh`

Launch Hey Mike! from source for development/testing.

```bash
./scripts/heymike.sh
```

**What it does:**
- Activates Python virtual environment
- Runs `python main.py`

**When to use:** Testing changes before building the .app bundle.

---

## 📦 Building for Distribution

### Step 1: Build the .app Bundle

```bash
pyinstaller heymike.spec --clean
```

**Output:** `dist/Hey Mike!.app` (327 MB)  
**Time:** 2-3 minutes

---

### Step 2: Create the DMG Installer

```bash
./scripts/create_macos_dmg.sh
```

**What it does:**
- Packages `dist/Hey Mike!.app` into a DMG
- Adds Applications folder symlink
- Compresses using UDZO format

**Output:** `HeyMike-v{VERSION}.dmg` (146 MB)  
**Time:** 30 seconds

**Requirements:** Must run Step 1 first.

---

### Step 3: Test the DMG

```bash
open HeyMike-v*.dmg
```

Drag "Hey Mike!" to Applications and launch to verify.

---

## 🎨 Icon Generation

### `create_icon.sh`

Generate `.icns` icon file from a PNG source.

```bash
./scripts/create_icon.sh
```

**What it does:**
- Takes source PNG from `assets/` (1024x1024 recommended)
- Creates iconset with multiple sizes (16px to 512px)
- Converts to `.icns` format

**Output:** `assets/icon.icns`

**When to use:** When updating the app icon.

---

## 📋 Quick Reference

| Script | Purpose |
|--------|---------|
| `heymike.sh` | Run from source |
| `create_macos_dmg.sh` | Package DMG installer |
| `create_icon.sh` | Generate app icon |

**Full documentation:** See `docs/build-process.md`