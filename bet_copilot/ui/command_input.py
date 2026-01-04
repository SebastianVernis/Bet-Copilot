"""
Advanced command input with history, completion, and keyboard navigation.
Uses prompt_toolkit for rich terminal interactions.
"""

from typing import List, Optional, Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from bet_copilot.ui.styles import NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_PINK


class BetCopilotCompleter(Completer):
    """Custom completer with context-aware suggestions."""
    
    def __init__(self, cli_instance=None):
        self.cli_instance = cli_instance
        
        # Base commands
        self.commands = {
            "dashboard": "Mostrar dashboard en vivo (4 zonas)",
            "mercados": "Obtener mercados de apuestas",
            "markets": "Get betting markets",
            "analizar": "Analizar un partido específico",
            "analyze": "Analyze a specific match",
            "analyse": "Analyze a specific match",
            "salud": "Verificar estado de las APIs",
            "health": "Check APIs health",
            "ayuda": "Mostrar menú de ayuda",
            "help": "Show help menu",
            "salir": "Salir de la aplicación",
            "quit": "Exit application",
            "exit": "Exit application",
            "q": "Quick exit",
        }
        
        # Sport keys for mercados/markets with descriptions
        self.sport_keys = {
            "soccer_epl": "Premier League (Inglaterra)",
            "soccer_la_liga": "La Liga (España)",
            "soccer_serie_a": "Serie A (Italia)",
            "soccer_bundesliga": "Bundesliga (Alemania)",
            "soccer_france_ligue_one": "Ligue 1 (Francia)",
            "soccer_brazil_campeonato": "Brasileirão (Brasil)",
            "soccer_uefa_champs_league": "UEFA Champions League",
            "soccer_uefa_europa_league": "UEFA Europa League",
            "soccer_portugal_primeira_liga": "Primeira Liga (Portugal)",
            "soccer_netherlands_eredivisie": "Eredivisie (Holanda)",
            "americanfootball_nfl": "NFL",
            "basketball_nba": "NBA",
            "icehockey_nhl": "NHL",
        }
    
    def get_completions(self, document, complete_event):
        """Generate completions based on current input."""
        text = document.text_before_cursor
        
        # Empty input - show all commands
        if not text:
            for cmd, desc in self.commands.items():
                yield Completion(
                    cmd,
                    start_position=0,
                    display=cmd,
                    display_meta=desc,
                )
            return
        
        # Split considering spaces
        text_stripped = text.strip()
        parts = text_stripped.split()
        
        if not parts:
            # Only spaces - show all commands
            for cmd, desc in self.commands.items():
                yield Completion(
                    cmd,
                    start_position=0,
                    display=cmd,
                    display_meta=desc,
                )
            return
        
        # First word not complete - command completion
        if len(parts) == 1 and not text.endswith(' '):
            word = parts[0]
            for cmd, desc in self.commands.items():
                if cmd.startswith(word.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display=cmd,
                        display_meta=desc,
                    )
            return
        
        # Command complete, waiting for argument
        if len(parts) == 1 and text.endswith(' '):
            command = parts[0].lower()
            
            # Sport keys for mercados/markets
            if command in ["mercados", "markets"]:
                for sport_key, description in self.sport_keys.items():
                    yield Completion(
                        sport_key,
                        start_position=0,
                        display=sport_key,
                        display_meta=description,
                    )
            
            # Match names for analizar/analyze - show all when just pressed space
            elif command in ["analizar", "analyze", "analyse"]:
                if self.cli_instance and hasattr(self.cli_instance, 'events') and self.cli_instance.events:
                    seen_matches = set()
                    for event in self.cli_instance.events:
                        match_str = f"{event.home_team} vs {event.away_team}"
                        if match_str not in seen_matches:
                            seen_matches.add(match_str)
                            yield Completion(
                                match_str,
                                start_position=0,
                                display=match_str,
                                display_meta=event.commence_time.strftime('%Y-%m-%d %H:%M'),
                            )
                else:
                    # Suggest getting markets first
                    yield Completion(
                        "",
                        start_position=0,
                        display="(ejecuta 'mercados' primero)",
                        display_meta="No hay partidos cargados",
                    )
            return
        
        # Command + partial argument
        if len(parts) >= 2:
            command = parts[0].lower()
            # Get the argument part (everything after command)
            arg_start = text.find(' ') + 1
            arg_text = text[arg_start:]
            
            # Sport keys for mercados/markets
            if command in ["mercados", "markets"]:
                for sport_key, description in self.sport_keys.items():
                    if sport_key.startswith(arg_text.lower()):
                        yield Completion(
                            sport_key,
                            start_position=-len(arg_text),
                            display=sport_key,
                            display_meta=description,
                        )
            
            # Match names for analizar/analyze
            elif command in ["analizar", "analyze", "analyse"]:
                if self.cli_instance and hasattr(self.cli_instance, 'events') and self.cli_instance.events:
                    seen_matches = set()
                    for event in self.cli_instance.events:
                        match_str = f"{event.home_team} vs {event.away_team}"
                        
                        # Avoid duplicates
                        if match_str in seen_matches:
                            continue
                        
                        # Check if arg_text matches any part
                        if (arg_text.lower() in event.home_team.lower() or 
                            arg_text.lower() in event.away_team.lower() or
                            arg_text.lower() in match_str.lower()):
                            
                            seen_matches.add(match_str)
                            yield Completion(
                                match_str,
                                start_position=-len(arg_text),
                                display=match_str,
                                display_meta=event.commence_time.strftime('%Y-%m-%d %H:%M'),
                            )


