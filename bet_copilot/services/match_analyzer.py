"""
Servicio integrador para análisis completo de partidos.
Combina datos de Odds API, API-Football y Gemini AI.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from bet_copilot.api.odds_client import OddsAPIClient
from bet_copilot.api.football_client import (
    FootballAPIClient,
    TeamStats,
    H2HStats,
    PlayerStats,
    TeamLineup,
)
from bet_copilot.ai.gemini_client import GeminiClient, ContextualAnalysis
from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.math_engine.kelly import KellyCriterion, KellyRecommendation
from bet_copilot.models.soccer import TeamForm, MatchResult, MatchPrediction

logger = logging.getLogger(__name__)


@dataclass
class EnhancedMatchAnalysis:
    """Análisis completo de un partido con todos los datos."""

    # Información básica
    home_team: str
    away_team: str
    league: str
    commence_time: datetime

    # Estadísticas de equipos
    home_stats: Optional[TeamStats] = None
    away_stats: Optional[TeamStats] = None

    # Estadísticas H2H
    h2h_stats: Optional[H2HStats] = None

    # Jugadores
    home_lineup: Optional[TeamLineup] = None
    away_lineup: Optional[TeamLineup] = None

    # Cuotas
    home_odds: Optional[float] = None
    away_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    bookmaker: Optional[str] = None

    # Predicción matemática
    prediction: Optional[MatchPrediction] = None

    # Análisis contextual IA
    ai_analysis: Optional[ContextualAnalysis] = None

    # Recomendación Kelly
    kelly_home: Optional[KellyRecommendation] = None
    kelly_away: Optional[KellyRecommendation] = None
    kelly_draw: Optional[KellyRecommendation] = None

    def get_best_value_bet(self) -> Optional[Dict]:
        """Obtiene la mejor apuesta de valor."""
        bets = []

        if self.kelly_home and self.kelly_home.is_value_bet:
            bets.append(
                {
                    "outcome": "Victoria Local",
                    "team": self.home_team,
                    "ev": self.kelly_home.ev,
                    "stake": self.kelly_home.recommended_stake,
                    "odds": self.kelly_home.odds,
                    "risk": self.kelly_home.risk_level,
                }
            )

        if self.kelly_away and self.kelly_away.is_value_bet:
            bets.append(
                {
                    "outcome": "Victoria Visitante",
                    "team": self.away_team,
                    "ev": self.kelly_away.ev,
                    "stake": self.kelly_away.recommended_stake,
                    "odds": self.kelly_away.odds,
                    "risk": self.kelly_away.risk_level,
                }
            )

        if self.kelly_draw and self.kelly_draw.is_value_bet:
            bets.append(
                {
                    "outcome": "Empate",
                    "team": None,
                    "ev": self.kelly_draw.ev,
                    "stake": self.kelly_draw.recommended_stake,
                    "odds": self.kelly_draw.odds,
                    "risk": self.kelly_draw.risk_level,
                }
            )

        if not bets:
            return None

        # Retornar la de mayor EV
        return max(bets, key=lambda x: x["ev"])

    def get_key_insights(self) -> List[str]:
        """Genera insights clave del análisis."""
        insights = []

        # Análisis de forma
        if self.home_stats and self.away_stats:
            if self.home_stats.form.count("W") >= 3:
                insights.append(f"🔥 {self.home_team} en buena racha ({self.home_stats.form})")
            if self.away_stats.form.count("L") >= 3:
                insights.append(f"📉 {self.away_team} en mala racha ({self.away_stats.form})")

        # Jugadores ausentes
        if self.home_lineup:
            missing = self.home_lineup.count_missing_key_players()
            if missing > 0:
                insights.append(f"⚠️ {self.home_team} sin {missing} jugador(es) clave")

        if self.away_lineup:
            missing = self.away_lineup.count_missing_key_players()
            if missing > 0:
                insights.append(f"⚠️ {self.away_team} sin {missing} jugador(es) clave")

        # H2H
        if self.h2h_stats and self.h2h_stats.matches_played >= 3:
            home_win_pct = (
                self.h2h_stats.home_wins / self.h2h_stats.matches_played
            ) * 100
            if home_win_pct >= 60:
                insights.append(
                    f"📊 {self.home_team} domina historial ({home_win_pct:.0f}% victorias)"
                )

        # Análisis IA
        if self.ai_analysis:
            insights.extend(self.ai_analysis.key_factors[:3])

        return insights


class MatchAnalyzer:
    """
    Servicio integrador para análisis completo de partidos.
    
    Combina:
    1. Odds API (cuotas en tiempo real)
    2. API-Football (stats, jugadores, H2H)
    3. Gemini AI (contexto y sentimiento)
    4. Motor Poisson (predicción matemática)
    5. Kelly Criterion (sizing óptimo)
    """

    def __init__(
        self,
        odds_client: Optional[OddsAPIClient] = None,
        football_client: Optional[FootballAPIClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        soccer_predictor: Optional[SoccerPredictor] = None,
        kelly: Optional[KellyCriterion] = None,
    ):
        self.odds_client = odds_client or OddsAPIClient()
        self.football_client = football_client or FootballAPIClient()
        self.gemini_client = gemini_client or GeminiClient()
        self.soccer_predictor = soccer_predictor or SoccerPredictor()
        self.kelly = kelly or KellyCriterion()

    async def analyze_match(
        self,
        home_team_name: str,
        away_team_name: str,
        league_id: int = 39,  # Premier League default
        season: int = 2024,
        include_players: bool = True,
        include_ai_analysis: bool = True,
    ) -> EnhancedMatchAnalysis:
        """
        Análisis completo de un partido.
        
        Args:
            home_team_name: Nombre del equipo local
            away_team_name: Nombre del equipo visitante
            league_id: ID de la liga
            season: Temporada
            include_players: Incluir análisis de jugadores
            include_ai_analysis: Incluir análisis de Gemini
            
        Returns:
            EnhancedMatchAnalysis con todos los datos
        """
        logger.info(f"Analizando: {home_team_name} vs {away_team_name}")

        analysis = EnhancedMatchAnalysis(
            home_team=home_team_name,
            away_team=away_team_name,
            league=f"League {league_id}",
            commence_time=datetime.now(),
        )

        # 1. Buscar IDs de equipos
        home_team_id = await self.football_client.search_team_by_name(home_team_name)
        away_team_id = await self.football_client.search_team_by_name(away_team_name)

        if not home_team_id or not away_team_id:
            logger.warning("No se pudieron encontrar los equipos en API-Football")
            return analysis

        # 2. Obtener estadísticas de equipos (en paralelo)
        home_stats_task = self.football_client.get_team_stats(
            home_team_id, season, league_id
        )
        away_stats_task = self.football_client.get_team_stats(
            away_team_id, season, league_id
        )
        h2h_task = self.football_client.get_h2h_stats(home_team_id, away_team_id)

        try:
            home_stats, away_stats, h2h_stats = await asyncio.gather(
                home_stats_task, away_stats_task, h2h_task, return_exceptions=True
            )

            if not isinstance(home_stats, Exception):
                analysis.home_stats = home_stats
            if not isinstance(away_stats, Exception):
                analysis.away_stats = away_stats
            if not isinstance(h2h_stats, Exception):
                analysis.h2h_stats = h2h_stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")

        # 3. Obtener jugadores e lesiones si se solicita
        if include_players and home_team_id and away_team_id:
            try:
                home_players_task = self.football_client.get_team_players(
                    home_team_id, season
                )
                away_players_task = self.football_client.get_team_players(
                    away_team_id, season
                )
                home_injuries_task = self.football_client.get_team_injuries(
                    home_team_id, season, league_id
                )
                away_injuries_task = self.football_client.get_team_injuries(
                    away_team_id, season, league_id
                )

                (
                    home_players,
                    away_players,
                    home_injuries,
                    away_injuries,
                ) = await asyncio.gather(
                    home_players_task,
                    away_players_task,
                    home_injuries_task,
                    away_injuries_task,
                    return_exceptions=True,
                )

                if not isinstance(home_players, Exception):
                    analysis.home_lineup = TeamLineup(
                        team_id=home_team_id,
                        team_name=home_team_name,
                        starting_xi=home_players[:11],
                        substitutes=home_players[11:],
                        missing_players=home_injuries
                        if not isinstance(home_injuries, Exception)
                        else [],
                    )

                if not isinstance(away_players, Exception):
                    analysis.away_lineup = TeamLineup(
                        team_id=away_team_id,
                        team_name=away_team_name,
                        starting_xi=away_players[:11],
                        substitutes=away_players[11:],
                        missing_players=away_injuries
                        if not isinstance(away_injuries, Exception)
                        else [],
                    )

            except Exception as e:
                logger.warning(f"Error obteniendo jugadores: {str(e)}")

        # 4. Calcular predicción Poisson con stats reales
        if analysis.home_stats and analysis.away_stats:
            # Usar xG aproximado de goles promedio
            home_xg = analysis.home_stats.avg_goals_for
            away_xg = analysis.away_stats.avg_goals_against

            prediction = self.soccer_predictor.predict_from_lambdas(
                home_team_name,
                away_team_name,
                lambda_home=home_xg,
                lambda_away=away_xg,
                include_details=True,
            )

            analysis.prediction = prediction

        # 5. Análisis contextual con IA
        if include_ai_analysis and self.gemini_client.is_available():
            try:
                home_form = analysis.home_stats.form if analysis.home_stats else ""
                away_form = analysis.away_stats.form if analysis.away_stats else ""
                h2h_results = (
                    analysis.h2h_stats.last_5_results if analysis.h2h_stats else None
                )

                # Construir contexto adicional
                additional_context = ""
                if analysis.home_lineup and analysis.home_lineup.missing_players:
                    missing_names = [p.player_name for p in analysis.home_lineup.missing_players]
                    additional_context += f"{home_team_name} ausentes: {', '.join(missing_names)}\n"

                if analysis.away_lineup and analysis.away_lineup.missing_players:
                    missing_names = [p.player_name for p in analysis.away_lineup.missing_players]
                    additional_context += f"{away_team_name} ausentes: {', '.join(missing_names)}\n"

                ai_analysis = await self.gemini_client.analyze_match_context(
                    home_team_name,
                    away_team_name,
                    home_form,
                    away_form,
                    h2h_results,
                    additional_context if additional_context else None,
                )

                analysis.ai_analysis = ai_analysis

                # Ajustar predicción con IA
                if analysis.prediction and ai_analysis:
                    adjusted_home_lambda = (
                        analysis.prediction.home_lambda
                        * ai_analysis.lambda_adjustment_home
                    )
                    adjusted_away_lambda = (
                        analysis.prediction.away_lambda
                        * ai_analysis.lambda_adjustment_away
                    )

                    # Recalcular con lambdas ajustadas
                    analysis.prediction = self.soccer_predictor.predict_from_lambdas(
                        home_team_name,
                        away_team_name,
                        lambda_home=adjusted_home_lambda,
                        lambda_away=adjusted_away_lambda,
                        include_details=True,
                    )

            except Exception as e:
                logger.warning(f"Error en análisis IA: {str(e)}")

        # 6. Calcular recomendaciones Kelly si hay predicción y odds
        if analysis.prediction:
            # Home win
            if analysis.home_odds:
                analysis.kelly_home = self.kelly.calculate(
                    analysis.prediction.home_win_prob, analysis.home_odds
                )

            # Away win
            if analysis.away_odds:
                analysis.kelly_away = self.kelly.calculate(
                    analysis.prediction.away_win_prob, analysis.away_odds
                )

            # Draw
            if analysis.draw_odds:
                analysis.kelly_draw = self.kelly.calculate(
                    analysis.prediction.draw_prob, analysis.draw_odds
                )

        return analysis

    async def analyze_from_odds_event(
        self, odds_event, league_id: int = 39, season: int = 2024
    ) -> EnhancedMatchAnalysis:
        """
        Analizar partido desde OddsEvent.
        
        Args:
            odds_event: OddsEvent de Odds API
            league_id: ID de liga para API-Football
            season: Temporada
            
        Returns:
            EnhancedMatchAnalysis
        """
        # Extraer mejor odds
        home_odds = odds_event.get_best_odds("h2h", odds_event.home_team)
        away_odds = odds_event.get_best_odds("h2h", odds_event.away_team)

        # Intentar obtener draw odds
        draw_odds = None
        for bookmaker in odds_event.bookmakers:
            for market in bookmaker.markets:
                if market.key == "h2h" and "Draw" in market.outcomes:
                    draw_odds = market.outcomes["Draw"]
                    break

        bookmaker_name = (
            odds_event.bookmakers[0].title if odds_event.bookmakers else "Unknown"
        )

        # Crear análisis
        analysis = await self.analyze_match(
            odds_event.home_team,
            odds_event.away_team,
            league_id=league_id,
            season=season,
            include_players=True,
            include_ai_analysis=True,
        )

        # Agregar odds
        analysis.home_odds = home_odds
        analysis.away_odds = away_odds
        analysis.draw_odds = draw_odds
        analysis.bookmaker = bookmaker_name
        analysis.commence_time = odds_event.commence_time

        # Recalcular Kelly con odds reales
        if analysis.prediction:
            if home_odds:
                analysis.kelly_home = self.kelly.calculate(
                    analysis.prediction.home_win_prob, home_odds
                )
            if away_odds:
                analysis.kelly_away = self.kelly.calculate(
                    analysis.prediction.away_win_prob, away_odds
                )
            if draw_odds:
                analysis.kelly_draw = self.kelly.calculate(
                    analysis.prediction.draw_prob, draw_odds
                )

        return analysis
