#!/usr/bin/env python3
"""
Quick test script to verify match analysis functionality.
Tests AI connections, predictions, and market analysis.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Set env vars
os.environ.setdefault('GEMINI_API_KEY', 'AIzaSyDND7qBj069zDABEFZmlEX678OTU0_KEjw')
os.environ.setdefault('BLACKBOX_API_KEY', 'sk-Vl6HBMkEaEzvj6x_qfrfhA')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

from bet_copilot.services.match_analyzer import MatchAnalyzer


async def test_match_analysis(home_team: str, away_team: str):
    """Test complete match analysis."""
    
    print(f"\n{'='*60}")
    print(f"TESTING: {home_team} vs {away_team}")
    print(f"{'='*60}\n")
    
    analyzer = MatchAnalyzer()
    
    try:
        # Run analysis
        print("Running analysis...")
        analysis = await analyzer.analyze_match(
            home_team_name=home_team,
            away_team_name=away_team,
            league_id=39,  # Premier League
            season=2024,
            include_players=False,  # Skip for speed
            include_ai_analysis=True
        )
        
        # Display results
        print(f"\n✅ ANALYSIS COMPLETE\n")
        
        # Basic info
        print(f"Match: {analysis.home_team} vs {analysis.away_team}")
        print(f"League: {analysis.league}")
        
        # Prediction
        if analysis.prediction:
            print(f"\n📊 PREDICTION:")
            print(f"  Home Win: {analysis.prediction.home_win_prob:.1%}")
            print(f"  Draw:     {analysis.prediction.draw_prob:.1%}")
            print(f"  Away Win: {analysis.prediction.away_win_prob:.1%}")
            print(f"  Expected Score: {analysis.prediction.most_likely_score}")
            print(f"  Expected Goals: {analysis.prediction.home_lambda:.2f} - {analysis.prediction.away_lambda:.2f}")
        
        # AI Analysis
        if analysis.ai_analysis:
            print(f"\n🤖 AI ANALYSIS:")
            print(f"  Confidence: {analysis.ai_analysis.confidence:.0%}")
            print(f"  Sentiment: {analysis.ai_analysis.sentiment}")
            print(f"  Key Factors:")
            for i, factor in enumerate(analysis.ai_analysis.key_factors[:5], 1):
                print(f"    {i}. {factor}")
        
        # Collaborative analysis
        if analysis.collaborative_analysis:
            print(f"\n🤝 COLLABORATIVE ANALYSIS:")
            print(f"  Agreement Score: {analysis.collaborative_analysis.agreement_score:.0%}")
            print(f"  Consensus Confidence: {analysis.collaborative_analysis.consensus.confidence:.0%}")
            if analysis.collaborative_analysis.gemini_analysis:
                print(f"  Gemini Confidence: {analysis.collaborative_analysis.gemini_analysis.confidence:.0%}")
            if analysis.collaborative_analysis.blackbox_analysis:
                print(f"  Blackbox Confidence: {analysis.collaborative_analysis.blackbox_analysis.confidence:.0%}")
        
        # Odds and Kelly
        print(f"\n💰 BETTING MARKETS:")
        print(f"  Odds Source: {analysis.bookmaker}")
        print(f"  Home Odds: {analysis.home_odds:.2f}")
        print(f"  Draw Odds: {analysis.draw_odds:.2f}")
        print(f"  Away Odds: {analysis.away_odds:.2f}")
        
        print(f"\n📈 KELLY CRITERION:")
        if analysis.kelly_home:
            print(f"  Home: EV={analysis.kelly_home.ev:+.1%} | "
                  f"Value={analysis.kelly_home.is_value_bet} | "
                  f"Risk={analysis.kelly_home.risk_level}")
        if analysis.kelly_draw:
            print(f"  Draw: EV={analysis.kelly_draw.ev:+.1%} | "
                  f"Value={analysis.kelly_draw.is_value_bet} | "
                  f"Risk={analysis.kelly_draw.risk_level}")
        if analysis.kelly_away:
            print(f"  Away: EV={analysis.kelly_away.ev:+.1%} | "
                  f"Value={analysis.kelly_away.is_value_bet} | "
                  f"Risk={analysis.kelly_away.risk_level}")
        
        # Alternative markets
        print(f"\n📐 ALTERNATIVE MARKETS:")
        if analysis.corners_prediction:
            print(f"  Corners: {analysis.corners_prediction.total_expected:.1f}")
        else:
            print(f"  Corners: N/A (API limitation)")
        
        if analysis.cards_prediction:
            print(f"  Cards: {analysis.cards_prediction.total_expected:.1f}")
        else:
            print(f"  Cards: N/A (API limitation)")
        
        if analysis.shots_prediction:
            print(f"  Shots: {analysis.shots_prediction.total_expected:.1f}")
        else:
            print(f"  Shots: N/A (API limitation)")
        
        # Best value bet
        best_bet = analysis.get_best_value_bet()
        if best_bet:
            print(f"\n⭐ BEST VALUE BET:")
            print(f"  Outcome: {best_bet['outcome']}")
            print(f"  Team: {best_bet.get('team', 'N/A')}")
            print(f"  EV: {best_bet['ev']:+.1%}")
            print(f"  Odds: {best_bet['odds']:.2f}")
            print(f"  Risk: {best_bet['risk']}")
        else:
            print(f"\n⚠️  NO VALUE BETS FOUND (Expected with estimated odds)")
        
        print(f"\n{'='*60}")
        print(f"✅ TEST SUCCESSFUL")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if hasattr(analyzer, 'blackbox_client'):
            await analyzer.blackbox_client.close()


async def main():
    """Run tests."""
    
    # Test matches
    matches = [
        ("Arsenal", "Chelsea"),
        ("Liverpool", "Manchester City"),
        ("Real Madrid", "Barcelona"),  # Will fail if not in Premier League
    ]
    
    print("\n" + "="*60)
    print("BET-COPILOT MATCH ANALYSIS TEST")
    print("="*60)
    
    for home, away in matches[:1]:  # Test only first match
        await test_match_analysis(home, away)


if __name__ == "__main__":
    asyncio.run(main())
