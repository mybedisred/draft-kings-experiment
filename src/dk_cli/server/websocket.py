"""WebSocket endpoint for real-time updates."""

import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .state import app_state

logger = logging.getLogger("dk_cli.server")
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates.

    Message types sent to clients:
    - connection_established: Sent immediately on connect with current state
    - games_update: Sent when new data is fetched
    - error: Sent when a fetch error occurs
    - pong: Response to client ping

    Message types accepted from clients:
    - ping: Client heartbeat, server responds with pong
    """
    await app_state.connect_websocket(websocket)
    logger.info(
        f"WebSocket connected. Total clients: {len(app_state.websocket_connections)}"
    )

    try:
        # Send current state on connection
        await websocket.send_json(
            {
                "type": "connection_established",
                "timestamp": datetime.now().isoformat(),
                "game_count": len(app_state.games),
                "games": app_state.get_games_dict() if app_state.games else [],
                "last_updated": (
                    app_state.last_updated.isoformat()
                    if app_state.last_updated
                    else None
                ),
            }
        )

        # Listen for client messages
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        app_state.disconnect_websocket(websocket)
        logger.info(
            f"WebSocket removed. Total clients: {len(app_state.websocket_connections)}"
        )
