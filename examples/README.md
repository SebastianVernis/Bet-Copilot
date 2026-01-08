# Examples Directory

Demo scripts showcasing different features of Bet-Copilot.

## 🎮 Demo Scripts

### DEMO.py
Comprehensive demo of all major features.
```bash
python examples/DEMO.py
```

## ⚽ Soccer Prediction Examples

### example_soccer_prediction.py
Basic Poisson prediction for soccer matches.
```bash
python examples/example_soccer_prediction.py
```
**Features**:
- Expected goals calculation
- Match outcome probabilities
- Most likely score
- Over/Under 2.5 predictions

### example_enhanced_analysis.py
Full match analysis with APIs and AI.
```bash
python examples/example_enhanced_analysis.py
```
**Features**:
- Odds API integration
- API-Football stats
- Gemini AI analysis
- Kelly Criterion recommendations
- Alternative markets

## 🤖 AI Analysis Examples

### example_collaborative_analysis.py
Multi-AI collaborative analysis (Gemini + Blackbox).
```bash
python examples/example_collaborative_analysis.py
```
**Features**:
- Parallel AI analysis
- Consensus building
- Agreement scoring
- Confidence boosting
- News integration

### test_ai_fallback.py
Test AI fallback chain (Gemini → Blackbox → Simple).
```bash
python examples/test_ai_fallback.py
```

## 📊 Alternative Markets

### example_alternative_markets.py
Predictions for corners, cards, shots, offsides.
```bash
python examples/example_alternative_markets.py
```
**Markets**:
- Corners (total, over/under)
- Cards (with referee factor)
- Shots (total, on target)
- Offsides

## 🔧 API Testing

### example_usage.py
Basic API client usage.
```bash
python examples/example_usage.py
```
**Tests**:
- Odds API connection
- Football API connection
- Circuit breaker
- Rate limiting

---

## 🚀 Quick Start

### Run All Examples
```bash
# Basic prediction
python examples/example_soccer_prediction.py

# With AI analysis
python examples/example_enhanced_analysis.py

# Collaborative AI
python examples/example_collaborative_analysis.py

# Alternative markets
python examples/example_alternative_markets.py
```

### Requirements
All examples require:
- Valid API keys in `.env`
- Python dependencies installed: `pip install -r requirements.txt`

### API Keys Needed
- **ODDS_API_KEY**: For odds data
- **API_FOOTBALL_KEY**: For detailed stats (optional)
- **GEMINI_API_KEY**: For AI analysis (optional)
- **BLACKBOX_API_KEY**: For fallback AI (optional)

---

## 📝 Example Output

### Soccer Prediction
```
=== Arsenal vs Chelsea ===
Expected goals: Arsenal 1.8, Chelsea 1.4
Win probabilities:
  Arsenal: 38.5%
  Draw: 29.3%
  Chelsea: 32.2%
Most likely score: 2-1
```

### AI Analysis
```
🤖 AI Analysis:
Confidence: 0.75
Lambda adjustments: Home +10%, Away -5%
Key factors:
  - Arsenal in excellent form (4W, 1D)
  - Chelsea missing key midfielder
  - Home advantage significant
```

### Collaborative AI
```
🤝 Collaborative Analysis:
Agreement: 85%
Confidence boost: +17%
Consensus: Slight advantage for home team
Divergence: Away lambda (Gemini: 0.95, Blackbox: 1.0)
```

---

**Note**: Some examples require active API keys. Check output for any API errors.
