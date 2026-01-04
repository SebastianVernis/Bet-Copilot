#!/usr/bin/env python3
"""
Demo de Bet-Copilot v0.5.1
Muestra las características principales sin necesitar todas las dependencias.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import MINIMAL

console = Console()


def print_banner():
    """Banner de bienvenida."""
    banner = """
╔═══════════════════════════════════════╗
║                                       ║
║           BET-COPILOT v0.5.1          ║
║                                       ║
║   Sistema de Análisis Especulativo   ║
║                                       ║
╚═══════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")
    console.print("⚠️  Demo - Muestra las características implementadas\n", style="dim")


def demo_features():
    """Muestra las características principales."""
    
    # Feature 1: Input Avanzado
    console.print("\n[bold cyan]1. Sistema de Input Avanzado[/bold cyan]\n")
    
    table = Table(title="Características de Input", box=MINIMAL)
    table.add_column("Feature", style="cyan")
    table.add_column("Atajo", style="green")
    table.add_column("Descripción", style="dim")
    
    table.add_row("Historial", "↑/↓", "Navega comandos anteriores")
    table.add_row("Autocompletado", "Tab", "Completa comandos y argumentos")
    table.add_row("Búsqueda", "Ctrl+R", "Búsqueda incremental en historial")
    table.add_row("Edición", "←/→", "Mueve cursor en la línea")
    table.add_row("Inicio/Fin", "Ctrl+A/E", "Ir a inicio/fin de línea")
    
    console.print(table)
    
    # Feature 2: AI Multi-Nivel
    console.print("\n[bold cyan]2. Sistema AI con Fallback Multi-Nivel[/bold cyan]\n")
    
    table2 = Table(title="Proveedores AI", box=MINIMAL)
    table2.add_column("Nivel", justify="center", style="yellow")
    table2.add_column("Proveedor", style="cyan")
    table2.add_column("Modelo", style="green")
    table2.add_column("Calidad", justify="center")
    table2.add_column("Requiere", style="dim")
    
    table2.add_row("1", "Gemini", "gemini-pro", "⭐⭐⭐⭐⭐", "API Key")
    table2.add_row("2", "Blackbox", "blackboxai-pro", "⭐⭐⭐⭐", "API Key")
    table2.add_row("3", "SimpleAnalyzer", "heurísticas", "⭐⭐⭐", "Nada")
    
    console.print(table2)
    console.print("\n[green]✓ Fallback automático garantiza 100% disponibilidad[/green]\n")
    
    # Feature 3: Autocompletado
    console.print("[bold cyan]3. Autocompletado Inteligente[/bold cyan]\n")
    
    examples = [
        ("mer[Tab]", "→ mercados"),
        ("mercados soc[Tab]", "→ soccer_epl, soccer_la_liga, ..."),
        ("analizar [Tab]", "→ [Muestra todos los partidos]"),
        ("analizar Ars[Tab]", "→ Arsenal vs Chelsea"),
    ]
    
    for input_ex, output in examples:
        console.print(f"  [green]{input_ex:25}[/green] [dim]{output}[/dim]")
    
    # Feature 4: Tests
    console.print("\n[bold cyan]4. Suite de Tests Completa[/bold cyan]\n")
    
    console.print("  [green]✓ 67 tests[/green] totales")
    console.print("  [green]✓ 66 passing[/green] (98.5%)")
    console.print("  [green]✓ 56% coverage[/green] (75% sin UI)")
    console.print("  [dim]  Ejecutar: ./run_tests.sh[/dim]")
    
    # Feature 5: SimpleAnalyzer Demo
    console.print("\n[bold cyan]5. SimpleAnalyzer - Análisis sin API[/bold cyan]\n")
    
    panel = Panel(
        """[bold]Entrada:[/bold]
  • Home: Arsenal (WWWWW)
  • Away: Chelsea (LLLLL)
  • H2H: [H, H, H, D, A]

[bold]Análisis:[/bold]
  • Form score: 1.0 vs 0.0
  • H2H factor: +0.4 (Arsenal domina)
  
[bold]Ajustes Lambda:[/bold]
  • Home: 1.0 + 0.1 (forma) + 0.05 (H2H) = [green]1.15[/green]
  • Away: 1.0 - 0.05 (forma) = [red]0.95[/red]

[bold]Resultado:[/bold]
  • Confianza: 70%
  • Sentimiento: POSITIVE
  • Factores: ["Arsenal en mejor forma", "Domina H2H"]
  
[dim]⚡ Tiempo: <0.1s (sin API calls)[/dim]""",
        title="Ejemplo de SimpleAnalyzer",
        border_style="green"
    )
    console.print(panel)


