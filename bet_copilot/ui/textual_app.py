"""
Textual TUI Application - Interactive Dashboard

Modern TUI with reactive updates, keyboard shortcuts, and full interactivity.
Alternative to Rich-based CLI for users who prefer persistent dashboards.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, DataTable, Input, Button, 
    Label, ProgressBar, Placeholder
)
from textual.reactive import reactive
from textual.message import Message
from textual.suggester import Suggester

from bet_copilot.news import NewsScraper, NewsArticle
from bet_copilot.services.match_analyzer import MatchAnalyzer
from bet_copilot.api.odds_client import OddsAPIClient
from bet_copilot.api.football_client_with_fallback import create_football_client
from bet_copilot.ai.ai_client import create_ai_client
from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.math_engine.kelly import KellyCriterion
from bet_copilot.math_engine.alternative_markets import AlternativeMarketsPredictor

logger = logging.getLogger(__name__)


class BetCopilotSuggester(Suggester):
    """Custom suggester for command autocompletion in TUI."""
    
    def __init__(self, app_instance=None):
        super().__init__()
        self.app_instance = app_instance
        
        # Base commands
        self.commands = [
            "ayuda", "help",
            "salud", "health",
            "dashboard",
            "mercados", "markets",
            "analizar", "analyze", "analyse",
            "salir", "quit", "exit",
        ]
        
        # Sport keys
        self.sport_keys = [
            "soccer_epl", "soccer_la_liga", "soccer_serie_a",
            "soccer_bundesliga", "soccer_france_ligue_one",
            "soccer_brazil_campeonato", "soccer_uefa_champs_league",
            "soccer_uefa_europa_league", "soccer_portugal_primeira_liga",
            "soccer_netherlands_eredivisie",
            "americanfootball_nfl", "basketball_nba", "icehockey_nhl",
        ]
    
    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestion based on current input."""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        parts = value_lower.split()
        
        # No parts - suggest first command
        if not parts:
            return None
        
        # First word - command completion
        if len(parts) == 1:
            for cmd in self.commands:
                if cmd.startswith(value_lower) and cmd != value_lower:
                    return cmd
            return None
        
        # Second word - context-specific suggestions
        if len(parts) >= 2:
            command = parts[0]
            
            # Sport keys for mercados/markets
            if command in ["mercados", "markets"]:
                arg = " ".join(parts[1:]).lower()
                for sport_key in self.sport_keys:
                    if sport_key.startswith(arg) and sport_key != arg:
                        return f"{command} {sport_key}"
            
            # Match names for analizar/analyze
            elif command in ["analizar", "analyze", "analyse"]:
                if self.app_instance and hasattr(self.app_instance, 'events'):
                    arg = " ".join(parts[1:]).lower()
                    for event in self.app_instance.events:
                        match_str = f"{event.home_team} vs {event.away_team}"
                        if match_str.lower().startswith(arg) and match_str.lower() != arg:
                            return f"{command} {match_str}"
        
        return None


class APIHealthWidget(Static):
    """
    API Health Status Display.
    
    Shows real-time status of all API endpoints with request counts.
    """
    
    odds_status = reactive("unknown")
    football_status = reactive("unknown")
    blackbox_status = reactive("unknown")
    
    odds_requests = reactive(0)
    football_requests = reactive(0)
    
    def compose(self) -> ComposeResult:
        yield Label("🏥 API Health Monitor")
        yield Static(id="health-content")
    
    def watch_odds_status(self, status: str) -> None:
        """Update when odds status changes."""
        self.update_display()
    
    def watch_football_status(self, status: str) -> None:
        """Update when football status changes."""
        self.update_display()
    
    def update_display(self):
        """Render current status."""
        content = self.query_one("#health-content", Static)
        
        # Status icons
        def status_icon(status: str) -> str:
            if status == "healthy":
                return "🟢"
            elif status == "degraded":
                return "🟡"
            elif status == "down":
                return "🔴"
            else:
                return "⚪"
        
        content.update(
            f"{status_icon(self.odds_status)} Odds API       "
            f"{self.odds_requests}/500 daily\n"
            f"{status_icon(self.football_status)} Football API   "
            f"{self.football_requests}/100 daily\n"
            f"{status_icon(self.blackbox_status)} Blackbox AI   "
            f"{'✓' if self.blackbox_status == 'healthy' else '✗'}"
        )


