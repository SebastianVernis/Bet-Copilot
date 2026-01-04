#!/usr/bin/env python3
"""
Interactive Setup Script for Bet-Copilot

Guides the user through configuration of API keys and settings.
Creates or updates .env file with provided values.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# API Configuration (same as check_apis.py)
API_CONFIGS = {
    "ODDS_API_KEY": {
        "name": "The Odds API",
        "description": "Required for fetching betting odds",
        "required": True,
        "docs": "https://the-odds-api.com/",
        "instructions": [
            "1. Visit https://the-odds-api.com/",
            "2. Create a free account",
            "3. Copy your API key from the dashboard",
        ],
        "placeholder": "your-odds-api-key-here",
    },
    "API_FOOTBALL_KEY": {
        "name": "API-Football",
        "description": "Optional - for historical statistics",
        "required": False,
        "docs": "https://www.api-football.com/",
        "instructions": [
            "1. Visit https://www.api-football.com/",
            "2. Sign up for a free account",
            "3. Get your API key from your dashboard",
        ],
        "placeholder": "your-api-football-key-here",
    },
    "GEMINI_API_KEY": {
        "name": "Google Gemini",
        "description": "Optional - for AI analysis",
        "required": False,
        "docs": "https://ai.google.dev/",
        "instructions": [
            "1. Visit https://ai.google.dev/",
            "2. Create a Google Cloud project",
            "3. Enable Gemini API",
            "4. Generate an API key",
        ],
        "placeholder": "your-gemini-api-key-here",
    },
}

# Other settings
OTHER_SETTINGS = {
    "LOG_LEVEL": {
        "name": "Log Level",
        "description": "Logging verbosity",
        "default": "INFO",
        "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
    },
}


def print_welcome():
    """Display welcome message"""
    console.print("\n")
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]⚡ Bet-Copilot Setup ⚡[/bold cyan]\n\n"
            "This script will guide you through configuring API keys\n"
            "and other settings for Bet-Copilot.\n\n"
            "[dim]Your keys will be stored in .env file (not committed to git)[/dim]"
        ),
        border_style="cyan"
    ))


def load_existing_env() -> Dict[str, str]:
    """Load existing .env file if it exists"""
    env_path = Path(__file__).parent.parent / ".env"
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    return env_vars


def display_api_info(key: str, config: Dict):
    """Display information about an API"""
    console.print(f"\n[bold cyan]━━━ {config['name']} ━━━[/bold cyan]")
    console.print(f"[dim]{config['description']}[/dim]")
    
    if config["required"]:
        console.print("[red]Status: REQUIRED[/red]")
    else:
        console.print("[yellow]Status: Optional[/yellow]")
    
    console.print(f"\n[dim]Documentation: {config['docs']}[/dim]")
    
    if Confirm.ask("\n[cyan]Show setup instructions?[/cyan]", default=False):
        console.print("\n[bold]Setup Instructions:[/bold]")
        for instruction in config["instructions"]:
            console.print(f"  {instruction}")
        console.print()


def prompt_api_key(key: str, config: Dict, existing_value: Optional[str]) -> Optional[str]:
    """Prompt user for an API key"""
    display_api_info(key, config)
    
    # Show existing value if present
    if existing_value:
        console.print(f"[green]Current value: {existing_value[:20]}...{existing_value[-10:]}[/green]")
        if not Confirm.ask("[cyan]Update this value?[/cyan]", default=False):
            return existing_value
    
    # Skip if optional
    if not config["required"]:
        if not Confirm.ask(f"[cyan]Configure {config['name']}?[/cyan]", default=False):
            return existing_value or ""
    
    # Prompt for key
    while True:
        value = Prompt.ask(
            f"[cyan]Enter your {config['name']} key[/cyan]",
            password=True,
            default=existing_value or ""
        )
        
        if value or not config["required"]:
            return value
        
        console.print("[red]This API key is required![/red]")


def prompt_settings(existing_values: Dict[str, str]) -> Dict[str, str]:
    """Prompt for other settings"""
    console.print("\n[bold cyan]━━━ General Settings ━━━[/bold cyan]\n")
    
    settings = {}
    
    for key, config in OTHER_SETTINGS.items():
        existing = existing_values.get(key, config["default"])
        
        if "options" in config:
            # Choice from list
            console.print(f"\n[cyan]{config['name']}:[/cyan] [dim]{config['description']}[/dim]")
            value = Prompt.ask(
                "Select",
                choices=config["options"],
                default=existing
            )
        else:
            # Free text
            value = Prompt.ask(
                f"[cyan]{config['name']}[/cyan] [dim]({config['description']})[/dim]",
                default=existing
            )
        
        settings[key] = value
    
    return settings


def write_env_file(api_keys: Dict[str, str], settings: Dict[str, str]):
    """Write .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    
    lines = [
        "# Bet-Copilot Configuration",
        f"# Generated: {Path(__file__).name}",
        "",
        "# API Keys",
    ]
    
    for key, value in api_keys.items():
        if value:
            lines.append(f"{key}={value}")
        else:
            lines.append(f"# {key}=")
    
    lines.extend([
        "",
        "# Settings",
    ])
    
    for key, value in settings.items():
        lines.append(f"{key}={value}")
    
    # Backup existing file
    if env_path.exists():
        backup_path = env_path.with_suffix('.env.backup')
        env_path.rename(backup_path)
        console.print(f"\n[dim]Backup created: {backup_path.name}[/dim]")
    
    # Write new file
    with open(env_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    
    console.print(f"[green]✓ Configuration saved to {env_path.name}[/green]")


def display_summary(api_keys: Dict[str, str], settings: Dict[str, str]):
    """Display configuration summary"""
    console.print("\n")
    
    table = Table(title="Configuration Summary", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # API Keys
    for key, value in api_keys.items():
        config = API_CONFIGS[key]
        if value:
            masked = f"{value[:10]}...{value[-6:]}" if len(value) > 20 else value
            table.add_row(config["name"], f"[green]✓[/green] {masked}")
        else:
            status = "[red]Missing[/red]" if config["required"] else "[dim]Not set[/dim]"
            table.add_row(config["name"], status)
    
    # Settings
    for key, value in settings.items():
        table.add_row(OTHER_SETTINGS[key]["name"], value)
    
    console.print(table)


def main():
    """Main entry point"""
    print_welcome()
    
    # Load existing configuration
    existing = load_existing_env()
    
    # Prompt for API keys
    api_keys = {}
    for key, config in API_CONFIGS.items():
        api_keys[key] = prompt_api_key(key, config, existing.get(key))
    
    # Prompt for settings
    settings = prompt_settings(existing)
    
    # Display summary
    display_summary(api_keys, settings)
    
    # Confirm
    console.print()
    if not Confirm.ask("[cyan]Save this configuration?[/cyan]", default=True):
        console.print("[yellow]Setup cancelled[/yellow]")
        return
    
    # Write .env file
    write_env_file(api_keys, settings)
    
    # Next steps
    console.print("\n")
    console.print(Panel(
        "[bold green]✓ Setup Complete![/bold green]\n\n"
        "Next steps:\n"
        "1. Test your API keys: [cyan]python scripts/check_apis.py[/cyan]\n"
        "2. Run a demo: [cyan]python example_usage.py[/cyan]\n"
        "3. Start the dashboard: [cyan]python scripts/start.py[/cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(1)
