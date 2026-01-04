#!/usr/bin/env python3
"""
Debug test for completion logic.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MockEvent:
    home_team: str
    away_team: str
    commence_time: datetime


class MockCLI:
    def __init__(self):
        now = datetime.now()
        self.events = [
            MockEvent("Arsenal", "Chelsea", now + timedelta(days=1)),
            MockEvent("Manchester United", "Liverpool", now + timedelta(days=2)),
            MockEvent("Barcelona", "Real Madrid", now + timedelta(days=3)),
        ]


def test_text_parsing():
    """Test how we parse different inputs."""
    
    test_cases = [
        ("", "Empty"),
        ("ana", "Partial command"),
        ("analizar", "Complete command no space"),
        ("analizar ", "Complete command with space"),
        ("analizar Ars", "Command + partial arg"),
        ("analizar Arsenal vs Chelsea", "Command + full arg"),
        ("mercados ", "Mercados with space"),
        ("mercados soc", "Mercados + partial"),
    ]
    
    print("=" * 60)
    print("TEXT PARSING TEST")
    print("=" * 60)
    
    for text, description in test_cases:
        text_stripped = text.strip()
        parts = text_stripped.split()
        
        print(f"\nInput: '{text}'")
        print(f"  Description: {description}")
        print(f"  text.strip(): '{text_stripped}'")
        print(f"  parts: {parts}")
        print(f"  len(parts): {len(parts)}")
        print(f"  text.endswith(' '): {text.endswith(' ')}")
        
        # Determine what should happen
        if not text:
            action = "Show all commands"
        elif not parts:
            action = "Show all commands"
        elif len(parts) == 1 and not text.endswith(' '):
            action = f"Complete command '{parts[0]}'"
        elif len(parts) == 1 and text.endswith(' '):
            action = f"Show arguments for '{parts[0]}'"
        else:
            command = parts[0]
            arg_start = text.find(' ') + 1
            arg_text = text[arg_start:]
            action = f"Complete argument '{arg_text}' for '{command}'"
        
        print(f"  → Action: {action}")


def test_match_filtering():
    """Test match filtering logic."""
    
    cli = MockCLI()
    
    print("\n" + "=" * 60)
    print("MATCH FILTERING TEST")
    print("=" * 60)
    
    test_args = [
        "",
        "Ars",
        "Man",
        "Real",
        "United",
        "vs",
    ]
    
    for arg in test_args:
        print(f"\nArg: '{arg}'")
        matches = []
        
        for event in cli.events:
            match_str = f"{event.home_team} vs {event.away_team}"
            
            if not arg or (
                arg.lower() in event.home_team.lower() or 
                arg.lower() in event.away_team.lower() or
                arg.lower() in match_str.lower()
            ):
                matches.append(match_str)
        
        print(f"  Matches ({len(matches)}):")
        for match in matches:
            print(f"    • {match}")


if __name__ == "__main__":
    test_text_parsing()
    test_match_filtering()
    
    print("\n" + "=" * 60)
    print("✓ Debug tests complete")
    print("=" * 60)
