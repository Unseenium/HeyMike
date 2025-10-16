#!/bin/bash
# Hey Mike! Development Launcher
# Run this script to start Hey Mike! from the source directory
# For development use only - end users should use the DMG installer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check for virtual environment (developers should create their own)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ No virtual environment detected."
    echo ""
    echo "For development, create a virtual environment first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Navigate to project root and run
cd "$PROJECT_ROOT"
echo "🎤 Starting Hey Mike! (development mode)..."
python main.py
