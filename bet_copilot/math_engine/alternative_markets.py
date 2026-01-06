"""
Predictor for alternative betting markets.
Covers corners, cards, shots, and other non-traditional markets.
"""

import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from statistics import mean, stdev

from bet_copilot.models.soccer import TeamForm
from bet_copilot.math_engine.poisson import PoissonCalculator

logger = logging.getLogger(__name__)


@dataclass
class AlternativeMarketPrediction:
    """Prediction for alternative betting markets."""
    
    market_type: str  # "corners", "cards", "shots", etc.
    home_team: str
    away_team: str
    
    # Total market predictions
    total_expected: float
    over_under_predictions: Dict[float, Dict[str, float]]  # {threshold: {"over": prob, "under": prob}}
    
    # Individual team predictions (for team-specific markets)
    home_expected: Optional[float] = None
    away_expected: Optional[float] = None
    
    # Distribution details
    distribution: Optional[Dict[int, float]] = None  # {value: probability}
    
    # Confidence and metadata
    confidence: float = 0.0
    data_quality: str = "unknown"  # "high", "medium", "low"
    reasoning: str = ""


class AlternativeMarketsPredictor:
    """
    Predictor for alternative betting markets.
    
    Uses Poisson distribution for count-based markets (corners, cards, shots)
    and historical averages with statistical adjustments.
    """
    
    def __init__(self):
        self.poisson = PoissonCalculator()
    
    def predict_corners(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        matches_to_consider: int = 5
    ) -> AlternativeMarketPrediction:
        """
        Predict corner kicks for a match.
        
        Uses team averages and Poisson distribution.
        
        Args:
            home_team: Home team form data
            away_team: Away team form data
            matches_to_consider: Number of recent matches to analyze
            
        Returns:
            AlternativeMarketPrediction for corners
        """
        # Calculate expected corners for each team
        home_corners_avg = home_team.average_corners_for(
            n=matches_to_consider, home_only=True
        )
        away_corners_avg = away_team.average_corners_for(
            n=matches_to_consider, away_only=True
        )
        
        # Adjust based on opponent's defensive style
        # Teams that defend deep tend to concede more corners
        home_defense_factor = self._calculate_defensive_factor(home_team, matches_to_consider, True)
        away_defense_factor = self._calculate_defensive_factor(away_team, matches_to_consider, False)
        
        home_expected = round(home_corners_avg * away_defense_factor, 2)
        away_expected = round(away_corners_avg * home_defense_factor, 2)
        total_expected = round(home_expected + away_expected, 2)
        
        # Calculate over/under probabilities for common thresholds
        thresholds = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5]
        over_under = self._calculate_over_under(total_expected, thresholds)
        
        # Calculate distribution
        distribution = self._calculate_distribution(total_expected, max_value=25)
        
        # Assess data quality
        data_quality = self._assess_data_quality(home_team, away_team, matches_to_consider, "corners")
        
        return AlternativeMarketPrediction(
            market_type="corners",
            home_team=home_team.team_name,
            away_team=away_team.team_name,
            total_expected=total_expected,
            over_under_predictions=over_under,
            home_expected=home_expected,
            away_expected=away_expected,
            distribution=distribution,
            confidence=self._calculate_confidence(data_quality, home_corners_avg, away_corners_avg),
            data_quality=data_quality,
            reasoning=f"Based on {matches_to_consider} recent matches. "
                     f"Home avg: {home_corners_avg:.1f}, Away avg: {away_corners_avg:.1f}"
        )
    
    def predict_cards(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        matches_to_consider: int = 5,
        referee_factor: float = 1.0
    ) -> AlternativeMarketPrediction:
        """
        Predict total cards (yellow + red) for a match.
        
        Args:
            home_team: Home team form data
            away_team: Away team form data
            matches_to_consider: Number of recent matches to analyze
            referee_factor: Multiplier for strict/lenient referees (0.8-1.2)
            
        Returns:
            AlternativeMarketPrediction for cards
        """
        home_cards_avg = home_team.average_cards(n=matches_to_consider)
        away_cards_avg = away_team.average_cards(n=matches_to_consider)
        
        # Average and apply referee factor
        total_expected = round((home_cards_avg + away_cards_avg) / 2 * referee_factor, 2)
        
        # Thresholds for cards market
        thresholds = [2.5, 3.5, 4.5, 5.5, 6.5]
        over_under = self._calculate_over_under(total_expected, thresholds)
        
        distribution = self._calculate_distribution(total_expected, max_value=15)
        
        data_quality = self._assess_data_quality(home_team, away_team, matches_to_consider, "cards")
        
        reasoning = f"Based on {matches_to_consider} recent matches. "
        if referee_factor != 1.0:
            reasoning += f"Referee adjustment: {referee_factor:.2f}x. "
        reasoning += f"Combined avg: {(home_cards_avg + away_cards_avg) / 2:.1f}"
        
        return AlternativeMarketPrediction(
            market_type="cards",
            home_team=home_team.team_name,
            away_team=away_team.team_name,
            total_expected=total_expected,
            over_under_predictions=over_under,
            distribution=distribution,
            confidence=self._calculate_confidence(data_quality, home_cards_avg, away_cards_avg),
            data_quality=data_quality,
            reasoning=reasoning
        )
    
    def predict_shots(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        matches_to_consider: int = 5,
        shots_on_target_only: bool = False
    ) -> AlternativeMarketPrediction:
        """
        Predict total shots for a match.
        
        Args:
            home_team: Home team form data
            away_team: Away team form data
            matches_to_consider: Number of recent matches to analyze
            shots_on_target_only: If True, only count shots on target
            
        Returns:
            AlternativeMarketPrediction for shots
        """
        home_shots_avg = home_team.average_shots(n=matches_to_consider, home_only=True)
        away_shots_avg = away_team.average_shots(n=matches_to_consider, away_only=True)
        
        total_expected = round(home_shots_avg + away_shots_avg, 2)
        
        # Thresholds depend on shots type
        if shots_on_target_only:
            thresholds = [8.5, 9.5, 10.5, 11.5, 12.5]
            max_value = 30
        else:
            thresholds = [18.5, 20.5, 22.5, 24.5, 26.5]
            max_value = 50
        
        over_under = self._calculate_over_under(total_expected, thresholds)
        distribution = self._calculate_distribution(total_expected, max_value=max_value)
        
        data_quality = self._assess_data_quality(home_team, away_team, matches_to_consider, "shots")
        
        market_type = "shots_on_target" if shots_on_target_only else "shots"
        
        return AlternativeMarketPrediction(
            market_type=market_type,
            home_team=home_team.team_name,
            away_team=away_team.team_name,
            total_expected=total_expected,
            over_under_predictions=over_under,
            home_expected=home_shots_avg,
            away_expected=away_shots_avg,
            distribution=distribution,
            confidence=self._calculate_confidence(data_quality, home_shots_avg, away_shots_avg),
            data_quality=data_quality,
            reasoning=f"Based on {matches_to_consider} recent matches. "
                     f"Home avg: {home_shots_avg:.1f}, Away avg: {away_shots_avg:.1f}"
        )
    
    def predict_offsides(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        matches_to_consider: int = 5
    ) -> AlternativeMarketPrediction:
        """
        Predict total offsides for a match.
        
        Offsides correlate with attacking intensity and opponent's defensive line.
        """
        # Get offside averages (if data available)
        home_matches = home_team.get_recent_matches(matches_to_consider, home_only=True)
        away_matches = away_team.get_recent_matches(matches_to_consider, away_only=True)
        
        home_offsides = [
            m.home_offsides for m in home_matches
            if m.home_offsides is not None
        ]
        away_offsides = [
            m.away_offsides for m in away_matches
            if m.away_offsides is not None
        ]
        
        home_avg = round(mean(home_offsides), 2) if home_offsides else 2.0
        away_avg = round(mean(away_offsides), 2) if away_offsides else 2.0
        total_expected = round(home_avg + away_avg, 2)
        
        thresholds = [3.5, 4.5, 5.5, 6.5]
        over_under = self._calculate_over_under(total_expected, thresholds)
        distribution = self._calculate_distribution(total_expected, max_value=15)
        
        data_quality = "high" if len(home_offsides) >= 3 and len(away_offsides) >= 3 else "low"
        
        return AlternativeMarketPrediction(
            market_type="offsides",
            home_team=home_team.team_name,
            away_team=away_team.team_name,
            total_expected=total_expected,
            over_under_predictions=over_under,
            home_expected=home_avg,
            away_expected=away_avg,
            distribution=distribution,
            confidence=0.7 if data_quality == "high" else 0.4,
            data_quality=data_quality,
            reasoning=f"Based on available data. Home avg: {home_avg:.1f}, Away avg: {away_avg:.1f}"
        )
    
    def _calculate_defensive_factor(
        self,
        team: TeamForm,
        n: int,
        is_home: bool
    ) -> float:
        """
        Calculate defensive factor (affects opponent's corners).
        
        Teams that concede more xG tend to defend deeper and concede more corners.
        """
        xg_against = team.average_xg_against(n=n, home_only=is_home)
        
        # Normalize: avg xG against is ~1.3
        # More xG against → more defensive → factor > 1.0
        if xg_against == 0:
            return 1.0
        
        factor = 0.8 + (xg_against / 1.3) * 0.4
        return max(0.8, min(1.2, factor))
    
    def _calculate_over_under(
        self,
        expected_value: float,
        thresholds: List[float]
    ) -> Dict[float, Dict[str, float]]:
        """
        Calculate over/under probabilities for given thresholds.
        
        Uses Poisson distribution.
        """
        result = {}
        
        for threshold in thresholds:
            # P(X > threshold) = 1 - P(X <= threshold)
            cumulative = self.poisson.cumulative_probability(
                k=int(threshold),
                lambda_=expected_value
            )
            
            over_prob = 1 - cumulative
            under_prob = cumulative
            
            result[threshold] = {
                "over": round(over_prob, 4),
                "under": round(under_prob, 4)
            }
        
        return result
    
    def _calculate_distribution(
        self,
        expected_value: float,
        max_value: int
    ) -> Dict[int, float]:
        """Calculate probability distribution for values 0 to max_value."""
        distribution = {}
        
        for k in range(max_value + 1):
            prob = self.poisson.probability(k, expected_value)
            if prob > 0.001:  # Only include meaningful probabilities
                distribution[k] = round(prob, 4)
        
        return distribution
    
    def _assess_data_quality(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        n: int,
        stat_type: str
    ) -> str:
        """
        Assess quality of available data.
        
        Returns:
            "high", "medium", or "low"
        """
        home_matches = home_team.get_recent_matches(n)
        away_matches = away_team.get_recent_matches(n)
        
        # Check data availability based on stat_type
        if stat_type == "corners":
            home_data = [m for m in home_matches if m.home_corners is not None]
            away_data = [m for m in away_matches if m.away_corners is not None]
        elif stat_type == "cards":
            home_data = [m for m in home_matches if m.home_yellow_cards is not None]
            away_data = [m for m in away_matches if m.away_yellow_cards is not None]
        elif stat_type == "shots":
            home_data = [m for m in home_matches if m.home_shots is not None]
            away_data = [m for m in away_matches if m.away_shots is not None]
        else:
            return "medium"
        
        home_coverage = len(home_data) / max(len(home_matches), 1)
        away_coverage = len(away_data) / max(len(away_matches), 1)
        avg_coverage = (home_coverage + away_coverage) / 2
        
        if avg_coverage >= 0.8:
            return "high"
        elif avg_coverage >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(
        self,
        data_quality: str,
        home_avg: float,
        away_avg: float
    ) -> float:
        """
        Calculate confidence score (0-1) based on data quality and consistency.
        """
        base_confidence = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }.get(data_quality, 0.5)
        
        # Adjust based on whether averages are reasonable
        if home_avg == 0 or away_avg == 0:
            base_confidence *= 0.7
        
        return round(base_confidence, 2)
