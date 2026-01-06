"""
Dashboard State Persistence
Manages persistent state for the Textual TUI dashboard.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardState:
    """
    Persistent state manager for dashboard.
    
    Stores:
    - Last used sport key
    - User preferences (refresh intervals, display settings)
    - Recent searches
    - Favorite markets
    - Window layout preferences
    """
    
    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to state file (default: ~/.bet_copilot_state.json)
        """
        if state_file is None:
            home = Path.home()
            state_file = home / ".bet_copilot_state.json"
        
        self.state_file = state_file
        
        # Default state
        self.last_sport_key: str = "soccer_epl"
        self.recent_searches: List[str] = []
        self.favorite_markets: List[str] = []
        self.preferences: Dict[str, Any] = {
            "auto_refresh_markets": True,
            "auto_refresh_news": True,
            "market_refresh_interval": 60,
            "news_refresh_interval": 3600,
            "show_news_feed": True,
            "show_alternative_markets": True,
            "max_markets_display": 20,
            "theme": "neon",
        }
        self.last_session: Optional[datetime] = None
        self.session_count: int = 0
    
    async def load(self) -> bool:
        """
        Load state from file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not self.state_file.exists():
                logger.info("No state file found, using defaults")
                return False
            
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            # Load state
            self.last_sport_key = data.get('last_sport_key', self.last_sport_key)
            self.recent_searches = data.get('recent_searches', [])
            self.favorite_markets = data.get('favorite_markets', [])
            self.preferences.update(data.get('preferences', {}))
            self.session_count = data.get('session_count', 0)
            
            # Parse last session timestamp
            last_session_str = data.get('last_session')
            if last_session_str:
                self.last_session = datetime.fromisoformat(last_session_str)
            
            logger.info(f"State loaded from {self.state_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading state: {str(e)}")
            return False
    
    async def save(self) -> bool:
        """
        Save state to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Increment session count
            self.session_count += 1
            self.last_session = datetime.now()
            
            # Prepare data
            data = {
                'last_sport_key': self.last_sport_key,
                'recent_searches': self.recent_searches[-20:],  # Keep last 20
                'favorite_markets': self.favorite_markets,
                'preferences': self.preferences,
                'last_session': self.last_session.isoformat(),
                'session_count': self.session_count,
                'version': '0.6.0',
            }
            
            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"State saved to {self.state_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")
            return False
    
    def add_recent_search(self, search: str) -> None:
        """Add a search to recent searches."""
        if search not in self.recent_searches:
            self.recent_searches.append(search)
            
            # Keep only last 20
            if len(self.recent_searches) > 20:
                self.recent_searches = self.recent_searches[-20:]
    
    def add_favorite_market(self, market: str) -> None:
        """Add a market to favorites."""
        if market not in self.favorite_markets:
            self.favorite_markets.append(market)
    
    def remove_favorite_market(self, market: str) -> None:
        """Remove a market from favorites."""
        if market in self.favorite_markets:
            self.favorite_markets.remove(market)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference value."""
        self.preferences[key] = value
    
    def clear(self) -> None:
        """Clear all state (reset to defaults)."""
        self.last_sport_key = "soccer_epl"
        self.recent_searches = []
        self.favorite_markets = []
        self.preferences = {
            "auto_refresh_markets": True,
            "auto_refresh_news": True,
            "market_refresh_interval": 60,
            "news_refresh_interval": 3600,
            "show_news_feed": True,
            "show_alternative_markets": True,
            "max_markets_display": 20,
            "theme": "neon",
        }
        self.last_session = None
        self.session_count = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current state."""
        return {
            'last_sport_key': self.last_sport_key,
            'recent_searches_count': len(self.recent_searches),
            'favorite_markets_count': len(self.favorite_markets),
            'last_session': self.last_session.isoformat() if self.last_session else None,
            'session_count': self.session_count,
            'preferences': self.preferences,
        }
