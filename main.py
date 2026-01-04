#!/usr/bin/env python3
"""
Bet-Copilot - Main entry point
Speculative Sports Analysis System
"""

import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bet_copilot.cli import main

if __name__ == "__main__":
    main()
