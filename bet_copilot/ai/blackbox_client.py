"""
Blackbox AI client as fallback for Gemini.
Uses Blackbox API for contextual analysis when Gemini is unavailable.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.config import BLACKBOX_API_KEY

logger = logging.getLogger(__name__)


@dataclass
class ContextualAnalysis:
    """Result of AI contextual analysis."""
    
    home_team: str
    away_team: str
    confidence: float  # 0-1, confidence in analysis
    lambda_adjustment_home: float  # Multiplier for home lambda
    lambda_adjustment_away: float  # Multiplier for away lambda
    key_factors: List[str]  # Important factors identified
    sentiment: str  # "POSITIVE", "NEUTRAL", "NEGATIVE"
    reasoning: str  # Explanation of adjustments


class BlackboxClient:
    """
    Client for Blackbox AI as fallback for Gemini.
    
    Uses OpenAI-compatible API format.
    Endpoint: https://api.blackbox.ai/chat/completions
    
    Provides same interface as GeminiClient for drop-in replacement.
    """
    
    # Official Blackbox API endpoint (OpenAI-compatible)
    API_URL = "https://api.blackbox.ai/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: str = "blackboxai-pro"):
        """
        Initialize Blackbox client.
        
        Args:
            api_key: Blackbox API key (get from https://www.blackbox.ai/)
            model: Model to use (default: blackboxai-pro)
                Options: blackboxai-pro, blackboxai, or any OpenAI/Anthropic model
        """
        self.api_key = api_key or BLACKBOX_API_KEY
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if self.api_key:
            logger.info(f"Blackbox client initialized with model {model} (authenticated)")
        else:
            logger.info(f"Blackbox client initialized with model {model} (no API key, limited)")
    
    def is_available(self) -> bool:
        """Check if Blackbox is available."""
        # Blackbox can work without API key (with limitations)
        return True
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
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
        # Build prompt
        prompt = self._build_analysis_prompt(
            home_team, away_team, home_form, away_form, h2h_results, additional_context
        )
        
        try:
            # Call Blackbox API
            response_text = await self._generate_response(prompt)
            
            # Parse response
            analysis = self._parse_response(response_text, home_team, away_team)
            
            logger.info(
                f"Blackbox analysis complete: "
                f"home_adj={analysis.lambda_adjustment_home:.2f}, "
                f"away_adj={analysis.lambda_adjustment_away:.2f}"
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Blackbox API error: {str(e)}")
            return self._neutral_analysis(home_team, away_team)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Blackbox API using OpenAI-compatible format."""
        session = await self._get_session()
        
        # OpenAI-compatible payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key if available (required for official API)
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            async with session.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    # Parse OpenAI-compatible response
                    data = await response.json()
                    
                    # Extract content from choices[0].message.content
                    if 'choices' in data and len(data['choices']) > 0:
                        message = data['choices'][0].get('message', {})
                        content = message.get('content', '')
                        return content
                    else:
                        logger.error(f"Unexpected response format: {data}")
                        raise Exception("Invalid response format")
                
                elif response.status == 401:
                    error_text = await response.text()
                    logger.error(f"Blackbox authentication failed. API key may be invalid.")
                    raise Exception(f"Authentication failed: {error_text[:100]}")
                
                else:
                    error_text = await response.text()
                    logger.error(f"Blackbox API error {response.status}: {error_text[:200]}")
                    raise Exception(f"API returned status {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("Blackbox API timeout (30s)")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Blackbox network error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Blackbox request failed: {str(e)}")
            raise
    
    def _build_analysis_prompt(
        self,
        home_team: str,
        away_team: str,
        home_form: str,
        away_form: str,
        h2h_results: Optional[List[str]],
        additional_context: Optional[str],
    ) -> str:
        """Build prompt for Blackbox."""
        h2h_str = ", ".join(h2h_results) if h2h_results else "No data"
        
        prompt = f"""You are a sports analytics AI helping to predict football match outcomes.

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

Respond ONLY with the JSON object, no additional text.
"""
        
        return prompt
    
    def _parse_response(
        self, response_text: str, home_team: str, away_team: str
    ) -> ContextualAnalysis:
        """Parse Blackbox response into ContextualAnalysis."""
        try:
            # Extract JSON from response
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in Blackbox response")
                return self._neutral_analysis(home_team, away_team)
            
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
            logger.error(f"Failed to parse Blackbox response: {str(e)}")
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
            reasoning="Blackbox not available or error occurred",
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
