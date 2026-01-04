"""
Tests for Football client with fallback.
"""

import pytest
from bet_copilot.api.football_client_with_fallback import (
    FootballClientWithFallback,
    create_football_client
)
from bet_copilot.api.simple_football_data import SimpleFootballDataProvider


class TestSimpleFootballDataProvider:
    """Test suite for SimpleFootballDataProvider."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return SimpleFootballDataProvider(league="Premier League")
    
    def test_initialization(self, provider):
        """Test provider initialization."""
        assert provider.league == "Premier League"
        assert provider.is_available() is True
    
    def test_estimate_team_tier_1(self, provider):
        """Test tier 1 team estimation."""
        assert provider._estimate_team_tier("Manchester City") == 1
        assert provider._estimate_team_tier("Barcelona") == 1
        assert provider._estimate_team_tier("Bayern Munich") == 1
    
    def test_estimate_team_tier_2(self, provider):
        """Test tier 2 team estimation."""
        assert provider._estimate_team_tier("Tottenham") == 2
        assert provider._estimate_team_tier("Sevilla") == 2
        assert provider._estimate_team_tier("Napoli") == 2
    
    def test_estimate_team_tier_3(self, provider):
        """Test tier 3 team estimation."""
        assert provider._estimate_team_tier("Unknown Team FC") == 3
        assert provider._estimate_team_tier("Random Team") == 3
    
    @pytest.mark.asyncio
    async def test_get_team_stats_tier1(self, provider):
        """Test team stats for tier 1 team."""
        stats = await provider.get_team_stats(1, "Arsenal", 39, 2024)
        
        assert stats.team_name == "Arsenal"
        assert stats.matches_played == 20
        assert stats.wins > stats.losses  # Tier 1 should have more wins
        assert stats.avg_goals_for > 2.0  # Tier 1 scores more
        assert stats.avg_goals_against < 2.0  # Tier 1 concedes less
        assert "W" in stats.form
    
    @pytest.mark.asyncio
    async def test_get_team_stats_tier3(self, provider):
        """Test team stats for tier 3 team."""
        stats = await provider.get_team_stats(999, "Small Team FC", 39, 2024)
        
        assert stats.team_name == "Small Team FC"
        assert stats.losses >= stats.wins  # Tier 3 has more losses
        assert stats.avg_goals_for < 2.0  # Scores less
        assert stats.avg_goals_against > 2.0  # Concedes more
    
    @pytest.mark.asyncio
    async def test_get_h2h_balanced(self, provider):
        """Test H2H for similarly ranked teams."""
        h2h = await provider.get_h2h(1, 2, "Arsenal", "Chelsea", 10)
        
        assert h2h.home_team == "Arsenal"
        assert h2h.away_team == "Chelsea"
        assert h2h.matches_played == 5
        assert h2h.home_wins + h2h.draws + h2h.away_wins == 5
        assert len(h2h.last_5_results) <= 5
    
    @pytest.mark.asyncio
    async def test_get_h2h_tier_difference(self, provider):
        """Test H2H with tier difference."""
        # Tier 1 vs Tier 3
        h2h = await provider.get_h2h(1, 999, "Manchester City", "Small Team", 10)
        
        # Stronger team should have more wins
        assert h2h.home_wins > h2h.away_wins
    
    @pytest.mark.asyncio
    async def test_get_team_lineup(self, provider):
        """Test lineup generation."""
        lineup = await provider.get_team_lineup(1, "Arsenal")
        
        assert lineup.team_name == "Arsenal"
        assert lineup.formation == "4-3-3"
        assert lineup.missing_players == []
    
    @pytest.mark.asyncio
    async def test_search_team_by_name(self, provider):
        """Test team search."""
        team_id = await provider.search_team_by_name("Arsenal", 39)
        
        assert team_id is not None
        assert isinstance(team_id, int)
        
        # Same name should return same ID
        team_id2 = await provider.search_team_by_name("Arsenal", 39)
        assert team_id == team_id2


class TestFootballClientWithFallback:
    """Test suite for FootballClientWithFallback."""
    
    def test_create_football_client(self):
        """Test factory function."""
        client = create_football_client()
        assert client is not None
        assert isinstance(client, FootballClientWithFallback)
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        client = create_football_client(api_key="test_key")
        assert client.use_api is True
        assert client.get_active_provider() == "API-Football"
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        client = create_football_client(api_key=None)
        assert client.use_api is False
        assert client.get_active_provider() == "SimpleProvider"
    
    def test_is_always_available(self):
        """Test that client is always available."""
        client = create_football_client()
        assert client.is_available() is True
        
        client2 = create_football_client(api_key=None)
        assert client2.is_available() is True
    
    @pytest.mark.asyncio
    async def test_get_team_stats_with_simple_provider(self):
        """Test getting stats with simple provider."""
        client = create_football_client(api_key=None)
        
        stats = await client.get_team_stats(1, "Arsenal", 39, 2024)
        
        assert stats is not None
        assert stats.team_name == "Arsenal"
        assert stats.matches_played > 0
        assert stats.avg_goals_for > 0
    
    @pytest.mark.asyncio
    async def test_get_h2h_with_simple_provider(self):
        """Test getting H2H with simple provider."""
        client = create_football_client(api_key=None)
        
        h2h = await client.get_h2h(1, 2, "Arsenal", "Chelsea", 10)
        
        assert h2h is not None
        assert h2h.matches_played > 0
        assert h2h.team1_wins + h2h.draws + h2h.team2_wins == h2h.matches_played
    
    @pytest.mark.asyncio
    async def test_get_lineup_with_simple_provider(self):
        """Test getting lineup with simple provider."""
        client = create_football_client(api_key=None)
        
        lineup = await client.get_team_lineup(1, "Arsenal")
        
        assert lineup is not None
        assert lineup.team_name == "Arsenal"
        assert lineup.formation is not None
    
    @pytest.mark.asyncio
    async def test_close_no_error(self):
        """Test closing client."""
        client = create_football_client()
        await client.close()  # Should not raise