class NewsWidget(Static):
    """
    Live news feed from free sources.
    
    Auto-refreshes every hour, shows latest football news.
    """
    
    articles = reactive([])
    loading = reactive(False)
    
    def compose(self) -> ComposeResult:
        yield Label("📰 Live News Feed")
        yield ScrollableContainer(id="news-list")
    
    async def on_mount(self) -> None:
        """Fetch news on startup."""
        await self.refresh_news()
        
        # Auto-refresh every 30 minutes
        self.set_interval(1800, self.refresh_news)
    
    async def refresh_news(self) -> None:
        """Fetch latest news."""
        self.loading = True
        
        try:
            scraper = NewsScraper()
            articles = await scraper.fetch_all_news(max_per_source=10)
            await scraper.close()
            
            logger.info(f"Fetched {len(articles)} news articles")
            self.articles = articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            self.articles = []
        finally:
            self.loading = False
    
    def watch_articles(self, articles: List[NewsArticle]) -> None:
        """Update display when articles change."""
        try:
            container = self.query_one("#news-list", ScrollableContainer)
            container.remove_children()
            
            if self.loading:
                container.mount(Label("🔄 Loading news..."))
                return
            
            if not articles:
                container.mount(Label("[dim]No news available[/dim]"))
                return
            
            logger.info(f"Displaying {len(articles)} articles")
            
            for article in articles[:10]:
                # Time ago
                time_diff = (datetime.now() - article.published).total_seconds() / 3600
                if time_diff < 1:
                    time_str = f"{int(time_diff * 60)}m"
                elif time_diff < 24:
                    time_str = f"{int(time_diff)}h"
                else:
                    time_str = f"{int(time_diff / 24)}d"
                
                # Category emoji
                emoji = {
                    "injury": "🏥",
                    "transfer": "🔄",
                    "match_preview": "⚽",
                    "general": "📋"
                }.get(article.category, "📋")
                
                # Render article
                article_text = (
                    f"[dim]{time_str}[/dim] {emoji} {article.title[:50]}\n"
                    f"[dim]{article.source}[/dim]"
                )
                
                container.mount(Label(article_text))
        
        except Exception as e:
            logger.error(f"Error updating news display: {str(e)}")


