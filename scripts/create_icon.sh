#!/bin/bash
# Create macOS .icns icon from PNG source
# Usage: ./scripts/create_icon.sh

set -e  # Exit on error

echo "🎨 Creating macOS icon (.icns) from source PNG..."

# Check if source icon exists
if [ ! -f "assets/icon.png" ]; then
    echo "❌ Error: assets/icon.png not found"
    exit 1
fi

# Create iconset directory
mkdir -p HeyMike.iconset

echo "📐 Generating icon sizes..."

# Generate all required sizes using sips (built-in macOS tool)
sips -z 16 16     assets/icon.png --out HeyMike.iconset/icon_16x16.png
sips -z 32 32     assets/icon.png --out HeyMike.iconset/icon_16x16@2x.png
sips -z 32 32     assets/icon.png --out HeyMike.iconset/icon_32x32.png
sips -z 64 64     assets/icon.png --out HeyMike.iconset/icon_32x32@2x.png
sips -z 128 128   assets/icon.png --out HeyMike.iconset/icon_128x128.png
sips -z 256 256   assets/icon.png --out HeyMike.iconset/icon_128x128@2x.png
sips -z 256 256   assets/icon.png --out HeyMike.iconset/icon_256x256.png
sips -z 512 512   assets/icon.png --out HeyMike.iconset/icon_256x256@2x.png
sips -z 512 512   assets/icon.png --out HeyMike.iconset/icon_512x512.png
sips -z 1024 1024 assets/icon.png --out HeyMike.iconset/icon_512x512@2x.png

echo "🔨 Converting to .icns format..."

# Convert iconset to .icns file using iconutil (built-in macOS tool)
iconutil -c icns HeyMike.iconset -o assets/icon.icns

echo "🧹 Cleaning up temporary files..."

# Cleanup
rm -rf HeyMike.iconset

echo "✅ Icon created: assets/icon.icns"
