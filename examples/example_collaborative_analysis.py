"""
Demo: Collaborative AI Analysis + Live News Feed

Demonstrates the enhanced analysis flow when both AIs are available:
1. Fetch live news from free sources (BBC, ESPN) - NO API CALLS
2. Run collaborative Gemini + Blackbox analysis
3. Generate comprehensive insights covering all markets
4. Display in rich dashboard format

This maximizes analytical depth while minimizing API usage.
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich import box
from rich.text import Text

from bet_copilot.ai.collaborative_analyzer import CollaborativeAnalyzer
from bet_copilot.ai.gemini_client import GeminiClient
from bet_copilot.ai.blackbox_client import BlackboxClient
from bet_copilot.news import NewsScraper


console = Console()


async def demo_news_feed():
    """Demonstrate news scraping without API calls."""
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📰 Live News Feed Demo[/bold cyan]\n"
        "[dim]Free sources - No API calls required[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    scraper = NewsScraper(cache_ttl=3600)
    
    # Fetch news from all sources
    console.print("[yellow]Fetching news from BBC Sport and ESPN...[/yellow]")
    articles = await scraper.fetch_all_news(max_per_source=15)
    
    if not articles:
        console.print("[red]No articles fetched[/red]")
        return
    
    console.print(f"[green]✓ Fetched {len(articles)} total articles[/green]")
    console.print()
    
    # Display all news
    console.rule("[bold]📰 Latest Football News[/bold]")
    
    news_table = Table(box=box.SIMPLE, show_header=True)
    news_table.add_column("Time", style="dim", width=10)
    news_table.add_column("Source", style="cyan", width=10)
    news_table.add_column("Title", style="white")
    news_table.add_column("Teams", style="yellow", width=20)
    news_table.add_column("Category", style="magenta", width=12)
    
    for article in articles[:20]:
        # Format time
        time_ago = (datetime.now() - article.published).total_seconds() / 3600
        if time_ago < 1:
            time_str = f"{int(time_ago * 60)}m ago"
        elif time_ago < 24:
            time_str = f"{int(time_ago)}h ago"
        else:
            time_str = f"{int(time_ago / 24)}d ago"
        
        # Teams
        teams_str = ", ".join(article.teams_mentioned[:2]) if article.teams_mentioned else "-"
        
        # Category emoji
        category_emoji = {
            "injury": "🏥",
            "transfer": "🔄",
            "match_preview": "⚽",
            "general": "📋"
        }.get(article.category, "📋")
        
        news_table.add_row(
            time_str,
            article.source,
            article.title[:60] + ("..." if len(article.title) > 60 else ""),
            teams_str,
            f"{category_emoji} {article.category}"
        )
    
    console.print(news_table)
    console.print()
    
    # Filter examples
    console.rule("[bold]🔍 Filtered Views[/bold]")
    
    # Filter by specific teams
    test_teams = ["Manchester City", "Liverpool", "Arsenal"]
    filtered = scraper.filter_by_teams(articles, test_teams)
    
    console.print(f"\n[cyan]Articles mentioning {', '.join(test_teams)}:[/cyan] {len(filtered)}")
    
    for article in filtered[:5]:
        console.print(f"  • {article.title}")
    
    # Filter by injuries
    injuries = scraper.filter_by_category(articles, ["injury"])
    
    console.print(f"\n[red]Injury/Suspension News:[/red] {len(injuries)}")
    for article in injuries[:5]:
        teams_str = f" ({', '.join(article.teams_mentioned)})" if article.teams_mentioned else ""
        console.print(f"  🏥 {article.title}{teams_str}")
    
    console.print()
    await scraper.close()


async def demo_collaborative_analysis():
    """Demonstrate collaborative AI analysis."""
    
    console.print()
    console.print(Panel.fit(
        "[bold green]🤝 Collaborative AI Analysis Demo[/bold green]\n"
        "[dim]Gemini + Blackbox working together[/dim]",
        border_style="green"
    ))
    console.print()
    
    # Initialize both AIs
    gemini = GeminiClient()
    blackbox = BlackboxClient()
    
    # Check availability
    gemini_available = gemini.is_available()
    blackbox_available = blackbox.is_available()
    
    console.print(f"[cyan]Gemini available:[/cyan] {'✓' if gemini_available else '✗'}")
    console.print(f"[cyan]Blackbox available:[/cyan] {'✓' if blackbox_available else '✗'}")
    console.print()
    
    if not (gemini_available and blackbox_available):
        console.print(
            "[yellow]⚠ Collaborative analysis requires both AIs to be configured[/yellow]"
        )
        console.print(
            "[dim]Set GEMINI_API_KEY and BLACKBOX_API_KEY in .env file[/dim]"
        )
        return
    
    # Initialize collaborative analyzer
    analyzer = CollaborativeAnalyzer(gemini_client=gemini, blackbox_client=blackbox)
    
    # Sample match data
    home_team = "Manchester City"
    away_team = "Liverpool"
    home_form = "WWWDW"
    away_form = "WDWWL"
    h2h = ["H", "A", "D", "H", "A"]
    
    console.print(f"[bold]Analyzing:[/bold] {home_team} vs {away_team}")
    console.print(f"[dim]Home form: {home_form} | Away form: {away_form} | H2H: {' '.join(h2h)}[/dim]")
    console.print()
    
    console.print("[yellow]🔄 Running parallel AI analysis...[/yellow]")
    
    # Run collaborative analysis
    result = await analyzer.analyze_match_comprehensive(
        home_team, away_team,
        home_form, away_form,
        h2h, None
    )
    
    console.print("[green]✓ Analysis complete![/green]")
    console.print()
    
    # Display results
    console.rule("[bold cyan]🎯 CONSENSUS ANALYSIS[/bold cyan]")
    
    consensus_panel = Panel(
        f"[bold]Lambda Adjustments:[/bold]\n"
        f"  Home: {result.consensus.lambda_adjustment_home:.2f}x\n"
        f"  Away: {result.consensus.lambda_adjustment_away:.2f}x\n\n"
        f"[bold]Sentiment:[/bold] {result.consensus.sentiment}\n"
        f"[bold]Confidence:[/bold] {result.consensus.confidence:.0%}\n\n"
        f"[bold]Key Factors:[/bold]\n" +
        "\n".join(f"  • {factor}" for factor in result.consensus.key_factors) +
        f"\n\n[bold]Reasoning:[/bold]\n{result.consensus.reasoning}",
        title=f"Consensus ({result.agreement_score:.0%} Agreement)",
        border_style="green" if result.agreement_score > 0.7 else "yellow"
    )
    
    console.print(consensus_panel)
    console.print()
    
    # Individual perspectives
    if result.gemini_analysis and result.blackbox_analysis:
        console.rule("[bold]🔍 Individual Perspectives[/bold]")
        
        comparison_table = Table(box=box.ROUNDED)
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column("Gemini", style="green", justify="center")
        comparison_table.add_column("Blackbox", style="magenta", justify="center")
        comparison_table.add_column("Consensus", style="yellow", justify="center")
        
        comparison_table.add_row(
            "Home λ Adjustment",
            f"{result.gemini_analysis.lambda_adjustment_home:.2f}",
            f"{result.blackbox_analysis.lambda_adjustment_home:.2f}",
            f"{result.consensus.lambda_adjustment_home:.2f}"
        )
        
        comparison_table.add_row(
            "Away λ Adjustment",
            f"{result.gemini_analysis.lambda_adjustment_away:.2f}",
            f"{result.blackbox_analysis.lambda_adjustment_away:.2f}",
            f"{result.consensus.lambda_adjustment_away:.2f}"
        )
        
        comparison_table.add_row(
            "Sentiment",
            result.gemini_analysis.sentiment,
            result.blackbox_analysis.sentiment,
            result.consensus.sentiment
        )
        
        comparison_table.add_row(
            "Confidence",
            f"{result.gemini_analysis.confidence:.0%}",
            f"{result.blackbox_analysis.confidence:.0%}",
            f"{result.consensus.confidence:.0%}"
        )
        
        console.print(comparison_table)
        console.print()
        
        # Divergence points
        if result.divergence_points:
            console.print("[bold red]⚠ Divergence Points:[/bold red]")
            for point in result.divergence_points:
                console.print(f"  • {point}")
            console.print()
    
    # Metadata
    console.rule("[bold]📊 Metadata[/bold]")
    
    metadata_text = (
        f"[green]Agreement Score:[/green] {result.agreement_score:.0%}\n"
        f"[green]Confidence Boost:[/green] +{result.confidence_boost:.0%}\n"
        f"[dim]Higher agreement = more reliable consensus[/dim]"
    )
    
    console.print(Panel(metadata_text, border_style="dim"))
    console.print()
    
    await analyzer.close()


async def demo_integrated_flow():
    """Demo the complete integrated flow."""
    
    console.print()
    console.print(Panel.fit(
        "[bold magenta]🚀 Integrated Analysis Flow[/bold magenta]\n"
        "[dim]News + Collaborative AI + Alternative Markets[/dim]",
        border_style="magenta"
    ))
    console.print()
    
    # Step 1: Fetch news (no API)
    console.print("[bold cyan]Step 1:[/bold cyan] Fetching live news from free sources...")
    scraper = NewsScraper()
    news = await scraper.fetch_all_news(max_per_source=10)
    console.print(f"[green]✓[/green] {len(news)} articles fetched\n")
    
    # Step 2: Filter relevant news
    console.print("[bold cyan]Step 2:[/bold cyan] Filtering relevant news...")
    teams = ["Manchester City", "Liverpool"]
    relevant = scraper.filter_by_teams(news, teams)
    injury_news = scraper.filter_by_category(relevant, ["injury"])
    
    console.print(f"[green]✓[/green] {len(relevant)} relevant, {len(injury_news)} injury-related\n")
    
    # Step 3: Show news context
    if relevant:
        console.print("[bold cyan]Latest News Context:[/bold cyan]")
        for article in relevant[:3]:
            console.print(f"  📰 {article.title[:70]}")
        console.print()
    
    # Step 4: Collaborative AI analysis
    console.print("[bold cyan]Step 3:[/bold cyan] Running collaborative AI analysis...")
    
    gemini = GeminiClient()
    blackbox = BlackboxClient()
    analyzer = CollaborativeAnalyzer(gemini, blackbox)
    
    if analyzer.is_collaborative_available():
        # Build context from news
        news_context = "\n".join(
            f"- {article.title}"
            for article in relevant[:3]
        ) if relevant else None
        
        result = await analyzer.analyze_match_comprehensive(
            "Manchester City", "Liverpool",
            "WWWDW", "WDWWL",
            ["H", "A", "D", "H", "A"],
            news_context
        )
        
        console.print(f"[green]✓[/green] Consensus reached (agreement: {result.agreement_score:.0%})\n")
        
        # Show key insights
        console.print(Panel(
            f"[bold]AI Consensus Insights:[/bold]\n\n" +
            "\n".join(f"  • {factor}" for factor in result.consensus.key_factors[:5]) +
            f"\n\n[dim]Confidence: {result.consensus.confidence:.0%} "
            f"(+{result.confidence_boost:.0%} from agreement)[/dim]",
            border_style="green",
            title="🧠 Multi-AI Analysis"
        ))
        
        await analyzer.close()
    else:
        console.print("[yellow]⚠ Collaborative mode unavailable[/yellow]")
    
    console.print()
    await scraper.close()


async def main():
    """Run all demos."""
    
    console.clear()
    
    # Title
    console.print(Panel.fit(
        "[bold white]BET-COPILOT: COLLABORATIVE ANALYSIS SYSTEM[/bold white]\n"
        "[dim]Multi-AI + Live News + Alternative Markets[/dim]",
        border_style="white"
    ))
    
    # Demo 1: News Feed
    await demo_news_feed()
    
    # Demo 2: Collaborative Analysis
    await demo_collaborative_analysis()
    
    # Demo 3: Integrated Flow
    await demo_integrated_flow()
    
    # Summary
    console.rule("[bold green]✅ SYSTEM CAPABILITIES[/bold green]")
    
    capabilities = Table(box=box.ROUNDED, show_header=False)
    capabilities.add_column("Feature", style="cyan")
    capabilities.add_column("Status", style="green")
    
    capabilities.add_row("📰 Free News Aggregation", "BBC Sport + ESPN RSS")
    capabilities.add_row("🤝 Collaborative AI", "Gemini + Blackbox consensus")
    capabilities.add_row("📐 Alternative Markets", "Corners, Cards, Shots, Offsides")
    capabilities.add_row("🎯 Traditional Markets", "1X2, Over/Under, BTTS")
    capabilities.add_row("💰 Kelly Criterion", "Optimal stake sizing")
    capabilities.add_row("⚡ Zero API Waste", "News cached 1hr, parallel fetching")
    
    console.print(capabilities)
    console.print()
    
    console.print(Panel(
        "[bold green]Benefits:[/bold green]\n"
        "• [cyan]Lower API costs:[/cyan] News from free RSS feeds\n"
        "• [cyan]Higher confidence:[/cyan] Two AIs cross-validate analysis\n"
        "• [cyan]More insights:[/cyan] Alternative markets + tactical analysis\n"
        "• [cyan]Real-time context:[/cyan] Live news without rate limits\n\n"
        "[dim]The system now provides institutional-grade analysis\n"
        "while remaining accessible for personal use.[/dim]",
        title="💡 Value Proposition",
        border_style="green"
    ))
    console.print()


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
