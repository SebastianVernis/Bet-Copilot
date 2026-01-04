#!/usr/bin/env python3
"""
Test script for advanced command input features.
Tests history navigation, tab completion, and keyboard shortcuts.
"""

import asyncio
from bet_copilot.ui.command_input import create_command_input
from bet_copilot.ui.styles import NEON_CYAN, NEON_GREEN, NEON_PURPLE
from rich.console import Console

console = Console()


async def main():
    """Test command input features."""
    
    # Banner
    console.print("\n╔═══════════════════════════════════════════════════╗", style=NEON_PURPLE)
    console.print("║  TEST: Advanced Command Input                     ║", style=NEON_PURPLE)
    console.print("╚═══════════════════════════════════════════════════╝\n", style=NEON_PURPLE)
    
    console.print("[bold]Características habilitadas:[/bold]\n")
    console.print("  [green]✓[/green] Historial de comandos (↑/↓)")
    console.print("  [green]✓[/green] Autocompletado con Tab")
    console.print("  [green]✓[/green] Edición inline con ←/→")
    console.print("  [green]✓[/green] Búsqueda en historial (Ctrl+R)")
    console.print("  [green]✓[/green] Sugerencias contextuales\n")
    
    console.print("[bold cyan]Instrucciones:[/bold cyan]")
    console.print("  • Escribe 'help' y presiona Tab para ver comandos")
    console.print("  • Presiona ↑ para ver comandos anteriores")
    console.print("  • Escribe 'mer' y presiona Tab para autocompletar 'mercados'")
    console.print("  • Escribe 'quit' para salir\n")
    
    # Create command input (without CLI instance for testing)
    cmd_input = create_command_input(cli_instance=None)
    
    command_count = 0
    
    try:
        while True:
            # Get command with all features
            command = await cmd_input.get_command()
            
            if not command:
                continue
            
            command_count += 1
            
            # Process command
            if command.lower() in ["quit", "exit", "q"]:
                console.print("\n[green]¡Hasta luego![/green]\n")
                break
            
            elif command.lower() == "history":
                # Show history
                history = cmd_input.get_history()
                console.print(f"\n[bold]Historial ({len(history)} comandos):[/bold]")
                for i, cmd in enumerate(history[-10:], 1):
                    console.print(f"  {i}. {cmd}", style="dim")
                console.print()
            
            elif command.lower() == "clear":
                # Clear history
                cmd_input.clear_history()
                console.print("[yellow]Historial limpiado[/yellow]\n")
            
            else:
                # Echo command
                console.print(f"[dim]→ Ejecutando:[/dim] [cyan]{command}[/cyan]")
                console.print(f"[dim]  Comando #{command_count}[/dim]\n")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrumpido[/yellow]\n")
    
    # Stats
    console.print(f"[dim]Total de comandos ejecutados: {command_count}[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
