# DraftKings NFL Betting CLI

Fetch live NFL betting lines from DraftKings Sportsbook.

## Installation

```bash
uv venv && source .venv/bin/activate
uv pip install -e .
dk install-browser
```

## Usage

```bash
dk fetch              # Fetch current lines
dk fetch --watch      # Watch mode
dk select             # Interactive selection
dk history            # View historical data
```

See [PLAN.md](PLAN.md) for full documentation.
