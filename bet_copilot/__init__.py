"""
Bet-Copilot - Sistema de especulación deportiva con CLI/TUI

Version: 0.6.0
"""

__version__ = "0.6.0"
__author__ = "SebastianVernisMora"

# Expose core components
from bet_copilot.config import (
    ODDS_API_KEY,
    API_FOOTBALL_KEY,
    GEMINI_API_KEY,
    DB_PATH,
)

__all__ = [
    "__version__",
    "__author__",
    "ODDS_API_KEY",
    "API_FOOTBALL_KEY",
    "GEMINI_API_KEY",
    "DB_PATH",
]
