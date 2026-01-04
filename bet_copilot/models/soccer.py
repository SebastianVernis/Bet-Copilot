"""
Data models for soccer prediction
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from statistics import mean


@dataclass
class MatchResult:
    """Historical match result with xG data"""
    date: datetime
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    home_xg: float  # Expected Goals for home team
    away_xg: float  # Expected Goals for away team
    is_home: bool  # True if this is from home team's perspective
    
    def __post_init__(self):
        """Validate data"""
        if self.home_xg < 0 or self.away_xg < 0:
            raise ValueError("xG values must be non-negative")
        if self.home_goals < 0 or self.away_goals < 0:
            raise ValueError("Goals must be non-negative")


@dataclass
class TeamForm:
    """Team's recent form and xG statistics"""
    team_name: str
    matches: List[MatchResult] = field(default_factory=list)
    
    def add_match(self, match: MatchResult):
        """Add a match to the team's history"""
        self.matches.append(match)
        # Keep only most recent matches (sorted by date)
        self.matches.sort(key=lambda m: m.date, reverse=True)
    
    def get_recent_matches(self, n: int = 5, home_only: bool = False, away_only: bool = False) -> List[MatchResult]:
        """
        Get most recent matches.
        
        Args:
            n: Number of matches
            home_only: Only home matches
            away_only: Only away matches
            
        Returns:
            List of recent matches
        """
        matches = self.matches
        
        if home_only:
            matches = [m for m in matches if m.is_home]
        elif away_only:
            matches = [m for m in matches if not m.is_home]
        
        return matches[:n]
    
    def average_xg_for(self, n: int = 5, home_only: bool = False, away_only: bool = False) -> float:
        """
        Calculate average xG generated (goals for).
        
        Args:
            n: Number of recent matches to consider
            home_only: Only consider home matches
            away_only: Only consider away matches
            
        Returns:
            Average xG for
        """
        matches = self.get_recent_matches(n, home_only, away_only)
        
        if not matches:
            return 0.0
        
        xg_values = [
            m.home_xg if m.is_home else m.away_xg
            for m in matches
        ]
        
        return round(mean(xg_values), 2) if xg_values else 0.0
    
    def average_xg_against(self, n: int = 5, home_only: bool = False, away_only: bool = False) -> float:
        """
        Calculate average xG conceded (goals against).
        
        Args:
            n: Number of recent matches to consider
            home_only: Only consider home matches
            away_only: Only consider away matches
            
        Returns:
            Average xG against
        """
        matches = self.get_recent_matches(n, home_only, away_only)
        
        if not matches:
            return 0.0
        
        xg_values = [
            m.away_xg if m.is_home else m.home_xg
            for m in matches
        ]
        
        return round(mean(xg_values), 2) if xg_values else 0.0
    
    def average_goals_for(self, n: int = 5, home_only: bool = False, away_only: bool = False) -> float:
        """Calculate average goals scored"""
        matches = self.get_recent_matches(n, home_only, away_only)
        
        if not matches:
            return 0.0
        
        goals = [
            m.home_goals if m.is_home else m.away_goals
            for m in matches
        ]
        
        return round(mean(goals), 2) if goals else 0.0
    
    def average_goals_against(self, n: int = 5, home_only: bool = False, away_only: bool = False) -> float:
        """Calculate average goals conceded"""
        matches = self.get_recent_matches(n, home_only, away_only)
        
        if not matches:
            return 0.0
        
        goals = [
            m.away_goals if m.is_home else m.home_goals
            for m in matches
        ]
        
        return round(mean(goals), 2) if goals else 0.0
    
    def get_form_string(self, n: int = 5) -> str:
        """
        Get form string (W/D/L).
        
        Returns:
            String like "WDWLW" (most recent first)
        """
        matches = self.get_recent_matches(n)
        form = []
        
        for match in matches:
            if match.is_home:
                if match.home_goals > match.away_goals:
                    form.append("W")
                elif match.home_goals == match.away_goals:
                    form.append("D")
                else:
                    form.append("L")
            else:
                if match.away_goals > match.home_goals:
                    form.append("W")
                elif match.away_goals == match.home_goals:
                    form.append("D")
                else:
                    form.append("L")
        
        return "".join(form)


