"""Configuration management for DraftKings CLI server."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class ServerConfig:
    """Server configuration with sensible defaults."""

    host: str = "127.0.0.1"
    port: int = 8000
    poll_interval: int = 60
    headless: bool = True
    save_to_db: bool = True
    log_level: str = "info"


DEFAULT_CONFIG_PATHS = [
    Path.cwd() / "config.toml",
    Path.cwd() / "dk_cli.toml",
    Path.home() / ".dk_cli" / "config.toml",
]


def load_config(config_path: Optional[Path] = None) -> ServerConfig:
    """Load configuration from TOML file, with defaults.

    Args:
        config_path: Explicit path to config file, or None to search defaults.

    Returns:
        ServerConfig with values from file (if found) or defaults.
    """
    config = ServerConfig()

    if tomllib is None:
        return config

    paths_to_try = [config_path] if config_path else DEFAULT_CONFIG_PATHS

    for path in paths_to_try:
        if path and path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)
                server_data = data.get("server", {})

                if "host" in server_data:
                    config.host = server_data["host"]
                if "port" in server_data:
                    config.port = server_data["port"]
                if "poll_interval" in server_data:
                    config.poll_interval = server_data["poll_interval"]
                if "headless" in server_data:
                    config.headless = server_data["headless"]
                if "save_to_db" in server_data:
                    config.save_to_db = server_data["save_to_db"]
                if "log_level" in server_data:
                    config.log_level = server_data["log_level"]
            break

    return config
