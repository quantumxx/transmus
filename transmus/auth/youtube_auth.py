"""YouTube Music authentication for Transmus.

Uses ytmusicapi's browser cookie-based authentication.
Users must export their browser headers/cookies for YouTube Music.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from transmus.config import (
    load_youtube_headers,
    save_youtube_headers,
    clear_youtube_headers,
    is_youtube_authenticated,
)

REQUIRED_HEADERS = [
    "Cookie",
    "X-Goog-AuthUser",
    "X-Goog-Visitor-Id",
    "Authorization",
]


def setup_auth_interactive() -> bool:
    """Guide the user through setting up YouTube Music authentication.

    Provides instructions for exporting browser cookies/headers
    and saves them to ~/.transmus/youtube_headers.json.

    Returns:
        True if authentication was successfully configured.
    """
    print("=" * 60)
    print("YouTube Music Authentication Setup")
    print("=" * 60)
    print()
    print("YouTube Music does not have an official API, so Transmus uses")
    print("browser authentication headers to access your account.")
    print()
    print("Option 1: Automatic (recommended)")
    print("  Install a browser extension like 'Get cookies.txt' or")
    print("  'Cookie-Editor' to export your YouTube Music cookies.")
    print()
    print("Option 2: Manual")
    print("  Follow the ytmusicapi setup guide:")
    print("  https://ytmusicapi.readthedocs.io/en/stable/setup.html")
    print()
    print("You'll need to provide a JSON file with headers including:")
    print("  - Cookie")
    print("  - X-Goog-AuthUser")
    print("  - X-Goog-Visitor-Id")
    print("  - Authorization")
    print()

    file_path = input("Enter path to headers JSON file: ").strip()
    if not file_path:
        print("No file provided. Authentication cancelled.")
        return False

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    try:
        with open(path, "r") as f:
            headers = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading file: {e}")
        return False

    # Validate required headers
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        print(f"Missing required headers: {', '.join(missing)}")
        print("Please ensure your exported headers include all required fields.")
        return False

    save_youtube_headers(headers)
    print()
    print("✓ YouTube Music authentication configured successfully!")
    return True


def validate_headers() -> bool:
    """Validate that stored YouTube Music headers are present and non-empty."""
    headers = load_youtube_headers()
    if not headers:
        return False
    return all(headers.get(h) for h in REQUIRED_HEADERS)


def get_auth_status() -> dict:
    """Get the current authentication status for YouTube Music.

    Returns:
        dict with 'authenticated' (bool) and 'message' (str).
    """
    if is_youtube_authenticated():
        headers = load_youtube_headers()
        if headers and validate_headers():
            return {
                "authenticated": True,
                "message": "YouTube Music is authenticated",
            }
        return {
            "authenticated": False,
            "message": "YouTube Music headers are incomplete or expired",
        }
    return {
        "authenticated": False,
        "message": "YouTube Music not configured. Run 'transmus auth youtube'",
    }


def logout() -> None:
    """Remove YouTube Music authentication."""
    clear_youtube_headers()
    print("YouTube Music authentication cleared.")