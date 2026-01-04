#!/usr/bin/env python3
"""
API Key Validator for Bet-Copilot

Verifies that all required API keys are present and valid.
Tests connectivity to each service before starting the application.
"""
import os
import sys
import asyncio
from typing import Dict, Tuple, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import aiohttp

console = Console()

# API Configuration
API_CONFIGS = {
    "ODDS_API": {
        "env_var": "ODDS_API_KEY",
        "name": "The Odds API",
        "test_url": "https://api.the-odds-api.com/v4/sports",
        "required": True,
        "docs": "https://the-odds-api.com/",
    },
    "API_FOOTBALL": {
        "env_var": "API_FOOTBALL_KEY",
        "name": "API-Football",
        "test_url": "https://v3.football.api-sports.io/status",
        "required": False,
        "docs": "https://www.api-football.com/",
    },
    "GEMINI_API": {
        "env_var": "GEMINI_API_KEY",
        "name": "Google Gemini",
        "test_url": None,  # No simple test endpoint
        "required": False,
        "docs": "https://ai.google.dev/",
    },
}


async def test_odds_api(api_key: str) -> Tuple[bool, str]:
    """Test The Odds API connectivity"""
    try:
        url = API_CONFIGS["ODDS_API"]["test_url"]
        params = {"apiKey": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if we got sports back
                    if isinstance(data, list) and len(data) > 0:
                        headers = response.headers
                        remaining = headers.get('x-requests-remaining', 'unknown')
                        return True, f"✓ Connected ({remaining} requests remaining)"
                    return False, "✗ Invalid response format"
                elif response.status == 401:
                    return False, "✗ Invalid API key"
                elif response.status == 429:
                    return False, "✗ Rate limit exceeded"
                else:
                    return False, f"✗ HTTP {response.status}"
    except asyncio.TimeoutError:
        return False, "✗ Connection timeout"
    except aiohttp.ClientError as e:
        return False, f"✗ Connection error: {str(e)[:50]}"
    except Exception as e:
        return False, f"✗ Error: {str(e)[:50]}"


async def test_api_football(api_key: str) -> Tuple[bool, str]:
    """Test API-Football connectivity"""
    try:
        url = API_CONFIGS["API_FOOTBALL"]["test_url"]
        headers = {"x-apisports-key": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check response structure
                    if "response" in data:
                        account = data["response"].get("account", {})
                        requests_remaining = account.get("requests", {}).get("current", "unknown")
                        return True, f"✓ Connected ({requests_remaining} requests left today)"
                    return False, "✗ Invalid response format"
                elif response.status == 401:
                    return False, "✗ Invalid API key"
                elif response.status == 429:
                    return False, "✗ Rate limit exceeded"
                else:
                    return False, f"✗ HTTP {response.status}"
    except asyncio.TimeoutError:
        return False, "✗ Connection timeout"
    except aiohttp.ClientError as e:
        return False, f"✗ Connection error: {str(e)[:50]}"
    except Exception as e:
        return False, f"✗ Error: {str(e)[:50]}"


async def test_gemini_api(api_key: str) -> Tuple[bool, str]:
    """Test Gemini API key format"""
    # Gemini keys start with specific prefixes
    if api_key and len(api_key) > 20:
        # Basic validation - real test would require google-generativeai
        return True, "✓ Key format valid (not tested)"
    return False, "✗ Invalid key format"


async def check_api(api_id: str, api_key: Optional[str]) -> Dict:
    """Check a single API"""
    config = API_CONFIGS[api_id]
    
    result = {
        "id": api_id,
        "name": config["name"],
        "required": config["required"],
        "present": bool(api_key),
        "valid": False,
        "message": "",
    }
    
    if not api_key:
        result["message"] = "✗ Not configured"
        return result
    
    # Test API
    if api_id == "ODDS_API":
        result["valid"], result["message"] = await test_odds_api(api_key)
    elif api_id == "API_FOOTBALL":
        result["valid"], result["message"] = await test_api_football(api_key)
    elif api_id == "GEMINI_API":
        result["valid"], result["message"] = await test_gemini_api(api_key)
    
    return result


async def check_all_apis() -> Dict[str, Dict]:
    """Check all configured APIs"""
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        for api_id in API_CONFIGS:
            task = progress.add_task(f"Checking {API_CONFIGS[api_id]['name']}...", total=None)
            
            # Get API key from environment
            env_var = API_CONFIGS[api_id]["env_var"]
            api_key = os.getenv(env_var)
            
            # Check API
            result = await check_api(api_id, api_key)
            results[api_id] = result
            
            progress.remove_task(task)
    
    return results


def display_results(results: Dict[str, Dict]):
    """Display API check results in a table"""
    table = Table(title="API Status", show_header=True, header_style="bold cyan")
    
    table.add_column("API", style="cyan", width=20)
    table.add_column("Required", justify="center", width=10)
    table.add_column("Status", width=50)
    
    all_required_valid = True
    
    for api_id, result in results.items():
        # Status with color
        if result["valid"]:
            status = f"[green]{result['message']}[/green]"
        elif not result["required"]:
            status = f"[yellow]{result['message']}[/yellow]"
        else:
            status = f"[red]{result['message']}[/red]"
            all_required_valid = False
        
        # Required indicator
        required = "[red]YES[/red]" if result["required"] else "[dim]no[/dim]"
        
        table.add_row(result["name"], required, status)
    
    console.print("\n")
    console.print(table)
    console.print("\n")
    
    return all_required_valid


def display_missing_apis(results: Dict[str, Dict]):
    """Display instructions for missing APIs"""
    missing = [r for r in results.values() if r["required"] and not r["valid"]]
    
    if not missing:
        return
    
    console.print(Panel(
        "[red]⚠️  Required API keys are missing or invalid[/red]\n\n"
        "Run the setup script to configure:\n"
        "[cyan]python scripts/setup.py[/cyan]",
        title="Configuration Required",
        border_style="red"
    ))


async def main():
    """Main entry point"""
    console.print("\n")
    console.print(Panel(
        "[bold cyan]API Key Validator[/bold cyan]\n"
        "Checking connectivity to external services...",
        border_style="cyan"
    ))
    
    # Check all APIs
    results = await check_all_apis()
    
    # Display results
    all_valid = display_results(results)
    
    if not all_valid:
        display_missing_apis(results)
        console.print("[yellow]Run 'python scripts/setup.py' to configure missing APIs[/yellow]\n")
        sys.exit(1)
    else:
        console.print("[green]✓ All required APIs are configured and working![/green]\n")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