class MarketWatchWidget(Static):
    """
    Market watch with live value bets.
    
    Shows EV opportunities across traditional and alternative markets.
    """
    
    markets = reactive([])
    last_update = reactive("")
    
    def compose(self) -> ComposeResult:
        yield Label("📊 Market Watch")
        yield DataTable(id="markets-table")
        yield Label("", id="last-update")
    
    def on_mount(self) -> None:
        """Initialize table."""
        table = self.query_one(DataTable)
        
        # Add columns
        table.add_column("Match", width=30)
        table.add_column("Market", width=15)
        table.add_column("EV", width=10)
        table.add_column("Odds", width=8)
        table.add_column("Conf", width=6)
        
        table.cursor_type = "row"  # Allow row selection
        
        # Auto-refresh every 5 minutes
        self.set_interval(300, self.refresh_markets)
        
        # Load initial data
        asyncio.create_task(self.refresh_markets())
    
    async def refresh_markets(self) -> None:
        """Fetch latest market opportunities from live odds."""
        try:
            app = self.app
            if not hasattr(app, 'odds_client'):
                return
            
            # Get top leagues matches
            sports = await app.odds_client.get_sports()
            if not sports:
                return
            
            # Get soccer matches
            soccer_key = next((s['key'] for s in sports if 'soccer' in s['key'].lower()), None)
            if not soccer_key:
                return
            
            odds = await app.odds_client.get_odds(sport_key=soccer_key, regions="us", markets="h2h")
            
            # Analyze top 5 matches
            markets = []
            for match in odds[:5]:
                try:
                    home_team = match.get('home_team', '')
                    away_team = match.get('away_team', '')
                    
                    # Quick analysis
                    analysis = await app.match_analyzer.analyze_match(
                        home_team=home_team,
                        away_team=away_team
                    )
                    
                    if analysis:
                        # Add value bets
                        if analysis.kelly_home and analysis.kelly_home.is_value_bet:
                            markets.append({
                                "id": f"{home_team}-home",
                                "match": f"{home_team} vs {away_team}",
                                "market_type": "Home Win",
                                "ev": analysis.kelly_home.ev,
                                "odds": analysis.kelly_home.odds,
                                "confidence": analysis.ai_analysis.confidence if analysis.ai_analysis else 0.5
                            })
                        
                        if analysis.kelly_away and analysis.kelly_away.is_value_bet:
                            markets.append({
                                "id": f"{away_team}-away",
                                "match": f"{home_team} vs {away_team}",
                                "market_type": "Away Win",
                                "ev": analysis.kelly_away.ev,
                                "odds": analysis.kelly_away.odds,
                                "confidence": analysis.ai_analysis.confidence if analysis.ai_analysis else 0.5
                            })
                except Exception as e:
                    logger.error(f"Error analyzing {home_team} vs {away_team}: {str(e)}")
                    continue
            
            self.markets = markets
            self.last_update = datetime.now().strftime("%H:%M:%S")
            
        except Exception as e:
            logger.error(f"Error refreshing markets: {str(e)}")
    
    def watch_markets(self, markets) -> None:
        """Update table when markets change."""
        table = self.query_one(DataTable)
        table.clear()
        
        if not markets:
            return
        
        for market in markets:
            ev = market.get('ev', 0)
            ev_str = f"{ev:+.1%}"
            
            # Mark value bets with emoji
            is_value = market.get('is_value', False)
            market_type = market.get('market_type', '')
            if is_value:
                market_type = f"✅ {market_type}"
            
            table.add_row(
                market.get('match', ''),
                market_type,
                ev_str,
                f"{market.get('odds', 0):.2f}",
                "⭐" * int(market.get('confidence', 0) * 5),
                key=market.get('id', ''),
            )
    
    def watch_last_update(self, timestamp: str) -> None:
        """Update timestamp label."""
        label = self.query_one("#last-update", Label)
        label.update(f"[dim]Last update: {timestamp}[/dim]")


class AlternativeMarketsWidget(Static):
    """
    Alternative markets summary.
    
    Quick view of corners, cards, shots predictions.
    """
    
    corners_data = reactive(None)
    cards_data = reactive(None)
    shots_data = reactive(None)
    
    def compose(self) -> ComposeResult:
        yield Label("📐 Alternative Markets")
        
        with Horizontal():
            yield Static("🏁 Corners: [dim]--[/dim]", id="corners-summary")
            yield Static("🟨 Cards: [dim]--[/dim]", id="cards-summary")
            yield Static("🎯 Shots: [dim]--[/dim]", id="shots-summary")
    
    def watch_corners_data(self, data) -> None:
        """Update corners display."""
        widget = self.query_one("#corners-summary", Static)
        if data and data.get('expected'):
            expected = data.get('expected', 0)
            widget.update(f"🏁 Corners: [bold cyan]{expected:.1f}[/bold cyan]")
        else:
            widget.update("🏁 Corners: [dim]N/A[/dim]")
    
    def watch_cards_data(self, data) -> None:
        """Update cards display."""
        widget = self.query_one("#cards-summary", Static)
        if data and data.get('expected'):
            expected = data.get('expected', 0)
            widget.update(f"🟨 Cards: [bold yellow]{expected:.1f}[/bold yellow]")
        else:
            widget.update("🟨 Cards: [dim]N/A[/dim]")
    
    def watch_shots_data(self, data) -> None:
        """Update shots display."""
        widget = self.query_one("#shots-summary", Static)
        if data and data.get('expected'):
            expected = data.get('expected', 0)
            widget.update(f"🎯 Shots: [bold green]{expected:.1f}[/bold green]")
        else:
            widget.update("🎯 Shots: [dim]N/A[/dim]")


