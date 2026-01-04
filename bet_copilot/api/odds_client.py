"""
The Odds API client with circuit breaker and rate limiting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.api.circuit_breaker import CircuitBreaker, CircuitBreakerError
from bet_copilot.config import ODDS_API_KEY, ODDS_API_BASE_URL
from bet_copilot.models.odds import OddsEvent, Bookmaker, Market

logger = logging.getLogger(__name__)


class OddsAPIError(Exception):
    """Base exception for Odds API errors."""

    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class RateLimitError(OddsAPIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status=429)
        self.retry_after = retry_after


class OddsAPIClient:
    """
    Client for The Odds API.
    
    Features:
    - Circuit breaker for resilience
    - Automatic retry with backoff
    - Rate limit handling
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = ODDS_API_BASE_URL,
        timeout: int = 10,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.api_key = api_key or ODDS_API_KEY
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            timeout=60, failure_threshold=3
        )

        if not self.api_key:
            logger.warning("Odds API key not configured")

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request with circuit breaker."""

        async def request_func():
            url = f"{self.base_url}/{endpoint}"
            request_params = {"apiKey": self.api_key, **(params or {})}

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        url, params=request_params, timeout=self.timeout
                    ) as response:
                        # Check rate limit
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 60))
                            logger.error(
                                f"Rate limit exceeded. Retry after {retry_after}s"
                            )
                            raise RateLimitError(
                                "The Odds API rate limit exceeded", retry_after
                            )

                        # Check other errors
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(
                                f"API error {response.status}: {error_text[:200]}"
                            )
                            raise OddsAPIError(
                                f"API error: {error_text[:200]}", response.status
                            )

                        data = await response.json()
                        logger.info(
                            f"Successfully fetched {endpoint} with params {params}"
                        )
                        return data

                except asyncio.TimeoutError:
                    logger.error(f"Request timeout for {endpoint}")
                    raise OddsAPIError("Request timeout")
                except aiohttp.ClientError as e:
                    logger.error(f"Client error: {str(e)}")
                    raise OddsAPIError(f"Client error: {str(e)}")

        try:
            return await self.circuit_breaker.call(request_func)
        except CircuitBreakerError:
            logger.error("Circuit breaker is open")
            raise OddsAPIError("Service temporarily unavailable", status=503)

    async def get_sports(self) -> List[Dict]:
        """Get list of available sports."""
        return await self._make_request("sports")

    async def get_odds(
        self,
        sport_key: str,
        regions: str = "us",
        markets: str = "h2h",
        odds_format: str = "decimal",
    ) -> List[OddsEvent]:
        """
        Get odds for a sport.
        
        Args:
            sport_key: Sport identifier (e.g., "soccer_epl")
            regions: Bookmaker regions
            markets: Market types
            odds_format: Odds format
            
        Returns:
            List of OddsEvent objects
        """
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        }

        data = await self._make_request(f"sports/{sport_key}/odds", params)

        if not isinstance(data, list):
            return []

        events = []
        for event_data in data:
            try:
                events.append(self._parse_event(event_data))
            except Exception as e:
                logger.warning(f"Failed to parse event: {str(e)}")

        return events

    def _parse_event(self, data: Dict) -> OddsEvent:
        """Parse event data into OddsEvent object."""
        bookmakers = []
        for bm_data in data.get("bookmakers", []):
            markets = []
            for market_data in bm_data.get("markets", []):
                outcomes = {}
                for outcome in market_data.get("outcomes", []):
                    outcomes[outcome.get("name")] = outcome.get("price")

                markets.append(
                    Market(
                        key=market_data.get("key"),
                        outcomes=outcomes,
                        last_update=datetime.fromisoformat(
                            market_data.get("last_update", "").replace("Z", "+00:00")
                        ),
                    )
                )

            bookmakers.append(
                Bookmaker(
                    key=bm_data.get("key"),
                    title=bm_data.get("title"),
                    markets=markets,
                    last_update=datetime.fromisoformat(
                        bm_data.get("last_update", "").replace("Z", "+00:00")
                    ),
                )
            )

        return OddsEvent(
            id=data.get("id"),
            sport_key=data.get("sport_key"),
            home_team=data.get("home_team"),
            away_team=data.get("away_team"),
            commence_time=datetime.fromisoformat(
                data.get("commence_time", "").replace("Z", "+00:00")
            ),
            bookmakers=bookmakers,
        )

    async def close(self):
        """Clean up resources."""
        pass
