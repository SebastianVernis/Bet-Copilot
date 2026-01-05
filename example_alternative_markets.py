"""
Demo: Alternative Markets Prediction

Demonstrates predictions for non-traditional betting markets:
- Corners
- Cards (yellow/red)
- Shots and shots on target
- Offsides

These markets offer different risk/reward profiles compared to traditional
match outcome betting.
"""

import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from bet_copilot.models.soccer import TeamForm, MatchResult
from bet_copilot.math_engine.alternative_markets import AlternativeMarketsPredictor


console = Console()


def create_sample_teams():
    """Create sample teams with historical data."""
    
    # Team A: Attacking team with high possession
    team_a = TeamForm(team_name="Manchester City")
    for i in range(5):
        match = MatchResult(
            date=datetime.now() - timedelta(days=i * 7),
            home_team="Manchester City" if i % 2 == 0 else f"Opponent {i}",
            away_team=f"Opponent {i}" if i % 2 == 0 else "Manchester City",
            home_goals=3 if i % 2 == 0 else 1,
            away_goals=1 if i % 2 == 0 else 2,
            home_xg=2.5 if i % 2 == 0 else 1.2,
            away_xg=1.0 if i % 2 == 0 else 1.8,
            is_home=(i % 2 == 0),
            # High corners (attacking team)
            home_corners=8 if i % 2 == 0 else 4,
            away_corners=3 if i % 2 == 0 else 7,
            # High shots (dominant team)
            home_shots=18 if i % 2 == 0 else 10,
            away_shots=8 if i % 2 == 0 else 16,
            home_shots_on_target=7 if i % 2 == 0 else 4,
            away_shots_on_target=3 if i % 2 == 0 else 6,
            # Moderate cards
            home_yellow_cards=2 if i % 2 == 0 else 1,
            away_yellow_cards=1 if i % 2 == 0 else 2,
            home_red_cards=0,
            away_red_cards=0,
            home_fouls=10 if i % 2 == 0 else 14,
            away_fouls=12 if i % 2 == 0 else 11,
            home_offsides=2 if i % 2 == 0 else 1,
            away_offsides=1 if i % 2 == 0 else 3,
        )
        team_a.add_match(match)
    
    # Team B: Defensive team
    team_b = TeamForm(team_name="Atletico Madrid")
    for i in range(5):
        match = MatchResult(
            date=datetime.now() - timedelta(days=i * 7),
            home_team=f"Opponent {i}" if i % 2 == 0 else "Atletico Madrid",
            away_team="Atletico Madrid" if i % 2 == 0 else f"Opponent {i}",
            home_goals=2 if i % 2 == 0 else 1,
            away_goals=1 if i % 2 == 0 else 1,
            home_xg=1.5 if i % 2 == 0 else 1.3,
            away_xg=1.2 if i % 2 == 0 else 1.2,
            is_home=(i % 2 != 0),
            # Lower corners (defensive team concedes more)
            home_corners=5 if i % 2 == 0 else 4,
            away_corners=4 if i % 2 == 0 else 5,
            # Lower shots (defensive style)
            home_shots=13 if i % 2 == 0 else 11,
            away_shots=10 if i % 2 == 0 else 12,
            home_shots_on_target=5 if i % 2 == 0 else 4,
            away_shots_on_target=4 if i % 2 == 0 else 5,
            # More cards (physical team)
            home_yellow_cards=3 if i % 2 == 0 else 2,
            away_yellow_cards=2 if i % 2 == 0 else 3,
            home_red_cards=0,
            away_red_cards=0 if i % 2 == 0 else 1,
            home_fouls=15 if i % 2 == 0 else 13,
            away_fouls=12 if i % 2 == 0 else 16,
            home_offsides=1 if i % 2 == 0 else 2,
            away_offsides=2 if i % 2 == 0 else 1,
        )
        team_b.add_match(match)
    
    return team_a, team_b


def display_prediction(prediction, market_emoji="⚽"):
    """Display prediction in a nice format."""
    
    # Main info panel
    info_text = f"""
[bold cyan]{market_emoji} {prediction.market_type.upper()} PREDICTION[/bold cyan]
[yellow]{prediction.home_team}[/yellow] vs [magenta]{prediction.away_team}[/magenta]

[green]Expected Total:[/green] {prediction.total_expected:.2f}
[dim]Data Quality: {prediction.data_quality.upper()} | Confidence: {prediction.confidence:.0%}[/dim]

{prediction.reasoning}
"""
    
    console.print(Panel(info_text, border_style="cyan", box=box.ROUNDED))
    
    # Over/Under table
    if prediction.over_under_predictions:
        table = Table(title="Over/Under Probabilities", box=box.SIMPLE)
        table.add_column("Threshold", justify="center", style="cyan")
        table.add_column("Over", justify="right", style="green")
        table.add_column("Under", justify="right", style="yellow")
        table.add_column("Best Value", justify="center", style="bold")
        
        for threshold, probs in sorted(prediction.over_under_predictions.items()):
            over_prob = probs["over"]
            under_prob = probs["under"]
            
            # Determine best value (closest to 50/50 or strong lean)
            if abs(over_prob - 0.5) < 0.1:
                best = "⚖️ Balanced"
            elif over_prob > 0.65:
                best = "✅ Over"
            elif under_prob > 0.65:
                best = "✅ Under"
            else:
                best = "⚠️ Risky"
            
            table.add_row(
                f"{threshold}",
                f"{over_prob:.1%}",
                f"{under_prob:.1%}",
                best
            )
        
        console.print(table)
    
    # Distribution (top values only)
    if prediction.distribution:
        dist_table = Table(title="Probability Distribution (Top Values)", box=box.SIMPLE)
        dist_table.add_column("Value", justify="center", style="cyan")
        dist_table.add_column("Probability", justify="right", style="green")
        dist_table.add_column("Visual", justify="left")
        
        # Get top 8 values
        top_values = sorted(
            prediction.distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:8]
        
        for value, prob in top_values:
            bar = "█" * int(prob * 100)
            dist_table.add_row(
                str(value),
                f"{prob:.1%}",
                bar
            )
        
        console.print(dist_table)
    
    console.print()


