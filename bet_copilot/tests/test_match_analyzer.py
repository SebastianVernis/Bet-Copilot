"""
Tests for MatchAnalyzer service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from bet_copilot.services.match_analyzer import MatchAnalyzer, EnhancedMatchAnalysis
from bet_copilot.api.football_client import TeamStats, H2HStats, PlayerStats, TeamLineup
from bet_copilot.models.soccer import MatchPrediction


class TestEnhancedMatchAnalysis:
    """Test EnhancedMatchAnalysis model."""

    def test_get_best_value_bet_with_values(self):
        """Test getting best value bet when value exists."""
        from bet_copilot.math_engine.kelly import KellyRecommendation

        analysis = EnhancedMatchAnalysis(
            home_team="Arsenal",
            away_team="Chelsea",
            league="EPL",
            commence_time=datetime.now(),
        )

        # Mock Kelly recommendations
        analysis.kelly_home = KellyRecommendation(
            model_prob=0.6,
            odds=2.0,
            ev=0.2,
            full_kelly=20.0,
            fractional_kelly=5.0,
            recommended_stake=5.0,
            is_value_bet=True,
            risk_level="MEDIUM",
        )

        analysis.kelly_away = KellyRecommendation(
            model_prob=0.3,
            odds=3.0,
            ev=0.1,
            full_kelly=10.0,
            fractional_kelly=2.5,
            recommended_stake=2.5,
            is_value_bet=True,
            risk_level="LOW",
        )

        best = analysis.get_best_value_bet()

        assert best is not None
        assert best["outcome"] == "Victoria Local"  # Higher EV
        assert best["ev"] == 0.2

    def test_get_best_value_bet_none(self):
        """Test when no value bets exist."""
        analysis = EnhancedMatchAnalysis(
            home_team="Arsenal",
            away_team="Chelsea",
            league="EPL",
            commence_time=datetime.now(),
        )

        best = analysis.get_best_value_bet()
        assert best is None

    def test_get_key_insights_form(self):
        """Test insights from team form."""
        analysis = EnhancedMatchAnalysis(
            home_team="Arsenal",
            away_team="Chelsea",
            league="EPL",
            commence_time=datetime.now(),
        )

        # Good home form
        analysis.home_stats = TeamStats(
            team_id=1,
            team_name="Arsenal",
            matches_played=10,
            wins=7,
            draws=2,
            losses=1,
            goals_for=25,
            goals_against=10,
            clean_sheets=4,
            failed_to_score=1,
            avg_goals_for=2.5,
            avg_goals_against=1.0,
            form="WWWDW",
        )

        # Bad away form
        analysis.away_stats = TeamStats(
            team_id=2,
            team_name="Chelsea",
            matches_played=10,
            wins=2,
            draws=3,
            losses=5,
            goals_for=10,
            goals_against=15,
            clean_sheets=1,
            failed_to_score=3,
            avg_goals_for=1.0,
            avg_goals_against=1.5,
            form="LLLWL",
        )

        insights = analysis.get_key_insights()

        assert len(insights) >= 2
        assert any("buena racha" in i.lower() for i in insights)
        assert any("mala racha" in i.lower() for i in insights)

    def test_get_key_insights_injuries(self):
        """Test insights from missing players."""
        analysis = EnhancedMatchAnalysis(
            home_team="Arsenal",
            away_team="Chelsea",
            league="EPL",
            commence_time=datetime.now(),
        )

        # Home team missing key player
        injured_player = PlayerStats(
            player_id=1,
            player_name="Star Player",
            team_id=1,
            team_name="Arsenal",
            position="Attacker",
            rating=8.5,
            is_injured=True,
        )

        analysis.home_lineup = TeamLineup(
            team_id=1,
            team_name="Arsenal",
            missing_players=[injured_player],
        )

        insights = analysis.get_key_insights()

        assert any("sin" in i.lower() and "jugador" in i.lower() for i in insights)


class TestMatchAnalyzer:
    """Test MatchAnalyzer service."""

    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = MatchAnalyzer()

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.odds_client is not None
        assert self.analyzer.football_client is not None
        assert self.analyzer.gemini_client is not None
        assert self.analyzer.soccer_predictor is not None
        assert self.analyzer.kelly is not None

    @pytest.mark.asyncio
    async def test_analyze_match_without_apis(self):
        """Test analysis when APIs are not available."""
        # Mock all API calls to fail
        with patch.object(
            self.analyzer.football_client, "search_team_by_name", return_value=None
        ):
            analysis = await self.analyzer.analyze_match(
                "Arsenal", "Chelsea", include_players=False, include_ai_analysis=False
            )

            assert isinstance(analysis, EnhancedMatchAnalysis)
            assert analysis.home_team == "Arsenal"
            assert analysis.away_team == "Chelsea"
            # Should have partial data even if APIs fail
