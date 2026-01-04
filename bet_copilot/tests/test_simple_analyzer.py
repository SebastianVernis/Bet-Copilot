"""
Tests for SimpleAnalyzer (rule-based fallback).
"""

import pytest
from bet_copilot.ai.simple_analyzer import SimpleAnalyzer


class TestSimpleAnalyzer:
    """Test suite for SimpleAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return SimpleAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.is_available() is True
    
    def test_calculate_form_score_all_wins(self, analyzer):
        """Test form score calculation with all wins."""
        score = analyzer._calculate_form_score("WWWWW")
        assert score == 1.0
    
    def test_calculate_form_score_all_losses(self, analyzer):
        """Test form score calculation with all losses."""
        score = analyzer._calculate_form_score("LLLLL")
        assert score == 0.0
    
    def test_calculate_form_score_mixed(self, analyzer):
        """Test form score calculation with mixed results."""
        score = analyzer._calculate_form_score("WWDLW")
        # W=3, W=3, D=1, L=0, W=3 → 10/15 = 0.667
        assert 0.6 < score < 0.7
    
    def test_calculate_form_score_empty(self, analyzer):
        """Test form score with empty string."""
        score = analyzer._calculate_form_score("")
        assert score == 0.5  # Neutral
    
    def test_analyze_h2h_home_dominance(self, analyzer):
        """Test H2H analysis with home dominance."""
        h2h = ["H", "H", "H", "D", "D"]
        factor = analyzer._analyze_h2h(h2h)
        assert factor > 0.4  # 3 home wins out of 5
    
    def test_analyze_h2h_away_dominance(self, analyzer):
        """Test H2H analysis with away dominance."""
        h2h = ["A", "A", "A", "D", "H"]
        factor = analyzer._analyze_h2h(h2h)
        assert factor < -0.2  # More away wins
    
    def test_analyze_h2h_balanced(self, analyzer):
        """Test H2H analysis with balanced results."""
        h2h = ["H", "A", "D", "H", "A"]
        factor = analyzer._analyze_h2h(h2h)
        assert -0.1 < factor < 0.1  # Close to neutral
    
    def test_analyze_context_injuries(self, analyzer):
        """Test context analysis for injuries."""
        context = "Arsenal sin Saka (lesionado). Odegaard también lesión."
        factors = analyzer._analyze_context(context)
        # Should detect injuries (currently defaults to home_injuries)
        assert len(factors) > 0
        assert 'home_injuries' in factors or 'away_injuries' in factors or factors.get('home_injuries', 0) >= 1
    
    @pytest.mark.asyncio
    async def test_analyze_match_basic(self, analyzer):
        """Test basic match analysis."""
        analysis = await analyzer.analyze_match_context(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWWWW",
            away_form="LLLLL",
            h2h_results=["H", "H", "H", "D", "A"],
        )
        
        assert analysis.home_team == "Arsenal"
        assert analysis.away_team == "Chelsea"
        assert analysis.confidence > 0.5
        assert analysis.lambda_adjustment_home > 1.0  # Strong home form
        assert analysis.lambda_adjustment_away < 1.0  # Weak away form
        assert len(analysis.key_factors) > 0
        assert analysis.sentiment in ["POSITIVE", "NEUTRAL", "NEGATIVE"]
    
    @pytest.mark.asyncio
    async def test_analyze_match_with_context(self, analyzer):
        """Test match analysis with additional context."""
        analysis = await analyzer.analyze_match_context(
            home_team="Barcelona",
            away_team="Real Madrid",
            home_form="WWDLW",
            away_form="DWLWW",
            h2h_results=["H", "A", "D", "H", "A"],
            additional_context="Barcelona sin Lewandowski (lesionado)"
        )
        
        assert analysis.home_team == "Barcelona"
        assert analysis.confidence >= 0.6  # Has context data
        # Should have detected injury in key factors or reasoning
        has_injury_mention = (
            any("lesion" in f.lower() or "baja" in f.lower() or "injured" in f.lower() 
                for f in analysis.key_factors) or
            "lesion" in analysis.reasoning.lower() or 
            "baja" in analysis.reasoning.lower()
        )
        assert has_injury_mention or analysis.lambda_adjustment_home < 1.0  # Adjustment for injuries
    
    @pytest.mark.asyncio
    async def test_adjustments_clamped(self, analyzer):
        """Test that adjustments are clamped to reasonable range."""
        # Extreme form difference
        analysis = await analyzer.analyze_match_context(
            home_team="Team A",
            away_team="Team B",
            home_form="WWWWW",
            away_form="LLLLL",
            h2h_results=["H", "H", "H", "H", "H"],
        )
        
        # Even with extreme data, should be clamped
        assert 0.8 <= analysis.lambda_adjustment_home <= 1.2
        assert 0.8 <= analysis.lambda_adjustment_away <= 1.2
    
    @pytest.mark.asyncio
    async def test_neutral_when_no_data(self, analyzer):
        """Test neutral analysis when no data available."""
        analysis = await analyzer.analyze_match_context(
            home_team="Team A",
            away_team="Team B",
            home_form="",
            away_form="",
        )
        
        assert analysis.confidence >= 0.5  # Still has base confidence
        assert abs(analysis.lambda_adjustment_home - 1.0) < 0.15
        assert abs(analysis.lambda_adjustment_away - 1.0) < 0.15
    
    @pytest.mark.asyncio
    async def test_is_always_available(self, analyzer):
        """Test that simple analyzer is always available."""
        assert analyzer.is_available() is True
    
    @pytest.mark.asyncio
    async def test_close_no_error(self, analyzer):
        """Test close doesn't raise error."""
        await analyzer.close()  # Should not raise
