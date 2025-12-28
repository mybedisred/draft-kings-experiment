"""REST API endpoints for DraftKings data."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import Database
from .state import app_state

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
