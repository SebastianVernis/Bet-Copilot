"""
Main CLI interface for Bet-Copilot.
Interactive command-line tool for sports betting analysis.
"""

import asyncio
import logging
import sys
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table
from rich.box import MINIMAL

from bet_copilot.api.odds_client import OddsAPIClient
from bet_copilot.api.football_client_with_fallback import create_football_client
from bet_copilot.ai.ai_client import create_ai_client
from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.math_engine.kelly import KellyCriterion
from bet_copilot.services.match_analyzer import MatchAnalyzer
from bet_copilot.ui.dashboard import Dashboard
from bet_copilot.ui.command_input import create_command_input
from bet_copilot.ui.styles import NEON_PURPLE, NEON_GREEN, NEON_RED, NEON_CYAN, NEON_PINK, LIGHT_GRAY, BET_COPILOT_THEME
from bet_copilot.config import LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BetCopilotCLI:
    """Main CLI application."""

    def __init__(self):
        self.console = Console(theme=BET_COPILOT_THEME)
        self.dashboard = Dashboard()

        # Initialize clients
        self.odds_client = OddsAPIClient()
        self.football_client = create_football_client()  # With fallback to SimpleProvider
        self.ai_client = create_ai_client()  # Unified AI with fallback
        self.soccer_predictor = SoccerPredictor()
        self.kelly = KellyCriterion()
        self.match_analyzer = MatchAnalyzer(
            self.odds_client,
            self.football_client,
            self.ai_client,
            self.soccer_predictor,
            self.kelly,
        )

        # Estado
        self.logs: list = ["Sistema inicializado"]
        self.tasks: list = []
        self.markets: list = []
        self.events: list = []  # Store full OddsEvent objects
        
        # Advanced command input (initialized after self.events exists)
        self.command_input = create_command_input(self)

    def print_banner(self):
        """Imprime banner de bienvenida."""
        banner = Text()
        banner.append("╔═══════════════════════════════════════╗\n", style=NEON_PURPLE)
        banner.append("║                                       ║\n", style=NEON_PURPLE)
        banner.append("║           ", style=NEON_PURPLE)
        banner.append("BET-COPILOT", style=f"bold {NEON_PURPLE}")
        banner.append("            ║\n", style=NEON_PURPLE)
        banner.append("║                                       ║\n", style=NEON_PURPLE)
        banner.append("║   Sistema de Análisis Especulativo   ║\n", style=NEON_PURPLE)
        banner.append("║                                       ║\n", style=NEON_PURPLE)
        banner.append("╚═══════════════════════════════════════╝\n", style=NEON_PURPLE)

        self.console.print(banner)
        self.console.print(
            Text(
                "⚠️  Herramienta de soporte a decisiones, NO asesoría financiera.\n",
                style="dim",
            )
        )

    def print_help(self):
        """Imprime menú de ayuda."""
        help_text = """
[bold]Comandos Disponibles:[/bold]

  [cyan]dashboard[/cyan]        Mostrar dashboard en vivo (4 zonas)
  [cyan]mercados[/cyan]         Obtener y mostrar mercados de apuestas
  [cyan]analizar[/cyan]         Analizar un partido específico
  [cyan]salud[/cyan]            Verificar estado de las APIs
  [cyan]ayuda[/cyan]            Mostrar este menú de ayuda
  [cyan]salir[/cyan]            Salir de la aplicación

[bold]Ejemplos:[/bold]

  > mercados
  > mercados soccer_la_liga
  > analizar Leeds United vs Manchester United
  > dashboard

[bold]Claves de Deportes:[/bold] soccer_epl (defecto), soccer_la_liga, soccer_serie_a, 
soccer_bundesliga, soccer_france_ligue_one, americanfootball_nfl, etc.

[bold]Atajos de Teclado:[/bold]

  [green]↑/↓[/green]             Navegar historial de comandos
  [green]Tab[/green]              Autocompletar comandos y argumentos
  [green]←/→[/green]             Mover cursor en la línea
  [green]Ctrl+R[/green]           Buscar en historial
  [green]Ctrl+C[/green]           Cancelar comando actual

[dim]Nota: El modelo actual usa ajustes simples de probabilidad implícita.
Para uso en producción, integre estadísticas de API-Football y predicciones Poisson.[/dim]
"""
        self.console.print(help_text)

    async def check_health(self):
        """Verifica salud de todas las APIs."""
        self.console.print("\n[bold]Verificando salud de las APIs...[/bold]\n")

        # Verificar Odds API
        try:
            await self.odds_client.get_sports()
            odds_status = "healthy"
            self.console.print("✓ The Odds API", style=f"bold {NEON_GREEN}")
        except Exception as e:
            odds_status = "down"
            self.console.print(
                f"✗ The Odds API: {str(e)[:50]}", style=f"bold {NEON_RED}"
            )

        # Verificar API-Football (con fallback)
        try:
            if self.football_client.is_available():
                provider = self.football_client.get_active_provider()
                football_status = "healthy"
                self.console.print(f"✓ Football Data ({provider})", style=f"bold {NEON_GREEN}")
            else:
                football_status = "degraded"
                self.console.print("⚠ Football Data: Usando estimaciones", style="bold yellow")
        except Exception as e:
            football_status = "degraded"
            self.console.print(
                f"⚠ Football Data: {str(e)[:50]}", style="bold yellow"
            )

        # Verificar AI (Gemini/Blackbox)
        if self.ai_client.is_available():
            ai_status = "healthy"
            provider = self.ai_client.get_active_provider()
            self.console.print(f"✓ AI ({provider})", style=f"bold {NEON_GREEN}")
        else:
            ai_status = "degraded"
            self.console.print("⚠ AI: No disponible", style="bold yellow")

        self.console.print()
        return {
            "odds": odds_status,
            "football": football_status,
            "ai": ai_status,
        }

    async def fetch_markets(self, sport_key: str = "soccer_epl"):
        """Obtiene mercados para un deporte."""
        self.console.print(f"\n[bold]Obteniendo mercados para {sport_key}...[/bold]\n")

        try:
            events = await self.odds_client.get_odds(sport_key)

            if not events:
                self.console.print("No se encontraron eventos", style="yellow")
                return

            self.console.print(f"Se encontraron {len(events)} eventos", style=NEON_GREEN)
            self.console.print("[dim]Usa 'analizar [nombre]' + Tab para autocompletar[/dim]\n")

            # Store full events for autocompletion
            self.events = events
            
            # Update completer with new events
            if hasattr(self, 'command_input'):
                self.command_input.completer.cli_instance = self

            # Display first few
            for event in events[:5]:
                self.console.print(
                    f"  • {event.home_team} vs {event.away_team}",
                    style="cyan",
                )
                self.console.print(
                    f"    {event.commence_time.strftime('%Y-%m-%d %H:%M')}",
                    style="dim",
                )

            # Build markets with real odds
            self.markets = []
            for event in events:
                # Try to get best odds for home win
                home_odds = event.get_best_odds("h2h", event.home_team)
                away_odds = event.get_best_odds("h2h", event.away_team)
                
                # Get bookmaker name (first available)
                bookmaker = event.bookmakers[0].title if event.bookmakers else "Unknown"
                
                # Simple model: implied probability as baseline
                if home_odds and home_odds > 1.0:
                    home_implied = 1.0 / home_odds
                    # Add small edge for demonstration (in production, use real model)
                    model_prob = min(0.95, home_implied * 1.05)  # 5% adjustment
                    ev = (model_prob * home_odds) - 1
                    
                    self.markets.append({
                        "home_team": event.home_team,
                        "away_team": event.away_team,
                        "market_type": "Home Win",
                        "model_prob": model_prob,
                        "odds": home_odds,
                        "ev": ev,
                        "bookmaker": bookmaker,
                    })
                
                # Also add away win market
                if away_odds and away_odds > 1.0:
                    away_implied = 1.0 / away_odds
                    model_prob = min(0.95, away_implied * 1.05)
                    ev = (model_prob * away_odds) - 1
                    
                    self.markets.append({
                        "home_team": event.home_team,
                        "away_team": event.away_team,
                        "market_type": "Away Win",
                        "model_prob": model_prob,
                        "odds": away_odds,
                        "ev": ev,
                        "bookmaker": bookmaker,
                    })

            self.logs.append(f"Obtenidos {len(events)} eventos, {len(self.markets)} mercados")

        except Exception as e:
            self.console.print(f"Error: {str(e)}", style=f"bold {NEON_RED}")
            self.logs.append(f"Error obteniendo mercados: {str(e)[:50]}")

    async def analyze_match(self, match_name: str):
        """Analiza un partido específico con datos completos."""
        self.console.print(f"\n[bold]Analizando: {match_name}[/bold]\n")

        # Buscar el evento completo
        event_found = None
        for event in self.events:
            match_str = f"{event.home_team} vs {event.away_team}"
            if match_name.lower() in match_str.lower():
                event_found = event
                break

        if not event_found:
            self.console.print(
                f"[yellow]Partido no encontrado en los mercados actuales.[/yellow]"
            )
            self.console.print(
                "[dim]Intenta obtener mercados primero con: mercados[/dim]\n"
            )
            return

        # Mostrar spinner de progreso
        from rich.spinner import Spinner
        from rich.live import Live

        with self.console.status(
            f"[bold cyan]Obteniendo datos de API-Football...", spinner="dots"
        ):
            # Análisis completo con MatchAnalyzer
            analysis = await self.match_analyzer.analyze_from_odds_event(
                event_found, league_id=39, season=2024
            )

        # Mostrar información del partido
        self.console.print(f"[bold]╔═══ {analysis.home_team} vs {analysis.away_team} ═══╗[/bold]", style=NEON_PURPLE)
        self.console.print(f"Liga: {analysis.league}")
        self.console.print(f"Fecha: {analysis.commence_time.strftime('%Y-%m-%d %H:%M')}\n")

        # Estadísticas de equipos
        if analysis.home_stats and analysis.away_stats:
            self.console.print("[bold]📊 Estadísticas de Equipos[/bold]\n", style=NEON_CYAN)

            from rich.table import Table
            stats_table = Table(box=MINIMAL, show_header=True)
            stats_table.add_column("Métrica", style=LIGHT_GRAY)
            stats_table.add_column(analysis.home_team, justify="center", style=NEON_CYAN)
            stats_table.add_column(analysis.away_team, justify="center", style=NEON_PINK)

            stats_table.add_row(
                "Partidos Jugados",
                str(analysis.home_stats.matches_played),
                str(analysis.away_stats.matches_played),
            )
            stats_table.add_row(
                "Forma (últimos 5)",
                analysis.home_stats.form or "N/A",
                analysis.away_stats.form or "N/A",
            )
            stats_table.add_row(
                "Goles Promedio",
                f"{analysis.home_stats.avg_goals_for:.2f}",
                f"{analysis.away_stats.avg_goals_for:.2f}",
            )
            stats_table.add_row(
                "Goles Recibidos",
                f"{analysis.home_stats.avg_goals_against:.2f}",
                f"{analysis.away_stats.avg_goals_against:.2f}",
            )

            self.console.print(stats_table)
            self.console.print()

        # Jugadores ausentes
        if analysis.home_lineup and analysis.home_lineup.missing_players:
            self.console.print(f"[bold red]⚠️ {analysis.home_team} - Jugadores Ausentes:[/bold red]")
            for player in analysis.home_lineup.missing_players[:5]:
                status = "Lesionado" if player.is_injured else "Suspendido"
                self.console.print(f"  • {player.player_name} ({status})", style="red")
            self.console.print()

        if analysis.away_lineup and analysis.away_lineup.missing_players:
            self.console.print(f"[bold red]⚠️ {analysis.away_team} - Jugadores Ausentes:[/bold red]")
            for player in analysis.away_lineup.missing_players[:5]:
                status = "Lesionado" if player.is_injured else "Suspendido"
                self.console.print(f"  • {player.player_name} ({status})", style="red")
            self.console.print()

        # H2H
        if analysis.h2h_stats and analysis.h2h_stats.matches_played > 0:
            self.console.print("[bold]🔄 Historial Directo (H2H)[/bold]\n", style=NEON_CYAN)
            self.console.print(
                f"Últimos {analysis.h2h_stats.matches_played} enfrentamientos: "
                f"[green]{analysis.h2h_stats.home_wins}[/green] - "
                f"[yellow]{analysis.h2h_stats.draws}[/yellow] - "
                f"[red]{analysis.h2h_stats.away_wins}[/red]"
            )
            self.console.print(
                f"Resultados recientes: {' '.join(analysis.h2h_stats.last_5_results)}\n"
            )

        # Predicción Poisson
        if analysis.prediction:
            self.console.print("[bold]🎲 Predicción Matemática (Poisson)[/bold]\n", style=NEON_CYAN)
            self.console.print(f"Expected Goals: [cyan]{analysis.prediction.home_lambda:.2f}[/cyan] - [pink]{analysis.prediction.away_lambda:.2f}[/pink]")
            self.console.print(f"Probabilidades:")
            self.console.print(
                f"  Victoria Local: [green]{analysis.prediction.home_win_prob*100:.1f}%[/green]"
            )
            self.console.print(f"  Empate: [yellow]{analysis.prediction.draw_prob*100:.1f}%[/yellow]")
            self.console.print(
                f"  Victoria Visitante: [red]{analysis.prediction.away_win_prob*100:.1f}%[/red]"
            )
            self.console.print(
                f"Score más probable: {analysis.prediction.most_likely_score[0]}-{analysis.prediction.most_likely_score[1]} "
                f"({analysis.prediction.most_likely_score_prob*100:.1f}%)\n"
            )

        # Análisis IA
        if analysis.ai_analysis:
            self.console.print("[bold]🤖 Análisis Contextual (Gemini AI)[/bold]\n", style=NEON_CYAN)
            self.console.print(f"Confianza: {analysis.ai_analysis.confidence*100:.0f}%")
            self.console.print(f"Sentimiento: {analysis.ai_analysis.sentiment}")
            self.console.print(f"Razonamiento: {analysis.ai_analysis.reasoning}")
            if analysis.ai_analysis.key_factors:
                self.console.print("\nFactores clave:")
                for factor in analysis.ai_analysis.key_factors:
                    self.console.print(f"  • {factor}", style=LIGHT_GRAY)
            self.console.print()

        # Insights clave
        insights = analysis.get_key_insights()
        if insights:
            self.console.print("[bold]💡 Insights Clave[/bold]\n", style=NEON_CYAN)
            for insight in insights:
                self.console.print(f"  {insight}")
            self.console.print()

        # Recomendaciones Kelly
        best_bet = analysis.get_best_value_bet()

        if best_bet:
            self.console.print("[bold]💰 Mejor Apuesta de Valor[/bold]\n", style=NEON_GREEN)
            self.console.print(f"Resultado: [bold]{best_bet['outcome']}[/bold]")
            if best_bet['team']:
                self.console.print(f"Equipo: {best_bet['team']}")
            self.console.print(f"Cuota: {best_bet['odds']:.2f}")
            self.console.print(f"Valor Esperado: [green]+{best_bet['ev']*100:.1f}%[/green]")

            risk_names = {"LOW": "BAJO", "MEDIUM": "MEDIO", "HIGH": "ALTO"}
            self.console.print(
                f"Apuesta Recomendada: [bold]{best_bet['stake']:.2f}%[/bold] del bankroll"
            )
            self.console.print(
                f"Nivel de Riesgo: {risk_names.get(best_bet['risk'], best_bet['risk'])}"
            )
            self.console.print()
        else:
            self.console.print(
                "[yellow]⚠️ No se detectaron apuestas de valor para este partido[/yellow]\n"
            )

    async def show_dashboard(self):
        """Muestra dashboard en vivo con actualización continua."""
        from rich.live import Live
        
        self.console.print("\n[bold]Iniciando dashboard en vivo...[/bold]")
        self.console.print("[dim]Presiona Ctrl+C para volver al CLI[/dim]\n")

        await asyncio.sleep(0.5)

        # Contador de actualizaciones para health check periódico
        update_counter = 0
        health_check_interval = 30  # Check health cada 30 actualizaciones (30 segundos)

        try:
            with Live(
                self.dashboard.layout,
                console=self.console,
                screen=True,
                auto_refresh=True,
                refresh_per_second=2,
            ) as live:
                while True:
                    # Health check periódico (no en cada actualización para ahorrar requests)
                    if update_counter % health_check_interval == 0:
                        # Quick health check sin hacer requests
                        health = {
                            "odds": "healthy" if self.odds_client.api_key else "down",
                            "football": "healthy" if self.football_client.use_api else "degraded",
                            "ai": "healthy" if self.ai_client.is_available() else "degraded",
                        }
                    
                    # Actualizar dashboard
                    self.dashboard.update(
                        odds_api_status=health.get("odds", "unknown"),
                        football_api_status=health.get("football", "unknown"),
                        gemini_status=health.get("ai", "unknown"),
                        odds_requests=len(self.markets) // 2,  # Estimado
                        football_requests=0,
                        tasks=self.tasks if self.tasks else None,
                        markets=self.markets[:10],
                        logs=self.logs[-5:],
                    )

                    update_counter += 1
                    await asyncio.sleep(1)

        except KeyboardInterrupt:
            # Limpiar pantalla y volver al CLI
            self.console.clear()
            self.console.print("\n[dim]Dashboard cerrado. Volviendo al CLI...[/dim]\n")

    async def run_command(self, command: str):
        """Ejecuta un comando."""
        command_lower = command.strip().lower()

        if not command_lower:
            return True

        # Comandos de salida (español e inglés)
        if command_lower in ["salir", "quit", "exit", "q"]:
            return False

        # Ayuda (español e inglés)
        elif command_lower in ["ayuda", "help"]:
            self.print_help()

        # Salud (español e inglés)
        elif command_lower in ["salud", "health"]:
            await self.check_health()

        # Dashboard
        elif command_lower == "dashboard":
            await self.show_dashboard()

        # Mercados (español e inglés)
        elif command_lower.startswith("mercados") or command_lower.startswith("markets"):
            parts = command_lower.split()
            sport_key = parts[1] if len(parts) > 1 else "soccer_epl"
            await self.fetch_markets(sport_key)

        # Analizar (español e inglés)
        elif command_lower.startswith("analizar") or command_lower.startswith("analyze") or command_lower.startswith("analyse"):
            # Extraer nombre del partido (preservar mayúsculas originales)
            if command_lower.startswith("analizar"):
                match_part = command.strip()[8:].strip()
            else:
                match_part = command.strip()[7:].strip()
            
            match_part = match_part.strip('"\'')  # Remover comillas si existen
            
            if match_part:
                await self.analyze_match(match_part)
            else:
                self.console.print(
                    "[yellow]Uso: analizar <partido>\nEjemplo: analizar Arsenal vs Chelsea[/yellow]"
                )

        else:
            self.console.print(
                f"[red]Comando desconocido: {command_lower}[/red]",
            )
            self.console.print("Escribe 'ayuda' para ver los comandos disponibles\n")

        return True

    async def run(self):
        """Bucle principal del CLI."""
        self.print_banner()
        self.print_help()

        try:
            while True:
                # Use advanced command input with history and completion
                command = await self.command_input.get_command()
                
                if not command:  # Empty or Ctrl+C/Ctrl+D
                    continue
                
                should_continue = await self.run_command(command)

                if not should_continue:
                    self.console.print(
                        "\n[bold]¡Gracias por usar Bet-Copilot![/bold]\n",
                        style=NEON_PURPLE,
                    )
                    break

        except KeyboardInterrupt:
            self.console.print(
                "\n\n[bold]Interrumpido. Saliendo...[/bold]\n",
                style=NEON_RED,
            )
        except Exception as e:
            self.console.print(
                f"\n[bold red]Error fatal: {str(e)}[/bold red]\n"
            )
            logger.exception("Error fatal en CLI")
            sys.exit(1)

        finally:
            # Limpieza
            await self.odds_client.close()
            await self.football_client.close()
            await self.ai_client.close()


def main():
    """Entry point for CLI."""
    cli = BetCopilotCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
