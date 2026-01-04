#!/usr/bin/env python3
"""
Test autocomplete functionality with mock data.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from bet_copilot.ui.command_input import create_command_input
from rich.console import Console

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
        # Simulate events loaded from mercados
        now = datetime.now()
        self.events = [
            MockEvent("Arsenal", "Chelsea", now + timedelta(days=1)),
            MockEvent("Manchester United", "Liverpool", now + timedelta(days=2)),
            MockEvent("Barcelona", "Real Madrid", now + timedelta(days=3)),
            MockEvent("Bayern Munich", "Borussia Dortmund", now + timedelta(days=4)),
            MockEvent("Paris Saint-Germain", "Marseille", now + timedelta(days=5)),
        ]


async def main():
    """Test autocomplete with mock data."""
    
    console.print("\n[bold cyan]═══ Test: Autocomplete con Datos Mock ═══[/bold cyan]\n")
    
    # Create mock CLI
    mock_cli = MockCLI()
    
    console.print("[green]✓[/green] Mock CLI creado con eventos:")
    for event in mock_cli.events:
        console.print(f"  • {event.home_team} vs {event.away_team}")
    console.print()
    
    # Create command input with mock CLI
    cmd_input = create_command_input(mock_cli)
    
    console.print("[bold]Instrucciones:[/bold]")
    console.print("  1. Escribe 'mer' + Tab → autocompleta 'mercados'")
    console.print("  2. Escribe 'mercados soc' + Tab → muestra ligas de fútbol")
    console.print("  3. Escribe 'analizar Ars' + Tab → muestra 'Arsenal vs Chelsea'")
    console.print("  4. Escribe 'analizar' + Tab → muestra TODOS los partidos")
    console.print("  5. Usa ↑/↓ para navegar historial")
    console.print("  6. Escribe 'quit' para salir\n")
    
    try:
        while True:
            command = await cmd_input.get_command()
            
            if not command:
                continue
            
            if command.lower() in ["quit", "exit", "q"]:
                console.print("\n[green]¡Test completado![/green]\n")
                break
            
            console.print(f"[dim]→ Comando:[/dim] [cyan]{command}[/cyan]\n")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrumpido[/yellow]\n")


if __name__ == "__main__":
    asyncio.run(main())
