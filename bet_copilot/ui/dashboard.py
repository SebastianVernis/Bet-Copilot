"""
Main dashboard with 4 zones: API Health, Tasks, Market Watch, Logs.
Built with Rich terminal UI.
"""

import asyncio
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import MINIMAL, ROUNDED

from bet_copilot.ui.styles import (
    NEON_GREEN,
    NEON_CYAN,
    NEON_PINK,
    NEON_YELLOW,
    NEON_PURPLE,
    NEON_RED,
    LIGHT_GRAY,
)

# Zona A: Salud de APIs
def render_api_health(
    odds_api_status: str = "unknown",
    football_api_status: str = "unknown",
    gemini_status: str = "unknown",
    odds_requests_today: int = 0,
    football_requests_today: int = 0,
) -> Panel:
    """Renderiza panel de estado de salud de APIs (Zona A)."""
    table = Table(box=MINIMAL, show_header=False, padding=(0, 1))
    table.add_column("API", style=f"bold {NEON_CYAN}")
    table.add_column("Estado", justify="center")
    table.add_column("Peticiones", justify="right")

    def status_icon(status: str) -> Text:
        if status == "healthy":
            return Text("●", style=f"bold {NEON_GREEN}")
        elif status == "degraded":
            return Text("●", style=f"bold {NEON_YELLOW}")
        elif status == "down":
            return Text("●", style=f"bold {NEON_RED}")
        else:
            return Text("●", style=f"dim {LIGHT_GRAY}")

    table.add_row(
        "The Odds API",
        status_icon(odds_api_status),
        f"{odds_requests_today}/500",
    )
    table.add_row(
        "API-Football",
        status_icon(football_api_status),
        f"{football_requests_today}/100",
    )
    table.add_row(
        "Gemini AI",
        status_icon(gemini_status),
        "∞",
    )

    return Panel(
        table,
        title="[bold]⚡ Salud de APIs[/bold]",
        border_style=NEON_PURPLE,
        box=ROUNDED,
    )


# Zona B: Tareas Activas
def render_active_tasks(tasks: Optional[List[dict]] = None) -> Panel:
    """Renderiza panel de tareas activas (Zona B)."""
    if not tasks:
        tasks = [{"name": "Esperando comandos...", "status": "idle"}]

    table = Table(box=MINIMAL, show_header=False, padding=(0, 1))
    table.add_column("Tarea", style=LIGHT_GRAY)
    table.add_column("Estado", justify="right")

    for task in tasks[:5]:  # Mostrar máximo 5 tareas
        name = task.get("name", "Desconocido")
        status = task.get("status", "idle")

        if status == "running":
            status_text = Text("⚙ Ejecutando", style=f"bold {NEON_CYAN}")
        elif status == "completed":
            status_text = Text("✓ Completo", style=f"bold {NEON_GREEN}")
        elif status == "failed":
            status_text = Text("✗ Fallido", style=f"bold {NEON_RED}")
        else:
            status_text = Text("○ Inactivo", style=f"dim {LIGHT_GRAY}")

        table.add_row(name, status_text)

    return Panel(
        table,
        title="[bold]📋 Tareas Activas[/bold]",
        border_style=NEON_PURPLE,
        box=ROUNDED,
    )


# Zona C: Vigilancia de Mercados
def render_market_watch(markets: Optional[List[dict]] = None) -> Panel:
    """Renderiza tabla de vigilancia de mercados (Zona C)."""
    if not markets:
        return Panel(
            Text("No hay mercados disponibles", style=f"dim {LIGHT_GRAY}", justify="center"),
            title="[bold]📊 Vigilancia de Mercados[/bold]",
            border_style=NEON_PURPLE,
            box=ROUNDED,
        )

    table = Table(box=MINIMAL, show_header=True, padding=(0, 1))
    table.add_column("Partido", width=25, style=LIGHT_GRAY)
    table.add_column("Mercado", width=12, style=NEON_CYAN)
    table.add_column("Modelo", width=8, justify="right", style=LIGHT_GRAY)
    table.add_column("Cuota", width=6, justify="right", style=LIGHT_GRAY)
    table.add_column("EV", width=8, justify="right")
    table.add_column("Casa", width=10, style=f"dim {LIGHT_GRAY}")

    for market in markets[:10]:  # Mostrar máximo 10
        match = f"{market['home_team']} vs {market['away_team']}"
        market_type = market.get("market_type", "Desconocido")
        model_prob = market.get("model_prob", 0.0)
        odds = market.get("odds", 1.0)
        ev = market.get("ev", 0.0)
        bookmaker = market.get("bookmaker", "Desconocido")

        # Colorear EV
        if ev > 0.05:
            ev_text = Text(f"+{ev*100:.1f}%", style=f"bold {NEON_GREEN}")
        elif ev > 0:
            ev_text = Text(f"+{ev*100:.1f}%", style=NEON_YELLOW)
        else:
            ev_text = Text(f"{ev*100:.1f}%", style=f"dim {NEON_RED}")

        table.add_row(
            match[:25],
            market_type,
            f"{model_prob*100:.0f}%",
            f"{odds:.2f}",
            ev_text,
            bookmaker,
        )

    return Panel(
        table,
        title="[bold]📊 Vigilancia de Mercados[/bold]",
        border_style=NEON_PURPLE,
        box=ROUNDED,
    )


