"""
Example usage of soccer prediction engine with Poisson distribution
"""
import json
from datetime import datetime, timedelta

from bet_copilot.math_engine.soccer_predictor import SoccerPredictor
from bet_copilot.models.soccer import TeamForm, MatchResult


def create_sample_teams():
    """Create sample teams with realistic xG data"""
    
    # Real Madrid (Home) - Strong attacking team
    real_madrid = TeamForm("Real Madrid")
    base_date = datetime.now()
    
    home_matches = [
        # Recent home matches (date, opponent, goals_for, goals_against, xg_for, xg_against)
        (0, "Sevilla", 3, 1, 2.4, 0.9),
        (7, "Valencia", 2, 1, 2.1, 1.2),
        (14, "Athletic Bilbao", 4, 0, 2.8, 0.6),
        (21, "Getafe", 1, 0, 1.7, 0.8),
        (28, "Real Sociedad", 2, 2, 2.3, 1.8),
    ]
    
    for days_ago, opponent, gf, ga, xgf, xga in home_matches:
        match = MatchResult(
            date=base_date - timedelta(days=days_ago),
            home_team="Real Madrid",
            away_team=opponent,
            home_goals=gf,
            away_goals=ga,
            home_xg=xgf,
            away_xg=xga,
            is_home=True
        )
        real_madrid.add_match(match)
    
    # Barcelona (Away) - Balanced team
    barcelona = TeamForm("Barcelona")
    
    away_matches = [
        # Recent away matches
        (0, "Villarreal", 2, 1, 1.9, 1.1),
        (7, "Atletico Madrid", 1, 1, 1.5, 1.4),
        (14, "Real Betis", 3, 2, 2.2, 1.6),
        (21, "Celta Vigo", 1, 0, 1.3, 0.9),
        (28, "Girona", 2, 1, 1.8, 1.3),
    ]
    
    for days_ago, opponent, gf, ga, xgf, xga in away_matches:
        match = MatchResult(
            date=base_date - timedelta(days=days_ago),
            home_team=opponent,
            away_team="Barcelona",
            home_goals=ga,
            away_goals=gf,
            home_xg=xga,
            away_xg=xgf,
            is_home=False
        )
        barcelona.add_match(match)
    
    return real_madrid, barcelona


def example_basic_prediction():
    """Example 1: Basic prediction"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Match Prediction")
    print("=" * 70)
    
    # Create teams
    home_team, away_team = create_sample_teams()
    
    # Create predictor
    predictor = SoccerPredictor(
        matches_to_consider=5,
        home_advantage_factor=1.0  # No home advantage for this example
    )
    
    # Make prediction
    prediction = predictor.predict(home_team, away_team, include_details=False)
    
    # Display results
    print(f"\n{prediction}\n")
    
    return prediction


def example_with_home_advantage():
    """Example 2: Prediction with home advantage"""
    print("=" * 70)
    print("EXAMPLE 2: Prediction with Home Advantage (10%)")
    print("=" * 70)
    
    home_team, away_team = create_sample_teams()
    
    # Predictor with 10% home advantage
    predictor = SoccerPredictor(
        matches_to_consider=5,
        home_advantage_factor=1.1  # 10% boost for home team
    )
    
    prediction = predictor.predict(home_team, away_team)
    
    print(f"\nMatch: {prediction.home_team} vs {prediction.away_team}")
    print(f"\nExpected Goals (with home advantage):")
    print(f"  {prediction.home_team}: {prediction.home_lambda}")
    print(f"  {prediction.away_team}: {prediction.away_lambda}")
    print(f"\nOutcome Probabilities:")
    print(f"  Home Win: {prediction.home_win_prob:.1%}")
    print(f"  Draw:     {prediction.draw_prob:.1%}")
    print(f"  Away Win: {prediction.away_win_prob:.1%}")
    print(f"\nOver/Under 2.5 Goals:")
    print(f"  Over:  {prediction.over_under_2_5['over']:.1%}")
    print(f"  Under: {prediction.over_under_2_5['under']:.1%}")
    print(f"\nBoth Teams To Score:")
    print(f"  Yes: {prediction.btts['yes']:.1%}")
    print(f"  No:  {prediction.btts['no']:.1%}")
    
    return prediction


def example_top_scorelines():
    """Example 3: Most likely scorelines"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Most Likely Scorelines")
    print("=" * 70)
    
    home_team, away_team = create_sample_teams()
    predictor = SoccerPredictor()
    
    scorelines = predictor.get_top_scorelines(home_team, away_team, top_n=10)
    
    print(f"\nTop 10 Most Likely Scorelines for {home_team.team_name} vs {away_team.team_name}:\n")
    for i, ((home_goals, away_goals), prob) in enumerate(scorelines, 1):
        print(f"{i:2d}. {home_goals}-{away_goals}  {prob:.1%}  {'█' * int(prob * 100)}")


