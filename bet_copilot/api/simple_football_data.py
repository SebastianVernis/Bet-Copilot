"""
Simple football data provider as fallback for API-Football.
Uses basic statistical estimations when API is unavailable.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SimpleTeamStats:
    """Basic team statistics from simple estimation."""
    
    team_name: str
    matches_played: int = 20
    wins: int = 10
    draws: int = 5
    losses: int = 5
    goals_for: int = 30
    goals_against: int = 25
    form: str = "WDWDL"  # Default balanced form
    
    @property
    def avg_goals_for(self) -> float:
        """Average goals scored per match."""
        return self.goals_for / self.matches_played if self.matches_played > 0 else 1.5
    
    @property
    def avg_goals_against(self) -> float:
        """Average goals conceded per match."""
        return self.goals_against / self.matches_played if self.matches_played > 0 else 1.5


@dataclass
class SimpleH2HStats:
    """Basic H2H statistics from simple estimation."""
    
    home_team: str
    away_team: str
    matches_played: int = 5
    home_wins: int = 2
    draws: int = 1
    away_wins: int = 2
    last_5_results: List[str] = None
    
    def __post_init__(self):
        if self.last_5_results is None:
            # Generate balanced H2H
            self.last_5_results = ["H"] * self.home_wins + ["D"] * self.draws + ["A"] * self.away_wins
            self.last_5_results = self.last_5_results[:5]


@dataclass
class SimpleLineup:
    """Basic lineup information from simple estimation."""
    
    team_name: str
    formation: str = "4-3-3"
    missing_players: List = None
    
    def __post_init__(self):
        if self.missing_players is None:
            self.missing_players = []


class SimpleFootballDataProvider:
    """
    Simple football data provider as fallback.
    
    Provides basic estimated data when API-Football is unavailable.
    Uses team name heuristics and league averages.
    """
    
    # League averages for estimation
    LEAGUE_AVERAGES = {
        "Premier League": {"avg_goals": 2.8, "home_advantage": 1.15},
        "La Liga": {"avg_goals": 2.6, "home_advantage": 1.12},
        "Serie A": {"avg_goals": 2.5, "home_advantage": 1.10},
        "Bundesliga": {"avg_goals": 3.0, "home_advantage": 1.13},
        "Ligue 1": {"avg_goals": 2.7, "home_advantage": 1.11},
        "default": {"avg_goals": 2.7, "home_advantage": 1.12},
    }
    
    # Team tier estimation (basic heuristic)
    TIER_1_TEAMS = [
        "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United",
        "Barcelona", "Real Madrid", "Atletico Madrid",
        "Bayern Munich", "Borussia Dortmund",
        "Paris Saint-Germain", "PSG",
        "Juventus", "Inter Milan", "AC Milan",
    ]
    
    TIER_2_TEAMS = [
        "Tottenham", "Newcastle", "Aston Villa",
        "Sevilla", "Real Sociedad", "Athletic Bilbao",
        "Napoli", "Roma", "Lazio",
        "RB Leipzig", "Bayer Leverkusen",
        "Marseille", "Monaco", "Lyon",
    ]
    
    def __init__(self, league: str = "Premier League"):
        """
        Initialize simple data provider.
        
        Args:
            league: League name for average data
        """
        self.league = league
        self.league_data = self.LEAGUE_AVERAGES.get(league, self.LEAGUE_AVERAGES["default"])
        logger.info(f"Simple football data provider initialized for {league}")
    
    def is_available(self) -> bool:
        """Simple provider is always available."""
        return True
    
    async def get_team_stats(
        self,
        team_id: int,
        team_name: str,
        league_id: int = 39,
        season: int = 2024
    ) -> SimpleTeamStats:
        """
        Get estimated team statistics.
        
        Args:
            team_id: Team ID (ignored in simple provider)
            team_name: Team name for estimation
            league_id: League ID (ignored)
            season: Season (ignored)
            
        Returns:
            SimpleTeamStats with estimated data
        """
        logger.info(f"Generating estimated stats for {team_name}")
        
        # Estimate tier
        tier = self._estimate_team_tier(team_name)
        
        # Base stats on tier
        if tier == 1:
            # Top teams
            wins = 14
            draws = 4
            losses = 2
            goals_for = int(self.league_data["avg_goals"] * 20 * 1.3)  # 30% above average
            goals_against = int(self.league_data["avg_goals"] * 20 * 0.7)  # 30% below average
            form = "WWWDW"
        elif tier == 2:
            # Mid-table teams
            wins = 10
            draws = 6
            losses = 4
            goals_for = int(self.league_data["avg_goals"] * 20 * 1.1)
            goals_against = int(self.league_data["avg_goals"] * 20 * 0.9)
            form = "WDWDL"
        else:
            # Lower teams
            wins = 6
            draws = 6
            losses = 8
            goals_for = int(self.league_data["avg_goals"] * 20 * 0.8)
            goals_against = int(self.league_data["avg_goals"] * 20 * 1.2)
            form = "LDLWD"
        
        return SimpleTeamStats(
            team_name=team_name,
            matches_played=20,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            form=form,
        )
    
    async def get_h2h(
        self,
        team1_id: int,
        team2_id: int,
        team1_name: str,
        team2_name: str,
        limit: int = 10
    ) -> SimpleH2HStats:
        """
        Get estimated H2H statistics.
        
        Args:
            team1_id: Team 1 ID (ignored)
            team2_id: Team 2 ID (ignored)
            team1_name: Team 1 name
            team2_name: Team 2 name
            limit: Number of matches (max 10)
            
        Returns:
            SimpleH2HStats with estimated data
        """
        logger.info(f"Generating estimated H2H for {team1_name} vs {team2_name}")
        
        # Estimate based on team tiers
        tier1 = self._estimate_team_tier(team1_name)
        tier2 = self._estimate_team_tier(team2_name)
        
        # Balanced by default
        home_wins = 2
        draws = 1
        away_wins = 2
        
        # Adjust based on tier difference
        if tier1 < tier2:  # Team 1 is stronger
            home_wins = 3
            away_wins = 1
        elif tier2 < tier1:  # Team 2 is stronger
            home_wins = 1
            away_wins = 3
        
        return SimpleH2HStats(
            home_team=team1_name,
            away_team=team2_name,
            matches_played=5,
            home_wins=home_wins,
            draws=draws,
            away_wins=away_wins,
        )
    
    async def get_team_lineup(
        self,
        team_id: int,
        team_name: str
    ) -> SimpleLineup:
        """
        Get basic lineup information.
        
        Args:
            team_id: Team ID (ignored)
            team_name: Team name
            
        Returns:
            SimpleLineup with basic formation
        """
        logger.info(f"Generating estimated lineup for {team_name}")
        
        # Standard formation
        return SimpleLineup(
            team_name=team_name,
            formation="4-3-3",
            missing_players=[]  # No injury data in simple provider
        )
    
    def _estimate_team_tier(self, team_name: str) -> int:
        """
        Estimate team tier based on name.
        
        Args:
            team_name: Team name
            
        Returns:
            Tier: 1 (top), 2 (mid), 3 (lower)
        """
        team_lower = team_name.lower()
        
        # Check tier 1
        for tier1_team in self.TIER_1_TEAMS:
            if tier1_team.lower() in team_lower:
                return 1
        
        # Check tier 2
        for tier2_team in self.TIER_2_TEAMS:
            if tier2_team.lower() in team_lower:
                return 2
        
        # Default to tier 3
        return 3
    
    async def search_team_by_name(self, team_name: str, league_id: int = 39) -> Optional[int]:
        """
        Search team and return ID.
        
        Args:
            team_name: Team name to search
            league_id: League ID (ignored)
            
        Returns:
            Dummy team ID (hash of name)
        """
        # Return a consistent ID based on team name
        return hash(team_name) % 10000
    
    async def close(self):
        """No resources to close."""
        pass
