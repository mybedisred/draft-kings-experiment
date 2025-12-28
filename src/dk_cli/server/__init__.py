"""FastAPI server for DraftKings NFL betting data."""

from .app import create_app
from .state import app_state

__all__ = ["create_app", "app_state"]