def example_direct_lambda():
    """Example 4: Prediction from direct lambda values"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Direct Lambda Input (Manual xG)")
    print("=" * 70)
    
    predictor = SoccerPredictor()
    
    # Predict with manually specified xG values
    prediction = predictor.predict_from_lambdas(
        home_team_name="Manchester City",
        away_team_name="Arsenal",
        lambda_home=2.5,  # Man City expected goals
        lambda_away=1.8,  # Arsenal expected goals
        include_details=True
    )
    
    print(f"\n{prediction}\n")
    
    # Show detailed breakdown
    print("Detailed Market Predictions:")
    print(f"\nTotal Goals: {prediction.expected_total_goals}")
    print(f"Over 2.5: {prediction.over_under_2_5['over']:.1%}")
    print(f"Under 2.5: {prediction.over_under_2_5['under']:.1%}")
    print(f"BTTS Yes: {prediction.btts['yes']:.1%}")


def example_comprehensive_analysis():
    """Example 5: Comprehensive match analysis"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Comprehensive Match Analysis")
    print("=" * 70)
    
    home_team, away_team = create_sample_teams()
    predictor = SoccerPredictor(home_advantage_factor=1.1)
    
    # Get comprehensive comparison
    analysis = predictor.compare_predictions(home_team, away_team)
    
    # Pretty print JSON
    print("\n" + json.dumps(analysis, indent=2))


def example_multiple_scenarios():
    """Example 6: Compare different scenarios"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Scenario Comparison")
    print("=" * 70)
    
    home_team, away_team = create_sample_teams()
    
    scenarios = [
        ("No Home Advantage", 1.0),
        ("Small Home Advantage (5%)", 1.05),
        ("Normal Home Advantage (10%)", 1.1),
        ("Strong Home Advantage (15%)", 1.15),
    ]
    
    print(f"\n{home_team.team_name} vs {away_team.team_name}\n")
    print(f"{'Scenario':<30} {'Home Win':<10} {'Draw':<10} {'Away Win':<10}")
    print("-" * 60)
    
    for scenario_name, ha_factor in scenarios:
        predictor = SoccerPredictor(home_advantage_factor=ha_factor)
        prediction = predictor.predict(home_team, away_team, include_details=False)
        
        print(f"{scenario_name:<30} {prediction.home_win_prob:<10.1%} "
              f"{prediction.draw_prob:<10.1%} {prediction.away_win_prob:<10.1%}")


def example_team_form_analysis():
    """Example 7: Detailed team form analysis"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Team Form Analysis")
    print("=" * 70)
    
    home_team, away_team = create_sample_teams()
    
    print(f"\n{home_team.team_name} (Home Form - Last 5 Matches):")
    print(f"  Form: {home_team.get_form_string(5)}")
    print(f"  Avg xG For (Home): {home_team.average_xg_for(5, home_only=True)}")
    print(f"  Avg xG Against (Home): {home_team.average_xg_against(5, home_only=True)}")
    print(f"  Avg Goals For (Home): {home_team.average_goals_for(5, home_only=True)}")
    print(f"  Avg Goals Against (Home): {home_team.average_goals_against(5, home_only=True)}")
    
    print(f"\n{away_team.team_name} (Away Form - Last 5 Matches):")
    print(f"  Form: {away_team.get_form_string(5)}")
    print(f"  Avg xG For (Away): {away_team.average_xg_for(5, away_only=True)}")
    print(f"  Avg xG Against (Away): {away_team.average_xg_against(5, away_only=True)}")
    print(f"  Avg Goals For (Away): {away_team.average_goals_for(5, away_only=True)}")
    print(f"  Avg Goals Against (Away): {away_team.average_goals_against(5, away_only=True)}")


def example_value_betting():
    """Example 8: Value betting analysis"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Value Betting Analysis")
    print("=" * 70)
    
    predictor = SoccerPredictor()
    prediction = predictor.predict_from_lambdas(
        "Team A", "Team B",
        lambda_home=1.8,
        lambda_away=1.5
    )
    
    # Simulate bookmaker odds (decimal format)
    bookmaker_odds = {
        "home_win": 2.10,  # Implied prob: 47.6%
        "draw": 3.40,      # Implied prob: 29.4%
        "away_win": 3.50   # Implied prob: 28.6%
    }
    
    print(f"\nMatch: {prediction.home_team} vs {prediction.away_team}\n")
    print(f"{'Market':<15} {'Model Prob':<12} {'Book Odds':<12} {'Implied Prob':<15} {'Value':<10}")
    print("-" * 65)
    
    markets = [
        ("Home Win", prediction.home_win_prob, bookmaker_odds["home_win"]),
        ("Draw", prediction.draw_prob, bookmaker_odds["draw"]),
        ("Away Win", prediction.away_win_prob, bookmaker_odds["away_win"]),
    ]
    
    for market, model_prob, odds in markets:
        implied_prob = 1 / odds
        value = (model_prob * odds) - 1  # Expected value
        
        value_str = f"+{value:.1%}" if value > 0 else f"{value:.1%}"
        indicator = " ✓✓" if value > 0.05 else " ✓" if value > 0 else ""
        
        print(f"{market:<15} {model_prob:<12.1%} {odds:<12.2f} "
              f"{implied_prob:<15.1%} {value_str:<10}{indicator}")
    
    print("\n✓✓ = Strong value (>5% edge)")
    print("✓  = Positive value")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "BET-COPILOT SOCCER PREDICTION ENGINE" + " " * 16 + "║")
    print("║" + " " * 20 + "Poisson Distribution Model" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run examples
    example_basic_prediction()
    example_with_home_advantage()
    example_top_scorelines()
    example_direct_lambda()
    example_comprehensive_analysis()
    example_multiple_scenarios()
    example_team_form_analysis()
    example_value_betting()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
