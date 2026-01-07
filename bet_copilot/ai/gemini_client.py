"""
Gemini AI client for contextual analysis of betting opportunities.
Analyzes news, injuries, form, and sentiment.
"""

import asyncio
import logging
from typing import Dict, List, Optional

try:
    # Use google.genai (new SDK)
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from bet_copilot.config import GEMINI_API_KEY
from bet_copilot.ai.types import ContextualAnalysis

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for Google Gemini AI to provide contextual analysis.
    
    Analyzes:
    - Team news (injuries, suspensions)
    - Recent form and momentum
    - Head-to-head history
    - External factors (weather, motivation)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model
        self.client = None

        if not GEMINI_AVAILABLE:
            logger.warning(
                "google-genai not installed. Install with: "
                "pip install google-genai"
            )
            return

        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini client initialized with model {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    def is_available(self) -> bool:
        """Check if Gemini is available and configured."""
        return GEMINI_AVAILABLE and self.client is not None

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
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
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
Eres un analista experto de fútbol con profundo conocimiento de tácticas, rendimiento de jugadores y tendencias estadísticas.

Partido: {home_team} vs {away_team}

Contexto:
- Forma equipo local (últimos 5): {home_form} (W=Victoria, D=Empate, L=Derrota)
- Forma equipo visitante (últimos 5): {away_form}
- Historial directo (últimos 5): {h2h_str} (H=Victoria local, A=Victoria visitante, D=Empate)
"""

        if additional_context:
            prompt += f"\nContexto adicional:\n{additional_context}\n"

        prompt += """
Tu tarea es analizar este partido desde múltiples ángulos:

1. **Análisis Táctico**:
   - Considera estilos de juego (ofensivo vs defensivo, posesión vs contraataque)
   - Enfrentamientos de formaciones y ventajas tácticas
   - Cómo los equipos típicamente abordan partidos de local vs visitante

2. **Factores Clave**:
   - Forma reciente y cambios de momentum
   - Lesiones/suspensiones de jugadores clave
   - Factores de motivación (lucha por descenso, carrera por título, derbi, etc.)
   - Condiciones climáticas o de estadio si son relevantes
   - Fatiga por partidos recientes

3. **Insights Estadísticos**:
   - Tendencias históricas entre estos equipos
   - Patrones en goles marcados/recibidos
   - Probabilidad de partido con muchos/pocos goles
   - Intensidad esperada (faltas, tarjetas, fisicalidad)

4. **Pistas de Mercados Alternativos**:
   - ¿Será un partido con muchos corners? (equipos ofensivos vs defensas cerradas)
   - ¿Muchas tarjetas? (enfrentamiento físico, árbitro estricto, rivalidad)
   - ¿Alto conteo de tiros? (equipos con posesión dominante)

Basado en tu análisis, proporciona:

Formato de salida (JSON estricto):
{
    "home_adjustment": 1.0,
    "away_adjustment": 1.0,
    "confidence": 0.7,
    "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
    "sentiment": "NEUTRAL",
    "reasoning": "Explicación de 2-3 oraciones cubriendo insights tácticos y contextuales EN ESPAÑOL",
    "alternative_markets_insights": {
        "corners": "Predicción: Alto/Medio/Bajo - razón",
        "cards": "Predicción: Alto/Medio/Bajo - razón",
        "total_goals": "Predicción: Alto/Medio/Bajo - razón"
    }
}

Directrices:
- Ajustes lambda: 0.8-1.2 (conservador, solo ajustar con evidencia fuerte)
- Confianza: 0.0-1.0 (basada en calidad de datos y claridad de tendencias)
- Sentimiento: POSITIVE (local favorecido), NEUTRAL, NEGATIVE (visitante favorecido)
- Enfócate en insights accionables, no comentarios genéricos
- IMPORTANTE: Escribe el 'reasoning' y 'key_factors' completamente en ESPAÑOL
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
            key_factors=["An\u00e1lisis de IA no disponible"],
            sentiment="NEUTRAL",
            reasoning="Gemini no disponible o ocurri\u00f3 un error",
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
