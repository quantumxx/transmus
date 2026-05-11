"""Transfer orchestration for Transmus.

Coordinates the end-to-end process of reading a playlist from one service,
matching tracks, and creating the playlist on the other service.
"""

from __future__ import annotations

import time
from typing import Callable, Optional

from transmus.matcher import match_tracks
from transmus.models import Playlist, Track, TransferResult
from transmus.services.youtube_music import YouTubeMusicService
from transmus.services.spotify_service import SpotifyService


def transfer_youtube_to_spotify(
    playlist_id: str,
    new_name: Optional[str] = None,
    public: bool = True,
    progress_callback: Optional[Callable] = None,
) -> TransferResult:
    """Transfer a YouTube Music playlist to Spotify.

    Args:
        playlist_id: YouTube Music playlist ID.
        new_name: Optional new name for the Spotify playlist.
                  Defaults to the original playlist name.
        public: Whether the new Spotify playlist should be public.
        progress_callback: Optional callback for progress updates.

    Returns:
        TransferResult with details of the transfer.
    """
    yt = YouTubeMusicService()
    sp = SpotifyService()

    # Step 1: Fetch source playlist
    if progress_callback:
        progress_callback("Fetching YouTube Music playlist...", 0)

    source_playlist = yt.get_playlist(playlist_id)
    dest_name = new_name or source_playlist.name

    if progress_callback:
        progress_callback(
            f"Found {len(source_playlist.tracks)} tracks in '{source_playlist.name}'",
            10,
        )

    # Step 2: Match tracks on Spotify
    if progress_callback:
        progress_callback("Matching tracks on Spotify...", 20)

    def search_spotify(title: str, artist: str) -> list[Track]:
        """Search for a track on Spotify with rate limiting."""
        result = sp.search_track(title, artist)
        time.sleep(0.1)  # Rate limiting: ~10 requests/second
        return [result] if result else []

    matched_pairs, unmatched = match_tracks(
        source_tracks=source_playlist.tracks,
        search_fn=search_spotify,
        progress_callback=_make_match_progress(progress_callback, 20, 70),
    )

    if progress_callback:
        progress_callback(
            f"Matched {len(matched_pairs)}/{len(source_playlist.tracks)} tracks",
            70,
        )

    # Step 3: Create Spotify playlist and add tracks
    if progress_callback:
        progress_callback("Creating Spotify playlist...", 80)

    track_uris = [sp_track.source_uri for _, sp_track in matched_pairs if sp_track.source_uri]
    dest_id = sp.create_playlist(
        name=dest_name,
        description=f"Transferred from YouTube Music: {source_playlist.name}",
        public=public,
        track_uris=track_uris,
    )

    # Get the destination URL
    dest_playlist = sp.get_playlist(dest_id)

    if progress_callback:
        progress_callback("Transfer complete!", 100)

    return TransferResult(
        source_playlist=source_playlist,
        destination_name=dest_name,
        matched_tracks=[yt_track for yt_track, _ in matched_pairs],
        unmatched_tracks=unmatched,
        destination_url=dest_playlist.url,
    )


def transfer_spotify_to_youtube(
    playlist_id: str,
    new_name: Optional[str] = None,
    public: bool = True,
    progress_callback: Optional[Callable] = None,
) -> TransferResult:
    """Transfer a Spotify playlist to YouTube Music.

    Args:
        playlist_id: Spotify playlist ID.
        new_name: Optional new name for the YouTube Music playlist.
        public: Whether the new YouTube Music playlist should be public.
        progress_callback: Optional callback for progress updates.

    Returns:
        TransferResult with details of the transfer.
    """
    sp = SpotifyService()
    yt = YouTubeMusicService()

    # Step 1: Fetch source playlist
    if progress_callback:
        progress_callback("Fetching Spotify playlist...", 0)

    source_playlist = sp.get_playlist(playlist_id)
    dest_name = new_name or source_playlist.name

    if progress_callback:
        progress_callback(
            f"Found {len(source_playlist.tracks)} tracks in '{source_playlist.name}'",
            10,
        )

    # Step 2: Match tracks on YouTube Music
    if progress_callback:
        progress_callback("Matching tracks on YouTube Music...", 20)

    def search_youtube(title: str, artist: str) -> list[Track]:
        """Search for a track on YouTube Music with rate limiting."""
        result = yt.search_track(title, artist)
        time.sleep(0.3)  # Rate limiting: ~3 requests/second for YT Music
        return [result] if result else []

    matched_pairs, unmatched = match_tracks(
        source_tracks=source_playlist.tracks,
        search_fn=search_youtube,
        progress_callback=_make_match_progress(progress_callback, 20, 70),
    )

    if progress_callback:
        progress_callback(
            f"Matched {len(matched_pairs)}/{len(source_playlist.tracks)} tracks",
            70,
        )

    # Step 3: Create YouTube Music playlist and add tracks
    if progress_callback:
        progress_callback("Creating YouTube Music playlist...", 80)

    track_ids = [
        yt_track.source_id
        for _, yt_track in matched_pairs
        if yt_track.source_id
    ]
    dest_id = yt.create_playlist(
        name=dest_name,
        description=f"Transferred from Spotify: {source_playlist.name}",
        track_ids=track_ids,
    )

    # Get the destination URL
    dest_playlist = yt.get_playlist(dest_id)

    if progress_callback:
        progress_callback("Transfer complete!", 100)

    return TransferResult(
        source_playlist=source_playlist,
        destination_name=dest_name,
        matched_tracks=[sp_track for sp_track, _ in matched_pairs],
        unmatched_tracks=unmatched,
        destination_url=dest_playlist.url,
    )


def _make_match_progress(
    outer_callback: Optional[Callable],
    start_pct: int,
    end_pct: int,
) -> Callable:
    """Create a progress callback for the matching phase.

    Maps the matching progress (0 to N tracks) to a percentage range.
    """

    def callback(track: Track, matched: bool, score: float) -> None:
        if outer_callback:
            # We don't know total tracks here, so we just pass info
            status = "✓" if matched else "✗"
            score_str = f" ({score:.0f}%)" if matched else ""
            outer_callback(f"  {status} {track}{score_str}", None)

    return callback