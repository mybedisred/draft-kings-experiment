"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import ServerConfig
from .routes import router as api_router
from .tasks import PollingTask
from .websocket import router as ws_router

# Module-level polling task reference
_polling_task: Optional[PollingTask] = None


def create_app(config: ServerConfig) -> FastAPI:
    """Create and configure the FastAPI application."""

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage application lifecycle - start/stop background tasks."""
        global _polling_task

        # Startup
        _polling_task = PollingTask(config)
        await _polling_task.start()

        yield

        # Shutdown
        if _polling_task:
            await _polling_task.stop()

    app = FastAPI(
        title="DraftKings NFL API",
        description="Real-time NFL betting lines from DraftKings",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix="/api", tags=["games"])
    app.include_router(ws_router, tags=["websocket"])

    @app.get("/")
    async def root():
        return {
            "message": "DraftKings NFL API",
            "docs": "/docs",
            "websocket": "/ws",
            "endpoints": {
                "games": "/api/games",
                "health": "/api/health",
                "history": "/api/history",
            },
        }

    @app.post("/api/refresh")
    async def trigger_refresh():
        """Manually trigger a data refresh."""
        if _polling_task:
            await _polling_task.trigger_fetch()
            return {"status": "refresh_triggered"}
        return {"status": "error", "message": "Polling task not running"}

    return app
