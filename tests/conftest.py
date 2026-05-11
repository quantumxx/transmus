"""Test fixtures and configuration for Transmus tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from transmus.models import Playlist, Track


# ── Sample Track Data ──────────────────────────────────────────────────────


def make_track(
    title: str = "Bohemian Rhapsody",
    artist: str = "Queen",
    album: str | None = "A Night at the Opera",
    source_id: str | None = "track-123",
    source_uri: str | None = "spotify:track:123",
) -> Track:
    return Track(
        title=title,
        artist=artist,
        album=album,
        duration_ms=354000,
        source_id=source_id,
        source_uri=source_uri,
    )


def make_playlist(
    name: str = "Test Playlist",
    track_count: int = 3,
    prefix: str = "pl",
) -> Playlist:
    tracks = [
        Track(
            title=f"Track {i}",
            artist=f"Artist {i}",
            album=f"Album {i}",
            source_id=f"{prefix}-track-{i}",
            source_uri=f"spotify:track:{prefix}{i}",
        )
        for i in range(1, track_count + 1)
    ]
    return Playlist(
        id=f"{prefix}-test-001",
        name=name,
        description="A test playlist",
        owner="Test User",
        track_count=len(tracks),
        url=f"https://open.spotify.com/playlist/{prefix}-test-001",
        tracks=tracks,
    )


# ── Sample Playlist Data (JSON) ────────────────────────────────────────────


SAMPLE_YOUTUBE_PLAYLIST = {
    "id": "PL_test_001",
    "title": "My YT Mix",
    "description": "My favorite YouTube Music playlist",
    "owner": {"name": "Test User"},
    "tracks": [
        {
            "title": "Bohemian Rhapsody",
            "artists": [{"name": "Queen"}],
            "album": {"name": "A Night at the Opera"},
            "durationMs": 354000,
            "videoId": "yt-video-1",
        },
        {
            "title": "Stairway to Heaven",
            "artists": [{"name": "Led Zeppelin"}],
            "album": {"name": "Led Zeppelin IV"},
            "durationMs": 482000,
            "videoId": "yt-video-2",
        },
    ],
}

SAMPLE_SPOTIFY_PLAYLIST = {
    "id": "37i9dQZF1DXcBWIGoYBM5M",
    "name": "Today's Top Hits",
    "description": "The hottest songs right now",
    "owner": {"display_name": "Spotify"},
    "tracks": {
        "items": [
            {
                "track": {
                    "id": "spotify-track-1",
                    "name": "Blinding Lights",
                    "artists": [{"name": "The Weeknd"}],
                    "album": {"name": "After Hours"},
                    "duration_ms": 200000,
                    "uri": "spotify:track:1",
                }
            },
            {
                "track": {
                    "id": "spotify-track-2",
                    "name": "Shape of You",
                    "artists": [{"name": "Ed Sheeran"}],
                    "album": {"name": "÷ (Divide)"},
                    "duration_ms": 233000,
                    "uri": "spotify:track:2",
                }
            },
        ]
    },
}


# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".transmus"
        config_dir.mkdir(parents=True)
        yield config_dir


@pytest.fixture
def sample_track() -> Track:
    return make_track()


@pytest.fixture
def sample_playlist() -> Playlist:
    return make_playlist()


@pytest.fixture
def youtube_playlist_data() -> dict[str, Any]:
    return SAMPLE_YOUTUBE_PLAYLIST


@pytest.fixture
def spotify_playlist_data() -> dict[str, Any]:
    return SAMPLE_SPOTIFY_PLAYLIST


@pytest.fixture
def mock_youtube_headers() -> dict[str, str]:
    return {
        "Cookie": "SID=test; HSID=test; SSID=test",
        "X-Goog-AuthUser": "0",
        "X-Goog-Visitor-Id": "test-visitor",
        "Authorization": "SAPISIDHASH test",
    }