class PredictionWidget(Static):
    """
    Match prediction display widget.
    
    Shows Poisson prediction, probabilities, and most likely score.
    """
    
    prediction_data = reactive(None)
    
    def compose(self) -> ComposeResult:
        yield Label("⚽ Match Prediction")
        yield Static(
            "[dim]No match analyzed yet\\n\\nType a match below:\\n'Arsenal vs Chelsea'\\n\\nThen press Enter[/dim]",
            id="prediction-content"
        )
    
    def watch_prediction_data(self, data) -> None:
        """Update prediction display."""
        content = self.query_one("#prediction-content", Static)
        
        if not data:
            content.update("[dim]No prediction available[/dim]")
            return
        
        pred = data.get('prediction')
        ai = data.get('ai_analysis')
        collab = data.get('collaborative_analysis')
        
        if not pred:
            content.update("[dim]No prediction data[/dim]")
            return
        
        # Build display
        display = f"""[bold]{data.get('home_team', '')}[/bold] vs [bold]{data.get('away_team', '')}[/bold]

Expected Goals:
  Home: [cyan]{pred.home_goals:.2f}[/cyan]  |  Away: [cyan]{pred.away_goals:.2f}[/cyan]

Win Probabilities:
  Home: [green]{pred.home_win_prob:.1%}[/green]
  Draw: [yellow]{pred.draw_prob:.1%}[/yellow]
  Away: [red]{pred.away_win_prob:.1%}[/red]

Most Likely: [bold]{pred.most_likely_score}[/bold]
"""
        
        # Show collaborative analysis info if available
        if collab:
            display += f"\n[bold]🤝 Collaborative AI:[/bold] Agreement {collab.agreement_score:.0%}"
            display += f"\n[bold]AI Confidence:[/bold] {'⭐' * int(ai.confidence * 5)} ({ai.confidence:.0%})"
        elif ai:
            display += f"\n[bold]AI Confidence:[/bold] {'⭐' * int(ai.confidence * 5)} ({ai.confidence:.0%})"
        
        if ai and ai.key_factors:
            display += f"\n\n[bold]Key Factors:[/bold]\n"
            for factor in ai.key_factors[:3]:
                display += f"  • {factor}\n"
        
        content.update(display)


