"""YouTube Music authentication for Transmus.

Uses ytmusicapi's browser cookie-based authentication.
Users provide their YouTube Music session cookie from browser DevTools.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Optional

from transmus.config import (
    clear_youtube_headers,
    is_youtube_authenticated,
    load_youtube_headers,
    save_youtube_headers,
)

REQUIRED_HEADERS = [
    "Cookie",
    "X-Goog-AuthUser",
    "X-Goog-Visitor-Id",
    "Authorization",
]


def _compute_sapisid_hash(sapisid: str, origin: str = "https://music.youtube.com") -> str:
    """Compute the SAPISID hash used in the Authorization header.

    This is the same algorithm used by ytmusicapi internally.
    """
    timestamp = int(time.time())
    hash_input = f"{timestamp} {sapisid} {origin}"
    hash_digest = hashlib.sha1(hash_input.encode("utf-8")).hexdigest()
    return f"SAPISIDHASH {timestamp}_{hash_digest}"


def _extract_from_cookie(cookie_str: str) -> Optional[dict[str, str]]:
    """Extract required headers from a raw Cookie string.

    Parses the cookie to find SAPISID (for Authorization),
    and sets sensible defaults for other required headers.

    Args:
        cookie_str: Raw Cookie header value from browser DevTools.

    Returns:
        Dict of headers, or None if SAPISID cookie is missing.
    """
    # Parse individual cookies from the Cookie header string
    cookies: dict[str, str] = {}
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookies[key.strip()] = value.strip()

    sapisid = cookies.get("SAPISID")
    if not sapisid:
        return None

    # Compute the Authorization header from SAPISID
    authorization = _compute_sapisid_hash(sapisid)

    # Extract or generate a visitor ID
    visitor_id = cookies.get("VISITOR_INFO1_LIVE", "Cg9iYXNlNjRlbmNvZGVkEgA=")

    headers = {
        "Cookie": cookie_str,
        "X-Goog-AuthUser": "0",
        "X-Goog-Visitor-Id": visitor_id,
        "Authorization": authorization,
    }
    return headers


def _prompt_cookie_method() -> Optional[dict[str, str]]:
    """Guide the user through the simplest cookie-paste method.

    Returns:
        Headers dict, or None if the user cancelled.
    """
    print()
    print("Method 1: Paste your Cookie (simplest)")
    print("-" * 40)
    print()
    print("1. Open Chrome/Edge/Firefox and go to https://music.youtube.com")
    print("   Make sure you are logged in to your Google account.")
    print()
    print("2. Open Developer Tools:")
    print("   - Chrome/Edge: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
    print("   - Firefox: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
    print()
    print("3. Go to the Network tab and refresh the page (F5)")
    print()
    print("4. Click on any request to 'music.youtube.com' in the list")
    print()
    print("5. Find the 'Cookie' header in the Request Headers section:")
    print("   - Chrome/Edge: Scroll down in the Headers tab")
    print("   - Firefox: Look under the 'Headers' tab")
    print()
    print("6. Right-click on the Cookie value → 'Copy value'")
    print()
    print("7. Paste it below and press Enter")
    print()

    cookie_str = input("Paste your Cookie value here: ").strip()

    if not cookie_str:
        print("No cookie provided.")
        return None

    headers = _extract_from_cookie(cookie_str)
    if headers is None:
        print()
        print("Could not find the SAPISID cookie in the value you provided.")
        print("Please make sure you copied the full Cookie header value.")
        return None

    return headers


def _prompt_json_file_method() -> Optional[dict[str, str]]:
    """Fallback method: user provides a JSON headers file.

    Returns:
        Headers dict, or None if the user cancelled.
    """
    print()
    print("Method 2: Provide a headers JSON file (advanced)")
    print("-" * 40)
    print()
    print("If you prefer, you can provide a JSON file containing the")
    print("required request headers. You can generate this file using:")
    print()
    print("  - The 'Cookie-Editor' browser extension (export as JSON)")
    print("  - The ytmusicapi setup guide:")
    print("    https://ytmusicapi.readthedocs.io/en/stable/setup.html")
    print()
    print("The JSON file must include these headers:")
    print("  - Cookie")
    print("  - X-Goog-AuthUser")
    print("  - X-Goog-Visitor-Id")
    print("  - Authorization")
    print()

    file_path = input("Enter path to headers JSON file: ").strip()
    if not file_path:
        print("No file provided.")
        return None

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return None

    try:
        with open(path, "r") as f:
            headers = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading file: {e}")
        return None

    # Validate required headers
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        print(f"Missing required headers: {', '.join(missing)}")
        print("Please ensure your exported headers include all required fields.")
        return None

    return headers


def setup_auth_interactive() -> bool:
    """Guide the user through setting up YouTube Music authentication.

    Provides step-by-step instructions for getting the YouTube Music
    session cookie from browser Developer Tools (no extensions needed).
    Saves the authentication headers to ~/.transmus/youtube_headers.json.

    Returns:
        True if authentication was successfully configured.
    """
    print("=" * 60)
    print("YouTube Music Authentication Setup")
    print("=" * 60)
    print()
    print("YouTube Music does not have an official API, so Transmus uses")
    print("your browser's session cookie to access your account.")
    print()
    print("You'll need to copy your YouTube Music Cookie from your browser.")
    print("Don't worry — this is a one-time setup and your cookie is stored")
    print("locally in ~/.transmus/ (never sent anywhere).")
    print()

    # Try Method 1 first (simplest - paste cookie)
    headers = _prompt_cookie_method()

    # Fall back to Method 2 (JSON file) if Method 1 failed
    if headers is None:
        print()
        headers = _prompt_json_file_method()

    if headers is None:
        print()
        print("Authentication cancelled.")
        return False

    save_youtube_headers(headers)
    print()
    print("✓ YouTube Music authentication configured successfully!")
    print("  Headers saved to ~/.transmus/youtube_headers.json")
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