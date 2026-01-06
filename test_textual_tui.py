#!/usr/bin/env python3
"""
Test script for Textual TUI Dashboard
Verifies all components load correctly without running the full app.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    
    try:
        from textual.app import App
        print("✓ Textual imported")
    except ImportError as e:
        print(f"✗ Textual import failed: {e}")
        return False
    
    try:
        from bet_copilot.ui.textual_dashboard import (
            BetCopilotDashboard,
            APIHealthWidget,
            NewsWidget,
            MarketWatchWidget,
            AlternativeMarketsWidget,
            SystemLogsWidget,
        )
        print("✓ Dashboard widgets imported")
    except ImportError as e:
        print(f"✗ Dashboard import failed: {e}")
        return False
    
    try:
        from bet_copilot.ui.dashboard_state import DashboardState
        print("✓ Dashboard state imported")
    except ImportError as e:
        print(f"✗ State import failed: {e}")
        return False
    
    return True


def test_state_manager():
    """Test state manager."""
    print("\nTesting state manager...")
    
    from bet_copilot.ui.dashboard_state import DashboardState
    
    # Create state manager
    state = DashboardState()
    print(f"✓ State manager created")
    
    # Test preferences
    state.set_preference("test_key", "test_value")
    value = state.get_preference("test_key")
    assert value == "test_value", "Preference not set correctly"
    print(f"✓ Preferences work")
    
    # Test recent searches
    state.add_recent_search("Arsenal vs Chelsea")
    assert "Arsenal vs Chelsea" in state.recent_searches
    print(f"✓ Recent searches work")
    
    # Test summary
    summary = state.get_summary()
    assert "last_sport_key" in summary
    print(f"✓ Summary generation works")
    
    return True


def test_widget_creation():
    """Test widget creation."""
    print("\nTesting widget creation...")
    
    from bet_copilot.ui.textual_dashboard import (
        APIHealthWidget,
        NewsWidget,
        MarketWatchWidget,
        AlternativeMarketsWidget,
        SystemLogsWidget,
    )
    
    # Create widgets (without mounting)
    try:
        api_widget = APIHealthWidget()
        print("✓ APIHealthWidget created")
        
        news_widget = NewsWidget()
        print("✓ NewsWidget created")
        
        market_widget = MarketWatchWidget()
        print("✓ MarketWatchWidget created")
        
        alt_widget = AlternativeMarketsWidget()
        print("✓ AlternativeMarketsWidget created")
        
        logs_widget = SystemLogsWidget()
        print("✓ SystemLogsWidget created")
        
    except Exception as e:
        print(f"✗ Widget creation failed: {e}")
        return False
    
    return True


def test_app_creation():
    """Test app creation."""
    print("\nTesting app creation...")
    
    from bet_copilot.ui.textual_dashboard import BetCopilotDashboard
    
    try:
        app = BetCopilotDashboard()
        print("✓ BetCopilotDashboard created")
        
        # Check attributes
        assert hasattr(app, 'odds_client')
        assert hasattr(app, 'football_client')
        assert hasattr(app, 'ai_client')
        assert hasattr(app, 'state')
        print("✓ App has all required attributes")
        
        # Check CSS
        assert app.CSS is not None
        print("✓ CSS defined")
        
        # Check bindings
        assert len(app.BINDINGS) > 0
        print("✓ Keyboard bindings defined")
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Textual TUI Dashboard - Component Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("State Manager", test_state_manager),
        ("Widget Creation", test_widget_creation),
        ("App Creation", test_app_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! TUI is ready to use.")
        print("\nTo run the TUI dashboard:")
        print("  python main.py --tui")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
