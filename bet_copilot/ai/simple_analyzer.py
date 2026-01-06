"""
Simple rule-based analyzer as ultimate fallback.
Uses statistical heuristics when AI providers are unavailable.
"""

import logging
from typing import Dict, List, Optional

from bet_copilot.ai.types import ContextualAnalysis

logger = logging.getLogger(__name__)


class SimpleAnalyzer:
    """
    Simple rule-based analyzer using form analysis.
    
    Fallback when AI providers (Gemini/Blackbox) are unavailable.
    Uses basic statistical heuristics instead of AI.
    """
    
    def __init__(self):
        """Initialize simple analyzer."""
        logger.info("Simple analyzer initialized (rule-based fallback)")
    
    def is_available(self) -> bool:
        """Simple analyzer is always available."""
        return True
    
    async def analyze_match_context(
        self,
        home_team: str,
        away_team: str,
        home_form: str,
        away_form: str,
        h2h_results: Optional[List[str]] = None,
        additional_context: Optional[str] = None,
    ) -> ContextualAnalysis:
        """
        Analyze match using simple heuristics.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_form: Recent form (e.g., "WWDLW")
            away_form: Recent form
            h2h_results: Head-to-head results (e.g., ["H", "A", "D"])
            additional_context: Extra context (injuries, news, etc.)
            
        Returns:
            ContextualAnalysis with basic adjustments
        """
        # Analyze form
        home_score = self._calculate_form_score(home_form)
        away_score = self._calculate_form_score(away_form)
        
        # Analyze H2H if available
        h2h_factor = self._analyze_h2h(h2h_results) if h2h_results else 0.0
        
        # Check for keywords in additional context
        context_factors = self._analyze_context(additional_context) if additional_context else {}
        
        # Calculate adjustments
        home_adj = 1.0
        away_adj = 1.0
        key_factors = []
        
        # Form-based adjustments (±10% max)
        form_diff = home_score - away_score
        if form_diff > 0.3:
            home_adj += 0.1
            away_adj -= 0.05
            key_factors.append(f"{home_team} en mejor forma reciente")
        elif form_diff < -0.3:
            home_adj -= 0.05
            away_adj += 0.1
            key_factors.append(f"{away_team} en mejor forma reciente")
        
        # H2H adjustments (±5% max)
        if h2h_factor > 0.2:
            home_adj += 0.05
            key_factors.append(f"{home_team} domina historial H2H")
        elif h2h_factor < -0.2:
            away_adj += 0.05
            key_factors.append(f"{away_team} domina historial H2H")
        
        # Context adjustments (injuries, suspensions)
        if context_factors.get('home_injuries', 0) > 0:
            home_adj -= 0.05 * context_factors['home_injuries']
            key_factors.append(f"{home_team} con jugadores lesionados")
        
        if context_factors.get('away_injuries', 0) > 0:
            away_adj -= 0.05 * context_factors['away_injuries']
            key_factors.append(f"{away_team} con jugadores lesionados")
        
        # Clamp adjustments to reasonable range
        home_adj = max(0.8, min(1.2, home_adj))
        away_adj = max(0.8, min(1.2, away_adj))
        
        # Determine sentiment
        if home_adj > away_adj + 0.05:
            sentiment = "POSITIVE"
        elif away_adj > home_adj + 0.05:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        # Build reasoning
        reasoning = self._build_reasoning(
            home_team, away_team, home_score, away_score, 
            h2h_factor, context_factors
        )
        
        # Confidence based on data available
        confidence = 0.6  # Base confidence for rule-based
        if h2h_results:
            confidence += 0.1
        if additional_context:
            confidence += 0.1
        confidence = min(0.8, confidence)  # Max 80% for non-AI
        
        if not key_factors:
            key_factors = ["Análisis basado en forma reciente"]
        
        return ContextualAnalysis(
            home_team=home_team,
            away_team=away_team,
            confidence=confidence,
            lambda_adjustment_home=home_adj,
            lambda_adjustment_away=away_adj,
            key_factors=key_factors,
            sentiment=sentiment,
            reasoning=reasoning,
        )
    
    def _calculate_form_score(self, form: str) -> float:
        """
        Calculate form score from recent results.
        
        Args:
            form: String like "WWDLW" (W=Win, D=Draw, L=Loss)
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not form:
            return 0.5  # Neutral
        
        points = 0
        for result in form.upper():
            if result == 'W':
                points += 3
            elif result == 'D':
                points += 1
            elif result == 'L':
                points += 0
        
        max_points = len(form) * 3
        return points / max_points if max_points > 0 else 0.5
    
    def _analyze_h2h(self, h2h_results: List[str]) -> float:
        """
        Analyze head-to-head results.
        
        Args:
            h2h_results: List like ["H", "A", "D", "H", "A"]
                H = Home win, A = Away win, D = Draw
                
        Returns:
            Factor between -1.0 and 1.0 (positive favors home)
        """
        if not h2h_results:
            return 0.0
        
        home_wins = h2h_results.count('H')
        away_wins = h2h_results.count('A')
        total = len(h2h_results)
        
        return (home_wins - away_wins) / total if total > 0 else 0.0
    
    def _analyze_context(self, context: str) -> Dict[str, int]:
        """
        Analyze additional context for keywords.
        
        Args:
            context: Additional text context
            
        Returns:
            Dict with factors found
        """
        if not context:
            return {}
        
        context_lower = context.lower()
        factors = {}
        
        # Look for injury keywords
        injury_keywords = ['lesionado', 'lesionada', 'lesión', 'injured', 'injury']
        has_injury = any(keyword in context_lower for keyword in injury_keywords)
        
        if has_injury:
            # Count occurrences
            injury_count = sum(context_lower.count(keyword) for keyword in injury_keywords)
            
            # Default to home injuries if not specified
            # In real usage, we get team names and check context around keywords
            factors['home_injuries'] = 1
        
        return factors
    
    def _build_reasoning(
        self,
        home_team: str,
        away_team: str,
        home_score: float,
        away_score: float,
        h2h_factor: float,
        context_factors: Dict,
    ) -> str:
        """Build human-readable reasoning."""
        parts = []
        
        # Form analysis
        if home_score > away_score + 0.2:
            parts.append(f"{home_team} muestra mejor forma reciente ({home_score:.0%} vs {away_score:.0%})")
        elif away_score > home_score + 0.2:
            parts.append(f"{away_team} muestra mejor forma reciente ({away_score:.0%} vs {home_score:.0%})")
        else:
            parts.append(f"Ambos equipos con forma similar ({home_score:.0%} vs {away_score:.0%})")
        
        # H2H
        if h2h_factor > 0.2:
            parts.append(f"{home_team} domina enfrentamientos directos")
        elif h2h_factor < -0.2:
            parts.append(f"{away_team} domina enfrentamientos directos")
        
        # Context
        if context_factors.get('home_injuries'):
            parts.append(f"Bajas importantes en {home_team}")
        if context_factors.get('away_injuries'):
            parts.append(f"Bajas importantes en {away_team}")
        
        if not parts:
            parts.append("Datos limitados para análisis profundo")
        
        parts.append("(Análisis heurístico simple, no AI)")
        
        return ". ".join(parts) + "."
    
    async def analyze_multiple_matches(
        self, matches: List[Dict]
    ) -> List[ContextualAnalysis]:
        """Analyze multiple matches."""
        import asyncio
        
        tasks = [
            self.analyze_match_context(
                match["home_team"],
                match["away_team"],
                match.get("home_form", ""),
                match.get("away_form", ""),
                match.get("h2h_results"),
                match.get("additional_context"),
            )
            for match in matches
        ]
        
        return await asyncio.gather(*tasks)
    
    async def close(self):
        """No resources to close."""
        pass