class CommandInput:
    """Advanced command input handler with history and completion."""
    
    def __init__(self, cli_instance=None):
        """Initialize command input.
        
        Args:
            cli_instance: Reference to CLI instance for context-aware completion
        """
        self.cli_instance = cli_instance
        self.history = InMemoryHistory()
        self.completer = BetCopilotCompleter(cli_instance)
        
        # Custom style
        self.style = Style.from_dict({
            'prompt': f'{NEON_CYAN}',
            'prompt-arrow': f'bold {NEON_CYAN}',
            'completion-menu': 'bg:#222222 #cccccc',
            'completion-menu.completion': 'bg:#222222 #00ffff',
            'completion-menu.completion.current': f'bg:#00ffff #000000 bold',
            'completion-menu.meta.completion': 'bg:#222222 #999999',
            'completion-menu.meta.completion.current': 'bg:#00ffff #000000',
        })
        
        # Create session with all features
        self.session = PromptSession(
            history=self.history,
            completer=self.completer,
            complete_while_typing=True,
            complete_in_thread=True,
            enable_history_search=True,
            mouse_support=True,
            style=self.style,
        )
    
    def get_prompt_message(self) -> HTML:
        """Generate prompt message with styling."""
        return HTML(f'<prompt-arrow>➜</prompt-arrow> <prompt>bet-copilot</prompt> ')
    
    async def get_command(self, message: Optional[str] = None) -> str:
        """Get command from user with all features enabled.
        
        Args:
            message: Optional custom prompt message
            
        Returns:
            User input command
        """
        if message is None:
            message = self.get_prompt_message()
        
        try:
            # Run prompt in thread to avoid blocking
            command = await self.session.prompt_async(message)
            return command.strip()
        except (EOFError, KeyboardInterrupt):
            # Return empty on Ctrl+C or Ctrl+D
            return ""
    
    def add_to_history(self, command: str):
        """Manually add command to history (if needed)."""
        if command.strip():
            self.history.append_string(command)
    
    def get_history(self) -> List[str]:
        """Get command history."""
        return list(self.history.load_history_strings())
    
    def clear_history(self):
        """Clear command history."""
        self.history = InMemoryHistory()
        self.session.history = self.history


def create_command_input(cli_instance=None) -> CommandInput:
    """Factory function to create CommandInput instance.
    
    Args:
        cli_instance: Reference to CLI instance for context-aware completion
        
    Returns:
        CommandInput instance
    """
    return CommandInput(cli_instance)