@dataclass
class PredictionInput:
    """Input data for match prediction"""
    home_team: TeamForm
    away_team: TeamForm
    matches_to_consider: int = 5
    home_advantage_factor: float = 1.0  # Multiplier for home xG (e.g., 1.1 = 10% boost)
    
    def get_home_lambda(self) -> float:
        """
        Calculate lambda (expected goals) for home team.
        
        Considers:
        - Home team's offensive strength (xG for at home)
        - Away team's defensive weakness (xG against away)
        - Home advantage factor
        """
        home_attack = self.home_team.average_xg_for(
            n=self.matches_to_consider,
            home_only=True
        )
        
        away_defense = self.away_team.average_xg_against(
            n=self.matches_to_consider,
            away_only=True
        )
        
        # Simple average, adjusted for home advantage
        lambda_home = ((home_attack + away_defense) / 2) * self.home_advantage_factor
        
        return round(lambda_home, 2)
    
    def get_away_lambda(self) -> float:
        """
        Calculate lambda (expected goals) for away team.
        
        Considers:
        - Away team's offensive strength (xG for away)
        - Home team's defensive weakness (xG against at home)
        """
        away_attack = self.away_team.average_xg_for(
            n=self.matches_to_consider,
            away_only=True
        )
        
        home_defense = self.home_team.average_xg_against(
            n=self.matches_to_consider,
            home_only=True
        )
        
        # Simple average
        lambda_away = (away_attack + home_defense) / 2
        
        return round(lambda_away, 2)


@dataclass
class MatchPrediction:
    """Complete match prediction with probabilities"""
    home_team: str
    away_team: str
    home_lambda: float  # Expected goals home
    away_lambda: float  # Expected goals away
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    most_likely_score: tuple[int, int]
    most_likely_score_prob: float
    expected_total_goals: float
    prediction_timestamp: datetime = field(default_factory=datetime.now)
    
    # Optional detailed probabilities
    scoreline_probabilities: Optional[Dict[tuple[int, int], float]] = None
    over_under_2_5: Optional[Dict[str, float]] = None
    btts: Optional[Dict[str, float]] = None
    
    def get_favorite(self) -> str:
        """Get the favorite outcome"""
        probs = {
            "home_win": self.home_win_prob,
            "draw": self.draw_prob,
            "away_win": self.away_win_prob
        }
        
        favorite = max(probs, key=probs.get)
        return favorite
    
    def get_confidence(self) -> float:
        """Get confidence level (max probability)"""
        return max(self.home_win_prob, self.draw_prob, self.away_win_prob)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_lambda": self.home_lambda,
            "away_lambda": self.away_lambda,
            "probabilities": {
                "home_win": self.home_win_prob,
                "draw": self.draw_prob,
                "away_win": self.away_win_prob
            },
            "most_likely_score": {
                "scoreline": f"{self.most_likely_score[0]}-{self.most_likely_score[1]}",
                "probability": self.most_likely_score_prob
            },
            "expected_total_goals": self.expected_total_goals,
            "favorite": self.get_favorite(),
            "confidence": self.get_confidence(),
            "timestamp": self.prediction_timestamp.isoformat()
        }
        
        if self.over_under_2_5:
            result["over_under_2_5"] = self.over_under_2_5
        
        if self.btts:
            result["btts"] = self.btts
        
        return result
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return (
            f"{self.home_team} vs {self.away_team}\n"
            f"Expected Goals: {self.home_lambda} - {self.away_lambda}\n"
            f"Probabilities: Home {self.home_win_prob:.1%} | Draw {self.draw_prob:.1%} | Away {self.away_win_prob:.1%}\n"
            f"Most Likely Score: {self.most_likely_score[0]}-{self.most_likely_score[1]} ({self.most_likely_score_prob:.1%})\n"
            f"Favorite: {self.get_favorite().replace('_', ' ').title()} (Confidence: {self.get_confidence():.1%})"
        )
