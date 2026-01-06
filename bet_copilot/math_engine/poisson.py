"""
Poisson distribution calculator for goal prediction
"""
import math
from typing import Dict, Tuple, List
from functools import lru_cache


class PoissonCalculator:
    """
    Pure mathematical implementation of Poisson distribution.
    
    Used to calculate probabilities of discrete events (goals) based on
    expected rate (lambda/xG).
    
    Formula: P(X = k) = (λ^k × e^-λ) / k!
    
    Where:
    - λ (lambda): Expected number of events
    - k: Actual number of events
    - e: Euler's constant (~2.71828)
    """
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _factorial(n: int) -> int:
        """
        Calculate factorial with caching.
        
        Args:
            n: Non-negative integer
            
        Returns:
            n! = n × (n-1) × ... × 2 × 1
        """
        if n <= 1:
            return 1
        return n * PoissonCalculator._factorial(n - 1)
    
    @staticmethod
    def probability(k: int, lambda_: float) -> float:
        """
        Calculate Poisson probability for exactly k events.
        
        P(X = k) = (λ^k × e^-λ) / k!
        
        Args:
            k: Number of events (goals)
            lambda_: Expected rate (xG)
            
        Returns:
            Probability between 0 and 1
            
        Example:
            >>> calc = PoissonCalculator()
            >>> calc.probability(2, 1.5)  # P(2 goals | xG=1.5)
            0.2510
        """
        if k < 0:
            return 0.0
        
        if lambda_ <= 0:
            return 1.0 if k == 0 else 0.0
        
        # P(X = k) = (λ^k × e^-λ) / k!
        numerator = (lambda_ ** k) * math.exp(-lambda_)
        denominator = PoissonCalculator._factorial(k)
        
        return numerator / denominator
    
    @staticmethod
    def probability_range(max_k: int, lambda_: float) -> List[float]:
        """
        Calculate Poisson probabilities for k = 0 to max_k.
        
        Args:
            max_k: Maximum number of events to calculate
            lambda_: Expected rate
            
        Returns:
            List of probabilities [P(0), P(1), ..., P(max_k)]
        """
        return [
            PoissonCalculator.probability(k, lambda_)
            for k in range(max_k + 1)
        ]
    
    @staticmethod
    def expected_value(lambda_: float) -> float:
        """
        Expected value (mean) of Poisson distribution.
        
        For Poisson, E[X] = λ
        
        Args:
            lambda_: Rate parameter
            
        Returns:
            Expected value
        """
        return lambda_
    
    @staticmethod
    def variance(lambda_: float) -> float:
        """
        Variance of Poisson distribution.
        
        For Poisson, Var(X) = λ
        
        Args:
            lambda_: Rate parameter
            
        Returns:
            Variance
        """
        return lambda_
    
    @staticmethod
    def standard_deviation(lambda_: float) -> float:
        """
        Standard deviation of Poisson distribution.
        
        For Poisson, σ = √λ
        
        Args:
            lambda_: Rate parameter
            
        Returns:
            Standard deviation
        """
        return math.sqrt(lambda_)
    
    @staticmethod
    def cumulative_probability(k: int, lambda_: float) -> float:
        """
        Calculate cumulative Poisson probability P(X <= k).
        
        This is the sum of probabilities from 0 to k.
        
        Args:
            k: Upper bound (inclusive)
            lambda_: Expected rate
            
        Returns:
            Cumulative probability P(X <= k)
            
        Example:
            >>> calc = PoissonCalculator()
            >>> calc.cumulative_probability(2, 1.5)  # P(X <= 2 | λ=1.5)
            0.8088
        """
        if k < 0:
            return 0.0
        
        if lambda_ <= 0:
            return 1.0
        
        # Sum probabilities from 0 to k
        cumulative = sum(
            PoissonCalculator.probability(i, lambda_)
            for i in range(k + 1)
        )
        
        return cumulative


