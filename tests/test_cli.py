"""Tests for CLI commands."""

from __future__ import annotations

from click.testing import CliRunner

from transmus.cli import main


class TestCLIBasic:
    """Tests for basic CLI functionality."""

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_help(self) -> None:
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Transmus" in result.output
        assert "Transfer music playlists" in result.output

    def test_version(self) -> None:
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "transmus" in result.output

    def test_no_args(self) -> None:
        result = self.runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Transmus" in result.output

    def test_auth_help(self) -> None:
        result = self.runner.invoke(main, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Manage authentication" in result.output

    def test_auth_youtube_help(self) -> None:
        result = self.runner.invoke(main, ["auth", "youtube", "--help"])
        assert result.exit_code == 0
        assert "YouTube Music" in result.output

    def test_auth_spotify_help(self) -> None:
        result = self.runner.invoke(main, ["auth", "spotify", "--help"])
        assert result.exit_code == 0
        assert "Spotify" in result.output

    def test_status_help(self) -> None:
        result = self.runner.invoke(main, ["status", "--help"])
        assert result.exit_code == 0

    def test_yt_help(self) -> None:
        result = self.runner.invoke(main, ["yt", "--help"])
        assert result.exit_code == 0
        assert "YouTube Music" in result.output

    def test_spotify_help(self) -> None:
        result = self.runner.invoke(main, ["spotify", "--help"])
        assert result.exit_code == 0
        assert "Spotify" in result.output

    def test_transfer_help(self) -> None:
        result = self.runner.invoke(main, ["transfer", "--help"])
        assert result.exit_code == 0
        assert "Transfer playlists" in result.output

    def test_transfer_yt_to_spotify_help(self) -> None:
        result = self.runner.invoke(main, ["transfer", "yt-to-spotify", "--help"])
        assert result.exit_code == 0
        assert "YouTube Music" in result.output

    def test_transfer_spotify_to_yt_help(self) -> None:
        result = self.runner.invoke(main, ["transfer", "spotify-to-yt", "--help"])
        assert result.exit_code == 0
        assert "Spotify" in result.output


class TestCLIErrors:
    """Tests for CLI error handling."""

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_yt_playlists_without_auth(self) -> None:
        """Should fail gracefully when not authenticated."""
        result = self.runner.invoke(main, ["yt", "playlists"])
        assert result.exit_code != 0
        assert "Error" in result.output or "not authenticated" in result.output.lower()

    def test_spotify_playlists_without_auth(self) -> None:
        """Should fail gracefully when not authenticated."""
        result = self.runner.invoke(main, ["spotify", "playlists"])
        assert result.exit_code != 0
        assert "Error" in result.output or "not configured" in result.output.lower()

    def test_transfer_without_args(self) -> None:
        """Transfer commands require playlist_id."""
        result = self.runner.invoke(main, ["transfer", "yt-to-spotify"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output