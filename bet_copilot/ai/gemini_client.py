"""
Gemini AI client for contextual analysis of betting opportunities.
Analyzes news, injuries, form, and sentiment.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    # Use google.generativeai (the correct package)
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from bet_copilot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


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


class GeminiClient:
    """
    Client for Google Gemini AI to provide contextual analysis.
    
    Analyzes:
    - Team news (injuries, suspensions)
    - Recent form and momentum
    - Head-to-head history
    - External factors (weather, motivation)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model to use (default: gemini-pro)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model
        self.model = None

        if not GEMINI_AVAILABLE:
            logger.warning(
                "google-generativeai not installed. Install with: "
                "pip install google-generativeai"
            )
            return

        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model)
            logger.info(f"Gemini client initialized with model {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    def is_available(self) -> bool:
        """Check if Gemini is available and configured."""
        return GEMINI_AVAILABLE and self.model is not None

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
        Analyze match context and suggest lambda adjustments.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_form: Recent form (e.g., "WWDLW")
            away_form: Recent form
            h2h_results: Head-to-head results (e.g., ["H", "A", "D"])
            additional_context: Extra context (news, injuries, etc.)
            
        Returns:
            ContextualAnalysis with lambda adjustments
        """
        if not self.is_available():
            logger.warning("Gemini not available, returning neutral analysis")
            return self._neutral_analysis(home_team, away_team)

        # Build prompt
        prompt = self._build_analysis_prompt(
            home_team, away_team, home_form, away_form, h2h_results, additional_context
        )

        try:
            # Call Gemini API (sync, so run in executor)
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_response, prompt
            )

            # Parse response
            analysis = self._parse_response(response, home_team, away_team)
            logger.info(
                f"Gemini analysis complete: "
                f"home_adj={analysis.lambda_adjustment_home:.2f}, "
                f"away_adj={analysis.lambda_adjustment_away:.2f}"
            )

            return analysis

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._neutral_analysis(home_team, away_team)

    def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini (sync method)."""
        response = self.model.generate_content(prompt)
        return response.text

    def _build_analysis_prompt(
        self,
        home_team: str,
        away_team: str,
        home_form: str,
        away_form: str,
        h2h_results: Optional[List[str]],
        additional_context: Optional[str],
    ) -> str:
        """Build prompt for Gemini."""
        h2h_str = ", ".join(h2h_results) if h2h_results else "No data"

        prompt = f"""
You are a sports analytics AI helping to predict football match outcomes.

Match: {home_team} vs {away_team}

Context:
- Home team form (last 5): {home_form} (W=Win, D=Draw, L=Loss)
- Away team form (last 5): {away_form}
- Head-to-head (last 5): {h2h_str} (H=Home win, A=Away win, D=Draw)
"""

        if additional_context:
            prompt += f"\nAdditional context:\n{additional_context}\n"

        prompt += """
Based on this context, provide lambda adjustments for our Poisson model:

Task:
1. Analyze team form, momentum, and context
2. Identify key factors (injuries, suspensions, motivation, etc.)
3. Suggest lambda adjustments (multipliers) for expected goals
   - Values: 0.8-1.2 (0.9 = -10%, 1.1 = +10%)
   - Default is 1.0 (no adjustment)
4. Explain reasoning

Output format (strict JSON):
{
    "home_adjustment": 1.0,
    "away_adjustment": 1.0,
    "confidence": 0.7,
    "key_factors": ["Factor 1", "Factor 2"],
    "sentiment": "NEUTRAL",
    "reasoning": "Brief explanation"
}

Important:
- Be conservative (small adjustments)
- Only deviate from 1.0 if strong evidence
- Confidence: 0.0-1.0 (how confident in adjustments)
- Sentiment: POSITIVE (home favored), NEUTRAL, NEGATIVE (away favored)
"""

        return prompt

    def _parse_response(
        self, response_text: str, home_team: str, away_team: str
    ) -> ContextualAnalysis:
        """Parse Gemini response into ContextualAnalysis."""
        try:
            # Extract JSON from response (might have markdown)
            import json
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group(0))

            return ContextualAnalysis(
                home_team=home_team,
                away_team=away_team,
                confidence=float(data.get("confidence", 0.5)),
                lambda_adjustment_home=float(data.get("home_adjustment", 1.0)),
                lambda_adjustment_away=float(data.get("away_adjustment", 1.0)),
                key_factors=data.get("key_factors", []),
                sentiment=data.get("sentiment", "NEUTRAL"),
                reasoning=data.get("reasoning", "No reasoning provided"),
            )

        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            return self._neutral_analysis(home_team, away_team)

    def _neutral_analysis(self, home_team: str, away_team: str) -> ContextualAnalysis:
        """Return neutral analysis (no adjustments)."""
        return ContextualAnalysis(
            home_team=home_team,
            away_team=away_team,
            confidence=0.5,
            lambda_adjustment_home=1.0,
            lambda_adjustment_away=1.0,
            key_factors=["No AI analysis available"],
            sentiment="NEUTRAL",
            reasoning="Gemini not available or error occurred",
        )

    async def analyze_multiple_matches(
        self, matches: List[Dict]
    ) -> List[ContextualAnalysis]:
        """
        Analyze multiple matches in parallel.
        
        Args:
            matches: List of dicts with match data
            
        Returns:
            List of ContextualAnalysis
        """
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
