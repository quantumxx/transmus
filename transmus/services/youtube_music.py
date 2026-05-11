"""YouTube Music service for Transmus.

Wraps ytmusicapi to provide playlist listing, reading, and creation.
"""

from __future__ import annotations

from typing import Optional

from ytmusicapi import YTMusic

from transmus.config import load_youtube_headers
from transmus.models import Playlist, Track


class YouTubeMusicService:
    """Service for interacting with YouTube Music via ytmusicapi."""

    def __init__(self) -> None:
        self._client: Optional[YTMusic] = None

    @property
    def client(self) -> YTMusic:
        """Get or initialize the YTMusic client."""
        if self._client is None:
            headers = load_youtube_headers()
            if not headers:
                raise RuntimeError(
                    "YouTube Music not authenticated. "
                    "Run 'transmus auth youtube' first."
                )
            self._client = YTMusic(headers)
        return self._client

    def get_playlists(self) -> list[Playlist]:
        """List all playlists in the user's YouTube Music library.

        Returns:
            List of Playlist objects (without tracks populated).
        """
        raw = self.client.get_library_playlists(limit=None)
        playlists = []
        for item in raw:
            playlists.append(
                Playlist(
                    id=item.get("playlistId", ""),
                    name=item.get("title", "Untitled"),
                    description=None,
                    owner=item.get("owner", {}).get("name"),
                    track_count=item.get("count", 0),
                    url=f"https://music.youtube.com/playlist?list={item.get('playlistId', '')}",
                )
            )
        return playlists

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Get a playlist with all its tracks.

        Args:
            playlist_id: The YouTube Music playlist ID.

        Returns:
            Playlist object with tracks populated.
        """
        raw = self.client.get_playlist(playlist_id, limit=None)
        tracks = []
        for item in raw.get("tracks", []):
            track = self._parse_track(item)
            if track:
                tracks.append(track)

        return Playlist(
            id=playlist_id,
            name=raw.get("title", "Untitled"),
            description=raw.get("description"),
            owner=raw.get("owner", {}).get("name"),
            track_count=len(tracks),
            url=f"https://music.youtube.com/playlist?list={playlist_id}",
            tracks=tracks,
        )

    def search_track(self, title: str, artist: str) -> Optional[Track]:
        """Search for a track on YouTube Music.

        Args:
            title: Track title to search for.
            artist: Artist name to search for.

        Returns:
            Best matching Track, or None if no match found.
        """
        query = f"{artist} - {title}"
        results = self.client.search(query, filter="songs", limit=5)

        if not results:
            return None

        best = results[0]
        return self._parse_track(best)

    def create_playlist(
        self, name: str, description: Optional[str] = None, track_ids: Optional[list[str]] = None
    ) -> str:
        """Create a new YouTube Music playlist.

        Args:
            name: Playlist name.
            description: Optional playlist description.
            track_ids: Optional list of video IDs to add.

        Returns:
            The new playlist ID.
        """
        playlist_id = self.client.create_playlist(
            title=name,
            description=description or "",
            privacy_status="public",
        )

        if track_ids:
            # ytmusicapi.add_playlist_items accepts video IDs
            self.client.add_playlist_items(playlist_id, track_ids)

        return playlist_id

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> None:
        """Add tracks to an existing YouTube Music playlist.

        Args:
            playlist_id: Target playlist ID.
            track_ids: List of video IDs to add.
        """
        # Add in batches of 100
        batch_size = 100
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i : i + batch_size]
            self.client.add_playlist_items(playlist_id, batch)

    def _parse_track(self, item: dict) -> Optional[Track]:
        """Parse a raw ytmusicapi track dict into a Track model.

        Args:
            item: Raw track dict from ytmusicapi.

        Returns:
            Track object, or None if parsing fails.
        """
        try:
            title = item.get("title", "")
            if not title:
                return None

            # Handle artist(s) - can be a list of dicts or a string
            artists = item.get("artists")
            if artists and isinstance(artists, list):
                artist = ", ".join(
                    a.get("name", "") for a in artists if isinstance(a, dict)
                )
            else:
                artist = item.get("artist", "Unknown Artist")

            # Handle album
            album = None
            album_data = item.get("album")
            if album_data and isinstance(album_data, dict):
                album = album_data.get("name")
            elif isinstance(album_data, str):
                album = album_data

            return Track(
                title=title,
                artist=artist or "Unknown Artist",
                album=album,
                duration_ms=item.get("durationMs"),
                source_id=item.get("videoId"),
                source_uri=item.get("videoId"),
            )
        except (KeyError, TypeError, ValueError):
            return None