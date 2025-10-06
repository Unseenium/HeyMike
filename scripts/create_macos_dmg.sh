#!/bin/bash
# Create traditional drag-and-drop DMG for Hey Mike!
# This creates a DMG with the .app and Applications folder shortcut

set -e

VERSION=$(cat VERSION)
APP_NAME="Hey Mike!"
DMG_NAME="HeyMike-v${VERSION}.dmg"
VOLUME_NAME="Install Hey Mike! v${VERSION}"
SOURCE_APP="dist/${APP_NAME}.app"

echo "🎤 Creating traditional macOS DMG installer..."
echo "   Version: ${VERSION}"
echo ""

# Check if .app exists
if [ ! -d "$SOURCE_APP" ]; then
    echo "❌ Error: ${SOURCE_APP} not found"
    echo "   Run: pyinstaller heymike.spec"
    exit 1
fi

# Get app size
APP_SIZE=$(du -sm "$SOURCE_APP" | cut -f1)
echo "📦 App size: ${APP_SIZE} MB"
echo ""

# Create temporary directory for DMG contents
TMP_DMG_DIR=$(mktemp -d)
echo "📁 Staging directory: ${TMP_DMG_DIR}"

# Copy app to staging
echo "📦 Copying ${APP_NAME}.app..."
cp -R "$SOURCE_APP" "$TMP_DMG_DIR/"

# Create Applications symlink
echo "🔗 Creating Applications folder link..."
ln -s /Applications "$TMP_DMG_DIR/Applications"

# Calculate DMG size (app size + 50MB buffer)
DMG_SIZE=$((APP_SIZE + 50))

echo ""
echo "🔨 Creating DMG (${DMG_SIZE} MB)..."

# Remove old DMG if exists
rm -f "$DMG_NAME"

# Create DMG
hdiutil create -volname "$VOLUME_NAME" \
               -srcfolder "$TMP_DMG_DIR" \
               -ov \
               -format UDZO \
               -size ${DMG_SIZE}m \
               "$DMG_NAME"

# Clean up
rm -rf "$TMP_DMG_DIR"

# Get final DMG size
DMG_SIZE_FINAL=$(du -h "$DMG_NAME" | cut -f1)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Traditional DMG Created!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Location: ${DMG_NAME}"
echo "📊 Size: ${DMG_SIZE_FINAL}"
echo ""
echo "🧪 To test:"
echo "   1. Open ${DMG_NAME}"
echo "   2. Drag 'Hey Mike!.app' to Applications"
echo "   3. Launch from Applications or Spotlight"
echo ""
echo "✨ This is a PROPER Mac DMG - drag and drop!"
echo ""
