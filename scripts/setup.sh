#!/bin/bash
# MagikMike Development Setup Script

set -e

echo "🎤 MagikMike Development Setup"
echo "=============================="

# Check macOS version
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

# Check for Apple Silicon
if [[ "$(uname -m)" != "arm64" ]]; then
    echo "⚠️  Warning: This app is optimized for Apple Silicon (M1/M2/M3)"
    echo "   It may work on Intel Macs but performance will be limited"
fi

echo "✅ macOS detected: $(sw_vers -productVersion)"
echo "✅ Architecture: $(uname -m)"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Check Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is required but not installed"
    echo "   Install from: https://brew.sh"
    exit 1
fi

echo "✅ Homebrew detected"

# Install system dependencies
echo ""
echo "🍺 Installing system dependencies..."
brew install portaudio ffmpeg

# Create virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🎯 Setup complete! To run MagikMike:"
echo ""
echo "   1. Activate virtual environment:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Grant permissions in System Preferences:"
echo "      Security & Privacy → Privacy → Microphone → Add Terminal"
echo "      Security & Privacy → Privacy → Accessibility → Add Terminal"
echo ""
echo "   3. Run the application:"
echo "      python main.py"
echo ""
echo "   4. Run tests:"
echo "      python tests/test_magikmike_complete.py"
echo ""
echo "🚀 Happy coding!"
