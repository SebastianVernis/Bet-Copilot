"""
Example usage of Bet-Copilot odds service
"""
import asyncio
import logging
from bet_copilot.services.odds_service import OddsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Example: Fetch odds for multiple sports"""
    
    # Initialize service
    service = OddsService()
    await service.initialize()
    
    try:
        print("=" * 60)
        print("BET-COPILOT - Example Usage")
        print("=" * 60)
        
        # Get available sports
        print("\n1. Fetching available sports...")
        sports = await service.get_sports()
        print(f"   Found {len(sports)} sports")
        
        # Show first 5 sports
        for sport in sports[:5]:
            print(f"   - {sport['title']} ({sport['key']})")
        
        # Get odds for a specific sport (e.g., soccer)
        sport_key = "soccer_epl"  # English Premier League
        print(f"\n2. Fetching odds for {sport_key}...")
        
        try:
            odds = await service.get_odds(
                sport_key=sport_key,
                regions="us,eu",
                markets="h2h"  # Head-to-head (match winner)
            )
            
            print(f"   Found {len(odds)} events")
            
            # Display first few events
            for event in odds[:3]:
                print(f"\n   Event: {event.home_team} vs {event.away_team}")
                print(f"   Start: {event.commence_time}")
                print(f"   Bookmakers: {len(event.bookmakers)}")
                
                # Show odds from first bookmaker
                if event.bookmakers:
                    bm = event.bookmakers[0]
                    print(f"   {bm.title}:")
                    for market in bm.markets:
                        for outcome in market.outcomes:
                            print(f"     - {outcome.name}: {outcome.price}")
        
        except Exception as e:
            print(f"   Error fetching odds: {e}")
            print("   This might be a rate limit or invalid sport key")
        
        # Get circuit breaker stats
        print("\n3. Circuit Breaker Status:")
        cb_stats = await service.get_circuit_stats()
        print(f"   State: {cb_stats['state']}")
        print(f"   Failures: {cb_stats['failure_count']}")
        if cb_stats['wait_time_remaining'] > 0:
            print(f"   Wait time: {cb_stats['wait_time_remaining']}s")
        
        # Get API request stats
        print("\n4. API Request Statistics (last 24h):")
        req_stats = await service.get_request_stats(hours=24)
        if req_stats:
            print(f"   Total requests: {req_stats.get('total_requests', 0)}")
            print(f"   Successful: {req_stats.get('successful', 0)}")
            print(f"   Rate limited: {req_stats.get('rate_limited', 0)}")
            print(f"   Server errors: {req_stats.get('server_errors', 0)}")
        
        # Test cache
        print("\n5. Testing cache (second fetch should be instant)...")
        import time
        start = time.time()
        odds_cached = await service.get_odds(sport_key, force_refresh=False)
        elapsed = time.time() - start
        print(f"   Fetched {len(odds_cached)} events in {elapsed:.3f}s")
        print(f"   (Cache hit: {elapsed < 0.1})")
        
        # Multiple sports concurrently
        print("\n6. Fetching multiple sports concurrently...")
        sport_keys = ["basketball_nba", "americanfootball_nfl", "icehockey_nhl"]
        results = await service.get_odds_multiple_sports(sport_keys)
        
        for sport_key, events in results.items():
            if isinstance(events, list):
                print(f"   {sport_key}: {len(events)} events")
            else:
                print(f"   {sport_key}: Error")
        
        print("\n" + "=" * 60)
        print("Example completed!")
        print("=" * 60)
    
    finally:
        # Clean up
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
