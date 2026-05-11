"""Configuration management for Transmus.

Stores configuration in ~/.transmus/config.json.
Sensitive data (tokens, headers) stored in separate files in ~/.transmus/.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

CONFIG_DIR = Path.home() / ".transmus"
CONFIG_FILE = CONFIG_DIR / "config.json"
YOUTUBE_HEADERS_FILE = CONFIG_DIR / "youtube_headers.json"
SPOTIFY_CACHE_DIR = CONFIG_DIR / "spotify_cache"

DEFAULT_CONFIG: dict[str, Any] = {
    "default_playlist_visibility": "public",
    "version": "0.1.0",
}


def ensure_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from ~/.transmus/config.json."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except (json.JSONDecodeError, OSError):
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to ~/.transmus/config.json."""
    ensure_config_dir()
    merged = {**DEFAULT_CONFIG, **config}
    with open(CONFIG_FILE, "w") as f:
        json.dump(merged, f, indent=2)


def get_config(key: str, default: Any = None) -> Any:
    """Get a specific config value."""
    return load_config().get(key, default)


def set_config(key: str, value: Any) -> None:
    """Set a specific config value and save."""
    config = load_config()
    config[key] = value
    save_config(config)


def load_youtube_headers() -> Optional[dict[str, str]]:
    """Load YouTube Music authentication headers."""
    if YOUTUBE_HEADERS_FILE.exists():
        try:
            with open(YOUTUBE_HEADERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_youtube_headers(headers: dict[str, str]) -> None:
    """Save YouTube Music authentication headers."""
    ensure_config_dir()
    with open(YOUTUBE_HEADERS_FILE, "w") as f:
        json.dump(headers, f, indent=2)
    # Restrict permissions on sensitive file
    try:
        os.chmod(YOUTUBE_HEADERS_FILE, 0o600)
    except OSError:
        pass  # Best effort on Windows


def clear_youtube_headers() -> None:
    """Remove stored YouTube Music headers."""
    if YOUTUBE_HEADERS_FILE.exists():
        YOUTUBE_HEADERS_FILE.unlink()


def get_spotify_cache_path() -> Path:
    """Get the path for Spotify token cache."""
    ensure_config_dir()
    return SPOTIFY_CACHE_DIR / ".cache"


def is_youtube_authenticated() -> bool:
    """Check if YouTube Music authentication is configured."""
    headers = load_youtube_headers()
    return headers is not None and "Cookie" in headers


def is_spotify_authenticated() -> bool:
    """Check if Spotify authentication is configured."""
    cache_path = get_spotify_cache_path()
    return cache_path.exists()