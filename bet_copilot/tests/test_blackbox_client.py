"""
Tests for BlackboxClient.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bet_copilot.ai.blackbox_client import BlackboxClient
from bet_copilot.ai.types import ContextualAnalysis


class TestBlackboxClient:
    """Test suite for BlackboxClient."""
    
    @pytest.fixture
    def client(self):
        """Create client instance."""
        return BlackboxClient(api_key="test_key")
    
    def test_initialization_with_key(self):
        """Test client initialization with API key."""
        client = BlackboxClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model == "blackboxai/anthropic/claude-sonnet-4"
        assert client.API_URL == "https://api.blackbox.ai/chat/completions"
    
    @patch('bet_copilot.ai.blackbox_client.BLACKBOX_API_KEY', '')
    def test_initialization_without_key(self):
        """Test client initialization without API key."""
        # Mock empty config and pass empty string
        client = BlackboxClient(api_key="")
        assert client.api_key == ""
        assert client.is_available() is True  # Still available
    
    def test_is_available(self, client):
        """Test availability check."""
        assert client.is_available() is True
    
    def test_build_analysis_prompt(self, client):
        """Test prompt building."""
        prompt = client._build_analysis_prompt(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWWWW",
            away_form="LLLLL",
            h2h_results=["H", "A", "D"],
            additional_context="Test context"
        )
        
        assert "Arsenal" in prompt
        assert "Chelsea" in prompt
        assert "WWWWW" in prompt
        assert "LLLLL" in prompt
        assert "Test context" in prompt
        assert "JSON" in prompt
        assert "home_adjustment" in prompt
    
    def test_parse_response_valid_json(self, client):
        """Test parsing valid JSON response."""
        response = """{
            "home_adjustment": 1.1,
            "away_adjustment": 0.9,
            "confidence": 0.75,
            "key_factors": ["Good form", "H2H advantage"],
            "sentiment": "POSITIVE",
            "reasoning": "Home team is stronger"
        }"""
        
        analysis = client._parse_response(response, "Arsenal", "Chelsea")
        
        assert analysis.home_team == "Arsenal"
        assert analysis.away_team == "Chelsea"
        assert analysis.lambda_adjustment_home == 1.1
        assert analysis.lambda_adjustment_away == 0.9
        assert analysis.confidence == 0.75
        assert len(analysis.key_factors) == 2
        assert analysis.sentiment == "POSITIVE"
    
    def test_parse_response_with_extra_text(self, client):
        """Test parsing JSON with extra text around it."""
        response = """Here's my analysis:
        
        {
            "home_adjustment": 1.05,
            "away_adjustment": 1.0,
            "confidence": 0.6,
            "key_factors": ["Recent form"],
            "sentiment": "NEUTRAL",
            "reasoning": "Close match"
        }
        
        Hope this helps!"""
        
        analysis = client._parse_response(response, "Team A", "Team B")
        
        assert analysis.lambda_adjustment_home == 1.05
        assert analysis.lambda_adjustment_away == 1.0
    
    def test_parse_response_invalid(self, client):
        """Test parsing invalid response returns neutral."""
        response = "This is not JSON at all"
        
        analysis = client._parse_response(response, "Team A", "Team B")
        
        # Should return neutral analysis
        assert analysis.lambda_adjustment_home == 1.0
        assert analysis.lambda_adjustment_away == 1.0
        assert analysis.confidence == 0.5
    
    def test_neutral_analysis(self, client):
        """Test neutral analysis creation."""
        analysis = client._neutral_analysis("Home", "Away")
        
        assert analysis.home_team == "Home"
        assert analysis.away_team == "Away"
        assert analysis.lambda_adjustment_home == 1.0
        assert analysis.lambda_adjustment_away == 1.0
        assert analysis.confidence == 0.5
        assert analysis.sentiment == "NEUTRAL"
    
    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test closing client session."""
        # Create session
        await client._get_session()
        assert client.session is not None
        
        # Close it
        await client.close()
        assert client.session.closed is True
    
    @pytest.mark.asyncio
    async def test_analyze_match_with_mock_response(self, client):
        """Test full analysis with mocked API response."""
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": """{
                            "home_adjustment": 1.1,
                            "away_adjustment": 0.95,
                            "confidence": 0.7,
                            "key_factors": ["Form advantage"],
                            "sentiment": "POSITIVE",
                            "reasoning": "Home team stronger"
                        }"""
                    }
                }
            ]
        }
        
        # Mock the API call
        with patch.object(client, '_generate_response', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response_data['choices'][0]['message']['content']
            
            analysis = await client.analyze_match_context(
                home_team="Arsenal",
                away_team="Chelsea",
                home_form="WWWWW",
                away_form="LLLLL",
            )
            
            assert analysis.lambda_adjustment_home == 1.1
            assert analysis.lambda_adjustment_away == 0.95
            assert analysis.confidence == 0.7
            assert "Form advantage" in analysis.key_factors
