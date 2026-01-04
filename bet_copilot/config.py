"""
Configuration for Bet-Copilot.
Loads from environment variables.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "bet_copilot.db"

# API Keys
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY", "")

# API URLs
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"

# Circuit Breaker Settings
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3

# Cache TTLs (seconds)
CACHE_TTL_LIVE = 300  # 5 minutes for live/upcoming events
CACHE_TTL_HISTORICAL = 86400  # 24 hours for historical data

# Rate Limiting
MAX_CONCURRENT_REQUESTS = 3
REQUEST_DELAY = 0.5  # seconds between requests

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Math Engine Settings
POISSON_MAX_GOALS = 10  # Maximum goals to calculate in Poisson
HOME_ADVANTAGE_FACTOR = 1.1  # 10% boost for home team

# Kelly Criterion Settings
KELLY_FRACTION = 0.25  # 1/4 Kelly (conservative)
MAX_STAKE_PERCENT = 5.0  # Maximum 5% of bankroll per bet
MIN_EV_THRESHOLD = 0.05  # Minimum 5% EV to consider

# UI Settings
UI_REFRESH_RATE = 1.0  # seconds
TABLE_MAX_ROWS = 20
