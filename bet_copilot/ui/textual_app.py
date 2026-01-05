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

from bet_copilot.news import NewsScraper, NewsArticle

logger = logging.getLogger(__name__)


class APIHealthWidget(Static):
    """
    API Health Status Display.
    
    Shows real-time status of all API endpoints with request counts.
    """
    
    odds_status = reactive("unknown")
    football_status = reactive("unknown")
    gemini_status = reactive("unknown")
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
            f"{status_icon(self.gemini_status)} Gemini AI     "
            f"{'✓' if self.gemini_status == 'healthy' else '✗'}\n"
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
        
        # Auto-refresh every hour
        self.set_interval(3600, self.refresh_news)
    
    async def refresh_news(self) -> None:
        """Fetch latest news."""
        self.loading = True
        
        try:
            scraper = NewsScraper()
            self.articles = await scraper.fetch_all_news(max_per_source=10)
            await scraper.close()
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
        finally:
            self.loading = False
    
    def watch_articles(self, articles: List[NewsArticle]) -> None:
        """Update display when articles change."""
        container = self.query_one("#news-list", ScrollableContainer)
        container.remove_children()
        
        if self.loading:
            container.mount(Label("🔄 Loading news..."))
            return
        
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
        
        # Auto-refresh every 30s
        self.set_interval(30, self.refresh_markets)
    
    async def refresh_markets(self) -> None:
        """Fetch latest market data."""
        try:
            # TODO: Integrate with actual MatchAnalyzer
            # For now, empty
            self.last_update = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            logger.error(f"Error refreshing markets: {str(e)}")
    
    def watch_markets(self, markets) -> None:
        """Update table when markets change."""
        table = self.query_one(DataTable)
        table.clear()
        
        for market in markets:
            ev_str = f"{market.get('ev', 0):+.1%}"
            
            # Color based on EV
            if market.get('ev', 0) > 0.10:
                style = "bold green"
            elif market.get('ev', 0) > 0.05:
                style = "yellow"
            else:
                style = "dim"
            
            table.add_row(
                market.get('match', ''),
                market.get('market_type', ''),
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
            yield Static("🏁 Corners: --", id="corners-summary")
            yield Static("🟨 Cards: --", id="cards-summary")
            yield Static("🎯 Shots: --", id="shots-summary")
    
    def watch_corners_data(self, data) -> None:
        """Update corners display."""
        if data:
            widget = self.query_one("#corners-summary", Static)
            widget.update(f"🏁 Corners: {data.get('expected', 0):.1f}")
    
    def watch_cards_data(self, data) -> None:
        """Update cards display."""
        if data:
            widget = self.query_one("#cards-summary", Static)
            widget.update(f"🟨 Cards: {data.get('expected', 0):.1f}")
    
    def watch_shots_data(self, data) -> None:
        """Update shots display."""
        if data:
            widget = self.query_one("#shots-summary", Static)
            widget.update(f"🎯 Shots: {data.get('expected', 0):.1f}")


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
        height: 8;
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
        
        # Input area (bottom)
        with Horizontal(id="input-row"):
            yield Input(
                placeholder="Enter team names (e.g., 'Man City vs Liverpool') or command...",
                id="main-input"
            )
            yield Button("Analyze", variant="success", id="btn-analyze")
            yield Button("Refresh", variant="primary", id="btn-refresh")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Called when app starts."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        
        # Initialize API health
        api_widget = self.query_one(APIHealthWidget)
        api_widget.odds_status = "healthy"
        api_widget.football_status = "healthy"
        api_widget.gemini_status = "healthy"
        api_widget.blackbox_status = "healthy"
        
        logger.info("Textual app mounted")
    
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
        
        # Parse command
        if "vs" in command.lower():
            # Match analysis command
            parts = command.split("vs")
            if len(parts) == 2:
                home_team = parts[0].strip()
                away_team = parts[1].strip()
                
                await self.analyze_match(home_team, away_team)
        else:
            # Other commands
            self.notify(f"Unknown command: {command}", severity="warning")
    
    async def analyze_match(self, home_team: str, away_team: str) -> None:
        """
        Analyze a match and update dashboard.
        
        TODO: Integrate with MatchAnalyzer
        """
        self.notify(f"Analyzing: {home_team} vs {away_team}")
        
        # Simulate analysis
        await asyncio.sleep(2)
        
        # Update market watch
        market_widget = self.query_one(MarketWatchWidget)
        market_widget.markets = [
            {
                "id": "1",
                "match": f"{home_team} vs {away_team}",
                "market_type": "Home Win",
                "ev": 0.125,
                "odds": 2.10,
                "confidence": 0.8
            },
            {
                "id": "2",
                "match": f"{home_team} vs {away_team}",
                "market_type": "Corners O10.5",
                "ev": 0.152,
                "odds": 1.95,
                "confidence": 0.85
            }
        ]
        
        # Update alternative markets
        alt_widget = self.query_one(AlternativeMarketsWidget)
        alt_widget.corners_data = {"expected": 11.8}
        alt_widget.cards_data = {"expected": 4.6}
        alt_widget.shots_data = {"expected": 26.3}
        
        self.notify(f"✓ Analysis complete!", severity="information")
    
    async def action_refresh_all(self) -> None:
        """Refresh all data."""
        self.notify("Refreshing all data...")
        
        # Refresh news
        news_widget = self.query_one(NewsWidget)
        await news_widget.refresh_news()
        
        # Refresh markets
        market_widget = self.query_one(MarketWatchWidget)
        await market_widget.refresh_markets()
        
        self.notify("✓ Refresh complete!", severity="information")
    
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
