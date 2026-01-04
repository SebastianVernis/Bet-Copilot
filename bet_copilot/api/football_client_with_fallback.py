"""
Football API client with automatic fallback to simple data provider.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple

from bet_copilot.api.football_client import FootballAPIClient
from bet_copilot.api.simple_football_data import SimpleFootballDataProvider
from bet_copilot.models.soccer import TeamStats, H2HStats, TeamLineup

logger = logging.getLogger(__name__)


class FootballClientWithFallback:
    """
    Football client with automatic fallback.
    
    Priority:
    1. API-Football (real data, if API key configured)
    2. SimpleFootballDataProvider (estimated data, always available)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        league: str = "Premier League",
    ):
        """
        Initialize football client with fallback.
        
        Args:
            api_key: API-Football key (optional)
            league: League name for simple provider estimates
        """
        self.api_client = FootballAPIClient(api_key=api_key)
        self.simple_provider = SimpleFootballDataProvider(league=league)
        
        self.use_api = bool(api_key)
        
        if self.use_api:
            logger.info("Football client with fallback initialized (API-Football primary)")
        else:
            logger.info("Football client with fallback initialized (SimpleProvider only)")
    
    def is_available(self) -> bool:
        """Always available (SimpleProvider guarantees)."""
        return True
    
    def get_active_provider(self) -> str:
        """Get name of active provider."""
        return "API-Football" if self.use_api else "SimpleProvider"
    
    async def get_team_stats(
        self,
        team_id: int,
        team_name: str,
        league_id: int = 39,
        season: int = 2024
    ) -> TeamStats:
        """
        Get team statistics with fallback.
        
        Args:
            team_id: Team ID
            team_name: Team name
            league_id: League ID
            season: Season year
            
        Returns:
            TeamStats from API or estimated
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting to get stats from API-Football for {team_name}")
                stats = await self.api_client.get_team_stats(team_id, league_id, season)
                if stats:
                    logger.info(f"✓ Stats retrieved from API-Football")
                    return stats
            except Exception as e:
                logger.warning(f"API-Football failed for team stats: {str(e)[:100]}")
        
        # Fallback to simple provider
        logger.info(f"Using SimpleProvider for {team_name} stats")
        simple_stats = await self.simple_provider.get_team_stats(
            team_id, team_name, league_id, season
        )
        
        # Convert to TeamStats
        return TeamStats(
            team_id=team_id,
            team_name=team_name,
            matches_played=simple_stats.matches_played,
            wins=simple_stats.wins,
            draws=simple_stats.draws,
            losses=simple_stats.losses,
            goals_for=simple_stats.goals_for,
            goals_against=simple_stats.goals_against,
            form=simple_stats.form,
        )
    
    async def get_h2h(
        self,
        team1_id: int,
        team2_id: int,
        team1_name: str,
        team2_name: str,
        limit: int = 10
    ) -> H2HStats:
        """
        Get H2H statistics with fallback.
        
        Args:
            team1_id: Team 1 ID
            team2_id: Team 2 ID
            team1_name: Team 1 name
            team2_name: Team 2 name
            limit: Number of matches
            
        Returns:
            H2HStats from API or estimated
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting H2H from API-Football: {team1_name} vs {team2_name}")
                h2h = await self.api_client.get_h2h(team1_id, team2_id, limit)
                if h2h and h2h.matches_played > 0:
                    logger.info(f"✓ H2H retrieved from API-Football")
                    return h2h
            except Exception as e:
                logger.warning(f"API-Football failed for H2H: {str(e)[:100]}")
        
        # Fallback to simple provider
        logger.info(f"Using SimpleProvider for H2H: {team1_name} vs {team2_name}")
        simple_h2h = await self.simple_provider.get_h2h(
            team1_id, team2_id, team1_name, team2_name, limit
        )
        
        # Convert to H2HStats
        return H2HStats(
            team1_id=team1_id,
            team2_id=team2_id,
            matches_played=simple_h2h.matches_played,
            team1_wins=simple_h2h.home_wins,
            draws=simple_h2h.draws,
            team2_wins=simple_h2h.away_wins,
            last_5_results=simple_h2h.last_5_results,
        )
    
    async def get_team_lineup(
        self,
        team_id: int,
        team_name: str
    ) -> TeamLineup:
        """
        Get team lineup with fallback.
        
        Args:
            team_id: Team ID
            team_name: Team name
            
        Returns:
            TeamLineup from API or basic lineup
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting lineup from API-Football for {team_name}")
                lineup = await self.api_client.get_team_lineup(team_id)
                if lineup:
                    logger.info(f"✓ Lineup retrieved from API-Football")
                    return lineup
            except Exception as e:
                logger.warning(f"API-Football failed for lineup: {str(e)[:100]}")
        
        # Fallback to simple provider
        logger.info(f"Using SimpleProvider for {team_name} lineup")
        simple_lineup = await self.simple_provider.get_team_lineup(team_id, team_name)
        
        # Convert to TeamLineup
        return TeamLineup(
            team_id=team_id,
            team_name=team_name,
            formation=simple_lineup.formation,
            coach=None,
            players=[],  # No player data in simple provider
            missing_players=[],  # No injury data
        )
    
    async def search_team_by_name(
        self,
        team_name: str,
        league_id: int = 39
    ) -> Optional[int]:
        """
        Search team by name with fallback.
        
        Args:
            team_name: Team name
            league_id: League ID
            
        Returns:
            Team ID from API or generated ID
        """
        # Try API-Football first
        if self.use_api:
            try:
                team_id = await self.api_client.search_team_by_name(team_name, league_id)
                if team_id:
                    return team_id
            except Exception as e:
                logger.warning(f"API-Football search failed: {str(e)[:100]}")
        
        # Fallback to simple provider
        return await self.simple_provider.search_team_by_name(team_name, league_id)
    
    async def close(self):
        """Close all client sessions."""
        await self.api_client.close()
        await self.simple_provider.close()


def create_football_client(
    api_key: Optional[str] = None,
    league: str = "Premier League"
) -> FootballClientWithFallback:
    """
    Create football client with automatic fallback.
    
    Args:
        api_key: API-Football key (optional)
        league: League name for estimates
        
    Returns:
        FootballClientWithFallback instance
    """
    return FootballClientWithFallback(api_key=api_key, league=league)
