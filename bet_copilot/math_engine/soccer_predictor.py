"""
Soccer match predictor using Poisson distribution and xG data
"""
import logging
from typing import Optional

from bet_copilot.math_engine.poisson import MatchSimulator
from bet_copilot.models.soccer import (
    TeamForm,
    PredictionInput,
    MatchPrediction
)

logger = logging.getLogger(__name__)


class SoccerPredictor:
    """
    High-level predictor for soccer matches using Poisson distribution.
    
    Uses Expected Goals (xG) from recent matches to predict:
    - Match outcome probabilities (Home/Draw/Away)
    - Most likely scorelines
    - Over/Under goals
    - Both Teams To Score (BTTS)
    
    Based on the assumption that goals follow a Poisson distribution
    with lambda (rate) derived from historical xG data.
    """
    
    def __init__(
        self,
        matches_to_consider: int = 5,
        home_advantage_factor: float = 1.0,
        max_goals: int = 8
    ):
        """
        Initialize soccer predictor.
        
        Args:
            matches_to_consider: Number of recent matches to analyze (default 5)
            home_advantage_factor: Multiplier for home xG (e.g., 1.1 = 10% boost)
            max_goals: Maximum goals to consider in simulation (default 8)
        """
        self.matches_to_consider = matches_to_consider
        self.home_advantage_factor = home_advantage_factor
        self.simulator = MatchSimulator(max_goals=max_goals)
        
        logger.info(
            f"SoccerPredictor initialized: matches={matches_to_consider}, "
            f"home_advantage={home_advantage_factor}"
        )
    
    def predict(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        include_details: bool = True
    ) -> MatchPrediction:
        """
        Predict match outcome based on team forms.
        
        Args:
            home_team: Home team form with recent matches
            away_team: Away team form with recent matches
            include_details: Include detailed probabilities (scorelines, over/under, BTTS)
            
        Returns:
            MatchPrediction object with probabilities
            
        Example:
            >>> predictor = SoccerPredictor()
            >>> home = TeamForm("Real Madrid")
            >>> away = TeamForm("Barcelona")
            >>> # Add matches with xG data...
            >>> prediction = predictor.predict(home, away)
            >>> print(prediction.home_win_prob)
            0.52
        """
        # Create prediction input
        prediction_input = PredictionInput(
            home_team=home_team,
            away_team=away_team,
            matches_to_consider=self.matches_to_consider,
            home_advantage_factor=self.home_advantage_factor
        )
        
        # Calculate lambdas (expected goals)
        lambda_home = prediction_input.get_home_lambda()
        lambda_away = prediction_input.get_away_lambda()
        
        logger.info(
            f"Predicting {home_team.team_name} vs {away_team.team_name}: "
            f"λ_home={lambda_home}, λ_away={lambda_away}"
        )
        
        # Calculate match outcome probabilities
        outcome_probs = self.simulator.calculate_match_outcome(lambda_home, lambda_away)
        
        # Get most likely scoreline
        scorelines = self.simulator.most_likely_scorelines(lambda_home, lambda_away, top_n=1)
        most_likely_score, most_likely_prob = scorelines[0]
        
        # Expected total goals
        expected_total = self.simulator.expected_total_goals(lambda_home, lambda_away)
        
        # Create prediction object
        prediction = MatchPrediction(
            home_team=home_team.team_name,
            away_team=away_team.team_name,
            home_lambda=lambda_home,
            away_lambda=lambda_away,
            home_win_prob=outcome_probs["home_win"],
            draw_prob=outcome_probs["draw"],
            away_win_prob=outcome_probs["away_win"],
            most_likely_score=most_likely_score,
            most_likely_score_prob=most_likely_prob,
            expected_total_goals=round(expected_total, 2)
        )
        
        # Add detailed probabilities if requested
        if include_details:
            prediction.scoreline_probabilities = self.simulator.calculate_scoreline_probabilities(
                lambda_home, lambda_away
            )
            prediction.over_under_2_5 = self.simulator.over_under_probability(
                lambda_home, lambda_away, threshold=2.5
            )
            prediction.btts = self.simulator.both_teams_to_score(
                lambda_home, lambda_away
            )
        
        logger.info(
            f"Prediction complete: {prediction.get_favorite()} "
            f"(confidence: {prediction.get_confidence():.1%})"
        )
        
        return prediction
    
    def predict_from_lambdas(
        self,
        home_team_name: str,
        away_team_name: str,
        lambda_home: float,
        lambda_away: float,
        include_details: bool = True
    ) -> MatchPrediction:
        """
        Predict match outcome directly from lambda values.
        
        Useful when you already have calculated xG values and don't need
        to process historical match data.
        
        Args:
            home_team_name: Name of home team
            away_team_name: Name of away team
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            include_details: Include detailed probabilities
            
        Returns:
            MatchPrediction object
            
        Example:
            >>> predictor = SoccerPredictor()
            >>> prediction = predictor.predict_from_lambdas(
            ...     "Real Madrid", "Barcelona",
            ...     lambda_home=2.1, lambda_away=1.5
            ... )
        """
        logger.info(
            f"Predicting {home_team_name} vs {away_team_name}: "
            f"λ_home={lambda_home}, λ_away={lambda_away}"
        )
        
        # Calculate match outcome probabilities
        outcome_probs = self.simulator.calculate_match_outcome(lambda_home, lambda_away)
        
        # Get most likely scoreline
        scorelines = self.simulator.most_likely_scorelines(lambda_home, lambda_away, top_n=1)
        most_likely_score, most_likely_prob = scorelines[0]
        
        # Expected total goals
        expected_total = self.simulator.expected_total_goals(lambda_home, lambda_away)
        
        # Create prediction object
        prediction = MatchPrediction(
            home_team=home_team_name,
            away_team=away_team_name,
            home_lambda=lambda_home,
            away_lambda=lambda_away,
            home_win_prob=outcome_probs["home_win"],
            draw_prob=outcome_probs["draw"],
            away_win_prob=outcome_probs["away_win"],
            most_likely_score=most_likely_score,
            most_likely_score_prob=most_likely_prob,
            expected_total_goals=round(expected_total, 2)
        )
        
        # Add detailed probabilities if requested
        if include_details:
            prediction.scoreline_probabilities = self.simulator.calculate_scoreline_probabilities(
                lambda_home, lambda_away
            )
            prediction.over_under_2_5 = self.simulator.over_under_probability(
                lambda_home, lambda_away, threshold=2.5
            )
            prediction.btts = self.simulator.both_teams_to_score(
                lambda_home, lambda_away
            )
        
        return prediction
    
    def get_top_scorelines(
        self,
        home_team: TeamForm,
        away_team: TeamForm,
        top_n: int = 10
    ) -> list:
        """
        Get most likely scorelines for a match.
        
        Args:
            home_team: Home team form
            away_team: Away team form
            top_n: Number of top scorelines to return
            
        Returns:
            List of ((home_goals, away_goals), probability) tuples
        """
        prediction_input = PredictionInput(
            home_team=home_team,
            away_team=away_team,
            matches_to_consider=self.matches_to_consider,
            home_advantage_factor=self.home_advantage_factor
        )
        
        lambda_home = prediction_input.get_home_lambda()
        lambda_away = prediction_input.get_away_lambda()
        
        return self.simulator.most_likely_scorelines(lambda_home, lambda_away, top_n)
    
    def compare_predictions(
        self,
        home_team: TeamForm,
        away_team: TeamForm
    ) -> dict:
        """
        Generate comprehensive comparison of prediction metrics.
        
        Returns:
            Dictionary with various statistics and probabilities
        """
        prediction = self.predict(home_team, away_team, include_details=True)
        
        # Get top 5 scorelines
        top_scorelines = self.get_top_scorelines(home_team, away_team, top_n=5)
        
        return {
            "match": f"{home_team.team_name} vs {away_team.team_name}",
            "expected_goals": {
                "home": prediction.home_lambda,
                "away": prediction.away_lambda,
                "total": prediction.expected_total_goals
            },
            "outcome_probabilities": {
                "home_win": prediction.home_win_prob,
                "draw": prediction.draw_prob,
                "away_win": prediction.away_win_prob
            },
            "top_scorelines": [
                {
                    "score": f"{score[0]}-{score[1]}",
                    "probability": prob
                }
                for score, prob in top_scorelines
            ],
            "over_under_2_5": prediction.over_under_2_5,
            "btts": prediction.btts,
            "favorite": prediction.get_favorite(),
            "confidence": prediction.get_confidence(),
            "team_form": {
                "home": {
                    "recent_form": home_team.get_form_string(),
                    "avg_xg_for": home_team.average_xg_for(home_only=True),
                    "avg_xg_against": home_team.average_xg_against(home_only=True)
                },
                "away": {
                    "recent_form": away_team.get_form_string(),
                    "avg_xg_for": away_team.average_xg_for(away_only=True),
                    "avg_xg_against": away_team.average_xg_against(away_only=True)
                }
            }
        }
