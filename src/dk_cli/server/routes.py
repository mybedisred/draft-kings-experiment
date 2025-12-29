"""REST API endpoints for DraftKings data."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import Database
from ..models import Bet
from ..betting import (
    calculate_payout,
    determine_bet_result,
    generate_mock_scores,
    validate_bet_placement,
)
from .state import app_state


# ==================== REQUEST MODELS ====================

class PlaceBetRequest(BaseModel):
    game_id: str
    bet_type: str  # 'spread_home', 'spread_away', 'total_over', 'total_under', 'ml_home', 'ml_away'
    stake: float = Field(ge=5.0, le=500.0)
    odds: int
    line_value: Optional[float] = None
    selection: str
    home_team_abbr: str
    away_team_abbr: str

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "last_updated": (
            app_state.last_updated.isoformat() if app_state.last_updated else None
        ),
        "is_fetching": app_state.is_fetching,
        "game_count": len(app_state.games),
        "websocket_clients": len(app_state.websocket_connections),
        "fetch_count": app_state.fetch_count,
        "last_error": app_state.last_error,
    }


@router.get("/games")
async def get_games():
    """Get current NFL games with betting lines."""
    if not app_state.games:
        return {
            "games": [],
            "last_updated": None,
            "message": "No games available. Data may still be loading.",
        }

    return {
        "games": app_state.get_games_dict(),
        "last_updated": (
            app_state.last_updated.isoformat() if app_state.last_updated else None
        ),
        "count": len(app_state.games),
    }


@router.get("/games/{game_id}")
async def get_game(game_id: str):
    """Get a specific game by ID."""
    for game in app_state.games:
        if game.game_id == game_id:
            return {"game": game.to_dict()}

    raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")


@router.get("/games/{game_id}/history")
async def get_game_history(game_id: str):
    """Get historical line movements for a game."""
    db = Database()
    history = db.get_line_history(game_id)

    if not history:
        raise HTTPException(status_code=404, detail=f"No history for game: {game_id}")

    return {"game_id": game_id, "history": history, "count": len(history)}


@router.get("/history")
async def get_historical_games(
    since: Optional[str] = Query(None, description="ISO datetime to filter from"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
):
    """Get historical games from database."""
    db = Database()

    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")

    games = db.get_games(since=since_dt, limit=limit)

    return {"games": [g.to_dict() for g in games], "count": len(games)}


@router.get("/game-ids")
async def get_game_ids():
    """Get list of all game IDs in database."""
    db = Database()
    game_ids = db.get_unique_games()

    return {"game_ids": game_ids, "count": len(game_ids)}


# ==================== BETTING ENDPOINTS ====================

@router.get("/bankroll")
async def get_bankroll():
    """Get current bankroll balance."""
    db = Database()
    bankroll = db.get_bankroll()
    return bankroll.to_dict()


@router.post("/bets")
async def place_bet(request: PlaceBetRequest):
    """Place a new bet."""
    db = Database()

    # Validate bet
    bankroll = db.get_bankroll()
    is_valid, error = validate_bet_placement(request.stake, bankroll.balance)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Verify game exists
    game_exists = any(g.game_id == request.game_id for g in app_state.games)
    if not game_exists:
        raise HTTPException(status_code=404, detail=f"Game not found: {request.game_id}")

    # Calculate potential payout
    potential_payout = calculate_payout(request.stake, request.odds)

    # Create and save bet
    bet = Bet(
        game_id=request.game_id,
        bet_type=request.bet_type,
        selection=request.selection,
        stake=request.stake,
        odds=request.odds,
        potential_payout=potential_payout,
        home_team_abbr=request.home_team_abbr,
        away_team_abbr=request.away_team_abbr,
        line_value=request.line_value,
    )

    saved_bet = db.place_bet(bet)
    updated_bankroll = db.get_bankroll()

    return {
        "bet": saved_bet.to_dict(),
        "bankroll": updated_bankroll.to_dict(),
    }


@router.get("/bets")
async def get_bets(
    status: Optional[str] = Query(None, description="Filter by status: pending, won, lost, push"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Get bet history with optional filters."""
    db = Database()

    bets = db.get_bets(status=status, limit=limit, offset=offset)
    total_count = db.get_bets_count(status=status)

    return {
        "bets": [b.to_dict() for b in bets],
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/bets/{bet_id}")
async def get_bet(bet_id: int):
    """Get a specific bet by ID."""
    db = Database()
    bet = db.get_bet(bet_id)

    if not bet:
        raise HTTPException(status_code=404, detail=f"Bet not found: {bet_id}")

    return {"bet": bet.to_dict()}


@router.post("/games/{game_id}/settle")
async def settle_game(game_id: str):
    """Simulate game end with random scores and settle all pending bets."""
    db = Database()

    # Get pending bets for this game
    pending_bets = db.get_pending_bets_for_game(game_id)

    if not pending_bets:
        raise HTTPException(
            status_code=400,
            detail=f"No pending bets for game: {game_id}"
        )

    # Generate mock scores
    home_score, away_score = generate_mock_scores()

    # Settle each bet
    settled_bets = []
    for bet in pending_bets:
        status, result_amount = determine_bet_result(
            bet_type=bet.bet_type,
            line_value=bet.line_value,
            odds=bet.odds,
            stake=bet.stake,
            home_score=home_score,
            away_score=away_score,
        )

        settled_bet = db.settle_bet(
            bet_id=bet.id,
            status=status,
            result_amount=result_amount,
            home_score=home_score,
            away_score=away_score,
        )

        if settled_bet:
            settled_bets.append(settled_bet.to_dict())

    # Get updated bankroll
    updated_bankroll = db.get_bankroll()

    return {
        "game_id": game_id,
        "final_score": {"home": home_score, "away": away_score},
        "settled_bets": settled_bets,
        "bankroll": updated_bankroll.to_dict(),
    }