def main():
    """Run alternative markets demo."""
    
    console.print()
    console.print(Panel.fit(
        "[bold green]Alternative Markets Prediction Demo[/bold green]\n"
        "[dim]Non-traditional betting markets analysis[/dim]",
        border_style="green"
    ))
    console.print()
    
    # Create sample data
    console.print("[yellow]Creating sample teams...[/yellow]")
    team_a, team_b = create_sample_teams()
    
    console.print(f"✅ {team_a.team_name}: {team_a.get_form_string()}")
    console.print(f"✅ {team_b.team_name}: {team_b.get_form_string()}")
    console.print()
    
    # Initialize predictor
    predictor = AlternativeMarketsPredictor()
    
    # 1. Corners Prediction
    console.rule("[bold cyan]📐 CORNERS PREDICTION[/bold cyan]")
    corners = predictor.predict_corners(team_a, team_b, matches_to_consider=5)
    display_prediction(corners, "📐")
    
    # 2. Cards Prediction
    console.rule("[bold yellow]🟨 CARDS PREDICTION[/bold yellow]")
    cards = predictor.predict_cards(team_a, team_b, matches_to_consider=5)
    display_prediction(cards, "🟨")
    
    # Test with strict referee
    console.print("[dim]Adjusting for strict referee (+20%)...[/dim]")
    cards_strict = predictor.predict_cards(
        team_a, team_b,
        matches_to_consider=5,
        referee_factor=1.2
    )
    console.print(f"[yellow]With strict referee:[/yellow] {cards_strict.total_expected:.2f} cards expected")
    console.print()
    
    # 3. Shots Prediction
    console.rule("[bold green]🎯 SHOTS PREDICTION[/bold green]")
    shots = predictor.predict_shots(team_a, team_b, matches_to_consider=5)
    display_prediction(shots, "🎯")
    
    # 4. Shots on Target
    console.rule("[bold magenta]🎯 SHOTS ON TARGET[/bold magenta]")
    shots_on_target = predictor.predict_shots(
        team_a, team_b,
        matches_to_consider=5,
        shots_on_target_only=True
    )
    display_prediction(shots_on_target, "🎯")
    
    # 5. Offsides
    console.rule("[bold red]🚩 OFFSIDES PREDICTION[/bold red]")
    offsides = predictor.predict_offsides(team_a, team_b, matches_to_consider=5)
    display_prediction(offsides, "🚩")
    
    # Summary
    console.rule("[bold white]📊 SUMMARY[/bold white]")
    summary_table = Table(box=box.ROUNDED)
    summary_table.add_column("Market", style="cyan", justify="left")
    summary_table.add_column("Expected", style="green", justify="right")
    summary_table.add_column("Confidence", style="yellow", justify="center")
    summary_table.add_column("Quality", style="magenta", justify="center")
    
    for market, pred in [
        ("Corners", corners),
        ("Cards", cards),
        ("Shots", shots),
        ("Shots on Target", shots_on_target),
        ("Offsides", offsides),
    ]:
        summary_table.add_row(
            market,
            f"{pred.total_expected:.2f}",
            f"{pred.confidence:.0%}",
            pred.data_quality.upper()
        )
    
    console.print(summary_table)
    console.print()
    
    # Key insights
    console.print(Panel(
        f"[bold green]Key Insights:[/bold green]\n\n"
        f"• [cyan]Corners:[/cyan] Expected {corners.total_expected:.1f} - "
        f"{'High' if corners.total_expected > 10 else 'Moderate'} corner count\n"
        f"• [yellow]Cards:[/yellow] Expected {cards.total_expected:.1f} - "
        f"{'Physical' if cards.total_expected > 4 else 'Clean'} match\n"
        f"• [green]Shots:[/green] Expected {shots.total_expected:.1f} - "
        f"{'High' if shots.total_expected > 20 else 'Low'} intensity\n\n"
        f"[dim]Use these insights to find value in alternative markets where "
        f"bookmakers may misprice due to less sophisticated models.[/dim]",
        title="💡 Analysis",
        border_style="green"
    ))
    console.print()


if __name__ == "__main__":
    main()
