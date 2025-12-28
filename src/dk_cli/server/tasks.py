"""Background polling task for fetching DraftKings data."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from ..client import DraftKingsClient
from ..config import ServerConfig
from ..database import Database
from .state import app_state

logger = logging.getLogger("dk_cli.server")


class PollingTask:
    """Background task that polls DraftKings for updated data."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.db: Optional[Database] = None
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start the background polling task."""
        if self.config.save_to_db:
            self.db = Database()

        self._stop_event.clear()
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"Started polling task (interval: {self.config.poll_interval}s)")

    async def stop(self) -> None:
        """Stop the background polling task."""
        self._stop_event.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped polling task")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        # Initial fetch immediately
        await self._fetch_and_broadcast()

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=self.config.poll_interval
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                # Timeout = time to poll again
                await self._fetch_and_broadcast()

    async def _fetch_and_broadcast(self) -> None:
        """Fetch data and broadcast to WebSocket clients."""
        app_state.is_fetching = True

        try:
            logger.info("Fetching NFL games from DraftKings...")

            async with DraftKingsClient(headless=self.config.headless) as client:
                games = await client.fetch_nfl_games()

            if games:
                await app_state.update_games(games)

                if self.db:
                    saved = self.db.save_games(games)
                    logger.info(f"Saved {saved} games to database")

                await app_state.broadcast(
                    {
                        "type": "games_update",
                        "timestamp": datetime.now().isoformat(),
                        "game_count": len(games),
                        "games": app_state.get_games_dict(),
                    }
                )

                logger.info(
                    f"Fetched {len(games)} games, broadcast to "
                    f"{len(app_state.websocket_connections)} clients"
                )
            else:
                logger.warning("No games fetched")

        except Exception as e:
            error_msg = str(e)
            await app_state.set_error(error_msg)
            logger.error(f"Fetch error: {error_msg}")

            await app_state.broadcast(
                {
                    "type": "error",
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg,
                }
            )

        finally:
            app_state.is_fetching = False

    async def trigger_fetch(self) -> None:
        """Manually trigger a fetch (for API endpoint)."""
        await self._fetch_and_broadcast()
