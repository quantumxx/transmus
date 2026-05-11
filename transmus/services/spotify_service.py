"""Spotify service for Transmus.

Wraps spotipy to provide playlist listing, reading, and creation.
"""

from __future__ import annotations

from typing import Optional

import spotipy

from transmus.auth.spotify_auth import get_spotify_client
from transmus.models import Playlist, Track


class SpotifyService:
    """Service for interacting with Spotify via spotipy."""

    def __init__(self) -> None:
        self._client: Optional[spotipy.Spotify] = None

    @property
    def client(self) -> spotipy.Spotify:
        """Get or initialize the Spotify client."""
        if self._client is None:
            self._client = get_spotify_client()
        return self._client

    def get_playlists(self) -> list[Playlist]:
        """List all playlists in the user's Spotify library.

        Returns:
            List of Playlist objects (without tracks populated).
        """
        playlists = []
        results = self.client.current_user_playlists(limit=50)
        while results:
            for item in results["items"]:
                playlists.append(
                    Playlist(
                        id=item["id"],
                        name=item["name"],
                        description=item.get("description"),
                        owner=item["owner"]["display_name"],
                        track_count=item["tracks"]["total"],
                        url=item.get("external_urls", {}).get("spotify"),
                    )
                )
            if results["next"]:
                results = self.client.next(results)
            else:
                break
        return playlists

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Get a Spotify playlist with all its tracks.

        Args:
            playlist_id: The Spotify playlist ID.

        Returns:
            Playlist object with tracks populated.
        """
        raw = self.client.playlist(playlist_id, fields=None)
        tracks = []

        results = self.client.playlist_items(playlist_id, limit=100)
        while results:
            for item in results["items"]:
                track = self._parse_track(item)
                if track:
                    tracks.append(track)
            if results["next"]:
                results = self.client.next(results)
            else:
                break

        return Playlist(
            id=playlist_id,
            name=raw["name"],
            description=raw.get("description"),
            owner=raw["owner"]["display_name"],
            track_count=len(tracks),
            url=raw.get("external_urls", {}).get("spotify"),
            tracks=tracks,
        )

    def search_track(self, title: str, artist: str) -> Optional[Track]:
        """Search for a track on Spotify.

        Args:
            title: Track title to search for.
            artist: Artist name to search for.

        Returns:
            Best matching Track, or None if no match found.
        """
        query = f"track:{title} artist:{artist}"
        results = self.client.search(q=query, type="track", limit=5)

        if not results or not results["tracks"]["items"]:
            # Fallback: broader search
            query = f"{title} {artist}"
            results = self.client.search(q=query, type="track", limit=5)

        if not results or not results["tracks"]["items"]:
            return None

        best = results["tracks"]["items"][0]
        return self._parse_track_from_search(best)

    def create_playlist(
        self,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
        track_uris: Optional[list[str]] = None,
    ) -> str:
        """Create a new Spotify playlist.

        Args:
            name: Playlist name.
            description: Optional playlist description.
            public: Whether the playlist is public.
            track_uris: Optional list of Spotify track URIs to add.

        Returns:
            The new playlist ID.
        """
        user_id = self.client.me()["id"]
        playlist = self.client.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            description=description or "",
        )
        playlist_id = playlist["id"]

        if track_uris:
            self.add_tracks_to_playlist(playlist_id, track_uris)

        return playlist_id

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: list[str]) -> None:
        """Add tracks to an existing Spotify playlist.

        Args:
            playlist_id: Target playlist ID.
            track_uris: List of Spotify track URIs to add.
        """
        # Spotify allows up to 100 tracks per request
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i : i + batch_size]
            self.client.playlist_add_items(playlist_id, batch)

    def _parse_track(self, item: dict) -> Optional[Track]:
        """Parse a raw Spotify playlist item into a Track model.

        Args:
            item: Raw track dict from Spotify API (playlist_items format).

        Returns:
            Track object, or None if parsing fails.
        """
        try:
            track_data = item.get("track")
            if not track_data:
                return None

            return self._parse_track_from_search(track_data)
        except (KeyError, TypeError, ValueError):
            return None

    def _parse_track_from_search(self, track_data: dict) -> Optional[Track]:
        """Parse a raw Spotify track dict into a Track model.

        Args:
            track_data: Raw track dict from Spotify API (search/track format).

        Returns:
            Track object, or None if parsing fails.
        """
        try:
            title = track_data.get("name", "")
            if not title:
                return None

            # Handle artists
            artists = track_data.get("artists", [])
            artist = ", ".join(a.get("name", "") for a in artists if isinstance(a, dict))

            # Handle album
            album = None
            album_data = track_data.get("album")
            if album_data and isinstance(album_data, dict):
                album = album_data.get("name")

            return Track(
                title=title,
                artist=artist or "Unknown Artist",
                album=album,
                duration_ms=track_data.get("duration_ms"),
                source_id=track_data.get("id"),
                source_uri=track_data.get("uri"),
            )
        except (KeyError, TypeError, ValueError):
            return None