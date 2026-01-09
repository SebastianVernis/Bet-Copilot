# API Integration Plan

## Available APIs

### 1. The Odds API ✅
**Status**: Configured
**Key**: `ODDS_API_KEY=26518b86c05fdcee897d5069272f69c3`
**URL**: https://the-odds-api.com/
**Use Cases**:
- Real-time betting odds from multiple bookmakers
- H2H, Spreads, Totals markets
- Live odds updates
**Limitations**:
- 500 requests/month on free plan
- Limited historical data

### 2. API-Football ✅
**Status**: Configured
**Key**: `API_FOOTBALL_KEY=90c6403a265e6509c7a658c56db84b72`
**URL**: https://www.api-football.com/
**Use Cases**:
- Team statistics and standings
- Match fixtures and results
- Player information
- League data
**Limitations**:
- Free plan: No `last` parameter (blocks recent matches with stats)
- 100 requests/day on free plan

### 3. TheSportsDB 🆕
**Status**: Needs API key
**URL**: https://www.thesportsdb.com/api.php
**Use Cases**:
- Team information and logos
- League tables
- Historical results
- Player data
- Free tier available (limited)
**Required**: `SPORTSDB_API_KEY`

### 4. SportsData.io 🆕
**Status**: Needs API key  
**URL**: https://sportsdata.io/
**Use Cases**:
- Detailed statistics
- Play-by-play data
- Player props
- Advanced metrics (corners, cards, shots)
**Required**: `SPORTSDATA_API_KEY`

### 5. Football-Data.org 🆕
**Status**: Needs API key
**URL**: https://www.football-data.org/
**Use Cases**:
- Free tier with good data
- Match schedules
- Team standings
- Head-to-head
**Required**: `FOOTBALL_DATA_API_KEY`

## Integration Strategy

### Phase 1: Odds Enhancement ✅
**Goal**: Get real odds from The Odds API
**Tasks**:
1. ✅ Integrate OddsAPIClient into match analyzer
2. ✅ Replace estimated odds with real bookmaker odds
3. ✅ Add multiple bookmaker comparison
4. ✅ Calculate best odds for Kelly recommendations

### Phase 2: Alternative Markets 🔄
**Goal**: Enable corners, cards, shots predictions
**Options**:
- **Option A**: Upgrade API-Football to paid plan ($15-50/month)
- **Option B**: Use SportsData.io for detailed stats
- **Option C**: Use TheSportsDB + Football-Data.org combination

**Recommendation**: Start with TheSportsDB (free tier) + Football-Data.org (free)

### Phase 3: Multi-Source Data Aggregation
**Goal**: Combine data from multiple sources for best coverage
**Architecture**:
```
MatchAnalyzer
    ├─ PrimarySource: API-Football (team stats)
    ├─ OddsSource: The Odds API (real odds)
    ├─ HistoricalSource: TheSportsDB (H2H, form)
    ├─ DetailedStats: SportsData.io (corners, cards, shots)
    └─ Fallback: SimpleFootballData (estimates)
```

## Implementation Checklist

### Immediate (No new keys needed)
- [ ] Integrate The Odds API for real bookmaker odds
- [ ] Test with current matches
- [ ] Compare estimated vs real odds

### Short-term (With API keys provided)
- [ ] Add TheSportsDB client
- [ ] Add Football-Data.org client
- [ ] Add SportsData.io client
- [ ] Implement data aggregation layer
- [ ] Enable alternative markets (corners, cards, shots)

### Long-term
- [ ] Implement intelligent source selection
- [ ] Add caching layer for API efficiency
- [ ] Monitor API usage and quotas
- [ ] Implement automatic fallback chains

## API Key Configuration

Add to `.env`:
```bash
# Current (Working)
ODDS_API_KEY=26518b86c05fdcee897d5069272f69c3
API_FOOTBALL_KEY=90c6403a265e6509c7a658c56db84b72
GEMINI_API_KEY=AIzaSyDND7qBj069zDABEFZmlEX678OTU0_KEjw
BLACKBOX_API_KEY=sk-Vl6HBMkEaEzvj6x_qfrfhA

# New (Pending)
SPORTSDB_API_KEY=your_key_here
SPORTSDATA_API_KEY=your_key_here
FOOTBALL_DATA_API_KEY=your_key_here
```

## Expected Improvements

### With Real Odds (The Odds API)
- ✅ Accurate bookmaker odds
- ✅ Multiple bookmaker comparison
- ✅ Real EV calculations (not -7.4%)
- ✅ Actual value bet detection

### With Alternative Data Sources
- ✅ Corners predictions (avg from recent matches)
- ✅ Cards predictions (referee data + team discipline)
- ✅ Shots predictions (team offensive/defensive stats)
- ✅ More accurate H2H data
- ✅ Better team form analysis

### User Experience
- ✅ More accurate predictions
- ✅ Real value bets identified
- ✅ Complete market coverage
- ✅ Multiple bookmaker comparison
- ✅ Historical data for better AI context
