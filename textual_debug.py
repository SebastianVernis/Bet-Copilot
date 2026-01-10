#!/usr/bin/env python3
"""
Bet-Copilot - Textual TUI with Debug Logging
"""

import sys
import logging
from pathlib import Path

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('textual_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bet_copilot.ui.textual_app import run_textual_app

if __name__ == "__main__":
    print("🚀 Starting Bet-Copilot Textual TUI (Debug Mode)...")
    print("📋 Logs: textual_debug.log")
    print("Press Ctrl+C to exit\n")
    
    try:
        run_textual_app()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
