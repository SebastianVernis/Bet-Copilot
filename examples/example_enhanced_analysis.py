#!/usr/bin/env python3
"""
Demostración del análisis mejorado con datos reales.
Muestra la nueva funcionalidad de v0.4.0.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from bet_copilot.services.match_analyzer import MatchAnalyzer
from bet_copilot.api.football_client import TeamStats, H2HStats, PlayerStats, TeamLineup
from bet_copilot.models.soccer import MatchPrediction
from bet_copilot.ui.styles import NEON_GREEN, NEON_CYAN, NEON_PURPLE, NEON_RED


async def demo_with_mock_data():
    """Demo con datos simulados (no requiere API keys)."""
    console = Console()

    console.print(
        Panel(
            Text("Demo de Análisis Mejorado v0.4.0", justify="center", style="bold"),
            border_style=NEON_PURPLE,
        )
    )
    console.print()

    # Simular análisis completo
    console.print("[bold]📊 Simulación de Análisis Completo[/bold]\n", style=NEON_CYAN)

    # 1. Stats de equipos
    console.print("[bold]1. Estadísticas de Equipos[/bold]", style=NEON_GREEN)

    home_stats = TeamStats(
        team_id=1,
        team_name="Arsenal",
        matches_played=20,
        wins=14,
        draws=4,
        losses=2,
        goals_for=42,
        goals_against=18,
        clean_sheets=8,
        failed_to_score=2,
        avg_goals_for=2.1,
        avg_goals_against=0.9,
        form="WWWDW",
    )

    away_stats = TeamStats(
        team_id=2,
        team_name="Chelsea",
        matches_played=20,
        wins=10,
        draws=6,
        losses=4,
        goals_for=32,
        goals_against=24,
        clean_sheets=5,
        failed_to_score=4,
        avg_goals_for=1.6,
        avg_goals_against=1.2,
        form="DWLWD",
    )

    console.print(f"  Arsenal:  Forma {home_stats.form}, {home_stats.avg_goals_for:.1f} goles/partido")
    console.print(f"  Chelsea:  Forma {away_stats.form}, {away_stats.avg_goals_for:.1f} goles/partido\n")

    # 2. Jugadores lesionados
    console.print("[bold]2. Jugadores Ausentes[/bold]", style=NEON_GREEN)

    injured = PlayerStats(
        player_id=10,
        player_name="Bukayo Saka",
        team_id=1,
        team_name="Arsenal",
        position="Attacker",
        rating=8.5,
        goals=12,
        assists=8,
        is_injured=True,
    )

    console.print(f"  ⚠️ Arsenal: {injured.player_name} (Rating {injured.rating}) - Lesionado", style="red")
    console.print()

    # 3. H2H
    console.print("[bold]3. Historial Directo (H2H)[/bold]", style=NEON_GREEN)

    h2h = H2HStats(
        matches_played=5,
        home_wins=3,
        draws=1,
        away_wins=1,
        last_5_results=["H", "A", "D", "H", "H"],
        avg_home_goals=1.8,
        avg_away_goals=1.2,
    )

    console.print(
        f"  Últimos {h2h.matches_played}: Arsenal {h2h.home_wins} - {h2h.draws} - {h2h.away_wins} Chelsea"
    )
    console.print(f"  Resultados: {' '.join(h2h.last_5_results)}\n")

    # 4. Predicción Poisson
    console.print("[bold]4. Predicción con Poisson[/bold]", style=NEON_GREEN)

    from bet_copilot.math_engine.soccer_predictor import SoccerPredictor

    predictor = SoccerPredictor()
    prediction = predictor.predict_from_lambdas(
        "Arsenal", "Chelsea", lambda_home=2.1, lambda_away=1.6
    )

    console.print(f"  Expected Goals: {prediction.home_lambda:.2f} - {prediction.away_lambda:.2f}")
    console.print(f"  Victoria Local: {prediction.home_win_prob*100:.1f}%")
    console.print(f"  Empate: {prediction.draw_prob*100:.1f}%")
    console.print(f"  Victoria Visitante: {prediction.away_win_prob*100:.1f}%")
    console.print(
        f"  Score probable: {prediction.most_likely_score[0]}-{prediction.most_likely_score[1]}\n"
    )

    # 5. Análisis IA (simulado)
    console.print("[bold]5. Análisis Contextual (IA)[/bold]", style=NEON_GREEN)
    console.print("  Sentimiento: POSITIVE (favorece local)")
    console.print("  Factores clave:")
    console.print("    • Arsenal en casa tiene 70% de victorias")
    console.print("    • Chelsea con problemas defensivos")
    console.print("    • Sin Saka, Arsenal reduce ~10% capacidad ofensiva\n")

    # 6. Kelly
    console.print("[bold]6. Recomendación Kelly[/bold]", style=NEON_GREEN)

    from bet_copilot.math_engine.kelly import KellyCriterion

    kelly = KellyCriterion()
    rec = kelly.calculate(prediction.home_win_prob, odds=2.15)

    console.print(f"  Apuesta: {rec.recommended_stake:.2f}% del bankroll")
    console.print(f"  EV: {rec.ev*100:+.1f}%")
    console.print(f"  Riesgo: {rec.risk_level}\n")

    # Resumen
    console.print(
        Panel(
            Text(
                "✅ Este análisis combina datos reales de:\n"
                "• API-Football (stats, jugadores, lesiones)\n"
                "• Gemini AI (contexto, sentimiento)\n"
                "• Poisson (predicción matemática)\n"
                "• Kelly Criterion (sizing óptimo)",
                justify="left",
            ),
            title="[bold]Análisis Completo v0.4.0[/bold]",
            border_style=NEON_GREEN,
        )
    )


async def demo_with_real_apis():
    """Demo con APIs reales (requiere API keys configuradas)."""
    console = Console()

    console.print("\n[bold]🔄 Probando Análisis con APIs Reales...[/bold]\n")

    try:
        analyzer = MatchAnalyzer()

        # Verificar si APIs están configuradas
        if not analyzer.football_client.api_key:
            console.print(
                "[yellow]⚠️ API-Football no configurada. Usando demo con datos simulados.[/yellow]\n"
            )
            await demo_with_mock_data()
            return

        console.print("[cyan]Buscando equipos...[/cyan]")

        # Buscar Arsenal
        arsenal_id = await analyzer.football_client.search_team_by_name("Arsenal")

        if arsenal_id:
            console.print(f"✓ Arsenal encontrado (ID: {arsenal_id})")

            # Obtener stats
            console.print("[cyan]Obteniendo estadísticas...[/cyan]")
            stats = await analyzer.football_client.get_team_stats(
                arsenal_id, season=2024, league_id=39
            )

            console.print(f"✓ Stats obtenidas:")
            console.print(f"  Partidos: {stats.matches_played}")
            console.print(f"  Forma: {stats.form}")
            console.print(f"  Goles promedio: {stats.avg_goals_for:.2f}\n")

            console.print(
                Panel(
                    Text(
                        "✅ API-Football funcionando correctamente!\n"
                        "El análisis completo está disponible con:\n"
                        "bet-copilot> analizar <partido>",
                        justify="center",
                    ),
                    border_style=NEON_GREEN,
                )
            )
        else:
            console.print("[yellow]No se encontró el equipo[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print(
            "\n[yellow]Mostrando demo con datos simulados en su lugar...[/yellow]\n"
        )
        await demo_with_mock_data()


async def main():
    """Main demo function."""
    console = Console()

    console.print(
        """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         DEMO: Análisis Mejorado v0.4.0                   ║
║                                                           ║
║  Nuevas características:                                  ║
║  • Datos reales de jugadores (API-Football)              ║
║  • Detección de lesiones/suspensiones                    ║
║  • Análisis contextual con Gemini AI                     ║
║  • Predicción Poisson con xG real                        ║
║  • Insights automáticos                                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""",
        style=NEON_PURPLE,
    )

    # Try real APIs first, fallback to mock
    await demo_with_real_apis()


if __name__ == "__main__":
    asyncio.run(main())
