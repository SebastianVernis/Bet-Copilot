#!/usr/bin/env python3
"""
Health Check Script for Bet-Copilot

Performs comprehensive system health checks:
- API connectivity
- Database status
- Circuit breaker state
- Cache statistics
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

# Import project modules
from bet_copilot.config import DB_PATH
from bet_copilot.db.odds_repository import OddsRepository
from bet_copilot.services.odds_service import OddsService

console = Console()


async def check_database() -> dict:
    """Check database health"""
    try:
        repo = OddsRepository()
        await repo.initialize()
        
        # Get stats
        stats = await repo.get_request_stats(hours=24)
        
        # Check if DB file exists
        db_exists = DB_PATH.exists()
        db_size = DB_PATH.stat().st_size if db_exists else 0
        
        return {
            "status": "healthy" if db_exists else "missing",
            "path": str(DB_PATH),
            "size_mb": round(db_size / 1024 / 1024, 2),
            "requests_24h": stats.get("total_requests", 0),
            "successful_24h": stats.get("successful", 0),
            "rate_limited_24h": stats.get("rate_limited", 0),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:100]
        }


async def check_circuit_breaker() -> dict:
    """Check circuit breaker status"""
    try:
        service = OddsService()
        stats = await service.get_circuit_stats()
        
        return {
            "status": stats["state"],
            "failure_count": stats["failure_count"],
            "last_failure": stats["last_failure"],
            "wait_time": stats["wait_time_remaining"],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:100]
        }


async def check_cache_stats() -> dict:
    """Check cache statistics"""
    try:
        repo = OddsRepository()
        await repo.initialize()
        
        # Count cached odds
        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            # Total cached
            cursor = await db.execute("SELECT COUNT(*) FROM odds_data")
            total = (await cursor.fetchone())[0]
            
            # Fresh (last hour)
            cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor = await db.execute(
                "SELECT COUNT(*) FROM odds_data WHERE fetched_at > ?",
                (cutoff,)
            )
            fresh = (await cursor.fetchone())[0]
            
            # Stale
            cursor = await db.execute(
                "SELECT COUNT(*) FROM odds_data WHERE is_stale = 1"
            )
            stale = (await cursor.fetchone())[0]
        
        return {
            "status": "healthy",
            "total_entries": total,
            "fresh_entries": fresh,
            "stale_entries": stale,
            "hit_rate_estimate": f"{(fresh / total * 100):.1f}%" if total > 0 else "N/A"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:100]
        }


async def check_apis() -> dict:
    """Check API keys presence (not connectivity)"""
    api_keys = {
        "ODDS_API_KEY": os.getenv("ODDS_API_KEY"),
        "API_FOOTBALL_KEY": os.getenv("API_FOOTBALL_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    }
    
    return {
        "odds_api": "configured" if api_keys["ODDS_API_KEY"] else "missing",
        "api_football": "configured" if api_keys["API_FOOTBALL_KEY"] else "missing",
        "gemini": "configured" if api_keys["GEMINI_API_KEY"] else "missing",
    }


def create_database_table(db_check: dict) -> Table:
    """Create database status table"""
    table = Table(title="Database", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    if db_check["status"] == "healthy":
        table.add_row("Status", "[green]✓ Healthy[/green]")
        table.add_row("Path", db_check["path"])
        table.add_row("Size", f"{db_check['size_mb']} MB")
        table.add_row("Requests (24h)", str(db_check["requests_24h"]))
        table.add_row("Successful (24h)", str(db_check["successful_24h"]))
        table.add_row("Rate Limited (24h)", str(db_check["rate_limited_24h"]))
    else:
        table.add_row("Status", f"[red]✗ {db_check['status'].title()}[/red]")
        if "error" in db_check:
            table.add_row("Error", f"[red]{db_check['error']}[/red]")
    
    return table


def create_circuit_breaker_table(cb_check: dict) -> Table:
    """Create circuit breaker status table"""
    table = Table(title="Circuit Breaker", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    
    if cb_check["status"] in ["closed", "half_open"]:
        status_color = "green"
        status_icon = "✓"
    elif cb_check["status"] == "open":
        status_color = "red"
        status_icon = "✗"
    else:
        status_color = "yellow"
        status_icon = "?"
    
    table.add_row("Status", f"[{status_color}]{status_icon} {cb_check['status'].upper()}[/{status_color}]")
    table.add_row("Failures", str(cb_check.get("failure_count", 0)))
    
    if cb_check.get("last_failure"):
        table.add_row("Last Failure", cb_check["last_failure"])
    
    if cb_check.get("wait_time", 0) > 0:
        table.add_row("Wait Time", f"{cb_check['wait_time']}s")
    
    return table


def create_cache_table(cache_check: dict) -> Table:
    """Create cache statistics table"""
    table = Table(title="Cache", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    if cache_check["status"] == "healthy":
        table.add_row("Status", "[green]✓ Healthy[/green]")
        table.add_row("Total Entries", str(cache_check["total_entries"]))
        table.add_row("Fresh (<1h)", str(cache_check["fresh_entries"]))
        table.add_row("Stale", str(cache_check["stale_entries"]))
        table.add_row("Est. Hit Rate", cache_check["hit_rate_estimate"])
    else:
        table.add_row("Status", f"[red]✗ {cache_check['status'].title()}[/red]")
        if "error" in cache_check:
            table.add_row("Error", f"[red]{cache_check['error']}[/red]")
    
    return table


def create_api_table(api_check: dict) -> Table:
    """Create API keys status table"""
    table = Table(title="API Keys", show_header=True, header_style="bold cyan")
    table.add_column("API", style="cyan")
    table.add_column("Status")
    
    for api, status in api_check.items():
        if status == "configured":
            status_str = "[green]✓ Configured[/green]"
        else:
            status_str = "[yellow]○ Not set[/yellow]"
        
        api_name = api.replace("_", " ").title()
        table.add_row(api_name, status_str)
    
    return table


async def run_health_check():
    """Run all health checks"""
    console.print("\n")
    console.print(Panel(
        "[bold cyan]System Health Check[/bold cyan]\n"
        "Running diagnostics...",
        border_style="cyan"
    ))
    
    # Run checks
    db_check = await check_database()
    cb_check = await check_circuit_breaker()
    cache_check = await check_cache_stats()
    api_check = await check_apis()
    
    # Create tables
    db_table = create_database_table(db_check)
    cb_table = create_circuit_breaker_table(cb_check)
    cache_table = create_cache_table(cache_check)
    api_table = create_api_table(api_check)
    
    # Display in layout
    console.print("\n")
    console.print(db_table)
    console.print()
    console.print(cb_table)
    console.print()
    console.print(cache_table)
    console.print()
    console.print(api_table)
    
    # Overall health
    console.print("\n")
    
    issues = []
    if db_check["status"] != "healthy":
        issues.append("Database not healthy")
    if cb_check["status"] == "open":
        issues.append("Circuit breaker is OPEN")
    if api_check["odds_api"] != "configured":
        issues.append("The Odds API key not configured")
    
    if issues:
        console.print(Panel(
            "[yellow]⚠️  Issues detected:[/yellow]\n" + "\n".join(f"  • {issue}" for issue in issues),
            title="Health Check",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[green]✓ All systems healthy![/green]",
            title="Health Check",
            border_style="green"
        ))
    
    console.print("\n")


async def main():
    """Main entry point"""
    await run_health_check()


if __name__ == "__main__":
    asyncio.run(main())
