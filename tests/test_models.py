"""Tests for data models."""

from __future__ import annotations

from transmus.models import Playlist, Track, TransferResult


class TestTrack:
    """Tests for the Track model."""

    def test_track_creation(self) -> None:
        track = Track(title="Test Song", artist="Test Artist")
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.album is None
        assert track.duration_ms is None

    def test_track_with_all_fields(self) -> None:
        track = Track(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_ms=200000,
            source_id="id-123",
            source_uri="spotify:track:id-123",
        )
        assert track.album == "Test Album"
        assert track.duration_ms == 200000
        assert track.source_id == "id-123"

    def test_track_str(self) -> None:
        track = Track(title="Bohemian Rhapsody", artist="Queen")
        assert str(track) == "Queen - Bohemian Rhapsody"

    def test_normalized_title(self) -> None:
        track = Track(title="Song (Remastered)", artist="Artist")
        assert track.normalized_title == "song"

    def test_normalized_artist(self) -> None:
        track = Track(title="Song", artist="  Artist  Name  ")
        assert track.normalized_artist == "artist name"


class TestPlaylist:
    """Tests for the Playlist model."""

    def test_playlist_creation(self) -> None:
        playlist = Playlist(id="pl-1", name="My Playlist")
        assert playlist.id == "pl-1"
        assert playlist.name == "My Playlist"
        assert playlist.track_count == 0
        assert playlist.tracks == []

    def test_playlist_with_tracks(self) -> None:
        tracks = [
            Track(title="Song 1", artist="Artist 1"),
            Track(title="Song 2", artist="Artist 2"),
        ]
        playlist = Playlist(
            id="pl-1",
            name="My Playlist",
            track_count=len(tracks),
            tracks=tracks,
        )
        assert len(playlist.tracks) == 2
        assert playlist.track_count == 2

    def test_playlist_str(self) -> None:
        playlist = Playlist(id="pl-1", name="My Playlist", track_count=15)
        assert str(playlist) == "My Playlist (15 tracks)"


class TestTransferResult:
    """Tests for the TransferResult model."""

    def test_empty_result(self) -> None:
        source = Playlist(id="src", name="Source")
        result = TransferResult(
            source_playlist=source,
            destination_name="Dest",
        )
        assert result.total == 0
        assert result.success_rate == 0.0

    def test_partial_success(self) -> None:
        source = Playlist(id="src", name="Source")
        result = TransferResult(
            source_playlist=source,
            destination_name="Dest",
            matched_tracks=[Track(title="A", artist="1")],
            unmatched_tracks=[Track(title="B", artist="2")],
        )
        assert result.total == 2
        assert result.success_rate == 50.0

    def test_full_success(self) -> None:
        source = Playlist(id="src", name="Source")
        result = TransferResult(
            source_playlist=source,
            destination_name="Dest",
            matched_tracks=[
                Track(title="A", artist="1"),
                Track(title="B", artist="2"),
            ],
        )
        assert result.total == 2
        assert result.success_rate == 100.0

    def test_summary_includes_url(self) -> None:
        source = Playlist(id="src", name="Source")
        result = TransferResult(
            source_playlist=source,
            destination_name="Dest",
            destination_url="https://spotify.com/playlist/abc",
        )
        summary = result.summary()
        assert "https://spotify.com/playlist/abc" in summary

    def test_summary_includes_unmatched(self) -> None:
        source = Playlist(id="src", name="Source")
        result = TransferResult(
            source_playlist=source,
            destination_name="Dest",
            unmatched_tracks=[Track(title="Lost Song", artist="Unknown")],
        )
        summary = result.summary()
        assert "Lost Song" in summary
        assert "Unknown" in summary