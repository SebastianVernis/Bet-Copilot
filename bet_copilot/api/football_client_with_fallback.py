"""
Football API client with automatic fallback to simple data provider.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple

from bet_copilot.api.football_client import FootballAPIClient, TeamStats, H2HStats, TeamLineup
from bet_copilot.api.simple_football_data import SimpleFootballDataProvider

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
        
        # Convert to TeamStats (matches FootballAPIClient structure)
        # Calculate missing fields
        clean_sheets = int(simple_stats.matches_played * 0.3)  # Estimate 30%
        failed_to_score = int(simple_stats.matches_played * 0.2)  # Estimate 20%
        
        return TeamStats(
            team_id=team_id,
            team_name=team_name,
            matches_played=simple_stats.matches_played,
            wins=simple_stats.wins,
            draws=simple_stats.draws,
            losses=simple_stats.losses,
            goals_for=simple_stats.goals_for,
            goals_against=simple_stats.goals_against,
            clean_sheets=clean_sheets,
            failed_to_score=failed_to_score,
            avg_goals_for=simple_stats.avg_goals_for,
            avg_goals_against=simple_stats.avg_goals_against,
            form=simple_stats.form,
        )
    
    async def get_h2h_stats(
        self,
        team1_id: int,
        team2_id: int,
        last_n: int = 10
    ) -> H2HStats:
        """
        Get H2H statistics with fallback.
        
        Args:
            team1_id: Team 1 ID
            team2_id: Team 2 ID
            last_n: Number of matches
            
        Returns:
            H2HStats from API or estimated
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting H2H from API-Football for teams {team1_id} vs {team2_id}")
                h2h = await self.api_client.get_h2h_stats(team1_id, team2_id, last_n)
                if h2h and h2h.matches_played > 0:
                    logger.info(f"✓ H2H retrieved from API-Football")
                    return h2h
            except Exception as e:
                logger.warning(f"API-Football failed for H2H: {str(e)[:100]}")
        
        # Fallback to simple provider - use generic names
        logger.info(f"Using SimpleProvider for H2H: Team {team1_id} vs Team {team2_id}")
        simple_h2h = await self.simple_provider.get_h2h(
            team1_id, team2_id, f"Team {team1_id}", f"Team {team2_id}", last_n
        )
        
        # Convert to H2HStats
        # Calculate averages
        avg_home = 2.5  # League average estimate
        avg_away = 2.0  # Slightly less for away
        
        return H2HStats(
            matches_played=simple_h2h.matches_played,
            home_wins=simple_h2h.home_wins,
            draws=simple_h2h.draws,
            away_wins=simple_h2h.away_wins,
            last_5_results=simple_h2h.last_5_results,
            avg_home_goals=avg_home,
            avg_away_goals=avg_away,
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
        
        # Convert to TeamLineup (matches FootballAPIClient structure)
        return TeamLineup(
            team_id=team_id,
            team_name=team_name,
            formation=simple_lineup.formation,
            starting_xi=[],
            substitutes=[],
            coach=None,
            missing_players=[],
        )
    
    async def get_team_players(
        self,
        team_id: int,
        season: int = 2024
    ) -> List:
        """
        Get team players with fallback.
        
        Args:
            team_id: Team ID
            season: Season year
            
        Returns:
            List of PlayerStats (empty in simple provider)
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting players from API-Football for team {team_id}")
                players = await self.api_client.get_team_players(team_id, season)
                if players:
                    logger.info(f"✓ Players retrieved from API-Football")
                    return players
            except Exception as e:
                logger.warning(f"API-Football failed for players: {str(e)[:100]}")
        
        # Fallback - no player data
        logger.info(f"SimpleProvider has no player data")
        return []
    
    async def get_team_injuries(
        self,
        team_id: int,
        season: int,
        league_id: int
    ) -> List:
        """
        Get team injuries with fallback.
        
        Args:
            team_id: Team ID
            season: Season year
            league_id: League ID
            
        Returns:
            List of injured PlayerStats (empty in simple provider)
        """
        # Try API-Football first
        if self.use_api:
            try:
                logger.info(f"Attempting injuries from API-Football for team {team_id}")
                injuries = await self.api_client.get_team_injuries(team_id, season, league_id)
                if injuries:
                    logger.info(f"✓ Injuries retrieved from API-Football")
                    return injuries
            except Exception as e:
                logger.warning(f"API-Football failed for injuries: {str(e)[:100]}")
        
        # Fallback - no injury data
        logger.info(f"SimpleProvider has no injury data for team {team_id}")
        return []
    
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
