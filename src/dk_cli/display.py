import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .models import NFLGame


console = Console()


def format_odds(odds: int | None) -> str:
    """Format odds with +/- prefix."""
    if odds is None:
        return "-"
    return f"+{odds}" if odds > 0 else str(odds)


def format_line(line: float | None) -> str:
    """Format spread/total line."""
    if line is None:
        return "-"
    return f"+{line}" if line > 0 else str(line)


def odds_color(odds: int | None) -> str:
    """Return color based on odds value."""
    if odds is None:
        return "dim"
    if odds > 0:
        return "green"  # Underdog
    if odds < -150:
        return "red"  # Heavy favorite
    return "yellow"  # Moderate favorite


def display_games_table(games: List[NFLGame]) -> None:
    """Display games in a rich table format."""
    if not games:
        console.print("[yellow]No games found.[/yellow]")
        return

    table = Table(
        title="NFL Betting Lines",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
    )

    table.add_column("Game", style="bold", min_width=20)
    table.add_column("Status", justify="center", min_width=10)
    table.add_column("Spread", justify="center", min_width=15)
    table.add_column("Total", justify="center", min_width=15)
    table.add_column("Money Line", justify="center", min_width=15)

    for game in games:
        # Format spread (show both teams)
        spread = game.betting_lines.spread
        spread_text = Text()
        if spread.away_line is not None or spread.home_line is not None:
            # Away team spread
            spread_text.append(f"{game.away_team.abbreviation} ", style="dim")
            spread_text.append(f"{format_line(spread.away_line)}", style="bold")
            spread_text.append(f" ({format_odds(spread.away_odds)})\n", style=odds_color(spread.away_odds))
            # Home team spread
            spread_text.append(f"{game.home_team.abbreviation} ", style="dim")
            spread_text.append(f"{format_line(spread.home_line)}", style="bold")
            spread_text.append(f" ({format_odds(spread.home_odds)})", style=odds_color(spread.home_odds))
        else:
            spread_text.append("-", style="dim")

        # Format total (show over and under)
        total = game.betting_lines.total
        total_text = Text()
        if total.over_line is not None or total.under_line is not None:
            # Over
            total_text.append(f"O {total.over_line} ", style="bold")
            total_text.append(f"({format_odds(total.over_odds)})\n", style=odds_color(total.over_odds))
            # Under
            total_text.append(f"U {total.under_line} ", style="bold")
            total_text.append(f"({format_odds(total.under_odds)})", style=odds_color(total.under_odds))
        else:
            total_text.append("-", style="dim")

        # Format moneyline
        ml = game.betting_lines.money_line
        ml_text = Text()
        if ml.away is not None or ml.home is not None:
            ml_text.append(f"{game.away_team.abbreviation} ", style="dim")
            ml_text.append(f"{format_odds(ml.away)}", style=odds_color(ml.away))
            ml_text.append(" | ", style="dim")
            ml_text.append(f"{game.home_team.abbreviation} ", style="dim")
            ml_text.append(f"{format_odds(ml.home)}", style=odds_color(ml.home))
        else:
            ml_text.append("-", style="dim")

        # Status styling
        status_style = {
            "live": "bold red",
            "final": "dim",
            "upcoming": "green",
        }.get(game.status, "white")

        table.add_row(
            game.matchup,
            Text(game.status.upper(), style=status_style),
            spread_text,
            total_text,
            ml_text,
        )

    console.print(table)


def display_game_detail(game: NFLGame) -> None:
    """Display detailed view of a single game."""
    content = Text()

    # Header
    content.append(f"\n{game.matchup}\n", style="bold cyan")
    content.append(f"Status: {game.status.upper()}\n", style="dim")
    content.append(f"Start: {game.start_time.strftime('%Y-%m-%d %H:%M')}\n\n", style="dim")

    # Spread
    content.append("SPREAD\n", style="bold yellow")
    spread = game.betting_lines.spread
    content.append(f"  {game.away_team.abbreviation}: ", style="white")
    content.append(f"{format_line(spread.away_line)} ({format_odds(spread.away_odds)})\n",
                   style=odds_color(spread.away_odds))
    content.append(f"  {game.home_team.abbreviation}: ", style="white")
    content.append(f"{format_line(spread.home_line)} ({format_odds(spread.home_odds)})\n\n",
                   style=odds_color(spread.home_odds))

    # Total
    content.append("TOTAL\n", style="bold yellow")
    total = game.betting_lines.total
    content.append(f"  Over {total.over_line}: ", style="white")
    content.append(f"{format_odds(total.over_odds)}\n", style=odds_color(total.over_odds))
    content.append(f"  Under {total.under_line}: ", style="white")
    content.append(f"{format_odds(total.under_odds)}\n\n", style=odds_color(total.under_odds))

    # Moneyline
    content.append("MONEYLINE\n", style="bold yellow")
    ml = game.betting_lines.money_line
    content.append(f"  {game.away_team.abbreviation}: ", style="white")
    content.append(f"{format_odds(ml.away)}\n", style=odds_color(ml.away))
    content.append(f"  {game.home_team.abbreviation}: ", style="white")
    content.append(f"{format_odds(ml.home)}\n", style=odds_color(ml.home))

    panel = Panel(content, title=f"[bold]{game.matchup}[/bold]", border_style="blue")
    console.print(panel)


def display_games_json(games: List[NFLGame]) -> None:
    """Display games as JSON."""
    data = [game.to_dict() for game in games]
    console.print_json(json.dumps(data, indent=2))


def display_games(games: List[NFLGame], format: str = "table") -> None:
    """Display games in the specified format."""
    if format == "json":
        display_games_json(games)
    else:
        display_games_table(games)
