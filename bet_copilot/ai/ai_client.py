"""
Unified AI client with automatic fallback.
Tries Gemini first, falls back to Blackbox if unavailable.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from bet_copilot.ai.types import ContextualAnalysis
from bet_copilot.ai.blackbox_client import BlackboxClient
from bet_copilot.ai.simple_analyzer import SimpleAnalyzer

logger = logging.getLogger(__name__)


class AIClient:
    """
    Unified AI client with automatic fallback.
    
    Priority:
    1. Blackbox (primary, if configured and available)
    2. SimpleAnalyzer (ultimate fallback, always available)
    
    Provides same interface as BlackboxClient for drop-in replacement.
    """
    
    def __init__(
        self,
        blackbox_api_key: Optional[str] = None,
    ):
        """
        Initialize AI client with fallback.
        
        Args:
            blackbox_api_key: Blackbox API key (optional)
        """
        # Initialize providers
        self.blackbox = BlackboxClient(api_key=blackbox_api_key)
        self.simple = SimpleAnalyzer()  # Always available
        
        # Determine primary
        if self.blackbox.is_available():
            self.primary = self.blackbox
            self.primary_name = "Blackbox"
        else:
            self.primary = self.simple
            self.primary_name = "SimpleAnalyzer"
        
        # Build fallback chain
        self.fallback_chain = []
        if self.blackbox.is_available() and self.primary != self.blackbox:
            self.fallback_chain.append(("Blackbox", self.blackbox))
        if self.primary != self.simple:
            self.fallback_chain.append(("SimpleAnalyzer", self.simple))
        
        fallback_names = ", ".join(name for name, _ in self.fallback_chain) or "None"
        logger.info(
            f"AI client initialized. Primary: {self.primary_name}, "
            f"Fallbacks: [{fallback_names}]"
        )
    
    def is_available(self) -> bool:
        """Check if any AI client is available."""
        return self.primary.is_available() or any(
            client.is_available() for _, client in self.fallback_chain
        )
    
    def get_active_provider(self) -> str:
        """Get name of currently active provider."""
        return self.primary_name
    
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
        Analyze match context with automatic multi-level fallback.
        
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
        # Try primary client
        try:
            logger.info(f"Attempting analysis with {self.primary_name}")
            analysis = await self.primary.analyze_match_context(
                home_team, away_team, home_form, away_form,
                h2h_results, additional_context
            )
            
            # Check if we got a real analysis (not neutral fallback)
            if analysis.confidence > 0.5 or analysis.lambda_adjustment_home != 1.0:
                logger.info(f"✓ Analysis successful with {self.primary_name}")
                return analysis
            else:
                raise Exception("Primary returned neutral analysis")
        
        except Exception as e:
            logger.warning(f"Primary ({self.primary_name}) failed: {str(e)[:100]}")
            
            # Try fallback chain
            for fallback_name, fallback_client in self.fallback_chain:
                try:
                    logger.info(f"Falling back to {fallback_name}")
                    analysis = await fallback_client.analyze_match_context(
                        home_team, away_team, home_form, away_form,
                        h2h_results, additional_context
                    )
                    
                    # SimpleAnalyzer always returns valid result
                    if fallback_name == "SimpleAnalyzer" or analysis.confidence > 0.5:
                        logger.info(f"✓ Fallback successful with {fallback_name}")
                        return analysis
                
                except Exception as e2:
                    logger.warning(f"Fallback ({fallback_name}) failed: {str(e2)[:100]}")
                    continue
            
            # All failed (shouldn't happen with SimpleAnalyzer), return neutral
            logger.error("All providers failed, returning neutral analysis")
            return self._neutral_analysis(home_team, away_team)
    
    async def analyze_multiple_matches(
        self, matches: List[Dict]
    ) -> List[ContextualAnalysis]:
        """
        Analyze multiple matches in parallel with fallback.
        
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
    
    def _neutral_analysis(self, home_team: str, away_team: str) -> ContextualAnalysis:
        """Return neutral analysis when all providers fail."""
        return ContextualAnalysis(
            home_team=home_team,
            away_team=away_team,
            confidence=0.5,
            lambda_adjustment_home=1.0,
            lambda_adjustment_away=1.0,
            key_factors=["No AI analysis available"],
            sentiment="NEUTRAL",
            reasoning="All AI providers unavailable or failed",
        )
    
    async def close(self):
        """Close all client sessions."""
        await self.blackbox.close()
        await self.simple.close()


# Convenience function for drop-in replacement
def create_ai_client(
    blackbox_api_key: Optional[str] = None,
) -> AIClient:
    """
    Create AI client with automatic fallback.
    
    Args:
        blackbox_api_key: Blackbox API key (optional)
        
    Returns:
        AIClient instance
    """
    return AIClient(
        blackbox_api_key=blackbox_api_key,
    )
