"""
Configuration for Bet-Copilot.
Loads from environment variables.
"""

import os
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    # Load from project root
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except ImportError:
    # python-dotenv not installed, use system env vars only
    pass

# Base paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "bet_copilot.db"

# API Keys
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
FALLBACK_FOOTBALL_API_KEY = os.getenv("FALLBACK_FOOTBALL_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY", "")

# Alternative Data Sources
THESPORTSDB_API_KEY = os.getenv("THESPORTSDB_API_KEY", "")
SPORTSDATA_API_KEY = os.getenv("SPORTSDATA_API_KEY", "")
FOOTBALLDATA_API_KEY = os.getenv("FOOTBALLDATA_API_KEY", "")

# API URLs
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
THESPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json"
FOOTBALLDATA_BASE_URL = "https://api.football-data.org/v4"
SPORTSDATA_BASE_URL = "https://api.sportsdata.io/v4/soccer/scores/json"

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
