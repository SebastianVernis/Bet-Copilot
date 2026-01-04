"""
UI styles and color palette for Bet-Copilot.
Neon cyberpunk aesthetic for terminal.
"""

# Neon color palette (hex)
NEON_GREEN = "#39FF14"  # Success, high EV
NEON_YELLOW = "#FFFF00"  # Warning, low EV
NEON_CYAN = "#00FFFF"  # Info, home team
NEON_PINK = "#FF10F0"  # Away team
NEON_PURPLE = "#9D00FF"  # Titles, borders
NEON_RED = "#FF073A"  # Error, negative EV
LIGHT_GRAY = "#CCCCCC"  # Secondary text
DARK_GRAY = "#444444"  # Backgrounds

# Rich theme configuration
from rich.theme import Theme

BET_COPILOT_THEME = Theme(
    {
        "title": f"bold {NEON_PURPLE}",
        "success": f"bold {NEON_GREEN}",
        "warning": f"bold {NEON_YELLOW}",
        "error": f"bold {NEON_RED}",
        "info": f"{NEON_CYAN}",
        "highlight": f"bold {NEON_GREEN}",
        "dim": f"dim {LIGHT_GRAY}",
    }
)