class BetCopilotApp(App):
    """
    Main Bet-Copilot Textual Application.
    
    Interactive TUI with live updates, keyboard shortcuts, and reactive data.
    """
    
    CSS = """
    Screen {
        background: #0a0a0a;
    }
    
    #top-row {
        height: 10;
        margin: 1;
    }
    
    #api-health {
        width: 1fr;
        border: solid green;
        padding: 1;
    }
    
    #news-feed {
        width: 1fr;
        border: solid cyan;
        padding: 1;
        overflow-y: auto;
    }
    
    #middle-row {
        height: 1fr;
        margin: 1;
    }
    
    #prediction {
        width: 2fr;
        border: solid cyan;
        padding: 1;
    }
    
    #market-watch {
        width: 3fr;
        border: solid yellow;
        padding: 1;
    }
    
    #market-watch {
        height: 1fr;
        border: solid yellow;
        margin: 1;
        padding: 1;
    }
    
    #alternative-markets {
        height: 5;
        border: solid magenta;
        margin: 1;
        padding: 1;
    }
    
    #input-row {
        height: 3;
        dock: bottom;
        background: #1a1a1a;
    }
    
    DataTable {
        background: #0f0f0f;
        color: #39ff14;
    }
    
    DataTable > .datatable--cursor {
        background: #2a2a2a;
    }
    
    Input {
        border: solid cyan;
    }
    
    Button {
        margin: 0 1;
    }
    
    Label {
        color: #00ffff;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_all", "Refresh All"),
        ("n", "toggle_news", "Toggle News"),
        ("m", "toggle_markets", "Alternative Markets"),
        ("ctrl+c", "quit", "Quit"),
    ]
    
    TITLE = "BET-COPILOT v0.5 - Multi-AI Analysis Dashboard"
    SUB_TITLE = "Collaborative Analysis | Alternative Markets | Live News"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize services
        self.odds_client = OddsAPIClient()
        self.football_client = create_football_client()  # With fallback to SimpleProvider
        self.ai_client = create_ai_client()  # Unified AI with fallback
        self.soccer_predictor = SoccerPredictor()
        self.kelly = KellyCriterion()
        
        # MatchAnalyzer creates its own clients for collaborative analysis
        self.match_analyzer = MatchAnalyzer(
            odds_client=self.odds_client,
            football_client=self.football_client,
            soccer_predictor=self.soccer_predictor,
            kelly=self.kelly,
            use_collaborative_analysis=True,
        )
        self.alt_markets = AlternativeMarketsPredictor()
    
    def compose(self) -> ComposeResult:
        """Create layout."""
        yield Header()
        
        # Top row: API Health + News
        with Horizontal(id="top-row"):
            yield APIHealthWidget(id="api-health")
            yield NewsWidget(id="news-feed")
        
        # Middle row: Prediction + Market Watch
        with Horizontal(id="middle-row"):
            yield PredictionWidget(id="prediction")
            yield MarketWatchWidget(id="market-watch")
        
        # Alternative markets summary
        yield AlternativeMarketsWidget(id="alternative-markets")
        
        # Input area (bottom) with suggester
        with Horizontal(id="input-row"):
            yield Input(
                placeholder="Enter team names (e.g., 'Man City vs Liverpool') or command...",
                suggester=BetCopilotSuggester(app_instance=self),
                id="main-input"
            )
            yield Button("Analyze", variant="success", id="btn-analyze")
            yield Button("Refresh", variant="primary", id="btn-refresh")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Called when app starts."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        
        # Initialize events list for autocompletion
        self.events = []
        
        # Check API health
        await self.update_api_health()
        
        # Show welcome notification
        self.notify("🚀 Bet-Copilot TUI iniciado! Comandos: mercados, analizar, ayuda", severity="information")
        
        logger.info("Textual app mounted")
    
    async def update_api_health(self) -> None:
        """Update API health status."""
        api_widget = self.query_one(APIHealthWidget)
        
        # Check each API
        api_widget.odds_status = "healthy" if self.odds_client.api_key else "unknown"
        api_widget.football_status = "healthy" if self.football_client.is_available() else "degraded"
        api_widget.blackbox_status = "healthy" if self.ai_client.is_available() else "down"
        
        # Get request counts from cache/circuit breaker
        api_widget.odds_requests = 0  # TODO: Get from circuit breaker
        api_widget.football_requests = 0  # TODO: Get from circuit breaker
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-analyze":
            await self.action_analyze()
        elif event.button.id == "btn-refresh":
            await self.action_refresh_all()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        command = event.value
        
        if not command:
            return
        
        # Clear input
        event.input.value = ""
        
        # Process command
        await self.process_command(command)
    
    async def process_command(self, command: str) -> None:
        """Process user command."""
        logger.info(f"Processing command: {command}")
        command_lower = command.strip().lower()
        
        if not command_lower:
            return
        
        # Comandos de ayuda (español e inglés)
        if command_lower in ["ayuda", "help"]:
            self.notify("Comandos: mercados [sport], analizar [partido], salud, dashboard, salir", severity="information")
            return
        
        # Comandos de salud (español e inglés)
        elif command_lower in ["salud", "health"]:
            await self.update_api_health()
            self.notify("✓ APIs verificadas", severity="information")
            return
        
        # Dashboard - refresh all
        elif command_lower == "dashboard":
            await self.action_refresh_all()
            return
        
        # Mercados (español e inglés)
        elif command_lower.startswith("mercados") or command_lower.startswith("markets"):
            parts = command_lower.split()
            sport_key = parts[1] if len(parts) > 1 else "soccer_epl"
            await self.fetch_markets(sport_key)
            return
        
        # Analizar (español e inglés)
        elif command_lower.startswith("analizar") or command_lower.startswith("analyze") or command_lower.startswith("analyse"):
            # Extraer nombre del partido (preservar mayúsculas originales)
            if command_lower.startswith("analizar"):
                match_part = command.strip()[8:].strip()
            else:
                match_part = command.strip()[7:].strip()
            
            match_part = match_part.strip('"\'')
            
            if match_part:
                await self.analyze_match_from_string(match_part)
            else:
                self.notify("Uso: analizar <partido>\nEjemplo: analizar Arsenal vs Chelsea", severity="warning")
            return
        
        # Salir (español e inglés)
        elif command_lower in ["salir", "quit", "exit", "q"]:
            self.exit()
            return
        
        # Parse match analysis ("Team1 vs Team2")
        elif "vs" in command_lower:
            parts = command.split("vs")
            if len(parts) == 2:
                home_team = parts[0].strip()
                away_team = parts[1].strip()
                await self.analyze_match(home_team, away_team)
        else:
            # Other commands
            self.notify(f"Comando desconocido: {command}\nEscribe 'ayuda' para ver comandos", severity="warning")
    
    async def fetch_markets(self, sport_key: str = "soccer_epl"):
        """Fetch markets for a sport."""
        self.notify(f"📊 Obteniendo mercados para {sport_key}...")
        
        try:
            events = await self.odds_client.get_odds(sport_key)
            
            if not events:
                self.notify("No se encontraron eventos", severity="warning")
                return
            
            self.notify(f"✓ {len(events)} eventos encontrados", severity="information")
            
            # Store events for autocompletion
            self.events = events
            
            # Update market watch with some events
            market_widget = self.query_one(MarketWatchWidget)
            await market_widget.refresh_markets()
            
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            self.notify(f"Error: {str(e)}", severity="error")
    
    async def analyze_match_from_string(self, match_str: str) -> None:
        """Analyze a match from string input."""
        # Search in loaded events first
        if hasattr(self, 'events') and self.events:
            for event in self.events:
                event_str = f"{event.home_team} vs {event.away_team}"
                if match_str.lower() in event_str.lower():
                    await self.analyze_match(event.home_team, event.away_team)
                    return
        
        # If not found, try parsing as "Team1 vs Team2"
        if "vs" in match_str.lower():
            parts = match_str.split("vs")
            if len(parts) == 2:
                await self.analyze_match(parts[0].strip(), parts[1].strip())
                return
        
        self.notify(f"Partido no encontrado: {match_str}\nIntenta 'mercados' primero", severity="warning")
    
    async def analyze_match(self, home_team: str, away_team: str) -> None:
        """
        Analyze a match and update dashboard with real data.
        """
        self.notify(f"🔍 Analizando: {home_team} vs {away_team}")
        
        try:
            # Run full analysis
            analysis = await self.match_analyzer.analyze_match(
                home_team=home_team,
                away_team=away_team
            )
            
            if not analysis:
                self.notify("❌ No data available for this match", severity="error")
                return
            
            # Update prediction widget
            pred_widget = self.query_one(PredictionWidget)
            pred_widget.prediction_data = {
                'home_team': home_team,
                'away_team': away_team,
                'prediction': analysis.prediction,
                'ai_analysis': analysis.ai_analysis,
                'collaborative_analysis': analysis.collaborative_analysis
            }
            
            # Update market watch with ALL Kelly recommendations
            markets = []
            
            if analysis.kelly_home:
                markets.append({
                    "id": "home",
                    "match": f"{home_team} vs {away_team}",
                    "market_type": "Home Win",
                    "ev": analysis.kelly_home.ev,
                    "odds": analysis.kelly_home.odds,
                    "confidence": analysis.ai_analysis.confidence if analysis.ai_analysis else 0.5,
                    "is_value": analysis.kelly_home.is_value_bet
                })
            
            if analysis.kelly_draw:
                markets.append({
                    "id": "draw",
                    "match": f"{home_team} vs {away_team}",
                    "market_type": "Draw",
                    "ev": analysis.kelly_draw.ev,
                    "odds": analysis.kelly_draw.odds,
                    "confidence": analysis.ai_analysis.confidence if analysis.ai_analysis else 0.5,
                    "is_value": analysis.kelly_draw.is_value_bet
                })
            
            if analysis.kelly_away:
                markets.append({
                    "id": "away",
                    "match": f"{home_team} vs {away_team}",
                    "market_type": "Away Win",
                    "ev": analysis.kelly_away.ev,
                    "odds": analysis.kelly_away.odds,
                    "confidence": analysis.ai_analysis.confidence if analysis.ai_analysis else 0.5,
                    "is_value": analysis.kelly_away.is_value_bet
                })
            
            market_widget = self.query_one(MarketWatchWidget)
            market_widget.markets = markets
            
            # Update alternative markets
            alt_widget = self.query_one(AlternativeMarketsWidget)
            
            if analysis.corners_prediction:
                alt_widget.corners_data = {"expected": analysis.corners_prediction.total_expected}
            else:
                alt_widget.corners_data = {"expected": None}
            
            if analysis.cards_prediction:
                alt_widget.cards_data = {"expected": analysis.cards_prediction.total_expected}
            else:
                alt_widget.cards_data = {"expected": None}
            
            if analysis.shots_prediction:
                alt_widget.shots_data = {"expected": analysis.shots_prediction.total_expected}
            else:
                alt_widget.shots_data = {"expected": None}
            
            # Show summary with AI analysis context
            value_bets = [m for m in markets if m.get('is_value')]
            if value_bets:
                self.notify(f"✅ Found {len(value_bets)} value bet(s)! (Total: {len(markets)} markets)", severity="information")
            else:
                self.notify(f"ℹ️ No value bets found - Using estimated odds (Total: {len(markets)} markets analyzed)", severity="warning")
            
            # Log AI analysis summary
            if analysis.ai_analysis:
                logger.info(f"AI Analysis: {analysis.ai_analysis.reasoning[:100]}...")
            
            # Log alternative markets availability
            if not analysis.corners_prediction:
                logger.info("Alternative markets not available (API-Football Free plan limitation)")
        
        except Exception as e:
            logger.error(f"Error analyzing match: {str(e)}")
            self.notify(f"❌ Error: {str(e)}", severity="error")
    
    async def action_refresh_all(self) -> None:
        """Refresh all data."""
        self.notify("🔄 Refreshing all data...")
        
        # Update API health
        await self.update_api_health()
        
        # Refresh news
        news_widget = self.query_one(NewsWidget)
        await news_widget.refresh_news()
        
        # Refresh markets
        market_widget = self.query_one(MarketWatchWidget)
        await market_widget.refresh_markets()
        
        self.notify("✅ Refresh complete!", severity="information")
    
    async def on_unmount(self) -> None:
        """Cleanup on exit."""
        try:
            if hasattr(self, 'match_analyzer'):
                await self.match_analyzer.close()
            if hasattr(self, 'odds_client'):
                await self.odds_client.close()
            if hasattr(self, 'football_client'):
                await self.football_client.close()
            if hasattr(self, 'ai_client'):
                await self.ai_client.close()
            logger.info("App cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def action_analyze(self) -> None:
        """Trigger analysis from button."""
        input_widget = self.query_one("#main-input", Input)
        command = input_widget.value
        
        if command:
            await self.process_command(command)
            input_widget.value = ""
    
    def action_toggle_news(self) -> None:
        """Toggle news feed visibility."""
        news_widget = self.query_one(NewsWidget)
        news_widget.display = not news_widget.display
    
    def action_toggle_markets(self) -> None:
        """Toggle alternative markets visibility."""
        alt_widget = self.query_one(AlternativeMarketsWidget)
        alt_widget.display = not alt_widget.display


def run_textual_app():
    """Run the Textual TUI application."""
    app = BetCopilotApp()
    app.run()


if __name__ == "__main__":
    # For standalone testing
    run_textual_app()
