#!/usr/bin/env python3
"""
Startup Script for Bet-Copilot

Pre-flight checks and system startup:
1. Check API keys
2. Verify database
3. Test connectivity
4. Launch application
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def preflight_checks():
    """Run preflight checks"""
    console.print("\n")
    console.print(Panel(
        "[bold cyan]⚡ Bet-Copilot Startup ⚡[/bold cyan]\n"
        "Running pre-flight checks...",
        border_style="cyan"
    ))
    
    checks_passed = True
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Check 1: Environment file
        task = progress.add_task("Checking environment configuration...", total=None)
        env_path = Path(__file__).parent.parent / ".env"
        if not env_path.exists():
            console.print("[red]✗ .env file not found[/red]")
            console.print("[yellow]Run: python scripts/setup.py[/yellow]")
            checks_passed = False
        else:
            console.print("[green]✓ Environment configured[/green]")
        progress.remove_task(task)
        
        # Check 2: API keys
        task = progress.add_task("Checking API keys...", total=None)
        odds_key = os.getenv("ODDS_API_KEY")
        if not odds_key:
            console.print("[red]✗ The Odds API key not configured[/red]")
            checks_passed = False
        else:
            console.print("[green]✓ API keys present[/green]")
        progress.remove_task(task)
        
        # Check 3: Database
        task = progress.add_task("Checking database...", total=None)
        from bet_copilot.config import DB_PATH
        from bet_copilot.db.odds_repository import OddsRepository
        
        try:
            repo = OddsRepository()
            await repo.initialize()
            console.print("[green]✓ Database ready[/green]")
        except Exception as e:
            console.print(f"[red]✗ Database error: {str(e)[:50]}[/red]")
            checks_passed = False
        progress.remove_task(task)
        
        # Check 4: Test API connectivity (optional, quick check)
        if odds_key:
            task = progress.add_task("Testing API connectivity...", total=None)
            try:
                from bet_copilot.services.odds_service import OddsService
                service = OddsService()
                # Quick test - just initialize, don't make actual request
                console.print("[green]✓ API client initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ API client warning: {str(e)[:50]}[/yellow]")
            progress.remove_task(task)
    
    return checks_passed


def show_startup_menu():
    """Show startup menu"""
    console.print("\n")
    console.print(Panel(
        "[bold]Select an option:[/bold]\n\n"
        "  [cyan]1[/cyan] - Run Market Watch Demo\n"
        "  [cyan]2[/cyan] - Run Soccer Prediction Demo\n"
        "  [cyan]3[/cyan] - Run API Usage Demo\n"
        "  [cyan]4[/cyan] - Health Check\n"
        "  [cyan]5[/cyan] - Test API Connectivity\n"
        "  [cyan]q[/cyan] - Quit",
        title="Bet-Copilot Menu",
        border_style="cyan"
    ))
    
    choice = console.input("\n[cyan]Select option:[/cyan] ").strip()
    return choice


async def main():
    """Main entry point"""
    # Run preflight checks
    checks_passed = await preflight_checks()
    
    if not checks_passed:
        console.print("\n")
        console.print(Panel(
            "[red]⚠️  Pre-flight checks failed[/red]\n\n"
            "Please fix the issues above before starting.\n"
            "Run [cyan]python scripts/setup.py[/cyan] to configure.",
            border_style="red"
        ))
        sys.exit(1)
    
    console.print("\n")
    console.print(Panel(
        "[green]✓ All pre-flight checks passed![/green]",
        border_style="green"
    ))
    
    # Show menu
    while True:
        choice = show_startup_menu()
        
        if choice == "1":
            console.print("\n[cyan]Launching Market Watch Demo...[/cyan]\n")
            import subprocess
            subprocess.run([sys.executable, "demo_market_watch_simple.py"])
        
        elif choice == "2":
            console.print("\n[cyan]Launching Soccer Prediction Demo...[/cyan]\n")
            import subprocess
            subprocess.run([sys.executable, "example_soccer_prediction.py"])
        
        elif choice == "3":
            console.print("\n[cyan]Launching API Usage Demo...[/cyan]\n")
            import subprocess
            subprocess.run([sys.executable, "example_usage.py"])
        
        elif choice == "4":
            console.print("\n[cyan]Running Health Check...[/cyan]\n")
            import subprocess
            subprocess.run([sys.executable, "scripts/health_check.py"])
        
        elif choice == "5":
            console.print("\n[cyan]Testing API Connectivity...[/cyan]\n")
            import subprocess
            subprocess.run([sys.executable, "scripts/check_apis.py"])
        
        elif choice.lower() == "q":
            console.print("\n[cyan]Goodbye![/cyan]\n")
            break
        
        else:
            console.print("\n[red]Invalid option. Please try again.[/red]")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]\n")
        sys.exit(0)
