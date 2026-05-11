"""Spotify authentication for Transmus.

Uses Spotify's OAuth Authorization Code flow via spotipy.
Users must create a free Spotify App at developer.spotify.com.
"""

from __future__ import annotations

import os
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from transmus.config import (
    get_config,
    set_config,
    get_spotify_cache_path,
    is_spotify_authenticated,
)

SCOPE = "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private"
REDIRECT_URI = "http://localhost:8888/callback"


def _get_client_id() -> Optional[str]:
    """Get Spotify client ID from config or environment."""
    return os.environ.get("SPOTIFY_CLIENT_ID") or get_config("spotify_client_id")


def _get_client_secret() -> Optional[str]:
    """Get Spotify client secret from config or environment."""
    return os.environ.get("SPOTIFY_CLIENT_SECRET") or get_config("spotify_client_secret")


def setup_auth_interactive() -> bool:
    """Guide the user through setting up Spotify OAuth authentication.

    Prompts for Spotify Developer App credentials, then initiates
    the OAuth flow via browser.

    Returns:
        True if authentication was successfully configured.
    """
    print("=" * 60)
    print("Spotify Authentication Setup")
    print("=" * 60)
    print()
    print("To use Spotify, you need to create a free Spotify App at:")
    print("  https://developer.spotify.com/dashboard")
    print()
    print("Steps:")
    print("  1. Log in with your Spotify account")
    print("  2. Click 'Create App'")
    print("  3. Enter any App name and description")
    print("  4. Set Redirect URI to: http://localhost:8888/callback")
    print("  5. Check 'Web API' under APIs Used")
    print("  6. Save and copy your Client ID and Client Secret")
    print()

    # Try environment variables first
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if client_id and client_secret:
        print("✓ Found SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in environment")
    else:
        client_id = input("Enter your Spotify Client ID: ").strip()
        if not client_id:
            print("Client ID is required. Authentication cancelled.")
            return False

        client_secret = input("Enter your Spotify Client Secret: ").strip()
        if not client_secret:
            print("Client Secret is required. Authentication cancelled.")
            return False

        # Store in config for future use
        set_config("spotify_client_id", client_id)
        set_config("spotify_client_secret", client_secret)

    print()
    print("Opening browser for Spotify authorization...")
    print("(If the browser doesn't open, copy the URL manually)")

    try:
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_handler=spotipy.cache_handler.CacheFileHandler(
                cache_path=str(get_spotify_cache_path())
            ),
            open_browser=True,
        )

        # Get the authorization URL
        auth_url = sp_oauth.get_authorize_url()
        print(f"\nAuthorization URL: {auth_url}")

        # This will block until the user authorizes and the callback is received
        token_info = sp_oauth.get_access_token(
            sp_oauth.get_cached_token() is None
        )

        if token_info:
            print()
            print("✓ Spotify authentication successful!")
            return True
        else:
            print()
            print("✗ Spotify authentication failed.")
            return False

    except Exception as e:
        print(f"\n✗ Authentication error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure your Redirect URI is exactly: http://localhost:8888/callback")
        print("  2. Make sure no other application is using port 8888")
        print("  3. Verify your Client ID and Client Secret are correct")
        return False


def get_spotify_client() -> spotipy.Spotify:
    """Get an authenticated Spotify client.

    Returns:
        Authenticated spotipy.Spotify instance.

    Raises:
        RuntimeError: If Spotify is not authenticated.
    """
    client_id = _get_client_id()
    client_secret = _get_client_secret()

    if not client_id or not client_secret:
        raise RuntimeError(
            "Spotify not configured. "
            "Run 'transmus auth spotify' or set "
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
        )

    cache_path = get_spotify_cache_path()
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_handler=spotipy.cache_handler.CacheFileHandler(
            cache_path=str(cache_path)
        ),
        open_browser=False,
    )

    return spotipy.Spotify(auth_manager=auth_manager)


def get_auth_status() -> dict:
    """Get the current authentication status for Spotify.

    Returns:
        dict with 'authenticated' (bool) and 'message' (str).
    """
    client_id = _get_client_id()
    client_secret = _get_client_secret()

    if not client_id or not client_secret:
        return {
            "authenticated": False,
            "message": "Spotify credentials not configured. Run 'transmus auth spotify'",
        }

    if is_spotify_authenticated():
        return {
            "authenticated": True,
            "message": "Spotify is authenticated",
        }

    return {
        "authenticated": False,
        "message": "Spotify token expired or missing. Run 'transmus auth spotify' to re-authenticate",
    }


def logout() -> None:
    """Remove Spotify authentication."""
    cache_path = get_spotify_cache_path()
    if cache_path.exists():
        cache_path.unlink()
    print("Spotify authentication cleared.")