# Zona D: Logs del Sistema
def render_system_logs(logs: Optional[List[str]] = None) -> Panel:
    """Renderiza panel de logs del sistema (Zona D)."""
    if not logs:
        logs = ["Sistema listo"]

    # Mostrar últimos 5 logs
    log_text = "\n".join([f"[dim]{LIGHT_GRAY}•[/dim] {log}" for log in logs[-5:]])

    return Panel(
        Text.from_markup(log_text),
        title="[bold]📝 Logs del Sistema[/bold]",
        border_style=NEON_PURPLE,
        box=ROUNDED,
    )


# Main Dashboard Layout
class Dashboard:
    """Main dashboard with 4 zones."""

    def __init__(self):
        self.console = Console()
        self.layout = Layout()

        # Setup layout structure
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        self.layout["left"].split_column(
            Layout(name="zone_a", size=10),
            Layout(name="zone_b", size=12),
        )

        self.layout["right"].split_column(
            Layout(name="zone_c"),
            Layout(name="zone_d", size=10),
        )

    def render_header(self) -> Panel:
        """Renderiza encabezado con título y marca de tiempo."""
        title = Text("BET-COPILOT", style=f"bold {NEON_PURPLE}", justify="center")
        subtitle = Text(
            f"Sistema de Análisis Especulativo • {datetime.now().strftime('%H:%M:%S')}",
            style=f"dim {LIGHT_GRAY}",
            justify="center",
        )

        return Panel(
            Text.assemble(title, "\n", subtitle),
            border_style=NEON_PURPLE,
            box=ROUNDED,
        )

    def render_footer(self) -> Panel:
        """Renderiza pie de página con controles."""
        controls = Text(
            "Ctrl+C: Volver al CLI  •  Dashboard se actualiza cada 1 segundo automáticamente",
            style=f"dim {LIGHT_GRAY}",
            justify="center",
        )

        return Panel(controls, border_style=NEON_PURPLE, box=ROUNDED)

    def update(
        self,
        odds_api_status: str = "unknown",
        football_api_status: str = "unknown",
        gemini_status: str = "unknown",
        odds_requests: int = 0,
        football_requests: int = 0,
        tasks: Optional[List[dict]] = None,
        markets: Optional[List[dict]] = None,
        logs: Optional[List[str]] = None,
    ):
        """Update all dashboard zones."""
        self.layout["header"].update(self.render_header())
        self.layout["footer"].update(self.render_footer())

        self.layout["zone_a"].update(
            render_api_health(
                odds_api_status,
                football_api_status,
                gemini_status,
                odds_requests,
                football_requests,
            )
        )

        self.layout["zone_b"].update(render_active_tasks(tasks))
        self.layout["zone_c"].update(render_market_watch(markets))
        self.layout["zone_d"].update(render_system_logs(logs))

    async def run_live(
        self,
        update_callback=None,
        update_interval: float = 1.0,
    ):
        """
        Run dashboard in live mode with auto-refresh.
        
        Args:
            update_callback: Async function that returns update data
            update_interval: Seconds between updates
        """
        with Live(
            self.layout, console=self.console, screen=True, auto_refresh=True, refresh_per_second=2
        ) as live:
            try:
                while True:
                    # Get fresh data if callback provided
                    if update_callback:
                        data = await update_callback()
                        if data:
                            self.update(**data)
                        else:
                            self.update()
                    else:
                        self.update()
                    
                    await asyncio.sleep(update_interval)
            except KeyboardInterrupt:
                pass

    def render_once(
        self,
        odds_api_status: str = "unknown",
        football_api_status: str = "unknown",
        gemini_status: str = "unknown",
        odds_requests: int = 0,
        football_requests: int = 0,
        tasks: Optional[List[dict]] = None,
        markets: Optional[List[dict]] = None,
        logs: Optional[List[str]] = None,
    ):
        """Render dashboard once (no live mode)."""
        self.update(
            odds_api_status,
            football_api_status,
            gemini_status,
            odds_requests,
            football_requests,
            tasks,
            markets,
            logs,
        )
        self.console.print(self.layout)
