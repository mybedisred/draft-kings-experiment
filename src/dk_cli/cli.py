import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click
import questionary
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from .client import DraftKingsClient, fetch_nfl_games
from .database import Database
from .display import display_games, display_game_detail, display_games_table
from .models import NFLGame


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """DraftKings NFL Betting Lines CLI

    Fetch live NFL betting lines including money lines, spreads, and totals.
    """
    pass


@main.command()
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format (table or json)"
)
@click.option(
    "--watch", "-w",
    is_flag=True,
    help="Continuously refresh data"
)
@click.option(
    "--interval", "-i",
    type=int,
    default=30,
    help="Refresh interval in seconds (default: 30)"
)
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save fetched data to database"
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: headless)"
)
def fetch(format: str, watch: bool, interval: int, no_save: bool, headless: bool):
    """Fetch current NFL betting lines from DraftKings."""
    db = None if no_save else Database()

    async def do_fetch() -> List[NFLGame]:
        try:
            async with DraftKingsClient(headless=headless) as client:
                games = await client.fetch_nfl_games()
                if db and games:
                    saved = db.save_games(games)
                    console.print(f"[dim]Saved {saved} games to database[/dim]")
                return games
        except Exception as e:
            console.print(f"[red]Error fetching data: {e}[/red]")
            return []

    if watch:
        console.print(f"[cyan]Watching NFL lines (refresh every {interval}s). Press Ctrl+C to stop.[/cyan]\n")
        try:
            while True:
                console.clear()
                console.print(f"[dim]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")
                games = asyncio.run(do_fetch())
                display_games(games, format)
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped watching.[/yellow]")
    else:
        games = asyncio.run(do_fetch())
        if games:
            display_games(games, format)
        else:
            console.print("[yellow]No games found. This could mean:[/yellow]")
            console.print("  - No NFL games scheduled")
            console.print("  - DraftKings page structure changed")
            console.print("  - Network/geo-blocking issue")


@main.command()
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode"
)
def select(format: str, headless: bool):
    """Interactively select games to view."""
    console.print("[cyan]Fetching games...[/cyan]")

    async def do_fetch() -> List[NFLGame]:
        async with DraftKingsClient(headless=headless) as client:
            return await client.fetch_nfl_games()

    games = asyncio.run(do_fetch())

    if not games:
        console.print("[yellow]No games found.[/yellow]")
        return

    # Create choices for interactive selection
    choices = [
        questionary.Choice(
            title=f"{g.matchup} ({g.status})",
            value=g
        )
        for g in games
    ]

    selected = questionary.checkbox(
        "Select games to view:",
        choices=choices,
    ).ask()

    if selected:
        for game in selected:
            display_game_detail(game)
    else:
        console.print("[yellow]No games selected.[/yellow]")


@main.command()
@click.option(
    "--game-id", "-g",
    help="Filter by game ID"
)
@click.option(
    "--since", "-s",
    type=click.DateTime(),
    help="Show records since date (YYYY-MM-DD)"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=50,
    help="Maximum records to show (default: 50)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def history(game_id: Optional[str], since: Optional[datetime], limit: int, format: str):
    """View historical betting line data."""
    db = Database()

    if game_id:
        # Show line movement for specific game
        history = db.get_line_history(game_id)
        if not history:
            console.print(f"[yellow]No history found for game: {game_id}[/yellow]")
            return

        console.print(f"[cyan]Line history for {game_id}:[/cyan]\n")
        for entry in history:
            console.print(f"  {entry['fetched_at']}")
            console.print(f"    ML: {entry['money_line']}")
            console.print(f"    Spread: {entry['spread']}")
            console.print(f"    Total: {entry['total']}\n")
    else:
        # Show all historical games
        games = db.get_games(since=since, limit=limit)
        if not games:
            console.print("[yellow]No historical data found.[/yellow]")
            console.print("Run 'dk fetch' to collect data.")
            return

        display_games(games, format)


@main.command()
def games():
    """List all game IDs in database."""
    db = Database()
    game_ids = db.get_unique_games()

    if not game_ids:
        console.print("[yellow]No games in database.[/yellow]")
        console.print("Run 'dk fetch' to collect data.")
        return

    console.print("[cyan]Games in database:[/cyan]\n")
    for game_id in game_ids:
        console.print(f"  {game_id}")


@main.command()
def install_browser():
    """Install Playwright browser (required before first use)."""
    import subprocess
    console.print("[cyan]Installing Playwright Chromium browser...[/cyan]")
    result = subprocess.run(
        ["playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        console.print("[green]Browser installed successfully![/green]")
    else:
        console.print(f"[red]Installation failed: {result.stderr}[/red]")


@main.command()
@click.option(
    "--host", "-h",
    type=str,
    default=None,
    help="Host to bind to (default: 127.0.0.1)"
)
@click.option(
    "--port", "-p",
    type=int,
    default=None,
    help="Port to bind to (default: 8000)"
)
@click.option(
    "--interval", "-i",
    type=int,
    default=None,
    help="Polling interval in seconds (default: 60)"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to config file (TOML)"
)
@click.option(
    "--headless/--no-headless",
    default=None,
    help="Run browser in headless mode"
)
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save fetched data to database"
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development"
)
def serve(
    host: Optional[str],
    port: Optional[int],
    interval: Optional[int],
    config: Optional[Path],
    headless: Optional[bool],
    no_save: bool,
    reload: bool
):
    """Start the API server with WebSocket support.

    The server provides:

    \b
    - REST API at /api/games, /api/health, etc.
    - WebSocket at /ws for real-time updates
    - Auto-documentation at /docs

    Configuration priority: CLI args > config file > defaults
    """
    import uvicorn
    from .config import load_config
    from .server import create_app

    # Load base config from file
    cfg = load_config(config)

    # Override with CLI arguments
    if host is not None:
        cfg.host = host
    if port is not None:
        cfg.port = port
    if interval is not None:
        cfg.poll_interval = interval
    if headless is not None:
        cfg.headless = headless
    if no_save:
        cfg.save_to_db = False

    console.print("[cyan]Starting DraftKings API Server[/cyan]")
    console.print(f"  Host: {cfg.host}")
    console.print(f"  Port: {cfg.port}")
    console.print(f"  Poll interval: {cfg.poll_interval}s")
    console.print(f"  Headless: {cfg.headless}")
    console.print(f"  Save to DB: {cfg.save_to_db}")
    console.print()
    console.print(f"[green]API docs: http://{cfg.host}:{cfg.port}/docs[/green]")
    console.print(f"[green]WebSocket: ws://{cfg.host}:{cfg.port}/ws[/green]")
    console.print()

    # Create app with config
    app = create_app(cfg)

    # Run with uvicorn
    uvicorn.run(
        app,
        host=cfg.host,
        port=cfg.port,
        reload=reload,
        log_level=cfg.log_level
    )


if __name__ == "__main__":
    main()
