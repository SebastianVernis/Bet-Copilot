"""
API-Football client with circuit breaker and rate limiting.
Fetches historical stats for football matches.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.api.circuit_breaker import CircuitBreaker, CircuitBreakerError
from bet_copilot.config import API_FOOTBALL_KEY, API_FOOTBALL_BASE_URL

logger = logging.getLogger(__name__)


class FootballAPIError(Exception):
    """Base exception for API-Football errors."""

    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class RateLimitError(FootballAPIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status=429)
        self.retry_after = retry_after


@dataclass
class TeamStats:
    """Statistics for a football team."""

    team_id: int
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    clean_sheets: int
    failed_to_score: int
    avg_goals_for: float
    avg_goals_against: float
    form: str  # e.g., "WWDLW"


@dataclass
class H2HStats:
    """Head-to-head statistics between two teams."""

    matches_played: int
    home_wins: int
    draws: int
    away_wins: int
    last_5_results: List[str]  # ["H", "A", "D", "H", "A"]
    avg_home_goals: float
    avg_away_goals: float


@dataclass
class PlayerStats:
    """Statistics for a player."""

    player_id: int
    player_name: str
    team_id: int
    team_name: str
    position: str  # "Attacker", "Midfielder", "Defender", "Goalkeeper"
    rating: Optional[float] = None  # Average rating
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    shots_total: int = 0
    shots_on_target: int = 0
    passes_total: int = 0
    passes_accuracy: Optional[float] = None
    tackles: int = 0
    duels_won: int = 0
    is_injured: bool = False
    is_suspended: bool = False


@dataclass
class TeamLineup:
    """Expected lineup for a team."""

    team_id: int
    team_name: str
    formation: Optional[str] = None  # e.g., "4-3-3"
    starting_xi: List[PlayerStats] = None
    substitutes: List[PlayerStats] = None
    coach: Optional[str] = None
    missing_players: List[PlayerStats] = None  # Injured/suspended

    def __post_init__(self):
        if self.starting_xi is None:
            self.starting_xi = []
        if self.substitutes is None:
            self.substitutes = []
        if self.missing_players is None:
            self.missing_players = []

    def get_attack_quality(self) -> float:
        """Calculate offensive quality based on attackers' stats."""
        attackers = [p for p in self.starting_xi if p.position == "Attacker"]
        if not attackers:
            return 0.0

        total_rating = sum(p.rating or 0.0 for p in attackers)
        return total_rating / len(attackers)

    def get_defense_quality(self) -> float:
        """Calculate defensive quality based on defenders' stats."""
        defenders = [
            p
            for p in self.starting_xi
            if p.position in ["Defender", "Goalkeeper"]
        ]
        if not defenders:
            return 0.0

        total_rating = sum(p.rating or 0.0 for p in defenders)
        return total_rating / len(defenders)

    def count_missing_key_players(self) -> int:
        """Count missing players with rating > 7.0."""
        return len([p for p in self.missing_players if p.rating and p.rating > 7.0])


@dataclass
class FixtureInfo:
    """Information about a fixture."""

    fixture_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    date: datetime
    league_id: int
    league_name: str
    status: str  # "NS" (not started), "LIVE", "FT" (finished)
    venue: Optional[str] = None


