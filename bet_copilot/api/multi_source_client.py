"""
Multi-source football data client with intelligent fallback.

Priority chain:
1. API-Football (most complete, but suspended)
2. Football-Data.org (free, good data)
3. TheSportsDB (free, basic data)
4. SimpleFootballData (estimates, always available)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple

from bet_copilot.api.football_client import FootballAPIClient, TeamStats
from bet_copilot.api.footballdata_client import FootballDataClient
from bet_copilot.api.thesportsdb_client import TheSportsDBClient
from bet_copilot.api.simple_football_data import SimpleFootballDataProvider
from bet_copilot.config import API_FOOTBALL_KEY, FALLBACK_FOOTBALL_API_KEY

logger = logging.getLogger(__name__)


class MultiSourceFootballClient:
    """
    Intelligent multi-source football data client.
    
    Automatically tries multiple data sources in priority order:
    1. API-Football (if available)
    2. Football-Data.org
    3. TheSportsDB
    4. SimpleFootballData (fallback estimates)
    """
    
    def __init__(self):
        """Initialize all clients."""
        # Primary source (may be suspended)
        self.api_football = FootballAPIClient(api_key=API_FOOTBALL_KEY)
        
        # Fallback API-Football key
        self.api_football_fallback = FootballAPIClient(api_key=FALLBACK_FOOTBALL_API_KEY)
        
        # Alternative sources
        self.footballdata = FootballDataClient()
        self.thesportsdb = TheSportsDBClient()
        
        # Always-available fallback
        self.simple = SimpleFootballDataProvider()
        
        logger.info("Multi-source football client initialized")
        logger.info(f"  API-Football primary: {bool(API_FOOTBALL_KEY)}")
        logger.info(f"  API-Football fallback: {bool(FALLBACK_FOOTBALL_API_KEY)}")
        logger.info(f"  Football-Data: {self.footballdata.is_available()}")
        logger.info(f"  TheSportsDB: {self.thesportsdb.is_available()}")
        logger.info(f"  SimpleProvider: {self.simple.is_available()}")
    
    async def search_team(
        self,
        team_name: str,
        league_id: Optional[int] = None
    ) -> Tuple[Optional[int], Optional[str], str]:
        """
        Search for team across all sources.
        
        Args:
            team_name: Team name to search
            league_id: Optional league ID (for API-Football)
            
        Returns:
            Tuple of (team_id, team_name, source_used)
        """
        # Try API-Football primary
        try:
            team_id = await self.api_football.search_team_by_name(team_name, league_id or 39)
            if team_id:
                logger.info(f"✓ Found {team_name} in API-Football primary (ID: {team_id})")
                return team_id, team_name, "API-Football"
        except Exception as e:
            logger.debug(f"API-Football primary failed: {str(e)[:100]}")
        
        # Try API-Football fallback
        try:
            team_id = await self.api_football_fallback.search_team_by_name(team_name, league_id or 39)
            if team_id:
                logger.info(f"✓ Found {team_name} in API-Football fallback (ID: {team_id})")
                return team_id, team_name, "API-Football-Fallback"
        except Exception as e:
            logger.debug(f"API-Football fallback failed: {str(e)[:100]}")
        
        # Try Football-Data.org
        try:
            team_data = await self.footballdata.get_team_by_name(team_name)
            if team_data:
                team_id = team_data.get("id")
                team_name_full = team_data.get("name", team_name)
                logger.info(f"✓ Found {team_name_full} in Football-Data (ID: {team_id})")
                return team_id, team_name_full, "Football-Data"
        except Exception as e:
            logger.debug(f"Football-Data failed: {str(e)[:100]}")
        
        # Try TheSportsDB
        try:
            team_data = await self.thesportsdb.search_team(team_name)
            if team_data:
                team_id = int(team_data.get("idTeam"))
                team_name_full = team_data.get("strTeam", team_name)
                logger.info(f"✓ Found {team_name_full} in TheSportsDB (ID: {team_id})")
                return team_id, team_name_full, "TheSportsDB"
        except Exception as e:
            logger.debug(f"TheSportsDB failed: {str(e)[:100]}")
        
        # Fallback to SimpleProvider (always works)
        team_id = await self.simple.search_team_by_name(team_name)
        logger.info(f"✓ Using SimpleProvider for {team_name} (estimated ID: {team_id})")
        return team_id, team_name, "SimpleProvider"
    
    async def get_team_stats(
        self,
        team_id: int,
        team_name: str,
        source: str,
        league_id: int = 39,
        season: int = 2024
    ) -> Optional[TeamStats]:
        """
        Get team statistics from appropriate source.
        
        Args:
            team_id: Team ID
            team_name: Team name
            source: Source that found the team
            league_id: League ID
            season: Season year
            
        Returns:
            TeamStats object
        """
        # Try API-Football sources first
        if source in ["API-Football", "API-Football-Fallback"]:
            client = (
                self.api_football if source == "API-Football"
                else self.api_football_fallback
            )
            
            try:
                stats = await client.get_team_stats(team_id, league_id, season)
                if stats:
                    logger.info(f"✓ Got stats from {source}")
                    return stats
            except Exception as e:
                logger.debug(f"{source} stats failed: {str(e)[:100]}")
        
        # Try alternative sources
        try:
            if source == "TheSportsDB":
                stats_dict = await self.thesportsdb.get_team_stats(team_id)
                
                # Convert to TeamStats
                return TeamStats(
                    team_id=team_id,
                    team_name=team_name,
                    matches_played=stats_dict["matches_played"],
                    wins=stats_dict["wins"],
                    draws=stats_dict["draws"],
                    losses=stats_dict["losses"],
                    goals_for=stats_dict["goals_for"],
                    goals_against=stats_dict["goals_against"],
                    clean_sheets=int(stats_dict["matches_played"] * 0.3),
                    failed_to_score=int(stats_dict["matches_played"] * 0.2),
                    avg_goals_for=stats_dict["goals_for"] / max(stats_dict["matches_played"], 1),
                    avg_goals_against=stats_dict["goals_against"] / max(stats_dict["matches_played"], 1),
                    form="",  # Not available from this source
                )
            
            elif source == "Football-Data":
                # Get recent matches to calculate stats
                matches = await self.footballdata.get_team_matches(team_id, limit=20)
                
                if matches:
                    wins = draws = losses = 0
                    goals_for = goals_against = 0
                    
                    for match in matches:
                        home_team = match.get("homeTeam", {})
                        away_team = match.get("awayTeam", {})
                        score = match.get("score", {}).get("fullTime", {})
                        
                        home_score = score.get("home", 0) or 0
                        away_score = score.get("away", 0) or 0
                        
                        is_home = (home_team.get("id") == team_id)
                        
                        if is_home:
                            goals_for += home_score
                            goals_against += away_score
                            if home_score > away_score:
                                wins += 1
                            elif home_score == away_score:
                                draws += 1
                            else:
                                losses += 1
                        else:
                            goals_for += away_score
                            goals_against += home_score
                            if away_score > home_score:
                                wins += 1
                            elif away_score == home_score:
                                draws += 1
                            else:
                                losses += 1
                    
                    return TeamStats(
                        team_id=team_id,
                        team_name=team_name,
                        matches_played=len(matches),
                        wins=wins,
                        draws=draws,
                        losses=losses,
                        goals_for=goals_for,
                        goals_against=goals_against,
                        clean_sheets=int(len(matches) * 0.3),
                        failed_to_score=int(len(matches) * 0.2),
                        avg_goals_for=goals_for / len(matches),
                        avg_goals_against=goals_against / len(matches),
                        form="",
                    )
        
        except Exception as e:
            logger.warning(f"Error getting stats from {source}: {str(e)[:100]}")
        
        # Fallback to SimpleProvider
        logger.info(f"Using SimpleProvider for {team_name} stats")
        simple_stats = await self.simple.get_team_stats(team_id, team_name, league_id, season)
        
        return TeamStats(
            team_id=team_id,
            team_name=team_name,
            matches_played=simple_stats.matches_played,
            wins=simple_stats.wins,
            draws=simple_stats.draws,
            losses=simple_stats.losses,
            goals_for=simple_stats.goals_for,
            goals_against=simple_stats.goals_against,
            clean_sheets=int(simple_stats.matches_played * 0.3),
            failed_to_score=int(simple_stats.matches_played * 0.2),
            avg_goals_for=simple_stats.avg_goals_for,
            avg_goals_against=simple_stats.avg_goals_against,
            form=simple_stats.form,
            home_wins=simple_stats.wins // 2,
            home_draws=simple_stats.draws // 2,
            home_losses=simple_stats.losses // 2,
            away_wins=simple_stats.wins // 2,
            away_draws=simple_stats.draws // 2,
            away_losses=simple_stats.losses // 2,
        )
    
    async def close(self):
        """Close all client sessions."""
        await self.footballdata.close()
        await self.thesportsdb.close()
        await self.simple.close()
        logger.info("All clients closed")
