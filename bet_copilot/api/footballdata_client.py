"""
Football-Data.org API client for match fixtures, standings, and team data.
Free tier: 10 requests/minute, excellent for schedules and H2H.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.config import FOOTBALLDATA_API_KEY, FOOTBALLDATA_BASE_URL

logger = logging.getLogger(__name__)


class FootballDataError(Exception):
    """Base exception for Football-Data API errors."""
    pass


class FootballDataClient:
    """
    Client for Football-Data.org API.
    
    Features:
    - Team information and standings
    - Match fixtures and results
    - Head-to-head data
    - Free tier: 10 requests/minute
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = FOOTBALLDATA_BASE_URL,
        timeout: int = 10,
    ):
        self.api_key = api_key or FOOTBALLDATA_API_KEY
        self.base_url = base_url
        self.timeout = timeout
        self.session = None
        
        if not self.api_key:
            logger.warning("Football-Data API key not configured")
        else:
            logger.info("Football-Data client initialized")
    
    def is_available(self) -> bool:
        """Check if API is available."""
        return bool(self.api_key)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Football-Data API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"X-Auth-Token": self.api_key}
        
        session = await self._get_session()
        
        try:
            async with session.get(
                url, headers=headers, params=params, timeout=self.timeout
            ) as response:
                if response.status == 429:
                    logger.error("Rate limit exceeded (10 req/min)")
                    raise FootballDataError("Rate limit exceeded")
                
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:200]}")
                    raise FootballDataError(f"API error: {response.status}")
                
                data = await response.json()
                logger.info(f"Successfully fetched {endpoint}")
                return data
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint}")
            raise FootballDataError("Request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            raise FootballDataError(f"Client error: {str(e)}")
    
    async def get_competitions(self) -> List[Dict]:
        """Get list of available competitions."""
        data = await self._make_request("competitions")
        return data.get("competitions", [])
    
    async def get_team_by_name(self, team_name: str) -> Optional[Dict]:
        """
        Search for team by name.
        
        Args:
            team_name: Team name to search
            
        Returns:
            Team data or None if not found
        """
        try:
            # Football-Data doesn't support name search directly
            # We need to get teams from competitions and filter
            # For now, use a mapping of common teams
            team_id_map = {
                "arsenal": 57,
                "aston villa": 58,
                "bournemouth": 1044,
                "brentford": 402,
                "brighton": 397,
                "chelsea": 61,
                "crystal palace": 354,
                "everton": 62,
                "fulham": 63,
                "liverpool": 64,
                "manchester city": 65,
                "manchester united": 66,
                "newcastle": 67,
                "nottingham forest": 351,
                "southampton": 340,
                "tottenham": 73,
                "west ham": 563,
                "wolves": 76,
                "leicester": 338,
                "leeds": 341,
            }
            
            team_name_lower = team_name.lower()
            
            # Try exact match
            if team_name_lower in team_id_map:
                team_id = team_id_map[team_name_lower]
                # Get team details
                data = await self._make_request(f"teams/{team_id}")
                logger.info(f"Found team: {data.get('name')} (ID: {team_id})")
                return data
            
            # Try partial match
            for key, team_id in team_id_map.items():
                if key in team_name_lower or team_name_lower in key:
                    data = await self._make_request(f"teams/{team_id}")
                    logger.info(f"Found team: {data.get('name')} (ID: {team_id})")
                    return data
            
            logger.warning(f"Team not found in mapping: {team_name}")
            return None
            
        except Exception as e:
            logger.warning(f"Error searching team: {str(e)}")
            return None
    
    async def get_team_matches(
        self,
        team_id: int,
        status: str = "FINISHED",
        limit: int = 10
    ) -> List[Dict]:
        """
        Get team matches.
        
        Args:
            team_id: Team ID
            status: Match status (SCHEDULED, LIVE, IN_PLAY, PAUSED, FINISHED, etc.)
            limit: Maximum number of matches
            
        Returns:
            List of matches
        """
        try:
            data = await self._make_request(
                f"teams/{team_id}/matches",
                params={"status": status, "limit": limit}
            )
            return data.get("matches", [])
        except Exception as e:
            logger.warning(f"Error fetching team matches: {str(e)}")
            return []
    
    async def get_h2h(self, team1_id: int, team2_id: int, limit: int = 10) -> Dict:
        """
        Get head-to-head statistics.
        
        Args:
            team1_id: First team ID
            team2_id: Second team ID
            limit: Maximum number of matches
            
        Returns:
            H2H data with match history
        """
        try:
            data = await self._make_request(
                f"teams/{team1_id}/matches",
                params={"limit": limit}
            )
            
            matches = data.get("matches", [])
            
            # Filter matches against team2
            h2h_matches = [
                m for m in matches
                if (m.get("homeTeam", {}).get("id") == team2_id or
                    m.get("awayTeam", {}).get("id") == team2_id)
            ]
            
            return {
                "matches": h2h_matches,
                "total": len(h2h_matches)
            }
        except Exception as e:
            logger.warning(f"Error fetching H2H: {str(e)}")
            return {"matches": [], "total": 0}
    
    async def get_standings(self, competition_id: int, season: Optional[int] = None) -> List[Dict]:
        """
        Get competition standings.
        
        Args:
            competition_id: Competition ID (e.g., 2021 for Premier League)
            season: Season year (optional, defaults to current)
            
        Returns:
            List of standings
        """
        try:
            endpoint = f"competitions/{competition_id}/standings"
            params = {"season": season} if season else None
            
            data = await self._make_request(endpoint, params)
            
            standings = data.get("standings", [])
            if standings:
                return standings[0].get("table", [])
            
            return []
        except Exception as e:
            logger.warning(f"Error fetching standings: {str(e)}")
            return []
    
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Football-Data client session closed")


# Competition ID mappings (most popular)
COMPETITION_IDS = {
    "Premier League": 2021,
    "La Liga": 2014,
    "Bundesliga": 2002,
    "Serie A": 2019,
    "Ligue 1": 2015,
    "Eredivisie": 2003,
    "Championship": 2016,
    "Champions League": 2001,
    "Europa League": 2146,
}
