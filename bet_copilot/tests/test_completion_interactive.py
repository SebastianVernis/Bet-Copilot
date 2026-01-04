#!/usr/bin/env python3
"""
Interactive test for completion with real prompt_toolkit.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel

# Import command input
from bet_copilot.ui.command_input import create_command_input

console = Console()


@dataclass
class MockEvent:
    """Mock event for testing."""
    home_team: str
    away_team: str
    commence_time: datetime


class MockCLI:
    """Mock CLI with events for testing completion."""
    
    def __init__(self):
        now = datetime.now()
        self.events = [
            MockEvent("Arsenal", "Chelsea", now + timedelta(days=1)),
            MockEvent("Manchester United", "Liverpool", now + timedelta(days=2)),
            MockEvent("Manchester City", "Tottenham", now + timedelta(days=3)),
            MockEvent("Barcelona", "Real Madrid", now + timedelta(days=4)),
            MockEvent("Bayern Munich", "Borussia Dortmund", now + timedelta(days=5)),
        ]
        
        console.print("\n[green]✓[/green] Mock CLI inicializado con eventos:")
        for event in self.events:
            console.print(f"  • {event.home_team} vs {event.away_team}", style="dim")


async def main():
    """Interactive completion test."""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Test Interactivo: Autocompletado            [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════[/bold cyan]\n")
    
    # Create mock CLI with events
    mock_cli = MockCLI()
    
    # Create command input with mock CLI
    cmd_input = create_command_input(mock_cli)
    
    # Show instructions
    instructions = """
[bold]Prueba estos casos:[/bold]

1. [cyan]ana[/cyan] + Tab → debe autocompletar [green]analizar[/green]

2. [cyan]analizar [/cyan] + Tab → debe mostrar TODOS los partidos:
   • Arsenal vs Chelsea
   • Manchester United vs Liverpool
   • Manchester City vs Tottenham
   • Barcelona vs Real Madrid
   • Bayern Munich vs Borussia Dortmund

3. [cyan]analizar Ars[/cyan] + Tab → debe mostrar:
   • Arsenal vs Chelsea

4. [cyan]analizar Man[/cyan] + Tab → debe mostrar:
   • Manchester United vs Liverpool
   • Manchester City vs Tottenham

5. [cyan]mercados [/cyan] + Tab → debe mostrar sport keys:
   • soccer_epl
   • soccer_la_liga
   • etc.

6. [cyan]mercados soc[/cyan] + Tab → debe filtrar solo soccer_*

[dim]Escribe 'quit' para salir[/dim]
"""
    
    console.print(Panel(instructions, title="Instrucciones", border_style="cyan"))
    
    try:
        command_count = 0
        
        while True:
            # Get command with completion
            command = await cmd_input.get_command()
            
            if not command:
                continue
            
            command_count += 1
            
            if command.lower() in ["quit", "exit", "q"]:
                console.print("\n[green]✓ Test completado[/green]\n")
                break
            
            # Show what was entered
            console.print(f"\n[dim]→ Comando #{command_count}:[/dim] [cyan]{command}[/cyan]")
            
            # Simulate processing
            if command.lower().startswith("analizar "):
                match_name = command[9:].strip()
                console.print(f"[dim]  (analizaría: {match_name})[/dim]")
            elif command.lower().startswith("mercados "):
                sport = command[9:].strip()
                console.print(f"[dim]  (obtendría mercados de: {sport})[/dim]")
            
            console.print()
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrumpido[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
