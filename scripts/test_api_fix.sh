#!/bin/bash
# Script temporal para testear API fix

export GEMINI_API_KEY="AIzaSyC1Ia7n0ck70psfdtzT1PjFy8YOMX0k0EE"

echo "🔑 Testing Gemini API Key..."
python3 << 'EOF'
from bet_copilot.config import GEMINI_API_KEY
print(f"Loaded key: {GEMINI_API_KEY[:30]}...")
EOF

echo ""
echo "🚀 Launching Bet-Copilot..."
python3 main.py
