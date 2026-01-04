"""
Data models for odds and betting markets.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Market:
    """Betting market with outcomes and odds."""

    key: str  # e.g., "h2h", "totals", "spreads"
    outcomes: Dict[str, float]  # {outcome_name: odds}
    last_update: datetime


@dataclass
class Bookmaker:
    """Bookmaker with available markets."""

    key: str  # e.g., "draftkings", "fanduel"
    title: str  # Display name
    markets: List[Market]
    last_update: datetime


@dataclass
class OddsEvent:
    """Sports event with odds from multiple bookmakers."""

    id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: datetime
    bookmakers: List[Bookmaker]

    def get_best_odds(self, market_key: str, outcome: str) -> Optional[float]:
        """
        Find best odds for an outcome across all bookmakers.
        
        Args:
            market_key: Market type (e.g., "h2h")
            outcome: Outcome name (e.g., home team name)
            
        Returns:
            Best odds or None
        """
        best_odds = None

        for bookmaker in self.bookmakers:
            for market in bookmaker.markets:
                if market.key == market_key and outcome in market.outcomes:
                    odds = market.outcomes[outcome]
                    if best_odds is None or odds > best_odds:
                        best_odds = odds

        return best_odds

    def get_bookmaker_odds(
        self, bookmaker_key: str, market_key: str, outcome: str
    ) -> Optional[float]:
        """
        Get odds from specific bookmaker.
        
        Args:
            bookmaker_key: Bookmaker identifier
            market_key: Market type
            outcome: Outcome name
            
        Returns:
            Odds or None
        """
        for bookmaker in self.bookmakers:
            if bookmaker.key == bookmaker_key:
                for market in bookmaker.markets:
                    if market.key == market_key and outcome in market.outcomes:
                        return market.outcomes[outcome]

        return None
