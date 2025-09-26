#!/bin/bash
# MagikMike Test Runner Script

set -e

echo "🧪 MagikMike Test Suite Runner"
echo "============================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "   Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $(basename $VIRTUAL_ENV)"

# Check if MagikMike is running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ MagikMike is running"
else
    echo "⚠️  MagikMike is not running"
    echo "   Start it with: python main.py"
    echo "   Then run this script again"
    exit 1
fi

echo ""
echo "🎯 Running comprehensive test suite..."
echo ""

# Run the test suite
python tests/test_magikmike_complete.py

echo ""
echo "📋 Manual testing required!"
echo "   Follow the checklist provided above"
echo "   Monitor terminal logs while testing"
echo ""
echo "📊 Test results saved to: test_results.json"
echo ""
echo "🎉 Testing complete!"
