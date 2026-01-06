"""
Tests for Gemini AI client.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bet_copilot.ai.gemini_client import GeminiClient, GEMINI_AVAILABLE
from bet_copilot.ai.types import ContextualAnalysis


class TestGeminiClient:
    """Test Gemini AI client."""

    def setup_method(self):
        """Setup test fixtures."""
        self.client = GeminiClient(api_key="test_key")

    def test_initialization(self):
        """Test client initialization."""
        assert self.client.api_key == "test_key"
        assert self.client.model_name == "gemini-2.0-flash-exp"

    def test_is_available(self):
        """Test availability check."""
        # Should return False if not configured or module not installed
        if not GEMINI_AVAILABLE:
            assert self.client.is_available() is False

    @pytest.mark.asyncio
    async def test_neutral_analysis(self):
        """Test neutral analysis fallback."""
        analysis = self.client._neutral_analysis("Arsenal", "Chelsea")

        assert isinstance(analysis, ContextualAnalysis)
        assert analysis.home_team == "Arsenal"
        assert analysis.away_team == "Chelsea"
        assert analysis.lambda_adjustment_home == 1.0
        assert analysis.lambda_adjustment_away == 1.0
        assert analysis.confidence == 0.5
        assert analysis.sentiment == "NEUTRAL"

    @pytest.mark.asyncio
    async def test_analyze_without_gemini(self):
        """Test analysis without Gemini available."""
        # Mock is_available to return False
        self.client.model = None

        analysis = await self.client.analyze_match_context(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWWDL",
            away_form="WDLWW",
        )

        # Should return neutral analysis
        assert analysis.lambda_adjustment_home == 1.0
        assert analysis.lambda_adjustment_away == 1.0

    def test_parse_valid_response(self):
        """Test parsing valid Gemini response."""
        response_text = '''
        Here's my analysis:
        
        {
            "home_adjustment": 1.1,
            "away_adjustment": 0.9,
            "confidence": 0.8,
            "key_factors": ["Home advantage", "Better form"],
            "sentiment": "POSITIVE",
            "reasoning": "Home team has momentum"
        }
        '''

        analysis = self.client._parse_response(response_text, "Arsenal", "Chelsea")

        assert analysis.lambda_adjustment_home == 1.1
        assert analysis.lambda_adjustment_away == 0.9
        assert analysis.confidence == 0.8
        assert len(analysis.key_factors) == 2
        assert analysis.sentiment == "POSITIVE"

    def test_parse_invalid_response(self):
        """Test parsing invalid response."""
        response_text = "This is not valid JSON"

        analysis = self.client._parse_response(response_text, "Arsenal", "Chelsea")

        # Should fall back to neutral
        assert analysis.lambda_adjustment_home == 1.0
        assert analysis.lambda_adjustment_away == 1.0

    def test_build_analysis_prompt(self):
        """Test prompt building."""
        prompt = self.client._build_analysis_prompt(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWWDL",
            away_form="WDLWW",
            h2h_results=["H", "A", "D"],
            additional_context="Arsenal missing key striker",
        )

        assert "Arsenal" in prompt
        assert "Chelsea" in prompt
        assert "WWWDL" in prompt
        assert "missing key striker" in prompt
        assert "H, A, D" in prompt

    @pytest.mark.asyncio
    async def test_analyze_multiple_matches(self):
        """Test analyzing multiple matches."""
        matches = [
            {
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "home_form": "WWW",
                "away_form": "DDD",
            },
            {
                "home_team": "Liverpool",
                "away_team": "Man City",
                "home_form": "WWD",
                "away_form": "WWW",
            },
        ]

        # Mock analyze_match_context
        with patch.object(
            self.client,
            "analyze_match_context",
            side_effect=[
                self.client._neutral_analysis("Arsenal", "Chelsea"),
                self.client._neutral_analysis("Liverpool", "Man City"),
            ],
        ):
            results = await self.client.analyze_multiple_matches(matches)

            assert len(results) == 2
            assert all(isinstance(r, ContextualAnalysis) for r in results)
