#!/usr/bin/env python3
"""
Script para verificar que todas las dependencias están instaladas.
"""


# Add project to path
from pathlib import Path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Dependencias requeridas
REQUIRED_DEPS = {
    'aiohttp': 'HTTP async client',
    'aiosqlite': 'SQLite async',
    'rich': 'Terminal UI',
    'textual': 'Dashboard TUI',
    'prompt_toolkit': 'Advanced input',
    'google.generativeai': 'Gemini AI',
    'pytest': 'Testing framework',
    'pytest_asyncio': 'Async testing',
    'dotenv': 'Environment variables',
}

# Dependencias opcionales
OPTIONAL_DEPS = {
    'pytest_cov': 'Coverage reports',
    'black': 'Code formatter',
    'mypy': 'Type checker',
    'flake8': 'Linter',
}


def check_dependencies():
    """Check if all dependencies are installed."""
    
    console.print("\n[bold cyan]Verificando dependencias...[/bold cyan]\n")
    
    # Check required
    table = Table(title="Dependencias Requeridas", show_header=True)
    table.add_column("Paquete", style="cyan")
    table.add_column("Descripción", style="dim")
    table.add_column("Estado", justify="center")
    
    required_missing = []
    for dep, desc in REQUIRED_DEPS.items():
        try:
            module_name = dep.replace('.', '_')
            __import__(module_name)
            status = "[green]✓ OK[/green]"
        except ImportError:
            status = "[red]✗ FALTA[/red]"
            required_missing.append(dep)
        
        table.add_row(dep, desc, status)
    
    console.print(table)
    console.print()
    
    # Check optional
    table2 = Table(title="Dependencias Opcionales", show_header=True)
    table2.add_column("Paquete", style="yellow")
    table2.add_column("Descripción", style="dim")
    table2.add_column("Estado", justify="center")
    
    optional_missing = []
    for dep, desc in OPTIONAL_DEPS.items():
        try:
            __import__(dep)
            status = "[green]✓ OK[/green]"
        except ImportError:
            status = "[yellow]⚠ No instalado[/yellow]"
            optional_missing.append(dep)
        
        table2.add_row(dep, desc, status)
    
    console.print(table2)
    console.print()
    
    # Summary
    if required_missing:
        panel = Panel(
            f"[red]Faltan {len(required_missing)} dependencias requeridas:[/red]\n\n"
            + "\n".join(f"  • {dep}" for dep in required_missing)
            + "\n\n[bold]Instalar con:[/bold]\n  pip install -r requirements.txt",
            title="❌ Error",
            border_style="red"
        )
        console.print(panel)
        return False
    
    else:
        msg = "[green]✅ Todas las dependencias requeridas están instaladas[/green]"
        
        if optional_missing:
            msg += f"\n\n[yellow]⚠ {len(optional_missing)} opcionales no instaladas:[/yellow]\n"
            msg += "\n".join(f"  • {dep}" for dep in optional_missing)
            msg += "\n\n[bold]Instalar con:[/bold]\n  pip install -r requirements-dev.txt"
        
        panel = Panel(msg, title="✓ Estado", border_style="green")
        console.print(panel)
        return True


if __name__ == "__main__":
    try:
        success = check_dependencies()
        console.print()
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