class FootballAPIClient:
    """
    Client for API-Football with circuit breaker and rate limiting.
    
    Rate limits (free plan):
    - 30 requests per minute
    - 100 requests per day
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = API_FOOTBALL_BASE_URL,
        timeout: int = 10,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.api_key = api_key or API_FOOTBALL_KEY
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            timeout=60, failure_threshold=3
        )

        if not self.api_key:
            logger.warning("API-Football key not configured")

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request with circuit breaker protection."""

        async def request_func():
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "v3.football.api-sports.io",
            }

            url = f"{self.base_url}/{endpoint}"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        url, headers=headers, params=params, timeout=self.timeout
                    ) as response:
                        # Check rate limit
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 60))
                            logger.error(
                                f"Rate limit exceeded. Retry after {retry_after}s"
                            )
                            raise RateLimitError(
                                "API-Football rate limit exceeded", retry_after
                            )

                        # Check other errors
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(
                                f"API error {response.status}: {error_text[:200]}"
                            )
                            raise FootballAPIError(
                                f"API error: {error_text[:200]}", response.status
                            )

                        data = await response.json()

                        # API-Football wraps response
                        if "errors" in data and data["errors"]:
                            error_msg = str(data["errors"])
                            logger.error(f"API returned errors: {error_msg}")
                            raise FootballAPIError(f"API error: {error_msg}")

                        logger.info(
                            f"Successfully fetched {endpoint} with params {params}"
                        )
                        return data

                except asyncio.TimeoutError:
                    logger.error(f"Request timeout for {endpoint}")
                    raise FootballAPIError("Request timeout")
                except aiohttp.ClientError as e:
                    logger.error(f"Client error: {str(e)}")
                    raise FootballAPIError(f"Client error: {str(e)}")

        try:
            return await self.circuit_breaker.call(request_func)
        except CircuitBreakerError:
            logger.error("Circuit breaker is open")
            raise FootballAPIError("Service temporarily unavailable", status=503)

    async def get_team_stats(
        self, team_id: int, season: int, league_id: int
    ) -> TeamStats:
        """
        Get team statistics for a season.
        
        Args:
            team_id: Team ID
            season: Year (e.g., 2024)
            league_id: League ID (e.g., 39 for Premier League)
            
        Returns:
            TeamStats object
        """
        params = {"team": team_id, "season": season, "league": league_id}

        data = await self._make_request("teams/statistics", params)

        response = data.get("response", {})
        fixtures = response.get("fixtures", {})
        goals = response.get("goals", {})
        clean_sheet = response.get("clean_sheet", {})
        failed_to_score = response.get("failed_to_score", {})

        matches_played = fixtures.get("played", {}).get("total", 0)
        wins = fixtures.get("wins", {}).get("total", 0)
        draws = fixtures.get("draws", {}).get("total", 0)
        losses = fixtures.get("loses", {}).get("total", 0)
        goals_for = goals.get("for", {}).get("total", {}).get("total", 0)
        goals_against = goals.get("against", {}).get("total", {}).get("total", 0)

        avg_goals_for = goals_for / matches_played if matches_played > 0 else 0.0
        avg_goals_against = (
            goals_against / matches_played if matches_played > 0 else 0.0
        )

        # Extract form (last 5 matches)
        form_str = response.get("form", "")
        form = "".join(form_str.split("%")[:5]) if form_str else ""

        return TeamStats(
            team_id=team_id,
            team_name=response.get("team", {}).get("name", "Unknown"),
            matches_played=matches_played,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            clean_sheets=clean_sheet.get("total", 0),
            failed_to_score=failed_to_score.get("total", 0),
            avg_goals_for=avg_goals_for,
            avg_goals_against=avg_goals_against,
            form=form,
        )

    async def get_h2h_stats(self, team1_id: int, team2_id: int, last_n: int = 10) -> H2HStats:
        """
        Get head-to-head statistics between two teams.
        
        Args:
            team1_id: First team ID (home)
            team2_id: Second team ID (away)
            last_n: Number of last matches to consider
            
        Returns:
            H2HStats object
        """
        params = {"h2h": f"{team1_id}-{team2_id}", "last": last_n}

        data = await self._make_request("fixtures/headtohead", params)

        fixtures = data.get("response", [])

        if not fixtures:
            return H2HStats(
                matches_played=0,
                home_wins=0,
                draws=0,
                away_wins=0,
                last_5_results=[],
                avg_home_goals=0.0,
                avg_away_goals=0.0,
            )

        home_wins = 0
        draws = 0
        away_wins = 0
        total_home_goals = 0
        total_away_goals = 0
        last_5_results = []

        for fixture in fixtures[:last_n]:
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            score = fixture.get("score", {})

            home_id = teams.get("home", {}).get("id")
            away_id = teams.get("away", {}).get("id")
            home_goals = goals.get("home", 0) or 0
            away_goals = goals.get("away", 0) or 0

            # Determine winner (from team1 perspective)
            if home_id == team1_id:
                total_home_goals += home_goals
                total_away_goals += away_goals

                if home_goals > away_goals:
                    home_wins += 1
                    last_5_results.append("H")
                elif home_goals < away_goals:
                    away_wins += 1
                    last_5_results.append("A")
                else:
                    draws += 1
                    last_5_results.append("D")
            else:  # team1 was away
                total_home_goals += away_goals
                total_away_goals += home_goals

                if away_goals > home_goals:
                    home_wins += 1
                    last_5_results.append("H")
                elif away_goals < home_goals:
                    away_wins += 1
                    last_5_results.append("A")
                else:
                    draws += 1
                    last_5_results.append("D")

        matches_played = len(fixtures)
        avg_home_goals = total_home_goals / matches_played if matches_played > 0 else 0.0
        avg_away_goals = total_away_goals / matches_played if matches_played > 0 else 0.0

        return H2HStats(
            matches_played=matches_played,
            home_wins=home_wins,
            draws=draws,
            away_wins=away_wins,
            last_5_results=last_5_results[:5],
            avg_home_goals=avg_home_goals,
            avg_away_goals=avg_away_goals,
        )

    async def get_upcoming_fixtures(
        self, league_id: int, season: int, next_n: int = 10
    ) -> List[FixtureInfo]:
        """
        Get upcoming fixtures for a league.
        
        Args:
            league_id: League ID
            season: Season year
            next_n: Number of fixtures to retrieve
            
        Returns:
            List of FixtureInfo objects
        """
        params = {"league": league_id, "season": season, "next": next_n}

        data = await self._make_request("fixtures", params)

        fixtures_data = data.get("response", [])
        fixtures = []

        for fixture_data in fixtures_data:
            fixture_info = fixture_data.get("fixture", {})
            teams = fixture_data.get("teams", {})
            league = fixture_data.get("league", {})

            fixtures.append(
                FixtureInfo(
                    fixture_id=fixture_info.get("id"),
                    home_team_id=teams.get("home", {}).get("id"),
                    home_team_name=teams.get("home", {}).get("name", "Unknown"),
                    away_team_id=teams.get("away", {}).get("id"),
                    away_team_name=teams.get("away", {}).get("name", "Unknown"),
                    date=datetime.fromisoformat(
                        fixture_info.get("date", "").replace("Z", "+00:00")
                    ),
                    league_id=league.get("id"),
                    league_name=league.get("name", "Unknown"),
                    status=fixture_info.get("status", {}).get("short", "NS"),
                    venue=fixture_info.get("venue", {}).get("name"),
                )
            )

        return fixtures

    async def get_team_players(
        self, team_id: int, season: int
    ) -> List[PlayerStats]:
        """
        Get players for a team in a season.
        
        Args:
            team_id: Team ID
            season: Season year
            
        Returns:
            List of PlayerStats
        """
        params = {"team": team_id, "season": season}

        data = await self._make_request("players", params)

        players_data = data.get("response", [])
        players = []

        for player_data in players_data[:25]:  # Limit to top 25 players
            player_info = player_data.get("player", {})
            statistics = player_data.get("statistics", [{}])[0]

            games = statistics.get("games", {})
            goals_data = statistics.get("goals", {})
            passes = statistics.get("passes", {})
            tackles_data = statistics.get("tackles", {})
            duels_data = statistics.get("duels", {})
            shots = statistics.get("shots", {})

            players.append(
                PlayerStats(
                    player_id=player_info.get("id", 0),
                    player_name=player_info.get("name", "Unknown"),
                    team_id=team_id,
                    team_name=statistics.get("team", {}).get("name", "Unknown"),
                    position=games.get("position", "Unknown"),
                    rating=float(games.get("rating") or 0.0) if games.get("rating") else None,
                    minutes_played=games.get("minutes") or 0,
                    goals=goals_data.get("total") or 0,
                    assists=goals_data.get("assists") or 0,
                    shots_total=shots.get("total") or 0,
                    shots_on_target=shots.get("on") or 0,
                    passes_total=passes.get("total") or 0,
                    passes_accuracy=passes.get("accuracy"),
                    tackles=tackles_data.get("total") or 0,
                    duels_won=duels_data.get("won") or 0,
                )
            )

        return players

    async def get_team_injuries(
        self, team_id: int, season: int, league_id: int
    ) -> List[PlayerStats]:
        """
        Get injured/suspended players for a team.
        
        Args:
            team_id: Team ID
            season: Season year
            league_id: League ID
            
        Returns:
            List of injured/suspended PlayerStats
        """
        params = {"team": team_id, "season": season, "league": league_id}

        try:
            data = await self._make_request("injuries", params)
        except FootballAPIError:
            # Injuries endpoint might not be available
            logger.warning(f"Could not fetch injuries for team {team_id}")
            return []

        injuries_data = data.get("response", [])
        injured_players = []

        for injury_data in injuries_data:
            player_info = injury_data.get("player", {})
            injury_type = injury_data.get("type", "Injury")

            injured_players.append(
                PlayerStats(
                    player_id=player_info.get("id", 0),
                    player_name=player_info.get("name", "Unknown"),
                    team_id=team_id,
                    team_name="",
                    position="Unknown",
                    is_injured=(injury_type == "Injury"),
                    is_suspended=(injury_type == "Suspension"),
                )
            )

        return injured_players

    async def search_team_by_name(self, team_name: str) -> Optional[int]:
        """
        Search for team ID by name.
        
        Args:
            team_name: Team name to search
            
        Returns:
            Team ID or None if not found
        """
        params = {"search": team_name}

        try:
            data = await self._make_request("teams", params)
            teams = data.get("response", [])

            if teams:
                # Return first match
                team_id = teams[0].get("team", {}).get("id")
                found_name = teams[0].get("team", {}).get("name")
                logger.info(f"Found team: {found_name} (ID: {team_id})")
                return team_id

            logger.warning(f"No team found for: {team_name}")
            return None

        except FootballAPIError as e:
            logger.error(f"Error searching team: {str(e)}")
            return None

    async def close(self):
        """Clean up resources."""
        pass
