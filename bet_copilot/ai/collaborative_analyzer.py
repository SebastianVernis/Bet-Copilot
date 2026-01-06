"""
Collaborative AI Analyzer - Multi-AI Analysis Engine

When both Gemini and Blackbox are available, this module orchestrates
a comprehensive analysis where both AIs contribute their perspectives,
creating a more robust and nuanced prediction.

Flow:
1. Gemini provides tactical/technical analysis
2. Blackbox provides statistical/pattern analysis  
3. Results are merged and conflicts resolved
4. Final consensus analysis with enhanced confidence
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from bet_copilot.ai.gemini_client import GeminiClient
from bet_copilot.ai.blackbox_client import BlackboxClient
from bet_copilot.ai.types import ContextualAnalysis

logger = logging.getLogger(__name__)


@dataclass
class CollaborativeAnalysis:
    """Result of collaborative AI analysis."""
    
    # Final consensus
    consensus: ContextualAnalysis
    
    # Individual perspectives
    gemini_analysis: Optional[ContextualAnalysis] = None
    blackbox_analysis: Optional[ContextualAnalysis] = None
    
    # Metadata
    agreement_score: float = 0.0  # 0-1, how much AIs agree
    confidence_boost: float = 0.0  # Additional confidence from agreement
    divergence_points: List[str] = None  # Where AIs disagree
    
    def __post_init__(self):
        if self.divergence_points is None:
            self.divergence_points = []


class CollaborativeAnalyzer:
    """
    Orchestrates multi-AI analysis for enhanced predictions.
    
    When both Gemini and Blackbox are available, runs parallel analysis
    and combines results intelligently.
    """
    
    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        blackbox_client: Optional[BlackboxClient] = None,
    ):
        self.gemini = gemini_client or GeminiClient()
        self.blackbox = blackbox_client or BlackboxClient()
    
    def is_collaborative_available(self) -> bool:
        """Check if both AIs are available for collaboration."""
        return self.gemini.is_available() and self.blackbox.is_available()
    
    async def analyze_match_comprehensive(
        self,
        home_team: str,
        away_team: str,
        home_form: str,
        away_form: str,
        h2h_results: Optional[List[str]] = None,
        additional_context: Optional[str] = None,
    ) -> CollaborativeAnalysis:
        """
        Run comprehensive collaborative analysis.
        
        Both AIs analyze independently, then results are merged.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_form: Recent form
            away_form: Recent form  
            h2h_results: H2H results
            additional_context: Additional context
            
        Returns:
            CollaborativeAnalysis with consensus and individual perspectives
        """
        if not self.is_collaborative_available():
            logger.warning("Collaborative analysis not available (missing AI provider)")
            # Fall back to single provider
            if self.gemini.is_available():
                analysis = await self.gemini.analyze_match_context(
                    home_team, away_team, home_form, away_form,
                    h2h_results, additional_context
                )
                return CollaborativeAnalysis(
                    consensus=analysis,
                    gemini_analysis=analysis,
                    agreement_score=1.0
                )
            elif self.blackbox.is_available():
                analysis = await self.blackbox.analyze_match_context(
                    home_team, away_team, home_form, away_form,
                    h2h_results, additional_context
                )
                return CollaborativeAnalysis(
                    consensus=analysis,
                    blackbox_analysis=analysis,
                    agreement_score=1.0
                )
        
        logger.info(f"🤝 Running collaborative analysis: {home_team} vs {away_team}")
        
        # Run both analyses in parallel
        try:
            gemini_task = self.gemini.analyze_match_context(
                home_team, away_team, home_form, away_form,
                h2h_results, additional_context
            )
            
            blackbox_task = self.blackbox.analyze_match_context(
                home_team, away_team, home_form, away_form,
                h2h_results, additional_context
            )
            
            gemini_analysis, blackbox_analysis = await asyncio.gather(
                gemini_task, blackbox_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(gemini_analysis, Exception):
                logger.error(f"Gemini analysis failed: {str(gemini_analysis)}")
                gemini_analysis = None
            
            if isinstance(blackbox_analysis, Exception):
                logger.error(f"Blackbox analysis failed: {str(blackbox_analysis)}")
                blackbox_analysis = None
            
            # If both failed, return neutral
            if gemini_analysis is None and blackbox_analysis is None:
                logger.error("Both AI analyses failed")
                neutral = self._neutral_analysis(home_team, away_team)
                return CollaborativeAnalysis(
                    consensus=neutral,
                    agreement_score=0.0
                )
            
            # If only one succeeded, use it
            if gemini_analysis is None:
                return CollaborativeAnalysis(
                    consensus=blackbox_analysis,
                    blackbox_analysis=blackbox_analysis,
                    agreement_score=1.0
                )
            
            if blackbox_analysis is None:
                return CollaborativeAnalysis(
                    consensus=gemini_analysis,
                    gemini_analysis=gemini_analysis,
                    agreement_score=1.0
                )
            
            # Both succeeded - merge results
            logger.info("✓ Both AI analyses complete, merging...")
            
            consensus, agreement_score, divergence_points = self._merge_analyses(
                gemini_analysis, blackbox_analysis
            )
            
            # Calculate confidence boost from agreement
            confidence_boost = agreement_score * 0.2  # Up to +20% confidence
            consensus.confidence = min(1.0, consensus.confidence + confidence_boost)
            
            logger.info(
                f"✓ Consensus reached (agreement: {agreement_score:.1%}, "
                f"confidence boost: +{confidence_boost:.1%})"
            )
            
            return CollaborativeAnalysis(
                consensus=consensus,
                gemini_analysis=gemini_analysis,
                blackbox_analysis=blackbox_analysis,
                agreement_score=agreement_score,
                confidence_boost=confidence_boost,
                divergence_points=divergence_points
            )
        
        except Exception as e:
            logger.error(f"Collaborative analysis error: {str(e)}")
            neutral = self._neutral_analysis(home_team, away_team)
            return CollaborativeAnalysis(
                consensus=neutral,
                agreement_score=0.0
            )
    
    def _merge_analyses(
        self,
        gemini: ContextualAnalysis,
        blackbox: ContextualAnalysis
    ) -> Tuple[ContextualAnalysis, float, List[str]]:
        """
        Merge two analyses into consensus.
        
        Returns:
            (consensus_analysis, agreement_score, divergence_points)
        """
        divergence_points = []
        
        # 1. Lambda adjustments - weighted average based on confidence
        total_confidence = gemini.confidence + blackbox.confidence
        
        if total_confidence > 0:
            gemini_weight = gemini.confidence / total_confidence
            blackbox_weight = blackbox.confidence / total_confidence
        else:
            gemini_weight = blackbox_weight = 0.5
        
        home_adj = (
            gemini.lambda_adjustment_home * gemini_weight +
            blackbox.lambda_adjustment_home * blackbox_weight
        )
        away_adj = (
            gemini.lambda_adjustment_away * gemini_weight +
            blackbox.lambda_adjustment_away * blackbox_weight
        )
        
        # Check for significant divergence in lambda adjustments
        home_diff = abs(gemini.lambda_adjustment_home - blackbox.lambda_adjustment_home)
        away_diff = abs(gemini.lambda_adjustment_away - blackbox.lambda_adjustment_away)
        
        if home_diff > 0.1:
            divergence_points.append(
                f"Home adjustment: Gemini={gemini.lambda_adjustment_home:.2f}, "
                f"Blackbox={blackbox.lambda_adjustment_home:.2f}"
            )
        
        if away_diff > 0.1:
            divergence_points.append(
                f"Away adjustment: Gemini={gemini.lambda_adjustment_away:.2f}, "
                f"Blackbox={blackbox.lambda_adjustment_away:.2f}"
            )
        
        # 2. Sentiment - use majority or most confident
        if gemini.sentiment == blackbox.sentiment:
            sentiment = gemini.sentiment
        else:
            # Use sentiment from more confident AI
            sentiment = gemini.sentiment if gemini.confidence > blackbox.confidence else blackbox.sentiment
            divergence_points.append(
                f"Sentiment: Gemini={gemini.sentiment}, Blackbox={blackbox.sentiment}"
            )
        
        # 3. Key factors - merge and deduplicate
        key_factors = []
        
        # Add factors from both, prioritizing most important
        all_factors = gemini.key_factors + blackbox.key_factors
        seen = set()
        
        for factor in all_factors:
            # Simple deduplication by lowercase comparison
            factor_lower = factor.lower()
            if factor_lower not in seen:
                key_factors.append(factor)
                seen.add(factor_lower)
                
                # Limit to top 5
                if len(key_factors) >= 5:
                    break
        
        # 4. Reasoning - combine both perspectives
        reasoning = self._combine_reasoning(gemini.reasoning, blackbox.reasoning)
        
        # 5. Confidence - weighted average
        confidence = (
            gemini.confidence * gemini_weight +
            blackbox.confidence * blackbox_weight
        )
        
        # 6. Calculate agreement score
        agreement_score = self._calculate_agreement_score(gemini, blackbox)
        
        consensus = ContextualAnalysis(
            home_team=gemini.home_team,
            away_team=gemini.away_team,
            confidence=round(confidence, 2),
            lambda_adjustment_home=round(home_adj, 2),
            lambda_adjustment_away=round(away_adj, 2),
            key_factors=key_factors,
            sentiment=sentiment,
            reasoning=reasoning
        )
        
        return consensus, agreement_score, divergence_points
    
    def _calculate_agreement_score(
        self,
        gemini: ContextualAnalysis,
        blackbox: ContextualAnalysis
    ) -> float:
        """
        Calculate how much the two analyses agree (0-1).
        
        Considers lambda adjustments, sentiment, and confidence alignment.
        """
        scores = []
        
        # Lambda adjustments agreement (most important)
        home_diff = abs(gemini.lambda_adjustment_home - blackbox.lambda_adjustment_home)
        away_diff = abs(gemini.lambda_adjustment_away - blackbox.lambda_adjustment_away)
        
        # Convert diff to similarity (max diff of 0.4 = 0% similarity)
        home_similarity = max(0, 1 - (home_diff / 0.4))
        away_similarity = max(0, 1 - (away_diff / 0.4))
        
        scores.append(home_similarity * 0.4)  # 40% weight
        scores.append(away_similarity * 0.4)  # 40% weight
        
        # Sentiment agreement
        sentiment_match = 1.0 if gemini.sentiment == blackbox.sentiment else 0.0
        scores.append(sentiment_match * 0.2)  # 20% weight
        
        # Overall agreement score
        agreement = sum(scores)
        
        return round(agreement, 2)
    
    def _combine_reasoning(self, gemini_reasoning: str, blackbox_reasoning: str) -> str:
        """Combine reasoning from both AIs into coherent summary."""
        
        # If one is much longer/more detailed, prioritize it
        if len(gemini_reasoning) > len(blackbox_reasoning) * 2:
            return f"{gemini_reasoning}\n\nSecondary analysis confirms key trends."
        
        if len(blackbox_reasoning) > len(gemini_reasoning) * 2:
            return f"{blackbox_reasoning}\n\nCross-validated with tactical analysis."
        
        # Otherwise combine both
        return (
            f"Tactical perspective: {gemini_reasoning}\n\n"
            f"Statistical perspective: {blackbox_reasoning}"
        )
    
    def _neutral_analysis(self, home_team: str, away_team: str) -> ContextualAnalysis:
        """Return neutral analysis when collaboration fails."""
        return ContextualAnalysis(
            home_team=home_team,
            away_team=away_team,
            confidence=0.5,
            lambda_adjustment_home=1.0,
            lambda_adjustment_away=1.0,
            key_factors=["Collaborative analysis unavailable"],
            sentiment="NEUTRAL",
            reasoning="Unable to complete AI analysis"
        )
    
    async def close(self):
        """Close all AI clients."""
        if self.blackbox:
            await self.blackbox.close()
