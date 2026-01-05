"""
Common types for AI analysis.
Shared across all AI providers (Gemini, Blackbox, SimpleAnalyzer).
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ContextualAnalysis:
    """Result of AI contextual analysis."""

    home_team: str
    away_team: str
    confidence: float  # 0-1, confidence in analysis
    lambda_adjustment_home: float  # Multiplier for home lambda (e.g., 0.9 = -10%)
    lambda_adjustment_away: float  # Multiplier for away lambda
    key_factors: List[str]  # Important factors identified
    sentiment: str  # "POSITIVE", "NEUTRAL", "NEGATIVE"
    reasoning: str  # Explanation of adjustments
