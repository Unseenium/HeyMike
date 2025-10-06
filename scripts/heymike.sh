#!/bin/bash
# Hey Mike! Quick Launcher
# Run this script to start Hey Mike! from the source directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.heymike_venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found."
    echo "   Run ./scripts/install.sh first to set up Hey Mike!"
    exit 1
fi

# Activate virtual environment and run
cd "$SCRIPT_DIR"
source "$VENV_DIR/bin/activate"

echo "🎤 Starting Hey Mike!..."
python main.py