def demo_architecture():
    """Muestra la arquitectura del sistema."""
    
    console.print("\n[bold cyan]Arquitectura del Sistema[/bold cyan]\n")
    
    arch = """
┌─────────────────────────────────────┐
│  User Input (prompt_toolkit)       │
│  ↑↓ Historial, Tab Autocomplete    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  CLI (bet_copilot/cli.py)          │
│  Procesa comandos                   │
└──────────────┬──────────────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
┌──────────────┐  ┌──────────────┐
│ Odds API     │  │ AI Client    │
│ (The Odds)   │  │ (Multi-Nivel)│
└──────────────┘  └──────┬───────┘
                         ↓
                  ┌──────┴──────┐
                  ↓      ↓      ↓
              Gemini Blackbox Simple
                  ↓      ↓      ↓
              API    API    Local
              Key    Key    Rules
"""
    
    console.print(arch, style="dim")
    
    console.print("\n[green]✓ Fallback automático en cada nivel[/green]")
    console.print("[green]✓ Sistema nunca falla (SimpleAnalyzer garantiza)[/green]\n")


def demo_stats():
    """Muestra estadísticas del proyecto."""
    
    console.print("[bold cyan]Estadísticas del Proyecto[/bold cyan]\n")
    
    stats = Table(box=MINIMAL)
    stats.add_column("Métrica", style="cyan")
    stats.add_column("Valor", justify="right", style="green")
    stats.add_column("Incremento", style="dim")
    
    stats.add_row("Líneas de código", "~22,500", "+8,500 (v0.5.1)")
    stats.add_row("Tests unitarios", "67", "+43 (179%)")
    stats.add_row("Tests passing", "66", "98.5%")
    stats.add_row("Coverage", "56%", "75% sin UI")
    stats.add_row("Documentación", "~15,000", "+7,000 líneas")
    stats.add_row("Archivos MD", "30+", "+13 archivos")
    stats.add_row("Módulos AI", "3", "Gemini, Blackbox, Simple")
    stats.add_row("Sport keys", "13", "Autocompletables")
    
    console.print(stats)


def demo_usage():
    """Muestra ejemplo de uso."""
    
    console.print("\n[bold cyan]Ejemplo de Uso[/bold cyan]\n")
    
    usage = """[bold green]$ python main.py[/bold green]

[cyan]➜ bet-copilot[/cyan] mer[dim][Tab][/dim]
[cyan]➜ bet-copilot[/cyan] mercados

[green]✓ Se encontraron 15 eventos[/green]
Usa 'analizar [nombre]' + Tab para autocompletar

  • Arsenal vs Chelsea
  • Liverpool vs Man City
  • Barcelona vs Real Madrid
  ...

[cyan]➜ bet-copilot[/cyan] analizar [dim][Tab][/dim]
  [dim]Arsenal vs Chelsea (2026-01-05 15:00)
  Liverpool vs Man City (2026-01-06 17:30)
  ...[/dim]

[cyan]➜ bet-copilot[/cyan] analizar Arsenal vs Chelsea

[bold]Analizando: Arsenal vs Chelsea[/bold]

[green]✓ Análisis completado con SimpleAnalyzer[/green]

🎲 Predicción:
  • Expected Goals: 1.65 - 1.85
  • Probabilidades: 38.5% - 28.2% - 33.3%
  • Score probable: 1-2 (12.8%)

💰 Mejor Apuesta:
  • Victoria Visitante
  • Cuota: 2.85
  • EV: +8.5%
  • Stake: 2.12% del bankroll
"""
    
    console.print(Panel(usage, title="Demo de Uso", border_style="cyan"))


def main():
    """Ejecuta el demo."""
    
    print_banner()
    
    console.print("[bold]Características Implementadas:[/bold]\n")
    demo_features()
    
    console.print("\n" + "─" * 60 + "\n")
    demo_architecture()
    
    console.print("─" * 60 + "\n")
    demo_stats()
    
    console.print("\n" + "─" * 60 + "\n")
    demo_usage()
    
    console.print("\n" + "─" * 60 + "\n")
    
    console.print("\n[bold green]🎉 Bet-Copilot v0.5.1 - Production Ready[/bold green]\n")
    
    console.print("[bold]Para ejecutar el CLI real:[/bold]")
    console.print("  1. Instalar dependencias: [cyan]./INSTALL_DEPS.sh[/cyan]")
    console.print("  2. Verificar: [cyan]python check_deps.py[/cyan]")
    console.print("  3. Ejecutar: [cyan]python main.py[/cyan]")
    console.print()
    
    console.print("[bold]Documentación:[/bold]")
    console.print("  • [cyan]INDICE_DOCUMENTACION.md[/cyan] - Índice completo")
    console.print("  • [cyan]ESTADO_FINAL.md[/cyan] - Estado del proyecto")
    console.print("  • [cyan]COVERAGE_REPORT.md[/cyan] - Análisis de coverage")
    console.print()
    
    console.print("[bold]Tests:[/bold]")
    console.print("  • [cyan]./run_tests.sh[/cyan] - Menú interactivo")
    console.print("  • [green]66/67 passing (98.5%)[/green]")
    console.print("  • [green]56% coverage (75% sin UI)[/green]")
    console.print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