class MatchSimulator:
    """
    Simulates match outcomes using independent Poisson distributions
    for home and away goals.
    """
    
    def __init__(self, max_goals: int = 8):
        """
        Initialize match simulator.
        
        Args:
            max_goals: Maximum goals to consider per team (default 8)
                      Higher values are more accurate but slower.
        """
        self.max_goals = max_goals
        self.calculator = PoissonCalculator()
    
    def calculate_scoreline_probabilities(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Dict[Tuple[int, int], float]:
        """
        Calculate probabilities for all possible scorelines.
        
        Assumes independence: P(i-j) = P(home=i) × P(away=j)
        
        Args:
            lambda_home: Expected goals for home team (xG)
            lambda_away: Expected goals for away team (xG)
            
        Returns:
            Dictionary mapping (home_goals, away_goals) to probability
            
        Example:
            >>> sim = MatchSimulator()
            >>> probs = sim.calculate_scoreline_probabilities(1.5, 1.2)
            >>> probs[(2, 1)]  # Probability of 2-1
            0.0897
        """
        # Pre-calculate probabilities for each team
        home_probs = self.calculator.probability_range(self.max_goals, lambda_home)
        away_probs = self.calculator.probability_range(self.max_goals, lambda_away)
        
        scorelines = {}
        
        # Calculate joint probability for each scoreline
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                # Independence assumption: multiply individual probabilities
                prob = home_probs[home_goals] * away_probs[away_goals]
                scorelines[(home_goals, away_goals)] = prob
        
        return scorelines
    
    def calculate_match_outcome(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Dict[str, float]:
        """
        Calculate probabilities for match outcomes (Home/Draw/Away).
        
        Args:
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            
        Returns:
            Dictionary with keys:
            - "home_win": Probability of home victory
            - "draw": Probability of draw
            - "away_win": Probability of away victory
            
        Example:
            >>> sim = MatchSimulator()
            >>> outcomes = sim.calculate_match_outcome(2.1, 1.5)
            >>> outcomes["home_win"]
            0.523
        """
        # Get all scoreline probabilities
        scorelines = self.calculate_scoreline_probabilities(lambda_home, lambda_away)
        
        # Aggregate by outcome
        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        
        for (home_goals, away_goals), prob in scorelines.items():
            if home_goals > away_goals:
                home_win += prob
            elif home_goals == away_goals:
                draw += prob
            else:
                away_win += prob
        
        return {
            "home_win": round(home_win, 4),
            "draw": round(draw, 4),
            "away_win": round(away_win, 4)
        }
    
    def most_likely_scorelines(
        self,
        lambda_home: float,
        lambda_away: float,
        top_n: int = 10
    ) -> List[Tuple[Tuple[int, int], float]]:
        """
        Get most likely scorelines sorted by probability.
        
        Args:
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            top_n: Number of top scorelines to return
            
        Returns:
            List of ((home_goals, away_goals), probability) tuples
            
        Example:
            >>> sim = MatchSimulator()
            >>> scorelines = sim.most_likely_scorelines(1.5, 1.2, top_n=5)
            >>> scorelines[0]
            ((1, 1), 0.1682)
        """
        scorelines = self.calculate_scoreline_probabilities(lambda_home, lambda_away)
        
        # Sort by probability (descending)
        sorted_scorelines = sorted(
            scorelines.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [(score, round(prob, 4)) for score, prob in sorted_scorelines[:top_n]]
    
    def expected_total_goals(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> float:
        """
        Calculate expected total goals in match.
        
        E[Total] = E[Home] + E[Away] = λ_home + λ_away
        
        Args:
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            
        Returns:
            Expected total goals
        """
        return lambda_home + lambda_away
    
    def over_under_probability(
        self,
        lambda_home: float,
        lambda_away: float,
        threshold: float = 2.5
    ) -> Dict[str, float]:
        """
        Calculate probability of total goals over/under threshold.
        
        Args:
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            threshold: Goals threshold (e.g., 2.5 for over/under 2.5)
            
        Returns:
            Dictionary with "over" and "under" probabilities
        """
        scorelines = self.calculate_scoreline_probabilities(lambda_home, lambda_away)
        
        over = 0.0
        under = 0.0
        
        for (home_goals, away_goals), prob in scorelines.items():
            total = home_goals + away_goals
            if total > threshold:
                over += prob
            else:
                under += prob
        
        return {
            "over": round(over, 4),
            "under": round(under, 4)
        }
    
    def both_teams_to_score(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Dict[str, float]:
        """
        Calculate probability of both teams scoring (BTTS).
        
        Args:
            lambda_home: Expected goals for home team
            lambda_away: Expected goals for away team
            
        Returns:
            Dictionary with "yes" and "no" probabilities
        """
        scorelines = self.calculate_scoreline_probabilities(lambda_home, lambda_away)
        
        btts_yes = 0.0
        btts_no = 0.0
        
        for (home_goals, away_goals), prob in scorelines.items():
            if home_goals > 0 and away_goals > 0:
                btts_yes += prob
            else:
                btts_no += prob
        
        return {
            "yes": round(btts_yes, 4),
            "no": round(btts_no, 4)
        }
