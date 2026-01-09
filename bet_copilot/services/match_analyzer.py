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
from bet_copilot.api.multi_source_client import MultiSourceFootballClient
from bet_copilot.ai.gemini_client import GeminiClient
from bet_copilot.ai.blackbox_client import BlackboxClient
from bet_copilot.ai.collaborative_analyzer import CollaborativeAnalyzer, CollaborativeAnalysis
from bet_copilot.ai.types import ContextualAnalysis
from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.math_engine.kelly import KellyCriterion, KellyRecommendation
from bet_copilot.math_engine.alternative_markets import (
    AlternativeMarketsPredictor,
    AlternativeMarketPrediction,
)
from bet_copilot.models.soccer import TeamForm, MatchResult, MatchPrediction
from bet_copilot.news import NewsScraper, NewsArticle

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
    
    # Predicciones de mercados alternativos
    corners_prediction: Optional[AlternativeMarketPrediction] = None
    cards_prediction: Optional[AlternativeMarketPrediction] = None
    shots_prediction: Optional[AlternativeMarketPrediction] = None
    
    # Análisis colaborativo (si ambas IAs disponibles)
    collaborative_analysis: Optional[CollaborativeAnalysis] = None
    
    # Noticias relevantes
    relevant_news: Optional[List[NewsArticle]] = None

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
        multi_source_client: Optional[MultiSourceFootballClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        blackbox_client: Optional[BlackboxClient] = None,
        soccer_predictor: Optional[SoccerPredictor] = None,
        kelly: Optional[KellyCriterion] = None,
        alternative_markets: Optional[AlternativeMarketsPredictor] = None,
        news_scraper: Optional[NewsScraper] = None,
        use_collaborative_analysis: bool = True,
    ):
        self.odds_client = odds_client or OddsAPIClient()
        self.football_client = football_client or FootballAPIClient()
        self.multi_source = multi_source_client or MultiSourceFootballClient()
        self.gemini_client = gemini_client or GeminiClient()
        self.blackbox_client = blackbox_client or BlackboxClient()
        self.soccer_predictor = soccer_predictor or SoccerPredictor()
        self.kelly = kelly or KellyCriterion()
        self.alternative_markets = alternative_markets or AlternativeMarketsPredictor()
        self.news_scraper = news_scraper or NewsScraper()
        self.use_collaborative = use_collaborative_analysis
        
        # Initialize collaborative analyzer
        self.collaborative_analyzer = CollaborativeAnalyzer(
            gemini_client=self.gemini_client,
            blackbox_client=self.blackbox_client
        )
        
        logger.info("MatchAnalyzer initialized with multi-source support")

    async def analyze_match(
        self,
        home_team_name: str,
        away_team_name: str,
        league_id: int = 39,  # Premier League default
        season: int = 2024,
        include_players: bool = True,
        include_ai_analysis: bool = True,
        fetch_odds: bool = True,
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
            fetch_odds: Obtener cuotas de Odds API
            
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

        # 1. Buscar IDs de equipos usando multi-source
        logger.info("🔍 Searching teams across multiple sources...")
        home_team_id, home_team_full_name, home_source = await self.multi_source.search_team(
            home_team_name, league_id
        )
        away_team_id, away_team_full_name, away_source = await self.multi_source.search_team(
            away_team_name, league_id
        )

        if not home_team_id or not away_team_id:
            logger.error("❌ Could not find teams in any source")
            return analysis
        
        logger.info(f"✓ {home_team_full_name} found in {home_source}")
        logger.info(f"✓ {away_team_full_name} found in {away_source}")

        # 2. Obtener estadísticas de equipos usando multi-source
        logger.info("📊 Fetching team statistics...")
        try:
            home_stats = await self.multi_source.get_team_stats(
                home_team_id, home_team_full_name, home_source, league_id, season
            )
            away_stats = await self.multi_source.get_team_stats(
                away_team_id, away_team_full_name, away_source, league_id, season
            )
            
            analysis.home_stats = home_stats
            analysis.away_stats = away_stats
            
            logger.info(f"✓ Home stats: {home_stats.wins}W-{home_stats.draws}D-{home_stats.losses}L")
            logger.info(f"✓ Away stats: {away_stats.wins}W-{away_stats.draws}D-{away_stats.losses}L")

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

        # 5. Obtener noticias relevantes (sin API calls)
        try:
            logger.info("Fetching relevant news from free sources...")
            all_news = await self.news_scraper.fetch_all_news(max_per_source=10)
            
            # Filter news relevant to these teams
            relevant_news = self.news_scraper.filter_by_teams(
                all_news, [home_team_name, away_team_name]
            )
            
            # Prioritize injury/suspension news
            injury_news = self.news_scraper.filter_by_category(
                relevant_news, ["injury"]
            )
            
            analysis.relevant_news = relevant_news[:5]  # Top 5 most recent
            
            logger.info(
                f"✓ Found {len(relevant_news)} relevant news articles "
                f"({len(injury_news)} injury-related)"
            )
        
        except Exception as e:
            logger.warning(f"Error fetching news: {str(e)}")
        
        # 6. Análisis contextual con IA (colaborativo si ambas disponibles)
        if include_ai_analysis:
            try:
                home_form = analysis.home_stats.form if analysis.home_stats else ""
                away_form = analysis.away_stats.form if analysis.away_stats else ""
                h2h_results = (
                    analysis.h2h_stats.last_5_results if analysis.h2h_stats else None
                )

                # Construir contexto adicional con jugadores Y noticias
                additional_context = ""
                
                # Jugadores ausentes
                if analysis.home_lineup and analysis.home_lineup.missing_players:
                    missing_names = [p.player_name for p in analysis.home_lineup.missing_players]
                    additional_context += f"{home_team_name} ausentes: {', '.join(missing_names)}\n"

                if analysis.away_lineup and analysis.away_lineup.missing_players:
                    missing_names = [p.player_name for p in analysis.away_lineup.missing_players]
                    additional_context += f"{away_team_name} ausentes: {', '.join(missing_names)}\n"
                
                # Noticias recientes
                if analysis.relevant_news:
                    additional_context += "\nNoticias recientes:\n"
                    for news in analysis.relevant_news[:3]:
                        additional_context += f"- {news.title}\n"

                # Usar análisis colaborativo si ambas IAs disponibles
                if (self.use_collaborative and 
                    self.collaborative_analyzer.is_collaborative_available()):
                    
                    logger.info("🤝 Running collaborative AI analysis (Gemini + Blackbox)...")
                    
                    collaborative_result = await self.collaborative_analyzer.analyze_match_comprehensive(
                        home_team_name,
                        away_team_name,
                        home_form,
                        away_form,
                        h2h_results,
                        additional_context if additional_context else None,
                    )
                    
                    analysis.collaborative_analysis = collaborative_result
                    analysis.ai_analysis = collaborative_result.consensus
                    
                    logger.info(
                        f"✓ Collaborative analysis complete "
                        f"(agreement: {collaborative_result.agreement_score:.0%}, "
                        f"confidence: {collaborative_result.consensus.confidence:.0%})"
                    )
                
                else:
                    # Single AI analysis
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
                if analysis.prediction and analysis.ai_analysis:
                    adjusted_home_lambda = (
                        analysis.prediction.home_lambda
                        * analysis.ai_analysis.lambda_adjustment_home
                    )
                    adjusted_away_lambda = (
                        analysis.prediction.away_lambda
                        * analysis.ai_analysis.lambda_adjustment_away
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

        # 7. Calcular recomendaciones Kelly si hay predicción y odds
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

        # 7b. Obtener odds si se solicita
        if fetch_odds and self.odds_client:
            try:
                logger.info(f"Fetching odds for {home_team_name} vs {away_team_name}...")
                
                # Map league_id to odds API sport key
                sport_key_map = {
                    39: "soccer_epl",  # Premier League
                    140: "soccer_spain_la_liga",  # La Liga
                    78: "soccer_germany_bundesliga",  # Bundesliga
                    135: "soccer_italy_serie_a",  # Serie A
                    61: "soccer_france_ligue_one",  # Ligue 1
                    # Add more leagues as needed
                }
                
                sport_key = sport_key_map.get(league_id, "soccer_epl")
                
                # Get odds from The Odds API
                odds_events = await self.odds_client.get_odds(
                    sport_key=sport_key,
                    regions="us,uk,eu",  # Multiple regions for better coverage
                    markets="h2h",  # Head-to-head market
                    odds_format="decimal"
                )
                
                # Find match by team names (fuzzy matching)
                for event in odds_events:
                    home_match = (
                        home_team_name.lower() in event.home_team.lower() or
                        event.home_team.lower() in home_team_name.lower()
                    )
                    away_match = (
                        away_team_name.lower() in event.away_team.lower() or
                        event.away_team.lower() in away_team_name.lower()
                    )
                    
                    if home_match and away_match:
                        logger.info(f"✓ Found matching event: {event.home_team} vs {event.away_team}")
                        
                        # Get best odds from all bookmakers
                        best_home = 0.0
                        best_draw = 0.0
                        best_away = 0.0
                        best_bookmaker = ""
                        
                        for bookmaker in event.bookmakers:
                            for market in bookmaker.markets:
                                if market.key == "h2h":
                                    outcomes = market.outcomes
                                    home_odd = outcomes.get(event.home_team, 0.0)
                                    draw_odd = outcomes.get("Draw", 0.0)
                                    away_odd = outcomes.get(event.away_team, 0.0)
                                    
                                    # Take best odds (highest)
                                    if home_odd > best_home:
                                        best_home = home_odd
                                    if draw_odd > best_draw:
                                        best_draw = draw_odd
                                    if away_odd > best_away:
                                        best_away = away_odd
                                        best_bookmaker = bookmaker.title
                        
                        if best_home > 0:
                            analysis.home_odds = best_home
                            analysis.draw_odds = best_draw if best_draw > 0 else None
                            analysis.away_odds = best_away
                            analysis.bookmaker = f"Best Odds (via The Odds API)"
                            
                            logger.info(
                                f"✓ Real odds from {best_bookmaker}: "
                                f"H={best_home:.2f} D={best_draw:.2f} A={best_away:.2f}"
                            )
                        break
                
                if not analysis.home_odds:
                    logger.info("No matching odds found in The Odds API")
                            
            except Exception as e:
                logger.warning(f"Error fetching odds: {str(e)}")
        
        # 7c. Calcular Kelly con odds
        if analysis.prediction:
            if analysis.home_odds:
                analysis.kelly_home = self.kelly.calculate(
                    analysis.prediction.home_win_prob, analysis.home_odds
                )
                logger.info(f"Kelly Home: EV={analysis.kelly_home.ev:+.1%}, Value={analysis.kelly_home.is_value_bet}")
                
            if analysis.away_odds:
                analysis.kelly_away = self.kelly.calculate(
                    analysis.prediction.away_win_prob, analysis.away_odds
                )
                logger.info(f"Kelly Away: EV={analysis.kelly_away.ev:+.1%}, Value={analysis.kelly_away.is_value_bet}")
                
            if analysis.draw_odds:
                analysis.kelly_draw = self.kelly.calculate(
                    analysis.prediction.draw_prob, analysis.draw_odds
                )
                logger.info(f"Kelly Draw: EV={analysis.kelly_draw.ev:+.1%}, Value={analysis.kelly_draw.is_value_bet}")
        
        # 8. Predicciones de mercados alternativos (si hay datos históricos)
        if analysis.home_stats and analysis.away_stats:
            try:
                # Construir TeamForm desde estadísticas disponibles
                # Necesitamos datos históricos detallados para esto
                # Por ahora, solo calculamos si tenemos partidos recientes con stats
                
                home_recent = await self.football_client.get_team_recent_matches_with_stats(
                    home_team_id, season, league_id, last_n=5
                )
                away_recent = await self.football_client.get_team_recent_matches_with_stats(
                    away_team_id, season, league_id, last_n=5
                )
                
                if home_recent and away_recent:
                    # Construir TeamForm con datos avanzados
                    home_form = self._build_team_form_from_matches(
                        home_team_name, home_recent, home_team_id
                    )
                    away_form = self._build_team_form_from_matches(
                        away_team_name, away_recent, away_team_id
                    )
                    
                    # Predicciones de mercados alternativos
                    analysis.corners_prediction = self.alternative_markets.predict_corners(
                        home_form, away_form, matches_to_consider=5
                    )
                    
                    analysis.cards_prediction = self.alternative_markets.predict_cards(
                        home_form, away_form, matches_to_consider=5
                    )
                    
                    analysis.shots_prediction = self.alternative_markets.predict_shots(
                        home_form, away_form, matches_to_consider=5
                    )
                    
                    logger.info(
                        f"Mercados alternativos: "
                        f"Corners={analysis.corners_prediction.total_expected:.1f}, "
                        f"Cards={analysis.cards_prediction.total_expected:.1f}, "
                        f"Shots={analysis.shots_prediction.total_expected:.1f}"
                    )
                
            except Exception as e:
                logger.warning(f"No se pudieron calcular mercados alternativos: {str(e)}")
        
        # 9. Asegurar que siempre hay odds (usar implícitas si no hay reales)
        if analysis.prediction and not analysis.home_odds:
            # Use fair odds WITH typical bookmaker margin
            # This way EV will be negative unless AI provides strong adjustments
            margin = 1.08  # 8% bookmaker margin (typical)
            
            analysis.home_odds = (1.0 / analysis.prediction.home_win_prob) / margin
            analysis.draw_odds = (1.0 / analysis.prediction.draw_prob) / margin
            analysis.away_odds = (1.0 / analysis.prediction.away_win_prob) / margin
            analysis.bookmaker = "Estimated Odds"
            
            # Calculate Kelly with estimated odds
            analysis.kelly_home = self.kelly.calculate(
                analysis.prediction.home_win_prob, analysis.home_odds
            )
            analysis.kelly_draw = self.kelly.calculate(
                analysis.prediction.draw_prob, analysis.draw_odds
            )
            analysis.kelly_away = self.kelly.calculate(
                analysis.prediction.away_win_prob, analysis.away_odds
            )
            
            logger.info(
                f"Using estimated odds: H={analysis.home_odds:.2f} "
                f"D={analysis.draw_odds:.2f} A={analysis.away_odds:.2f}"
            )

        return analysis
    
    def _build_team_form_from_matches(
        self, team_name: str, matches: List[Dict], team_id: int
    ) -> TeamForm:
        """
        Construye TeamForm desde lista de partidos con estadísticas detalladas.
        
        Args:
            team_name: Nombre del equipo
            matches: Lista de partidos con estadísticas
            team_id: ID del equipo (no usado directamente, para referencia)
            
        Returns:
            TeamForm con datos históricos
        """
        team_form = TeamForm(team_name=team_name)
        
        for match in matches:
            try:
                date_str = match.get("date", "")
                match_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                
                home_team = match.get("home_team")
                away_team = match.get("away_team")
                is_home = (home_team == team_name)
                
                home_stats = match.get("home_stats", {})
                away_stats = match.get("away_stats", {})
                
                # Crear MatchResult con estadísticas avanzadas
                match_result = MatchResult(
                    date=match_date,
                    home_team=home_team,
                    away_team=away_team,
                    home_goals=match.get("home_goals", 0),
                    away_goals=match.get("away_goals", 0),
                    home_xg=0.0,  # xG no disponible en API-Football básico
                    away_xg=0.0,
                    is_home=is_home,
                    # Estadísticas avanzadas
                    home_corners=home_stats.get("corners"),
                    away_corners=away_stats.get("corners"),
                    home_shots=home_stats.get("shots"),
                    away_shots=away_stats.get("shots"),
                    home_shots_on_target=home_stats.get("shots_on_target"),
                    away_shots_on_target=away_stats.get("shots_on_target"),
                    home_fouls=home_stats.get("fouls"),
                    away_fouls=away_stats.get("fouls"),
                    home_yellow_cards=home_stats.get("yellow_cards"),
                    away_yellow_cards=away_stats.get("yellow_cards"),
                    home_red_cards=home_stats.get("red_cards"),
                    away_red_cards=away_stats.get("red_cards"),
                    home_offsides=home_stats.get("offsides"),
                    away_offsides=away_stats.get("offsides"),
                    home_possession=home_stats.get("possession"),
                    away_possession=away_stats.get("possession"),
                )
                
                team_form.add_match(match_result)
                
            except Exception as e:
                logger.warning(f"Error procesando partido: {str(e)}")
                continue
        
        return team_form

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
