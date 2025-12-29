# DraftKings NFL Betting CLI

A CLI tool and web dashboard for fetching live NFL betting lines from DraftKings Sportsbook. Includes a mock betting system for tracking wagers and simulating game outcomes.

## Features

- **Live NFL Lines** - Fetch real-time spreads, totals, and moneylines from DraftKings
- **Web Dashboard** - React-based UI with real-time updates via WebSocket
- **Mock Betting System** - Place bets with virtual bankroll ($10,000 starting balance)
- **Bet History** - Track all bets with win/loss statistics
- **Game Settlement** - Simulate game endings with random NFL scores

## Installation

```bash
# Create virtual environment and install
uv venv && source .venv/bin/activate
uv pip install -e .

# Install browser for web scraping
dk install-browser
```

## CLI Usage

```bash
dk fetch              # Fetch current lines (one-time)
dk fetch --watch      # Watch mode (continuous updates)
dk select             # Interactive game selection
dk history            # View historical line data
dk serve              # Start API server with web dashboard
```

## Web Dashboard

Start the server to access the web dashboard:

```bash
dk serve
```

Then open http://localhost:8000 in your browser.

### Dashboard Features

- **Games View** - All NFL games with live betting lines
- **Bet Placement** - Click any odds button to open the bet slip
- **Bankroll** - Displayed in header, starts at $10,000
- **Bet History** - View all bets at `/history` with filtering and stats
- **Game Settlement** - "Simulate End" button generates random scores and settles bets

### Betting Rules

- **Minimum bet**: $5.00
- **Maximum bet**: $500.00
- **Bet types**: Spread, Total (Over/Under), Moneyline
- **Payout**: American odds (e.g., -110 pays $90.91 on $100, +150 pays $150 on $100)

## Development

### Backend (Python/FastAPI)

```bash
# Run development server
dk serve --reload
```

### Frontend (React/TypeScript)

```bash
cd web
npm install
npm run dev      # Development server (port 5173)
npm run build    # Production build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/games` | Current NFL games with lines |
| GET | `/api/games/{id}` | Single game details |
| GET | `/api/bankroll` | Current bankroll balance |
| POST | `/api/bets` | Place a new bet |
| GET | `/api/bets` | Bet history (supports `?status=pending\|won\|lost`) |
| POST | `/api/games/{id}/settle` | Simulate game end and settle bets |

## Project Structure

```
draftkings-cli/
├── src/dk_cli/           # Python CLI and API
│   ├── cli.py            # CLI commands
│   ├── server/           # FastAPI server
│   ├── database.py       # SQLite persistence
│   ├── betting.py        # Betting logic
│   └── models.py         # Data models
├── web/                  # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── context/      # React context (betting state)
│   │   ├── pages/        # Page components
│   │   ├── api/          # API client
│   │   └── types/        # TypeScript types
│   └── dist/             # Production build
└── data/                 # SQLite database
```

## License

MIT
