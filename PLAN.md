# DraftKings NFL Betting CLI

## Overview
Python CLI tool for fetching live NFL betting lines (money lines, spreads, totals) from DraftKings Sportsbook using Playwright headless browser.

## Features
- Fetch live NFL betting lines
- Interactive game selection
- Watch mode with configurable refresh interval
- Table and JSON output formats
- SQLite database for historical data storage
- Line movement history tracking

## Installation

```bash
cd draftkings-cli
pip install -e .
dk install-browser  # Install Playwright Chromium
```

## Usage

```bash
# Fetch current lines (table format)
dk fetch

# Fetch in JSON format
dk fetch --format json

# Watch mode (refresh every 30 seconds)
dk fetch --watch

# Custom refresh interval (60 seconds)
dk fetch --watch --interval 60

# Interactive game selection
dk select

# View historical data
dk history

# View line movement for specific game
dk history --game-id "NYG_DAL_20241228"

# List all games in database
dk games
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `dk fetch` | Fetch current NFL betting lines |
| `dk select` | Interactively select games to view |
| `dk history` | View historical betting line data |
| `dk games` | List all game IDs in database |
| `dk install-browser` | Install Playwright browser |

## Flags

### `dk fetch`
- `--format, -f`: Output format (`table` or `json`)
- `--watch, -w`: Continuously refresh data
- `--interval, -i`: Refresh interval in seconds (default: 30)
- `--no-save`: Don't save to database
- `--headless/--no-headless`: Browser visibility

### `dk history`
- `--game-id, -g`: Filter by game ID
- `--since, -s`: Show records since date
- `--limit, -l`: Maximum records (default: 50)
- `--format, -f`: Output format

## Implementation Status

- [x] Project structure setup
- [x] Data models (Team, BettingLines, NFLGame)
- [x] Playwright-based DraftKings scraper
- [x] Rich table display formatter
- [x] JSON output formatter
- [x] SQLite database layer
- [x] CLI with click
- [x] Watch mode with interval flag
- [x] Interactive game selection
- [x] Historical data storage/retrieval

## Technical Notes

- Uses Playwright headless browser to bypass API restrictions
- DraftKings Sportsbook data loads dynamically via JavaScript
- NFL eventGroupId: 88808
- Data stored in `~/.dk_cli/history.db`

## Dependencies

- click (CLI framework)
- playwright (headless browser)
- rich (terminal formatting)
- questionary (interactive prompts)
