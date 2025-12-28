"""Shared application state for the server."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set

from fastapi import WebSocket

from ..models import NFLGame


@dataclass
class AppState:
    """Shared application state for the server.

    This singleton manages:
    - Cached games data from latest fetch
    - WebSocket connections for broadcasting updates
    - Fetch status for health checks
    """

    games: List[NFLGame] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    is_fetching: bool = False
    last_error: Optional[str] = None
    fetch_count: int = 0
    websocket_connections: Set[WebSocket] = field(default_factory=set)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def update_games(self, games: List[NFLGame]) -> None:
        """Update cached games with thread safety."""
        async with self._lock:
            self.games = games
            self.last_updated = datetime.now()
            self.fetch_count += 1
            self.last_error = None

    async def set_error(self, error: str) -> None:
        """Record a fetch error."""
        async with self._lock:
            self.last_error = error

    def get_games_dict(self) -> List[dict]:
        """Get games as list of dicts for JSON serialization."""
        return [game.to_dict() for game in self.games]

    async def connect_websocket(self, websocket: WebSocket) -> None:
        """Register a new WebSocket connection."""
        await websocket.accept()
        self.websocket_connections.add(websocket)

    def disconnect_websocket(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.websocket_connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected WebSocket clients."""
        if not self.websocket_connections:
            return

        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            self.websocket_connections.discard(ws)


# Global singleton state instance
app_state = AppState()
