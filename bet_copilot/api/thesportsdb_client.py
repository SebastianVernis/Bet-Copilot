"""
TheSportsDB API client for team information, leagues, and historical data.
Free tier available with good coverage for major leagues.
"""

import asyncio
import logging
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.config import THESPORTSDB_API_KEY, THESPORTSDB_BASE_URL

logger = logging.getLogger(__name__)


class TheSportsDBError(Exception):
    """Base exception for TheSportsDB API errors."""
    pass


class TheSportsDBClient:
    """
    Client for TheSportsDB API.
    
    Features:
    - Team information and logos
    - League tables
    - Match results
    - Player data
    - Free tier available
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = THESPORTSDB_BASE_URL,
        timeout: int = 10,
    ):
        self.api_key = api_key or THESPORTSDB_API_KEY
        self.base_url = base_url
        self.timeout = timeout
        self.session = None
        
        if not self.api_key:
            logger.warning("TheSportsDB API key not configured")
        else:
            logger.info(f"TheSportsDB client initialized with key: {self.api_key}")
    
    def is_available(self) -> bool:
        """Check if API is available."""
        return bool(self.api_key)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str) -> Dict:
        """Make HTTP request to TheSportsDB API."""
        url = f"{self.base_url}/{self.api_key}/{endpoint}"
        
        session = await self._get_session()
        
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:200]}")
                    raise TheSportsDBError(f"API error: {response.status}")
                
                data = await response.json()
                logger.info(f"Successfully fetched {endpoint}")
                return data
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint}")
            raise TheSportsDBError("Request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            raise TheSportsDBError(f"Client error: {str(e)}")
    
    async def search_team(self, team_name: str) -> Optional[Dict]:
        """
        Search for team by name.
        
        Args:
            team_name: Team name to search
            
        Returns:
            Team data or None if not found
        """
        try:
            data = await self._make_request(f"searchteams.php?t={team_name}")
            teams = data.get("teams", [])
            
            if teams:
                team = teams[0]
                logger.info(f"Found team: {team.get('strTeam')} (ID: {team.get('idTeam')})")
                return team
            
            logger.warning(f"No team found for: {team_name}")
            return None
        except Exception as e:
            logger.warning(f"Error searching team: {str(e)}")
            return None
    
    async def get_team_details(self, team_id: int) -> Optional[Dict]:
        """
        Get detailed team information.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team details
        """
        try:
            data = await self._make_request(f"lookupteam.php?id={team_id}")
            teams = data.get("teams", [])
            
            if teams:
                return teams[0]
            
            return None
        except Exception as e:
            logger.warning(f"Error fetching team details: {str(e)}")
            return None
    
    async def get_last_matches(
        self,
        team_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get team's last matches.
        
        Args:
            team_id: Team ID
            limit: Maximum number of matches
            
        Returns:
            List of recent matches
        """
        try:
            data = await self._make_request(f"eventslast.php?id={team_id}")
            events = data.get("results", [])
            
            return events[:limit] if events else []
        except Exception as e:
            logger.warning(f"Error fetching last matches: {str(e)}")
            return []
    
    async def get_next_matches(
        self,
        team_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get team's upcoming matches.
        
        Args:
            team_id: Team ID
            limit: Maximum number of matches
            
        Returns:
            List of upcoming matches
        """
        try:
            data = await self._make_request(f"eventsnext.php?id={team_id}")
            events = data.get("events", [])
            
            return events[:limit] if events else []
        except Exception as e:
            logger.warning(f"Error fetching next matches: {str(e)}")
            return []
    
    async def get_league_table(self, league_id: int, season: str) -> List[Dict]:
        """
        Get league table/standings.
        
        Args:
            league_id: League ID
            season: Season (e.g., "2023-2024")
            
        Returns:
            League table
        """
        try:
            data = await self._make_request(
                f"lookuptable.php?l={league_id}&s={season}"
            )
            return data.get("table", [])
        except Exception as e:
            logger.warning(f"Error fetching league table: {str(e)}")
            return []
    
    async def get_team_stats(self, team_id: int) -> Dict:
        """
        Get basic team statistics from recent matches.
        
        Args:
            team_id: Team ID
            
        Returns:
            Dict with calculated stats
        """
        matches = await self.get_last_matches(team_id, limit=10)
        
        if not matches:
            return {
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
            }
        
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        
        for match in matches:
            home_score = int(match.get("intHomeScore") or 0)
            away_score = int(match.get("intAwayScore") or 0)
            
            # Check if team is home or away
            is_home = (int(match.get("idHomeTeam")) == team_id)
            
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
        
        return {
            "matches_played": len(matches),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
        }
    
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("TheSportsDB client session closed")


# League ID mappings (most popular)
LEAGUE_IDS = {
    "Premier League": 4328,
    "La Liga": 4335,
    "Bundesliga": 4331,
    "Serie A": 4332,
    "Ligue 1": 4334,
    "Champions League": 4480,
    "Europa League": 4481,
}
