#!/usr/bin/env python3
"""
Script para verificar todas las API keys configuradas.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from bet_copilot.config import (
    ODDS_API_KEY,
    API_FOOTBALL_KEY,
    GEMINI_API_KEY,
    BLACKBOX_API_KEY
)

console = Console()


def verify_api_keys():
    """Verify all API keys."""
    
    console.print("\n[bold cyan]═══ Verificación de API Keys ═══[/bold cyan]\n")
    
    table = Table(title="Estado de API Keys", show_header=True)
    table.add_column("API", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("Key (primeros 10 chars)", style="dim")
    table.add_column("Prioridad")
    
    # Check each API key
    apis = [
        ("The Odds API", ODDS_API_KEY, "🔴 CRÍTICA"),
        ("API-Football", API_FOOTBALL_KEY, "🟡 IMPORTANTE"),
        ("Gemini AI", GEMINI_API_KEY, "🟢 OPCIONAL"),
        ("Blackbox AI", BLACKBOX_API_KEY, "🟢 OPCIONAL"),
    ]
    
    configured_count = 0
    
    for api_name, api_key, priority in apis:
        if api_key and len(api_key) > 0:
            status = "[green]✓ Configurada[/green]"
            key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
            configured_count += 1
        else:
            status = "[red]✗ No configurada[/red]"
            key_preview = "N/A"
        
        table.add_row(api_name, status, key_preview, priority)
    
    console.print(table)
    console.print()
    
    # Summary
    if configured_count == 4:
        panel_content = "[green]✅ Todas las API keys configuradas[/green]\n\n"
        panel_content += "El sistema funcionará con máxima calidad:\n"
        panel_content += "  • Datos de odds reales (The Odds API)\n"
        panel_content += "  • Stats de equipos reales (API-Football)\n"
        panel_content += "  • Análisis AI avanzado (Gemini)\n"
        panel_content += "  • Fallback a Blackbox si Gemini falla\n"
        border_style = "green"
        title = "✓ Configuración Completa"
    
    elif configured_count >= 2:
        panel_content = "[yellow]⚠ Configuración parcial[/yellow]\n\n"
        panel_content += f"Keys configuradas: {configured_count}/4\n\n"
        panel_content += "El sistema funcionará con fallbacks:\n"
        if not ODDS_API_KEY:
            panel_content += "  • ⚠️ The Odds API: REQUERIDA para odds reales\n"
        if not API_FOOTBALL_KEY:
            panel_content += "  • ⚠️ API-Football: Usará estimaciones (SimpleProvider)\n"
        if not GEMINI_API_KEY:
            panel_content += "  • ℹ️ Gemini: Usará Blackbox o SimpleAnalyzer\n"
        if not BLACKBOX_API_KEY:
            panel_content += "  • ℹ️ Blackbox: Usará SimpleAnalyzer si Gemini falla\n"
        border_style = "yellow"
        title = "⚠ Configuración Parcial"
    
    else:
        panel_content = "[red]❌ Pocas API keys configuradas[/red]\n\n"
        panel_content += f"Keys configuradas: {configured_count}/4\n\n"
        panel_content += "Sistema funcionará en modo degradado:\n"
        panel_content += "  • Football Data: Estimaciones (SimpleProvider)\n"
        panel_content += "  • AI: Heurísticas (SimpleAnalyzer)\n\n"
        panel_content += "[bold]Mínimo recomendado:[/bold]\n"
        panel_content += "  • ODDS_API_KEY (crítica)\n"
        panel_content += "  • API_FOOTBALL_KEY o GEMINI_API_KEY\n"
        border_style = "red"
        title = "❌ Configuración Mínima"
    
    console.print(Panel(panel_content, title=title, border_style=border_style))
    console.print()
    
    # Instructions
    console.print("[bold]Configurar API Keys:[/bold]\n")
    console.print("  1. Editar archivo: [cyan].env[/cyan]")
    console.print("  2. Agregar keys en formato: [dim]API_NAME_KEY=\"tu_key_aqui\"[/dim]")
    console.print("  3. Ejecutar este script nuevamente para verificar\n")
    
    console.print("[bold]Obtener API Keys:[/bold]\n")
    console.print("  • The Odds API: [cyan]https://the-odds-api.com/[/cyan]")
    console.print("  • API-Football: [cyan]https://www.api-football.com/[/cyan]")
    console.print("  • Gemini: [cyan]https://makersuite.google.com/app/apikey[/cyan]")
    console.print("  • Blackbox: [cyan]https://app.blackbox.ai/dashboard[/cyan]")
    console.print()
    
    return configured_count


if __name__ == "__main__":
    try:
        count = verify_api_keys()
        
        # Exit code based on configuration
        if count >= 2:
            sys.exit(0)  # OK
        else:
            sys.exit(1)  # Insufficient
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
