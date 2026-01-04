"""
Tests for Kelly Criterion calculator.
"""

import pytest
from bet_copilot.math_engine.kelly import KellyCriterion, KellyRecommendation


class TestKellyCriterion:
    """Test Kelly Criterion calculations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.kelly = KellyCriterion(
            kelly_fraction=0.25, max_stake=5.0, min_ev=0.05
        )

    def test_calculate_ev(self):
        """Test EV calculation."""
        # Positive EV
        ev = self.kelly.calculate_ev(model_prob=0.6, odds=2.0)
        assert ev == pytest.approx(0.2, abs=0.01)  # (0.6 * 2.0) - 1 = 0.2

        # Zero EV
        ev = self.kelly.calculate_ev(model_prob=0.5, odds=2.0)
        assert ev == pytest.approx(0.0, abs=0.01)

        # Negative EV
        ev = self.kelly.calculate_ev(model_prob=0.4, odds=2.0)
        assert ev < 0

    def test_calculate_full_kelly(self):
        """Test full Kelly stake calculation."""
        # Classic example: 60% win prob, 2.0 odds
        # Kelly = (0.6 * 1.0 - 0.4) / 1.0 = 0.2 = 20%
        stake = self.kelly.calculate_full_kelly(model_prob=0.6, odds=2.0)
        assert stake == pytest.approx(0.2, abs=0.01)

        # No value bet
        stake = self.kelly.calculate_full_kelly(model_prob=0.4, odds=2.0)
        assert stake == 0.0

        # High odds scenario
        stake = self.kelly.calculate_full_kelly(model_prob=0.3, odds=4.0)
        assert stake > 0

    def test_invalid_inputs(self):
        """Test invalid input handling."""
        # Invalid probability
        stake = self.kelly.calculate_full_kelly(model_prob=0.0, odds=2.0)
        assert stake == 0.0

        stake = self.kelly.calculate_full_kelly(model_prob=1.0, odds=2.0)
        assert stake == 0.0

        # Invalid odds
        stake = self.kelly.calculate_full_kelly(model_prob=0.6, odds=1.0)
        assert stake == 0.0

    def test_fractional_kelly(self):
        """Test fractional Kelly application."""
        rec = self.kelly.calculate(model_prob=0.6, odds=2.0, apply_fraction=True)

        # Full Kelly is 20%, fractional (1/4) should be 5%
        assert rec.full_kelly == pytest.approx(20.0, abs=0.1)
        assert rec.fractional_kelly == pytest.approx(5.0, abs=0.1)
        assert rec.recommended_stake == pytest.approx(5.0, abs=0.1)

    def test_max_stake_cap(self):
        """Test max stake capping."""
        # High probability should trigger cap
        rec = self.kelly.calculate(
            model_prob=0.8, odds=1.5, apply_fraction=True, apply_max_stake=True
        )

        # Should be capped at 5%
        assert rec.recommended_stake <= 5.0

    def test_risk_level(self):
        """Test risk level classification."""
        # Low risk
        assert self.kelly.get_risk_level(0.5) == "LOW"

        # Medium risk
        assert self.kelly.get_risk_level(2.0) == "MEDIUM"

        # High risk
        assert self.kelly.get_risk_level(4.0) == "HIGH"

    def test_value_bet_detection(self):
        """Test value bet identification."""
        # Value bet (EV > 5%)
        rec = self.kelly.calculate(model_prob=0.6, odds=2.0)
        assert rec.is_value_bet is True
        assert rec.ev > 0.05

        # Not a value bet
        rec = self.kelly.calculate(model_prob=0.5, odds=2.0)
        assert rec.is_value_bet is False

    def test_implied_probability(self):
        """Test implied probability calculation."""
        # 2.0 odds = 50%
        prob = KellyCriterion.implied_probability(2.0)
        assert prob == pytest.approx(0.5, abs=0.01)

        # 4.0 odds = 25%
        prob = KellyCriterion.implied_probability(4.0)
        assert prob == pytest.approx(0.25, abs=0.01)

        # 1.5 odds = 66.67%
        prob = KellyCriterion.implied_probability(1.5)
        assert prob == pytest.approx(0.6667, abs=0.01)

    def test_edge_calculation(self):
        """Test edge calculation."""
        # 60% model prob, 2.0 odds (50% implied)
        # Edge = 60% - 50% = 10%
        edge = KellyCriterion.edge(model_prob=0.6, odds=2.0)
        assert edge == pytest.approx(0.1, abs=0.01)

        # No edge
        edge = KellyCriterion.edge(model_prob=0.5, odds=2.0)
        assert edge == pytest.approx(0.0, abs=0.01)

        # Negative edge
        edge = KellyCriterion.edge(model_prob=0.4, odds=2.0)
        assert edge < 0

    def test_calculate_stake_amount(self):
        """Test stake amount calculation."""
        bankroll = 1000.0

        # 60% prob, 2.0 odds -> 20% full Kelly -> 5% fractional
        # 5% of $1000 = $50
        stake = self.kelly.calculate_stake_amount(
            model_prob=0.6, odds=2.0, bankroll=bankroll
        )

        assert stake == pytest.approx(50.0, abs=1.0)

    def test_recommendation_object(self):
        """Test KellyRecommendation object."""
        rec = self.kelly.calculate(model_prob=0.6, odds=2.0)

        assert isinstance(rec, KellyRecommendation)
        assert rec.model_prob == 0.6
        assert rec.odds == 2.0
        assert rec.ev > 0
        assert rec.full_kelly > 0
        assert rec.fractional_kelly > 0
        assert rec.recommended_stake > 0
        assert isinstance(rec.is_value_bet, bool)
        assert rec.risk_level in ["LOW", "MEDIUM", "HIGH"]
