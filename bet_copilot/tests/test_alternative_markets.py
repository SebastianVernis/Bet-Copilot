"""
Tests for alternative markets predictor.
"""

import pytest
from datetime import datetime, timedelta

from bet_copilot.math_engine.alternative_markets import (
    AlternativeMarketsPredictor,
    AlternativeMarketPrediction,
)
from bet_copilot.models.soccer import TeamForm, MatchResult


class TestAlternativeMarketsPredictor:
    """Test suite for alternative markets predictor."""
    
    @pytest.fixture
    def predictor(self):
        """Create predictor instance."""
        return AlternativeMarketsPredictor()
    
    @pytest.fixture
    def home_team(self):
        """Create home team with corner data."""
        team = TeamForm(team_name="Home FC")
        
        # Add matches with corner statistics
        for i in range(5):
            match = MatchResult(
                date=datetime.now() - timedelta(days=i * 7),
                home_team="Home FC",
                away_team=f"Away {i}",
                home_goals=2,
                away_goals=1,
                home_xg=1.8,
                away_xg=1.2,
                is_home=True,
                home_corners=6,
                away_corners=4,
                home_shots=14,
                away_shots=10,
                home_yellow_cards=2,
                away_yellow_cards=2,
                home_fouls=12,
                away_fouls=14,
            )
            team.add_match(match)
        
        return team
    
    @pytest.fixture
    def away_team(self):
        """Create away team with corner data."""
        team = TeamForm(team_name="Away FC")
        
        for i in range(5):
            match = MatchResult(
                date=datetime.now() - timedelta(days=i * 7),
                home_team=f"Home {i}",
                away_team="Away FC",
                home_goals=1,
                away_goals=1,
                home_xg=1.3,
                away_xg=1.3,
                is_home=False,
                home_corners=5,
                away_corners=5,
                home_shots=11,
                away_shots=11,
                home_yellow_cards=2,
                away_yellow_cards=1,
                home_fouls=13,
                away_fouls=11,
            )
            team.add_match(match)
        
        return team
    
    def test_predict_corners(self, predictor, home_team, away_team):
        """Test corner prediction."""
        prediction = predictor.predict_corners(home_team, away_team)
        
        assert isinstance(prediction, AlternativeMarketPrediction)
        assert prediction.market_type == "corners"
        assert prediction.total_expected > 0
        assert prediction.home_expected > 0
        assert prediction.away_expected > 0
        assert 0 <= prediction.confidence <= 1
        
        # Check over/under predictions
        assert len(prediction.over_under_predictions) > 0
        for threshold, probs in prediction.over_under_predictions.items():
            assert "over" in probs
            assert "under" in probs
            assert 0 <= probs["over"] <= 1
            assert 0 <= probs["under"] <= 1
            # Should roughly sum to 1
            assert abs(probs["over"] + probs["under"] - 1.0) < 0.01
    
    def test_predict_cards(self, predictor, home_team, away_team):
        """Test card prediction."""
        prediction = predictor.predict_cards(home_team, away_team)
        
        assert isinstance(prediction, AlternativeMarketPrediction)
        assert prediction.market_type == "cards"
        assert prediction.total_expected > 0
        assert 0 <= prediction.confidence <= 1
        assert prediction.data_quality in ["high", "medium", "low"]
    
    def test_predict_shots(self, predictor, home_team, away_team):
        """Test shots prediction."""
        prediction = predictor.predict_shots(home_team, away_team)
        
        assert isinstance(prediction, AlternativeMarketPrediction)
        assert prediction.market_type == "shots"
        assert prediction.total_expected > 0
        assert prediction.home_expected > 0
        assert prediction.away_expected > 0
    
    def test_predict_shots_on_target(self, predictor, home_team, away_team):
        """Test shots on target prediction."""
        prediction = predictor.predict_shots(
            home_team, away_team, shots_on_target_only=True
        )
        
        assert prediction.market_type == "shots_on_target"
    
    def test_predict_with_referee_factor(self, predictor, home_team, away_team):
        """Test cards prediction with referee adjustment."""
        strict_ref = predictor.predict_cards(
            home_team, away_team, referee_factor=1.2
        )
        lenient_ref = predictor.predict_cards(
            home_team, away_team, referee_factor=0.8
        )
        
        assert strict_ref.total_expected > lenient_ref.total_expected
    
    def test_predict_offsides(self, predictor, home_team, away_team):
        """Test offsides prediction."""
        # Add offside data
        for match in home_team.matches:
            match.home_offsides = 2
            match.away_offsides = 1
        
        for match in away_team.matches:
            match.home_offsides = 1
            match.away_offsides = 2
        
        prediction = predictor.predict_offsides(home_team, away_team)
        
        assert isinstance(prediction, AlternativeMarketPrediction)
        assert prediction.market_type == "offsides"
        assert prediction.total_expected > 0
    
    def test_data_quality_assessment(self, predictor):
        """Test data quality assessment."""
        # Team with incomplete data
        incomplete_team = TeamForm(team_name="Incomplete FC")
        for i in range(5):
            match = MatchResult(
                date=datetime.now() - timedelta(days=i * 7),
                home_team="Incomplete FC",
                away_team=f"Away {i}",
                home_goals=1,
                away_goals=1,
                home_xg=1.0,
                away_xg=1.0,
                is_home=True,
                # No corner data
            )
            incomplete_team.add_match(match)
        
        prediction = predictor.predict_corners(incomplete_team, incomplete_team)
        
        # Should have low quality due to missing data
        assert prediction.data_quality in ["medium", "low"]
    
    def test_over_under_thresholds(self, predictor, home_team, away_team):
        """Test that over/under thresholds are reasonable."""
        prediction = predictor.predict_corners(home_team, away_team)
        
        # Common corner thresholds
        assert 7.5 in prediction.over_under_predictions
        assert 9.5 in prediction.over_under_predictions
        assert 11.5 in prediction.over_under_predictions
    
    def test_distribution_calculation(self, predictor, home_team, away_team):
        """Test probability distribution."""
        prediction = predictor.predict_corners(home_team, away_team)
        
        assert prediction.distribution is not None
        assert len(prediction.distribution) > 0
        
        # Distribution values should sum close to 1.0
        total_prob = sum(prediction.distribution.values())
        assert 0.95 <= total_prob <= 1.0
    
    def test_corners_expected_in_range(self, predictor, home_team, away_team):
        """Test that corner predictions are in reasonable range."""
        prediction = predictor.predict_corners(home_team, away_team)
        
        # Typical match has 8-12 corners
        assert 4 <= prediction.total_expected <= 20
    
    def test_cards_expected_in_range(self, predictor, home_team, away_team):
        """Test that card predictions are in reasonable range."""
        prediction = predictor.predict_cards(home_team, away_team)
        
        # Typical match has 2-6 cards
        assert 0 <= prediction.total_expected <= 12
    
    def test_reasoning_present(self, predictor, home_team, away_team):
        """Test that predictions include reasoning."""
        prediction = predictor.predict_corners(home_team, away_team)
        
        assert prediction.reasoning != ""
        assert len(prediction.reasoning) > 20
