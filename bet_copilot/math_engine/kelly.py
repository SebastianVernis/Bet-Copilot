"""
Kelly Criterion calculator for optimal bet sizing.
Uses fractional Kelly for conservative approach.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from bet_copilot.config import (
    KELLY_FRACTION,
    MAX_STAKE_PERCENT,
    MIN_EV_THRESHOLD,
)

logger = logging.getLogger(__name__)


@dataclass
class KellyRecommendation:
    """Recommendation from Kelly Criterion calculator."""

    model_prob: float  # Our model's probability
    odds: float  # Bookmaker odds (decimal)
    ev: float  # Expected Value
    full_kelly: float  # Full Kelly stake (%)
    fractional_kelly: float  # Fractional Kelly stake (%)
    recommended_stake: float  # Final recommendation (%)
    is_value_bet: bool  # EV > threshold
    risk_level: str  # "LOW", "MEDIUM", "HIGH"


class KellyCriterion:
    """
    Kelly Criterion calculator for bet sizing.
    
    Formula:
        f* = (p * b - q) / b
        
    Where:
        f* = fraction of bankroll to bet
        p = probability of winning (our model)
        q = probability of losing (1 - p)
        b = odds - 1 (profit on $1 bet)
    """

    def __init__(
        self,
        kelly_fraction: float = KELLY_FRACTION,
        max_stake: float = MAX_STAKE_PERCENT,
        min_ev: float = MIN_EV_THRESHOLD,
    ):
        """
        Initialize Kelly calculator.
        
        Args:
            kelly_fraction: Fraction of Kelly to use (0.25 = 1/4 Kelly)
            max_stake: Maximum stake as % of bankroll
            min_ev: Minimum EV to consider a value bet
        """
        self.kelly_fraction = kelly_fraction
        self.max_stake = max_stake
        self.min_ev = min_ev

    def calculate_ev(self, model_prob: float, odds: float) -> float:
        """
        Calculate Expected Value.
        
        Args:
            model_prob: Probability from our model (0-1)
            odds: Decimal odds from bookmaker
            
        Returns:
            Expected Value (as decimal, e.g., 0.15 = +15%)
        """
        return (model_prob * odds) - 1

    def calculate_full_kelly(self, model_prob: float, odds: float) -> float:
        """
        Calculate full Kelly stake.
        
        Args:
            model_prob: Probability from our model (0-1)
            odds: Decimal odds from bookmaker
            
        Returns:
            Stake as fraction of bankroll (0-1)
        """
        # Validate inputs
        if model_prob <= 0 or model_prob >= 1:
            logger.warning(f"Invalid probability: {model_prob}")
            return 0.0

        if odds <= 1.0:
            logger.warning(f"Invalid odds: {odds}")
            return 0.0

        # Kelly formula
        p = model_prob
        q = 1 - p
        b = odds - 1

        full_kelly = (p * b - q) / b

        # Kelly can be negative (no bet) or > 1 (over-bet)
        if full_kelly < 0:
            logger.debug(f"Negative Kelly: {full_kelly:.4f} - no value")
            return 0.0

        if full_kelly > 1:
            logger.warning(f"Kelly > 100%: {full_kelly:.4f} - capping at 100%")
            return 1.0

        return full_kelly

    def get_risk_level(self, stake_percent: float) -> str:
        """
        Determine risk level based on stake size.
        
        Args:
            stake_percent: Stake as % of bankroll
            
        Returns:
            Risk level: "LOW", "MEDIUM", "HIGH"
        """
        if stake_percent < 1.0:
            return "LOW"
        elif stake_percent < 3.0:
            return "MEDIUM"
        else:
            return "HIGH"

    def calculate(
        self,
        model_prob: float,
        odds: float,
        apply_fraction: bool = True,
        apply_max_stake: bool = True,
    ) -> KellyRecommendation:
        """
        Calculate Kelly recommendation with safety limits.
        
        Args:
            model_prob: Probability from our model (0-1)
            odds: Decimal odds from bookmaker
            apply_fraction: Apply fractional Kelly (default True)
            apply_max_stake: Apply max stake cap (default True)
            
        Returns:
            KellyRecommendation object
        """
        # Calculate EV
        ev = self.calculate_ev(model_prob, odds)

        # Calculate full Kelly
        full_kelly = self.calculate_full_kelly(model_prob, odds)
        full_kelly_percent = full_kelly * 100

        # Apply fractional Kelly
        fractional_kelly = full_kelly * self.kelly_fraction if apply_fraction else full_kelly
        fractional_kelly_percent = fractional_kelly * 100

        # Apply max stake cap
        recommended_stake = fractional_kelly_percent
        if apply_max_stake and recommended_stake > self.max_stake:
            logger.info(
                f"Capping stake from {recommended_stake:.2f}% to {self.max_stake:.2f}%"
            )
            recommended_stake = self.max_stake

        # Determine if value bet
        is_value_bet = ev >= self.min_ev and recommended_stake > 0

        # Risk level
        risk_level = self.get_risk_level(recommended_stake)

        return KellyRecommendation(
            model_prob=model_prob,
            odds=odds,
            ev=ev,
            full_kelly=full_kelly_percent,
            fractional_kelly=fractional_kelly_percent,
            recommended_stake=recommended_stake,
            is_value_bet=is_value_bet,
            risk_level=risk_level,
        )

    def calculate_stake_amount(
        self, model_prob: float, odds: float, bankroll: float
    ) -> float:
        """
        Calculate stake amount in currency.
        
        Args:
            model_prob: Probability from our model (0-1)
            odds: Decimal odds from bookmaker
            bankroll: Total bankroll in currency
            
        Returns:
            Stake amount in currency
        """
        recommendation = self.calculate(model_prob, odds)
        stake_amount = bankroll * (recommendation.recommended_stake / 100)

        logger.info(
            f"Bankroll: ${bankroll:.2f}, "
            f"Stake: {recommendation.recommended_stake:.2f}% "
            f"(${stake_amount:.2f})"
        )

        return stake_amount

    @staticmethod
    def implied_probability(odds: float) -> float:
        """
        Calculate implied probability from decimal odds.
        
        Args:
            odds: Decimal odds
            
        Returns:
            Implied probability (0-1)
        """
        if odds <= 0:
            return 0.0
        return 1.0 / odds

    @staticmethod
    def edge(model_prob: float, odds: float) -> float:
        """
        Calculate edge (difference between model and bookmaker).
        
        Args:
            model_prob: Our model's probability
            odds: Bookmaker odds
            
        Returns:
            Edge as decimal (0.1 = 10% edge)
        """
        implied = KellyCriterion.implied_probability(odds)
        return model_prob - implied
