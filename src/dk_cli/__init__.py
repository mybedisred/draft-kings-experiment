"""DraftKings NFL Betting Lines CLI"""

__version__ = "0.1.0"

from .models import NFLGame, Team, BettingLines, MoneyLine, Spread, Total
from .client import DraftKingsClient, fetch_nfl_games
from .database import Database
from .display import display_games, display_game_detail

__all__ = [
    "NFLGame",
    "Team",
    "BettingLines",
    "MoneyLine",
    "Spread",
    "Total",
    "DraftKingsClient",
    "fetch_nfl_games",
    "Database",
    "display_games",
    "display_game_detail",
]
