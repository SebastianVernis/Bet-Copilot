"""
Complete Textual TUI Dashboard with Persistence
Modern interactive dashboard with state management and live updates.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, DataTable, Input, Button, 
    Label, ProgressBar, TabbedContent, TabPane, Log
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.screen import Screen

from bet_copilot.api.odds_client import OddsAPIClient
from bet_copilot.api.football_client_with_fallback import create_football_client
from bet_copilot.ai.ai_client import create_ai_client
from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.math_engine.kelly import KellyCriterion
from bet_copilot.services.match_analyzer import MatchAnalyzer
from bet_copilot.news import NewsScraper, NewsArticle
from bet_copilot.ui.dashboard_state import DashboardState

logger = logging.getLogger(__name__)


class APIHealthWidget(Static):
    """
    API Health Status Display with real-time monitoring.
    Shows status, request counts, and availability.
    """
    
    odds_status = reactive("unknown")
    football_status = reactive("unknown")
    gemini_status = reactive("unknown")
    blackbox_status = reactive("unknown")
    
    odds_requests = reactive(0)
    football_requests = reactive(0)
    
    collaborative_mode = reactive(False)
    agreement_score = reactive(0.0)
    
    def compose(self) -> ComposeResult:
        yield Label("⚡ API Health Monitor", classes="widget-title")
        yield Static(id="health-content", classes="health-display")
    
    def on_mount(self) -> None:
        """Initialize display."""
        self.update_display()
    
    def watch_odds_status(self, status: str) -> None:
        """Update when odds status changes."""
        self.update_display()
    
    def watch_football_status(self, status: str) -> None:
        """Update when football status changes."""
        self.update_display()
    
    def watch_gemini_status(self, status: str) -> None:
        """Update when Gemini status changes."""
        self.update_display()
    
    def watch_blackbox_status(self, status: str) -> None:
        """Update when Blackbox status changes."""
        self.update_display()
    
    def watch_collaborative_mode(self, active: bool) -> None:
        """Update when collaborative mode changes."""
        self.update_display()
    
    def update_display(self):
        """Render current status."""
        content = self.query_one("#health-content", Static)
        
        def status_icon(status: str) -> str:
            if status == "healthy":
                return "🟢"
            elif status == "degraded":
                return "🟡"
            elif status == "down":
                return "🔴"
            else:
                return "⚪"
        
        # Build status text
        status_text = (
            f"{status_icon(self.odds_status)} [bold cyan]Odds API[/]       "
            f"{self.odds_requests}/500 daily\n"
            f"{status_icon(self.football_status)} [bold cyan]Football API[/]   "
            f"{self.football_requests}/100 daily\n"
            f"{status_icon(self.gemini_status)} [bold cyan]Gemini AI[/]      "
            f"{'✓ Available' if self.gemini_status == 'healthy' else '✗ Unavailable'}\n"
            f"{status_icon(self.blackbox_status)} [bold cyan]Blackbox AI[/]    "
            f"{'✓ Available' if self.blackbox_status == 'healthy' else '✗ Unavailable'}\n"
        )
        
        # Add collaborative mode info
        if self.collaborative_mode:
            status_text += (
                f"\n[bold green]🤝 Collaborative Mode: ACTIVE[/]\n"
                f"Agreement: {self.agreement_score*100:.0f}%"
            )
        
        content.update(status_text)


class NewsWidget(Static):
    """
    Live news feed from free sources with auto-refresh.
    Displays latest football news with categorization.
    """
    
    articles = reactive([])
    loading = reactive(False)
    last_update = reactive("")
    
    def compose(self) -> ComposeResult:
        yield Label("📰 Live News Feed", classes="widget-title")
        yield ScrollableContainer(id="news-list", classes="news-container")
        yield Label("", id="news-status", classes="status-label")
    
    async def on_mount(self) -> None:
        """Fetch news on startup."""
        await self.refresh_news()
        
        # Auto-refresh every hour
        self.set_interval(3600, self.refresh_news)
    
    async def refresh_news(self) -> None:
        """Fetch latest news."""
        self.loading = True
        
        try:
            scraper = NewsScraper()
            self.articles = await scraper.fetch_all_news(max_per_source=15)
            await scraper.close()
            self.last_update = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            self.articles = []
        finally:
            self.loading = False
    
    def watch_articles(self, articles: List[NewsArticle]) -> None:
        """Update display when articles change."""
        container = self.query_one("#news-list", ScrollableContainer)
        container.remove_children()
        
        if self.loading:
            container.mount(Label("🔄 Loading news...", classes="loading-text"))
            return
        
        if not articles:
            container.mount(Label("No news available", classes="empty-text"))
            return
        
        for article in articles[:15]:
            # Time ago
            time_diff = (datetime.now() - article.published).total_seconds() / 3600
            if time_diff < 1:
                time_str = f"{int(time_diff * 60)}m ago"
            elif time_diff < 24:
                time_str = f"{int(time_diff)}h ago"
            else:
                time_str = f"{int(time_diff / 24)}d ago"
            
            # Category emoji
            emoji = {
                "injury": "🏥",
                "transfer": "🔄",
                "match_preview": "⚽",
                "general": "📋"
            }.get(article.category, "📋")
            
            # Render article
            article_text = (
                f"[dim]{time_str}[/] {emoji} [bold]{article.title[:60]}[/]\n"
                f"[dim]{article.source}[/]"
            )
            
            container.mount(Label(article_text, classes="news-item"))
    
    def watch_last_update(self, timestamp: str) -> None:
        """Update status label."""
        if timestamp:
            status = self.query_one("#news-status", Label)
            status.update(f"[dim]Last update: {timestamp}[/]")


class MarketWatchWidget(Static):
    """
    Market watch with live value bets.
    Shows EV opportunities across traditional and alternative markets.
    """
    
    markets = reactive([])
    last_update = reactive("")
    loading = reactive(False)
    
    def compose(self) -> ComposeResult:
        yield Label("📊 Market Watch - Live Value Bets", classes="widget-title")
        yield DataTable(id="markets-table", classes="markets-table")
        yield Label("", id="market-status", classes="status-label")
    
    def on_mount(self) -> None:
        """Initialize table."""
        table = self.query_one(DataTable)
        
        # Add columns
        table.add_column("Match", width=28)
        table.add_column("Market", width=16)
        table.add_column("EV", width=10)
        table.add_column("Odds", width=8)
        table.add_column("Stake", width=8)
        table.add_column("Conf", width=8)
        
        table.cursor_type = "row"
        
        # Auto-refresh every 60s
        self.set_interval(60, self.refresh_markets)
    
    async def refresh_markets(self) -> None:
        """Fetch latest market data."""
        self.loading = True
        
        try:
            # Markets will be updated by parent app
            self.last_update = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            logger.error(f"Error refreshing markets: {str(e)}")
        finally:
            self.loading = False
    
    def watch_markets(self, markets: List[Dict[str, Any]]) -> None:
        """Update table when markets change."""
        table = self.query_one(DataTable)
        table.clear()
        
        if not markets:
            return
        
        for market in markets[:20]:
            ev = market.get('ev', 0)
            
            # Color based on EV
            if ev > 0.10:
                ev_style = "bold green"
            elif ev > 0.05:
                ev_style = "yellow"
            else:
                ev_style = "dim"
            
            # Confidence stars
            confidence = market.get('confidence', 0)
            stars = "⭐" * int(confidence * 5)
            
            table.add_row(
                market.get('match', '')[:28],
                market.get('market_type', ''),
                f"[{ev_style}]{ev:+.1%}[/]",
                f"{market.get('odds', 0):.2f}",
                f"{market.get('stake', 0):.1%}",
                stars,
            )
    
    def watch_last_update(self, timestamp: str) -> None:
        """Update timestamp label."""
        if timestamp:
            status = self.query_one("#market-status", Label)
            status.update(f"[dim]Last update: {timestamp} | Auto-refresh: 60s[/]")


class AlternativeMarketsWidget(Static):
    """
    Alternative markets summary with predictions.
    Shows corners, cards, shots, offsides predictions.
    """
    
    current_match = reactive("")
    corners_data = reactive(None)
    cards_data = reactive(None)
    shots_data = reactive(None)
    offsides_data = reactive(None)
    
    def compose(self) -> ComposeResult:
        yield Label("📐 Alternative Markets", classes="widget-title")
        
        with Horizontal(classes="alt-markets-row"):
            yield Static("🏁 Corners: --", id="corners-summary", classes="alt-market-item")
            yield Static("🟨 Cards: --", id="cards-summary", classes="alt-market-item")
            yield Static("🎯 Shots: --", id="shots-summary", classes="alt-market-item")
            yield Static("🚩 Offsides: --", id="offsides-summary", classes="alt-market-item")
        
        yield Label("", id="alt-match-name", classes="match-name")
    
    def watch_current_match(self, match: str) -> None:
        """Update match name."""
        if match:
            label = self.query_one("#alt-match-name", Label)
            label.update(f"[dim]Analysis for: {match}[/]")
    
    def watch_corners_data(self, data: Optional[Dict]) -> None:
        """Update corners display."""
        widget = self.query_one("#corners-summary", Static)
        if data:
            expected = data.get('expected', 0)
            widget.update(f"🏁 [bold cyan]Corners:[/] {expected:.1f}")
        else:
            widget.update("🏁 Corners: --")
    
    def watch_cards_data(self, data: Optional[Dict]) -> None:
        """Update cards display."""
        widget = self.query_one("#cards-summary", Static)
        if data:
            expected = data.get('expected', 0)
            widget.update(f"🟨 [bold yellow]Cards:[/] {expected:.1f}")
        else:
            widget.update("🟨 Cards: --")
    
    def watch_shots_data(self, data: Optional[Dict]) -> None:
        """Update shots display."""
        widget = self.query_one("#shots-summary", Static)
        if data:
            expected = data.get('expected', 0)
            widget.update(f"🎯 [bold green]Shots:[/] {expected:.1f}")
        else:
            widget.update("🎯 Shots: --")
    
    def watch_offsides_data(self, data: Optional[Dict]) -> None:
        """Update offsides display."""
        widget = self.query_one("#offsides-summary", Static)
        if data:
            expected = data.get('expected', 0)
            widget.update(f"🚩 [bold magenta]Offsides:[/] {expected:.1f}")
        else:
            widget.update("🚩 Offsides: --")


class SystemLogsWidget(Static):
    """
    System logs display with scrollable history.
    Shows recent activity and errors.
    """
    
    logs = reactive([])
    
    def compose(self) -> ComposeResult:
        yield Label("📝 System Logs", classes="widget-title")
        yield Log(id="log-display", classes="log-container")
    
    def watch_logs(self, logs: List[str]) -> None:
        """Update logs display."""
        log_widget = self.query_one(Log)
        
        # Clear and add recent logs
        log_widget.clear()
        for log_entry in logs[-50:]:  # Keep last 50 logs
            log_widget.write_line(log_entry)


class BetCopilotDashboard(App):
    """
    Main Bet-Copilot Textual Dashboard Application.
    
    Features:
    - Live API health monitoring
    - Real-time market watch with value bets
    - News feed with auto-refresh
    - Alternative markets predictions
    - Interactive command input
    - Persistent state management
    - Keyboard shortcuts
    """
    
    CSS = """
    Screen {
        background: #0a0a0a;
    }
    
    .widget-title {
        color: #00ffff;
        text-style: bold;
        margin: 0 0 1 0;
    }
    
    #top-row {
        height: 14;
        margin: 1;
    }
    
    #api-health {
        width: 1fr;
        border: solid #00ff00;
        padding: 1;
    }
    
    #news-feed {
        width: 1fr;
        border: solid #00ffff;
        padding: 1;
    }
    
    #market-watch {
        height: 1fr;
        border: solid #ffff00;
        margin: 1;
        padding: 1;
    }
    
    #alternative-markets {
        height: 7;
        border: solid #ff00ff;
        margin: 1;
        padding: 1;
    }
    
    #system-logs {
        height: 12;
        border: solid #ff6600;
        margin: 1;
        padding: 1;
    }
    
    #input-row {
        height: 3;
        dock: bottom;
        background: #1a1a1a;
        padding: 0 1;
    }
    
    DataTable {
        background: #0f0f0f;
        color: #39ff14;
    }
    
    DataTable > .datatable--cursor {
        background: #2a2a2a;
    }
    
    Input {
        border: solid #00ffff;
        width: 1fr;
    }
    
    Button {
        margin: 0 1;
    }
    
    .health-display {
        color: #cccccc;
    }
    
    .news-container {
        height: 1fr;
    }
    
    .news-item {
        margin: 0 0 1 0;
    }
    
    .loading-text {
        color: #ffff00;
        text-style: italic;
    }
    
    .empty-text {
        color: #666666;
        text-style: dim;
    }
    
    .status-label {
        color: #666666;
        text-style: dim;
        margin: 1 0 0 0;
    }
    
    .alt-markets-row {
        height: 3;
    }
    
    .alt-market-item {
        width: 1fr;
        content-align: center middle;
        border: solid #333333;
        margin: 0 1;
    }
    
    .match-name {
        color: #00ffff;
        margin: 1 0 0 0;
    }
    
    .log-container {
        height: 1fr;
        background: #0a0a0a;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh_all", "Refresh All"),
        Binding("n", "toggle_news", "Toggle News"),
        Binding("m", "fetch_markets", "Fetch Markets"),
        Binding("h", "show_help", "Help"),
        Binding("ctrl+c", "quit", "Quit", priority=True),
    ]
    
    TITLE = "BET-COPILOT v0.6 - Interactive TUI Dashboard"
    SUB_TITLE = "Multi-AI Analysis | Alternative Markets | Live News | Persistent State"
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.odds_client = OddsAPIClient()
        self.football_client = create_football_client()
        self.ai_client = create_ai_client()
        self.soccer_predictor = SoccerPredictor()
        self.kelly = KellyCriterion()
        self.match_analyzer = MatchAnalyzer(
            self.odds_client,
            self.football_client,
            self.ai_client,
            self.soccer_predictor,
            self.kelly,
        )
        
        # State management
        self.state = DashboardState()
        
        # Data storage
        self.events = []
        self.markets = []
        self.logs = ["System initialized"]
    
    def compose(self) -> ComposeResult:
        """Create layout."""
        yield Header()
        
        # Top row: API Health + News
        with Horizontal(id="top-row"):
            yield APIHealthWidget(id="api-health")
            yield NewsWidget(id="news-feed")
        
        # Main area: Market Watch
        yield MarketWatchWidget(id="market-watch")
        
        # Alternative markets summary
        yield AlternativeMarketsWidget(id="alternative-markets")
        
        # System logs
        yield SystemLogsWidget(id="system-logs")
        
        # Input area (bottom)
        with Horizontal(id="input-row"):
            yield Input(
                placeholder="Enter team names (e.g., 'Man City vs Liverpool') or command (mercados, analizar, salud)...",
                id="main-input"
            )
            yield Button("Analyze", variant="success", id="btn-analyze")
            yield Button("Refresh", variant="primary", id="btn-refresh")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Called when app starts."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        
        # Load persisted state
        await self.state.load()
        
        # Initialize API health check
        await self.check_api_health()
        
        # Restore last session data if available
        if self.state.last_sport_key:
            self.add_log(f"Restoring last session: {self.state.last_sport_key}")
            await self.fetch_markets(self.state.last_sport_key)
        
        self.add_log("Dashboard ready")
        
        # Start periodic health checks (every 5 minutes)
        self.set_interval(300, self.check_api_health)
    
    async def check_api_health(self) -> None:
        """Check health of all APIs."""
        api_widget = self.query_one(APIHealthWidget)
        
        # Check Odds API
        try:
            if self.odds_client.api_key:
                await self.odds_client.get_sports()
                api_widget.odds_status = "healthy"
            else:
                api_widget.odds_status = "down"
        except Exception as e:
            api_widget.odds_status = "down"
            self.add_log(f"Odds API error: {str(e)[:50]}")
        
        # Check Football API
        try:
            if self.football_client.is_available():
                api_widget.football_status = "healthy"
            else:
                api_widget.football_status = "degraded"
        except Exception:
            api_widget.football_status = "degraded"
        
        # Check AI services
        if self.ai_client.is_available():
            provider = self.ai_client.get_active_provider()
            
            if provider == "collaborative":
                api_widget.collaborative_mode = True
                api_widget.gemini_status = "healthy"
                api_widget.blackbox_status = "healthy"
            elif provider == "gemini":
                api_widget.gemini_status = "healthy"
                api_widget.blackbox_status = "down"
            elif provider == "blackbox":
                api_widget.gemini_status = "down"
                api_widget.blackbox_status = "healthy"
        else:
            api_widget.gemini_status = "down"
            api_widget.blackbox_status = "down"
    
    async def fetch_markets(self, sport_key: str = "soccer_epl") -> None:
        """Fetch markets for a sport."""
        self.add_log(f"Fetching markets for {sport_key}...")
        
        try:
            events = await self.odds_client.get_odds(sport_key)
            
            if not events:
                self.add_log("No events found")
                return
            
            self.events = events
            self.add_log(f"Loaded {len(events)} events")
            
            # Build markets
            self.markets = []
            for event in events:
                home_odds = event.get_best_odds("h2h", event.home_team)
                away_odds = event.get_best_odds("h2h", event.away_team)
                
                bookmaker = event.bookmakers[0].title if event.bookmakers else "Unknown"
                
                if home_odds and home_odds > 1.0:
                    home_implied = 1.0 / home_odds
                    model_prob = min(0.95, home_implied * 1.05)
                    ev = (model_prob * home_odds) - 1
                    
                    self.markets.append({
                        "match": f"{event.home_team} vs {event.away_team}",
                        "market_type": "Home Win",
                        "ev": ev,
                        "odds": home_odds,
                        "stake": min(5.0, ev * 100) if ev > 0.05 else 0,
                        "confidence": 0.75,
                        "bookmaker": bookmaker,
                    })
                
                if away_odds and away_odds > 1.0:
                    away_implied = 1.0 / away_odds
                    model_prob = min(0.95, away_implied * 1.05)
                    ev = (model_prob * away_odds) - 1
                    
                    self.markets.append({
                        "match": f"{event.home_team} vs {event.away_team}",
                        "market_type": "Away Win",
                        "ev": ev,
                        "odds": away_odds,
                        "stake": min(5.0, ev * 100) if ev > 0.05 else 0,
                        "confidence": 0.75,
                        "bookmaker": bookmaker,
                    })
            
            # Update market widget
            market_widget = self.query_one(MarketWatchWidget)
            market_widget.markets = sorted(self.markets, key=lambda x: x['ev'], reverse=True)
            
            # Save state
            self.state.last_sport_key = sport_key
            await self.state.save()
            
            self.add_log(f"Markets updated: {len(self.markets)} opportunities")
            
        except Exception as e:
            self.add_log(f"Error fetching markets: {str(e)}")
            logger.exception("Error fetching markets")
    
    async def analyze_match(self, match_query: str) -> None:
        """Analyze a specific match."""
        self.add_log(f"Analyzing: {match_query}")
        
        # Find matching event
        event_found = None
        for event in self.events:
            match_str = f"{event.home_team} vs {event.away_team}"
            if match_query.lower() in match_str.lower():
                event_found = event
                break
        
        if not event_found:
            self.add_log("Match not found in current markets")
            self.notify("Match not found. Try 'mercados' first.", severity="warning")
            return
        
        try:
            # Perform analysis
            analysis = await self.match_analyzer.analyze_from_odds_event(
                event_found, league_id=39, season=2024
            )
            
            # Update alternative markets widget
            alt_widget = self.query_one(AlternativeMarketsWidget)
            alt_widget.current_match = f"{analysis.home_team} vs {analysis.away_team}"
            
            # Mock alternative markets data (would come from analysis)
            alt_widget.corners_data = {"expected": 11.5}
            alt_widget.cards_data = {"expected": 4.8}
            alt_widget.shots_data = {"expected": 24.3}
            alt_widget.offsides_data = {"expected": 3.2}
            
            self.add_log(f"Analysis complete for {analysis.home_team} vs {analysis.away_team}")
            self.notify(f"✓ Analysis complete!", severity="information")
            
        except Exception as e:
            self.add_log(f"Error analyzing match: {str(e)}")
            self.notify(f"Error: {str(e)[:50]}", severity="error")
            logger.exception("Error analyzing match")
    
    def add_log(self, message: str) -> None:
        """Add a log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        # Update logs widget
        logs_widget = self.query_one(SystemLogsWidget)
        logs_widget.logs = self.logs
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-analyze":
            input_widget = self.query_one("#main-input", Input)
            command = input_widget.value.strip()
            
            if command:
                await self.process_command(command)
                input_widget.value = ""
        
        elif event.button.id == "btn-refresh":
            await self.action_refresh_all()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        command = event.value.strip()
        
        if not command:
            return
        
        # Clear input
        event.input.value = ""
        
        # Process command
        await self.process_command(command)
    
    async def process_command(self, command: str) -> None:
        """Process user command."""
        command_lower = command.lower()
        
        # Mercados / Markets
        if command_lower.startswith("mercados") or command_lower.startswith("markets"):
            parts = command_lower.split()
            sport_key = parts[1] if len(parts) > 1 else "soccer_epl"
            await self.fetch_markets(sport_key)
        
        # Analizar / Analyze
        elif command_lower.startswith("analizar") or command_lower.startswith("analyze"):
            match_part = command[8:].strip() if command_lower.startswith("analizar") else command[7:].strip()
            
            if match_part:
                await self.analyze_match(match_part)
            else:
                self.notify("Usage: analizar <team names>", severity="warning")
        
        # Salud / Health
        elif command_lower in ["salud", "health"]:
            await self.check_api_health()
            self.notify("Health check complete", severity="information")
        
        # Help
        elif command_lower in ["ayuda", "help"]:
            self.action_show_help()
        
        # Match analysis (contains "vs")
        elif "vs" in command_lower:
            await self.analyze_match(command)
        
        else:
            self.add_log(f"Unknown command: {command}")
            self.notify(f"Unknown command. Press 'h' for help.", severity="warning")
    
    async def action_refresh_all(self) -> None:
        """Refresh all data."""
        self.add_log("Refreshing all data...")
        self.notify("Refreshing all data...")
        
        # Refresh API health
        await self.check_api_health()
        
        # Refresh news
        news_widget = self.query_one(NewsWidget)
        await news_widget.refresh_news()
        
        # Refresh markets if we have a sport key
        if self.state.last_sport_key:
            await self.fetch_markets(self.state.last_sport_key)
        
        self.add_log("Refresh complete")
        self.notify("✓ Refresh complete!", severity="information")
    
    def action_toggle_news(self) -> None:
        """Toggle news feed visibility."""
        news_widget = self.query_one(NewsWidget)
        news_widget.display = not news_widget.display
        
        status = "shown" if news_widget.display else "hidden"
        self.add_log(f"News feed {status}")
    
    async def action_fetch_markets(self) -> None:
        """Fetch markets shortcut."""
        sport_key = self.state.last_sport_key or "soccer_epl"
        await self.fetch_markets(sport_key)
    
    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
[bold cyan]BET-COPILOT TUI Commands:[/]

[bold]Commands:[/]
  mercados [league]    - Fetch markets (default: soccer_epl)
  analizar <match>     - Analyze specific match
  salud                - Check API health
  ayuda                - Show this help

[bold]Keyboard Shortcuts:[/]
  q                    - Quit application
  r                    - Refresh all data
  n                    - Toggle news feed
  m                    - Fetch markets
  h                    - Show help
  Ctrl+C               - Quit

[bold]Examples:[/]
  mercados soccer_la_liga
  analizar Man City vs Liverpool
  Man City vs Liverpool (direct analysis)
"""
        self.notify(help_text, timeout=10)
        self.add_log("Help displayed")
    
    async def on_unmount(self) -> None:
        """Cleanup on exit."""
        # Save state
        await self.state.save()
        
        # Close clients
        await self.odds_client.close()
        await self.football_client.close()
        await self.ai_client.close()


def run_textual_dashboard():
    """Run the Textual TUI dashboard."""
    app = BetCopilotDashboard()
    app.run()


if __name__ == "__main__":
    run_textual_dashboard()
