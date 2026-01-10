#!/usr/bin/env python3
"""
Demo script for Textual TUI with sample analysis.

This script launches the TUI and can be used to test the interface
without needing live API keys.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bet_copilot.ui.textual_app import run_textual_app

if __name__ == "__main__":
    print("⚽ Bet-Copilot Textual TUI Demo")
    print("="*50)
    print()
    print("📋 Instructions:")
    print("  1. Type a match: 'Arsenal vs Chelsea'")
    print("  2. Press Enter to analyze")
    print("  3. Use keyboard shortcuts:")
    print("     - 'r' = Refresh all")
    print("     - 'n' = Toggle news")
    print("     - 'm' = Toggle alt markets")
    print("     - 'q' = Quit")
    print()
    print("💡 Tip: News feed loads automatically from RSS")
    print("💡 Market scan runs every 5 minutes")
    print()
    print("Press Ctrl+C to exit anytime")
    print("="*50)
    print()
    
    input("Press Enter to start TUI... ")
    
    try:
        run_textual_app()
    except KeyboardInterrupt:
        print("\n\n👋 Demo finished!")
        sys.exit(0)
