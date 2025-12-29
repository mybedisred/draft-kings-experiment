from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class Team:
    name: str
    abbreviation: str


@dataclass
class MoneyLine:
    home: Optional[int] = None
    away: Optional[int] = None

    def to_dict(self) -> dict:
        return {"home": self.home, "away": self.away}


@dataclass
class Spread:
    home_line: Optional[float] = None
    home_odds: Optional[int] = None
    away_line: Optional[float] = None
    away_odds: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "home": {"line": self.home_line, "odds": self.home_odds},
            "away": {"line": self.away_line, "odds": self.away_odds},
        }


@dataclass
class Total:
    over_line: Optional[float] = None
    over_odds: Optional[int] = None
    under_line: Optional[float] = None
    under_odds: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "over": {"line": self.over_line, "odds": self.over_odds},
            "under": {"line": self.under_line, "odds": self.under_odds},
        }


@dataclass
class BettingLines:
    money_line: MoneyLine = field(default_factory=MoneyLine)
    spread: Spread = field(default_factory=Spread)
    total: Total = field(default_factory=Total)

    def to_dict(self) -> dict:
        return {
            "money_line": self.money_line.to_dict(),
            "spread": self.spread.to_dict(),
            "total": self.total.to_dict(),
        }


@dataclass
class NFLGame:
    game_id: str
    home_team: Team
    away_team: Team
    start_time: datetime
    status: str  # "upcoming", "live", "final"
    betting_lines: BettingLines = field(default_factory=BettingLines)
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "home_team": {"name": self.home_team.name, "abbreviation": self.home_team.abbreviation},
            "away_team": {"name": self.away_team.name, "abbreviation": self.away_team.abbreviation},
            "start_time": self.start_time.isoformat(),
            "status": self.status,
            "betting_lines": self.betting_lines.to_dict(),
            "fetched_at": self.fetched_at.isoformat(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @property
    def matchup(self) -> str:
        return f"{self.away_team.abbreviation} @ {self.home_team.abbreviation}"


@dataclass
class Bankroll:
    balance: float
    updated_at: datetime

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Bet:
    game_id: str
    bet_type: str  # 'spread_home', 'spread_away', 'total_over', 'total_under', 'ml_home', 'ml_away'
    selection: str  # Human-readable: "KC Chiefs -3.5", "Over 45.5", etc.
    stake: float
    odds: int  # American odds at time of bet
    potential_payout: float
    home_team_abbr: str
    away_team_abbr: str
    line_value: Optional[float] = None  # The spread/total line (null for moneyline)
    id: Optional[int] = None
    status: str = "pending"  # 'pending', 'won', 'lost', 'push'
    result_amount: Optional[float] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    placed_at: datetime = field(default_factory=datetime.now)
    settled_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "game_id": self.game_id,
            "bet_type": self.bet_type,
            "selection": self.selection,
            "stake": self.stake,
            "odds": self.odds,
            "potential_payout": self.potential_payout,
            "status": self.status,
            "result_amount": self.result_amount,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "placed_at": self.placed_at.isoformat(),
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
            "home_team_abbr": self.home_team_abbr,
            "away_team_abbr": self.away_team_abbr,
            "line_value": self.line_value,
        }
