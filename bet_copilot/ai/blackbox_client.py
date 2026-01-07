"""
Blackbox AI client as fallback for Gemini.
Uses Blackbox API for contextual analysis when Gemini is unavailable.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional

import aiohttp

from bet_copilot.config import BLACKBOX_API_KEY
from bet_copilot.ai.types import ContextualAnalysis

logger = logging.getLogger(__name__)


class BlackboxClient:
    """
    Client for Blackbox AI as fallback for Gemini.
    
    Uses OpenAI-compatible API format.
    Endpoint: https://api.blackbox.ai/chat/completions
    
    Provides same interface as GeminiClient for drop-in replacement.
    """
    
    # Official Blackbox API endpoint (OpenAI-compatible)
    API_URL = "https://api.blackbox.ai/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: str = "blackboxai/anthropic/claude-sonnet-4"):
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
        
        prompt = f"""Eres una IA de análisis deportivo que ayuda a predecir resultados de partidos de fútbol.

Partido: {home_team} vs {away_team}

Contexto:
- Forma equipo local (últimos 5): {home_form} (W=Victoria, D=Empate, L=Derrota)
- Forma equipo visitante (últimos 5): {away_form}
- Historial directo (últimos 5): {h2h_str} (H=Victoria local, A=Victoria visitante, D=Empate)
"""
        
        if additional_context:
            prompt += f"\nContexto adicional:\n{additional_context}\n"
        
        prompt += """
Basado en este contexto, proporciona ajustes lambda para nuestro modelo de Poisson:

Tarea:
1. Analiza forma de equipos, momentum y contexto
2. Identifica factores clave (lesiones, suspensiones, motivación, etc.)
3. Sugiere ajustes lambda (multiplicadores) para goles esperados
   - Valores: 0.8-1.2 (0.9 = -10%, 1.1 = +10%)
   - Por defecto es 1.0 (sin ajuste)
4. Explica el razonamiento

Formato de salida (JSON estricto):
{
    "home_adjustment": 1.0,
    "away_adjustment": 1.0,
    "confidence": 0.7,
    "key_factors": ["Factor 1", "Factor 2"],
    "sentiment": "NEUTRAL",
    "reasoning": "Explicación breve EN ESPAÑOL"
}

Importante:
- Sé conservador (ajustes pequeños)
- Solo desvíate de 1.0 si hay evidencia fuerte
- Confianza: 0.0-1.0 (qué tan confiado en los ajustes)
- Sentimiento: POSITIVE (local favorecido), NEUTRAL, NEGATIVE (visitante favorecido)
- CRUCIAL: Escribe el 'reasoning' y 'key_factors' completamente en ESPAÑOL

Responde SOLO con el objeto JSON, sin texto adicional.
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
            key_factors=["An\u00e1lisis de IA no disponible"],
            sentiment="NEUTRAL",
            reasoning="Blackbox no disponible o ocurri\u00f3 un error",
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
