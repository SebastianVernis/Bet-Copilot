"""
Tests for unified AI client with fallback.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from bet_copilot.ai.ai_client import AIClient, create_ai_client
from bet_copilot.ai.simple_analyzer import ContextualAnalysis


class TestAIClient:
    """Test suite for AIClient."""
    
    def test_create_ai_client(self):
        """Test factory function."""
        client = create_ai_client()
        assert client is not None
        assert isinstance(client, AIClient)
    
    def test_is_always_available(self):
        """Test that at least SimpleAnalyzer is always available."""
        client = create_ai_client()
        assert client.is_available() is True
    
    def test_get_active_provider(self):
        """Test get active provider name."""
        client = create_ai_client()
        provider = client.get_active_provider()
        assert provider in ["Gemini", "Blackbox", "SimpleAnalyzer"]
    
    def test_fallback_chain_exists(self):
        """Test fallback chain is created."""
        client = create_ai_client()
        assert hasattr(client, 'fallback_chain')
        assert isinstance(client.fallback_chain, list)
        # Should have at least SimpleAnalyzer
        assert len(client.fallback_chain) >= 1
    
    def test_prefer_gemini_true(self):
        """Test prefer_gemini parameter."""
        client = create_ai_client(prefer_gemini=True)
        # Should try Gemini first if available
        assert client.primary_name in ["Gemini", "SimpleAnalyzer"]
    
    def test_prefer_gemini_false(self):
        """Test prefer_gemini=False uses Blackbox."""
        client = create_ai_client(prefer_gemini=False)
        # Should prefer Blackbox or SimpleAnalyzer
        assert client.primary_name in ["Blackbox", "SimpleAnalyzer"]
    
    @pytest.mark.asyncio
    async def test_analyze_with_simple_analyzer(self):
        """Test analysis falls through to SimpleAnalyzer."""
        # Force SimpleAnalyzer by not configuring keys
        client = create_ai_client(
            gemini_api_key=None,
            blackbox_api_key=None,
        )
        
        analysis = await client.analyze_match_context(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWWWW",
            away_form="LLLLL",
        )
        
        assert analysis is not None
        assert analysis.home_team == "Arsenal"
        assert analysis.away_team == "Chelsea"
        assert analysis.confidence > 0.0
        assert 0.8 <= analysis.lambda_adjustment_home <= 1.2
        assert 0.8 <= analysis.lambda_adjustment_away <= 1.2
    
    @pytest.mark.asyncio
    async def test_analyze_returns_valid_result(self):
        """Test that analysis always returns valid result."""
        client = create_ai_client()
        
        analysis = await client.analyze_match_context(
            home_team="Team A",
            away_team="Team B",
            home_form="WWDLW",
            away_form="DWLWW",
        )
        
        # Should always return valid analysis (never None)
        assert analysis is not None
        assert isinstance(analysis, ContextualAnalysis)
        assert analysis.confidence >= 0.0
        assert analysis.lambda_adjustment_home > 0.0
        assert analysis.lambda_adjustment_away > 0.0
    
    @pytest.mark.asyncio
    async def test_close_no_error(self):
        """Test close doesn't raise error."""
        client = create_ai_client()
        await client.close()  # Should not raise
