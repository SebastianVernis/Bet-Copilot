#!/usr/bin/env python3
"""
Test script for AI fallback system.
Tests Gemini → Blackbox → SimpleAnalyzer fallback.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bet_copilot.ai.ai_client import create_ai_client

console = Console()


async def test_ai_fallback():
    """Test AI client with fallback."""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Test: AI Client con Fallback                [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════[/bold cyan]\n")
    
    # Create AI client
    console.print("[bold]Inicializando AI client...[/bold]\n")
    ai_client = create_ai_client()
    
    # Check availability
    table = Table(title="Estado de Proveedores", show_header=True)
    table.add_column("Proveedor", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("Rol")
    
    provider = ai_client.get_active_provider()
    table.add_row(
        provider,
        "[green]✓ Activo[/green]",
        "Primario"
    )
    
    # Show fallback chain
    for i, (name, client) in enumerate(ai_client.fallback_chain, 1):
        status = "[green]✓ Disponible[/green]" if client.is_available() else "[yellow]⚠ No disponible[/yellow]"
        table.add_row(
            name,
            status,
            f"Fallback {i}"
        )
    
    console.print(table)
    console.print()
    
    # Test match analysis
    console.print("[bold]Probando análisis de partido...[/bold]\n")
    
    try:
        analysis = await ai_client.analyze_match_context(
            home_team="Arsenal",
            away_team="Chelsea",
            home_form="WWDLW",
            away_form="DWLWW",
            h2h_results=["H", "A", "D", "H", "A"],
            additional_context="Arsenal sin Saka (lesionado). Chelsea en buena racha."
        )
        
        # Display results
        panel_content = f"""[green]✓ Análisis completado exitosamente[/green]

[bold]Partido:[/bold] {analysis.home_team} vs {analysis.away_team}

[bold]Ajustes Lambda:[/bold]
  • Local: {analysis.lambda_adjustment_home:.2f}
  • Visitante: {analysis.lambda_adjustment_away:.2f}

[bold]Confianza:[/bold] {analysis.confidence*100:.0f}%
[bold]Sentimiento:[/bold] {analysis.sentiment}

[bold]Factores Clave:[/bold]
{chr(10).join(f'  • {factor}' for factor in analysis.key_factors)}

[bold]Razonamiento:[/bold]
{analysis.reasoning}
"""
        
        console.print(Panel(
            panel_content,
            title=f"Análisis con {ai_client.get_active_provider()}",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]✗ Error en análisis:[/red]\n{str(e)}",
            title="Error",
            border_style="red"
        ))
    
    finally:
        await ai_client.close()
    
    console.print()


async def test_multiple_providers():
    """Test both providers independently."""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Test: Comparar Proveedores                  [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════[/bold cyan]\n")
    
    results = []
    
    # Test Gemini first
    console.print("[bold]1. Probando Gemini...[/bold]\n")
    gemini_client = create_ai_client(prefer_gemini=True)
    
    try:
        analysis = await gemini_client.analyze_match_context(
            home_team="Barcelona",
            away_team="Real Madrid",
            home_form="WWWDW",
            away_form="WWLWW",
            h2h_results=["H", "A", "H", "D", "A"],
        )
        
        results.append(("Gemini", analysis))
        console.print(f"[green]✓ Gemini:[/green] Confianza {analysis.confidence*100:.0f}%")
    except Exception as e:
        console.print(f"[yellow]⚠ Gemini:[/yellow] {str(e)}")
    finally:
        await gemini_client.close()
    
    console.print()
    
    # Test Blackbox
    console.print("[bold]2. Probando Blackbox...[/bold]\n")
    blackbox_client = create_ai_client(prefer_gemini=False)
    
    try:
        analysis = await blackbox_client.analyze_match_context(
            home_team="Barcelona",
            away_team="Real Madrid",
            home_form="WWWDW",
            away_form="WWLWW",
            h2h_results=["H", "A", "H", "D", "A"],
        )
        
        results.append(("Blackbox", analysis))
        console.print(f"[green]✓ Blackbox:[/green] Confianza {analysis.confidence*100:.0f}%")
    except Exception as e:
        console.print(f"[yellow]⚠ Blackbox:[/yellow] {str(e)}")
    finally:
        await blackbox_client.close()
    
    console.print()
    
    # Compare results
    if len(results) > 1:
        console.print("[bold]Comparación:[/bold]\n")
        
        table = Table(show_header=True)
        table.add_column("Aspecto")
        table.add_column(results[0][0], style="cyan")
        table.add_column(results[1][0], style="pink")
        
        table.add_row(
            "Lambda Local",
            f"{results[0][1].lambda_adjustment_home:.2f}",
            f"{results[1][1].lambda_adjustment_home:.2f}"
        )
        table.add_row(
            "Lambda Visitante",
            f"{results[0][1].lambda_adjustment_away:.2f}",
            f"{results[1][1].lambda_adjustment_away:.2f}"
        )
        table.add_row(
            "Confianza",
            f"{results[0][1].confidence*100:.0f}%",
            f"{results[1][1].confidence*100:.0f}%"
        )
        table.add_row(
            "Sentimiento",
            results[0][1].sentiment,
            results[1][1].sentiment
        )
        
        console.print(table)
    
    console.print()


async def main():
    """Main test runner."""
    
    try:
        # Test 1: Fallback system
        await test_ai_fallback()
        
        # Test 2: Compare providers
        console.print()
        choice = console.input("[cyan]¿Comparar ambos proveedores? (s/n):[/cyan] ").strip().lower()
        
        if choice in ['s', 'y', 'si', 'yes']:
            await test_multiple_providers()
        
        console.print("[green]✓ Tests completados[/green]\n")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrumpido[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
