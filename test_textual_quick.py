#!/usr/bin/env python3
"""
Quick test for Textual TUI - Check import and initialization
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 Testing Textual TUI Integration...\n")

# Test 1: Import
print("1. Testing imports...")
try:
    from bet_copilot.ui.textual_app import (
        BetCopilotApp,
        APIHealthWidget,
        NewsWidget,
        MarketWatchWidget,
        AlternativeMarketsWidget,
        PredictionWidget
    )
    print("   ✅ All widgets imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialization
print("\n2. Testing app initialization...")
try:
    app = BetCopilotApp()
    print("   ✅ App initialized")
    
    # Check services
    assert hasattr(app, 'match_analyzer'), "Missing match_analyzer"
    assert hasattr(app, 'odds_client'), "Missing odds_client"
    assert hasattr(app, 'gemini_client'), "Missing gemini_client"
    assert hasattr(app, 'blackbox_client'), "Missing blackbox_client"
    assert hasattr(app, 'alt_markets'), "Missing alt_markets"
    
    print("   ✅ All services initialized")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Widget availability
print("\n3. Testing widget composition...")
try:
    widgets = [
        APIHealthWidget,
        NewsWidget,
        MarketWatchWidget,
        AlternativeMarketsWidget,
        PredictionWidget
    ]
    
    for widget_class in widgets:
        widget = widget_class()
        print(f"   ✅ {widget_class.__name__} OK")
    
except Exception as e:
    print(f"   ❌ Widget test failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - Textual TUI Ready!")
print("="*60)
print("\n🚀 Run with: python textual_main.py")
