#!/usr/bin/env python3
"""
Bet-Copilot - Textual TUI Mode
Alternative interactive dashboard with Textual
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bet_copilot.ui.textual_app import run_textual_app

if __name__ == "__main__":
    print("🚀 Starting Bet-Copilot Textual TUI...")
    print("Press Ctrl+C to exit\n")
    
    try:
        run_textual_app()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
        sys.exit(0)
