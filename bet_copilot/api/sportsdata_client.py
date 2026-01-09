"""
SportsData.io API client for detailed soccer statistics and advanced metrics.
Provides corners, cards, shots, and other alternative markets data.
"""

import asyncio
import logging
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.config import SPORTSDATA_API_KEY, SPORTSDATA_BASE_URL

logger = logging.getLogger(__name__)


class SportsDataError(Exception):
    """Base exception for SportsData API errors."""
    pass


class SportsDataClient:
    """
    Client for SportsData.io API.
    
    Features:
    - Detailed match statistics (corners, cards, shots, etc.)
    - Player statistics and props
    - Advanced metrics
    - Real-time data
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = SPORTSDATA_BASE_URL,
        timeout: int = 10,
    ):
        self.api_key = api_key or SPORTSDATA_API_KEY
        self.base_url = base_url
        self.timeout = timeout
        self.session = None
        
        if not self.api_key:
            logger.warning("SportsData API key not configured")
        else:
            logger.info("SportsData client initialized")
    
    def is_available(self) -> bool:
        """Check if API is available."""
        return bool(self.api_key)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to SportsData API."""
        url = f"{self.base_url}/{endpoint}"
        
        # API key as query parameter
        request_params = {"key": self.api_key}
        if params:
            request_params.update(params)
        
        session = await self._get_session()
        
        try:
            async with session.get(
                url, params=request_params, timeout=self.timeout
            ) as response:
                if response.status == 401:
                    logger.error("Unauthorized - check API key")
                    raise SportsDataError("Unauthorized")
                
                if response.status == 429:
                    logger.error("Rate limit exceeded")
                    raise SportsDataError("Rate limit exceeded")
                
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:200]}")
                    raise SportsDataError(f"API error: {response.status}")
                
                data = await response.json()
                logger.info(f"Successfully fetched {endpoint}")
                return data
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint}")
            raise SportsDataError("Request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            raise SportsDataError(f"Client error: {str(e)}")
    
    async def get_competitions(self) -> List[Dict]:
        """Get list of available competitions."""
        try:
            data = await self._make_request("competitions")
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Error fetching competitions: {str(e)}")
            return []
    
    async def get_teams(self, competition: str) -> List[Dict]:
        """
        Get teams in a competition.
        
        Args:
            competition: Competition code (e.g., "EPL", "LALIGA")
            
        Returns:
            List of teams
        """
        try:
            data = await self._make_request(f"teams/{competition}")
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Error fetching teams: {str(e)}")
            return []
    
    async def get_team_games(
        self,
        competition: str,
        team_key: str,
        season: str
    ) -> List[Dict]:
        """
        Get team games with detailed statistics.
        
        Args:
            competition: Competition code (e.g., "EPL")
            team_key: Team key/code
            season: Season (e.g., "2024")
            
        Returns:
            List of games with detailed stats
        """
        try:
            data = await self._make_request(
                f"gamesbytm/{competition}/{season}/{team_key}"
            )
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Error fetching team games: {str(e)}")
            return []
    
    async def get_game_stats(self, game_id: int) -> Optional[Dict]:
        """
        Get detailed game statistics including corners, cards, shots.
        
        Args:
            game_id: Game ID
            
        Returns:
            Game statistics dict
        """
        try:
            data = await self._make_request(f"game/{game_id}")
            return data
        except Exception as e:
            logger.warning(f"Error fetching game stats: {str(e)}")
            return None
    
    async def get_standings(self, competition: str, season: str) -> List[Dict]:
        """
        Get competition standings.
        
        Args:
            competition: Competition code (e.g., "EPL")
            season: Season (e.g., "2024")
            
        Returns:
            List of standings
        """
        try:
            data = await self._make_request(f"standings/{competition}/{season}")
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Error fetching standings: {str(e)}")
            return []
    
    async def get_player_stats(
        self,
        competition: str,
        season: str
    ) -> List[Dict]:
        """
        Get player statistics.
        
        Args:
            competition: Competition code (e.g., "EPL")
            season: Season (e.g., "2024")
            
        Returns:
            List of player stats
        """
        try:
            data = await self._make_request(f"playerstats/{competition}/{season}")
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Error fetching player stats: {str(e)}")
            return []
    
    async def calculate_alternative_markets(
        self,
        games: List[Dict],
        limit: int = 5
    ) -> Dict:
        """
        Calculate alternative markets averages from recent games.
        
        Args:
            games: List of game statistics
            limit: Number of recent games to consider
            
        Returns:
            Dict with corners, cards, shots averages
        """
        if not games:
            return {
                "avg_corners": 0.0,
                "avg_cards": 0.0,
                "avg_shots": 0.0,
                "avg_shots_on_target": 0.0,
            }
        
        recent = games[:limit]
        
        total_corners = 0
        total_cards = 0
        total_shots = 0
        total_shots_on_target = 0
        count = 0
        
        for game in recent:
            # Sum home and away stats
            corners = (game.get("Corners", 0) or 0) + (game.get("CornerKicks", 0) or 0)
            cards = (
                (game.get("YellowCards", 0) or 0) +
                (game.get("RedCards", 0) or 0) * 2  # Weight red cards more
            )
            shots = (game.get("Shots", 0) or 0) + (game.get("ShotsOnGoal", 0) or 0)
            shots_on_target = game.get("ShotsOnGoal", 0) or 0
            
            total_corners += corners
            total_cards += cards
            total_shots += shots
            total_shots_on_target += shots_on_target
            count += 1
        
        if count == 0:
            return {
                "avg_corners": 0.0,
                "avg_cards": 0.0,
                "avg_shots": 0.0,
                "avg_shots_on_target": 0.0,
            }
        
        return {
            "avg_corners": round(total_corners / count, 2),
            "avg_cards": round(total_cards / count, 2),
            "avg_shots": round(total_shots / count, 2),
            "avg_shots_on_target": round(total_shots_on_target / count, 2),
        }
    
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("SportsData client session closed")


# Competition code mappings
COMPETITION_CODES = {
    "Premier League": "EPL",
    "La Liga": "LALIGA",
    "Bundesliga": "BUNDESLIGA",
    "Serie A": "SERIEA",
    "Ligue 1": "LIGUE1",
    "Champions League": "UCL",
    "Europa League": "UEL",
}
