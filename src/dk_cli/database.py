import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import (
    NFLGame, Team, BettingLines, MoneyLine, Spread, Total
)


DEFAULT_DB_PATH = Path.home() / ".dk_cli" / "history.db"


class Database:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    home_team_name TEXT NOT NULL,
                    home_team_abbr TEXT NOT NULL,
                    away_team_name TEXT NOT NULL,
                    away_team_abbr TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    UNIQUE(game_id, fetched_at)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS betting_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    ml_home INTEGER,
                    ml_away INTEGER,
                    spread_home_line REAL,
                    spread_home_odds INTEGER,
                    spread_away_line REAL,
                    spread_away_odds INTEGER,
                    total_over_line REAL,
                    total_over_odds INTEGER,
                    total_under_line REAL,
                    total_under_odds INTEGER,
                    UNIQUE(game_id, fetched_at)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_game_id ON games(game_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_fetched_at ON games(fetched_at)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_betting_lines_game_id ON betting_lines(game_id)
            """)

    def save_games(self, games: List[NFLGame]) -> int:
        """Save games to database. Returns number of games saved."""
        saved = 0
        with sqlite3.connect(self.db_path) as conn:
            for game in games:
                try:
                    fetched_at = game.fetched_at.isoformat()

                    conn.execute("""
                        INSERT OR REPLACE INTO games
                        (game_id, home_team_name, home_team_abbr, away_team_name, away_team_abbr,
                         start_time, status, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        game.game_id,
                        game.home_team.name,
                        game.home_team.abbreviation,
                        game.away_team.name,
                        game.away_team.abbreviation,
                        game.start_time.isoformat(),
                        game.status,
                        fetched_at,
                    ))

                    bl = game.betting_lines
                    conn.execute("""
                        INSERT OR REPLACE INTO betting_lines
                        (game_id, fetched_at, ml_home, ml_away,
                         spread_home_line, spread_home_odds, spread_away_line, spread_away_odds,
                         total_over_line, total_over_odds, total_under_line, total_under_odds)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        game.game_id,
                        fetched_at,
                        bl.money_line.home,
                        bl.money_line.away,
                        bl.spread.home_line,
                        bl.spread.home_odds,
                        bl.spread.away_line,
                        bl.spread.away_odds,
                        bl.total.over_line,
                        bl.total.over_odds,
                        bl.total.under_line,
                        bl.total.under_odds,
                    ))

                    saved += 1
                except sqlite3.Error as e:
                    print(f"Warning: Failed to save game {game.game_id}: {e}")

        return saved

    def get_games(
        self,
        game_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[NFLGame]:
        """Retrieve games from database."""
        query = """
            SELECT g.game_id, g.home_team_name, g.home_team_abbr,
                   g.away_team_name, g.away_team_abbr, g.start_time, g.status, g.fetched_at,
                   b.ml_home, b.ml_away,
                   b.spread_home_line, b.spread_home_odds, b.spread_away_line, b.spread_away_odds,
                   b.total_over_line, b.total_over_odds, b.total_under_line, b.total_under_odds
            FROM games g
            LEFT JOIN betting_lines b ON g.game_id = b.game_id AND g.fetched_at = b.fetched_at
            WHERE 1=1
        """
        params = []

        if game_id:
            query += " AND g.game_id = ?"
            params.append(game_id)

        if since:
            query += " AND g.fetched_at >= ?"
            params.append(since.isoformat())

        query += " ORDER BY g.fetched_at DESC LIMIT ?"
        params.append(limit)

        games = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor:
                game = NFLGame(
                    game_id=row[0],
                    home_team=Team(name=row[1], abbreviation=row[2]),
                    away_team=Team(name=row[3], abbreviation=row[4]),
                    start_time=datetime.fromisoformat(row[5]),
                    status=row[6],
                    fetched_at=datetime.fromisoformat(row[7]),
                    betting_lines=BettingLines(
                        money_line=MoneyLine(home=row[8], away=row[9]),
                        spread=Spread(
                            home_line=row[10], home_odds=row[11],
                            away_line=row[12], away_odds=row[13]
                        ),
                        total=Total(
                            over_line=row[14], over_odds=row[15],
                            under_line=row[16], under_odds=row[17]
                        ),
                    ),
                )
                games.append(game)

        return games

    def get_line_history(self, game_id: str) -> List[dict]:
        """Get historical line movements for a game."""
        query = """
            SELECT fetched_at, ml_home, ml_away,
                   spread_home_line, spread_home_odds, spread_away_line, spread_away_odds,
                   total_over_line, total_over_odds
            FROM betting_lines
            WHERE game_id = ?
            ORDER BY fetched_at ASC
        """

        history = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, (game_id,))
            for row in cursor:
                history.append({
                    "fetched_at": row[0],
                    "money_line": {"home": row[1], "away": row[2]},
                    "spread": {
                        "home_line": row[3], "home_odds": row[4],
                        "away_line": row[5], "away_odds": row[6]
                    },
                    "total": {"over_line": row[7], "over_odds": row[8]},
                })

        return history

    def get_unique_games(self) -> List[str]:
        """Get list of unique game IDs in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT game_id FROM games ORDER BY game_id")
            return [row[0] for row in cursor]
