"""CLI entry point for Transmus.

Defines the click command tree:
  transmus
    ├── auth youtube
    ├── auth spotify
    ├── status
    ├── yt playlists
    ├── yt playlist <id>
    ├── spotify playlists
    ├── spotify playlist <id>
    ├── transfer yt-to-spotify <id>
    └── transfer spotify-to-yt <id>
"""

from __future__ import annotations

import sys

import click

from transmus import __version__
from transmus.auth import youtube_auth, spotify_auth
from transmus.services.youtube_music import YouTubeMusicService
from transmus.services.spotify_service import SpotifyService
from transmus.transfer import (
    transfer_youtube_to_spotify,
    transfer_spotify_to_youtube,
)


class TransmusContext:
    """Shared context for CLI commands."""

    def __init__(self) -> None:
        self.yt_service: YouTubeMusicService | None = None
        self.sp_service: SpotifyService | None = None

    @property
    def youtube(self) -> YouTubeMusicService:
        if self.yt_service is None:
            self.yt_service = YouTubeMusicService()
        return self.yt_service

    @property
    def spotify(self) -> SpotifyService:
        if self.sp_service is None:
            self.sp_service = SpotifyService()
        return self.sp_service


@click.group()
@click.version_option(version=__version__, prog_name="transmus")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Transmus - Transfer music playlists between YouTube Music and Spotify.

    \b
    Quick start:
        transmus auth youtube       # Set up YouTube Music
        transmus auth spotify       # Set up Spotify
        transmus status             # Check authentication
        transmus yt playlists       # List your YT Music playlists
        transmus transfer yt-to-spotify <playlist_id>  # Transfer!
    """
    ctx.ensure_object(TransmusContext)


# ── Auth Commands ──────────────────────────────────────────────────────────


@main.group()
def auth() -> None:
    """Manage authentication for music services."""


@auth.command("youtube")
def auth_youtube() -> None:
    """Set up YouTube Music authentication (cookie-based)."""
    success = youtube_auth.setup_auth_interactive()
    if success:
        click.echo()
        click.secho("✓ YouTube Music is ready to use!", fg="green", bold=True)
    else:
        click.secho("✗ YouTube Music setup failed.", fg="red", bold=True)
        sys.exit(1)


@auth.command("spotify")
def auth_spotify() -> None:
    """Set up Spotify authentication (OAuth)."""
    success = spotify_auth.setup_auth_interactive()
    if success:
        click.echo()
        click.secho("✓ Spotify is ready to use!", fg="green", bold=True)
    else:
        click.secho("✗ Spotify setup failed.", fg="red", bold=True)
        sys.exit(1)


# ── Status Command ─────────────────────────────────────────────────────────


@main.command()
def status() -> None:
    """Check authentication status for all services."""
    click.echo("Transmus Status")
    click.echo("=" * 40)

    yt_status = youtube_auth.get_auth_status()
    sp_status = spotify_auth.get_auth_status()

    yt_icon = "✓" if yt_status["authenticated"] else "✗"
    sp_icon = "✓" if sp_status["authenticated"] else "✗"

    click.echo(f"  YouTube Music: {yt_icon} {yt_status['message']}")
    click.echo(f"  Spotify:       {sp_icon} {sp_status['message']}")

    if not yt_status["authenticated"] or not sp_status["authenticated"]:
        click.echo()
        click.echo("Run the following to set up missing services:")
        if not yt_status["authenticated"]:
            click.echo("  transmus auth youtube")
        if not sp_status["authenticated"]:
            click.echo("  transmus auth spotify")


# ── YouTube Music Commands ─────────────────────────────────────────────────


@main.group()
def yt() -> None:
    """Commands for YouTube Music."""


@yt.command("playlists")
@click.pass_context
def yt_playlists(ctx: click.Context) -> None:
    """List your YouTube Music playlists."""
    ctx_obj = ctx.ensure_object(TransmusContext)
    try:
        playlists = ctx_obj.youtube.get_playlists()
    except RuntimeError as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)

    if not playlists:
        click.echo("No playlists found in your YouTube Music library.")
        return

    click.echo(f"YouTube Music Playlists ({len(playlists)}):")
    click.echo("-" * 60)
    for pl in playlists:
        click.echo(f"  {pl.id}")
        click.echo(f"  {pl.name} ({pl.track_count} tracks)")
        if pl.url:
            click.echo(f"  {pl.url}")
        click.echo()


@yt.command("playlist")
@click.argument("playlist_id")
@click.pass_context
def yt_playlist(ctx: click.Context, playlist_id: str) -> None:
    """View tracks in a YouTube Music playlist."""
    ctx_obj = ctx.ensure_object(TransmusContext)
    try:
        playlist = ctx_obj.youtube.get_playlist(playlist_id)
    except RuntimeError as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)

    click.echo(f"Playlist: {playlist.name}")
    click.echo(f"Tracks: {playlist.track_count}")
    if playlist.description:
        click.echo(f"Description: {playlist.description}")
    click.echo("-" * 60)

    for i, track in enumerate(playlist.tracks, 1):
        click.echo(f"  {i:3d}. {track}")


# ── Spotify Commands ───────────────────────────────────────────────────────


@main.group()
def spotify() -> None:
    """Commands for Spotify."""


@spotify.command("playlists")
@click.pass_context
def sp_playlists(ctx: click.Context) -> None:
    """List your Spotify playlists."""
    ctx_obj = ctx.ensure_object(TransmusContext)
    try:
        playlists = ctx_obj.spotify.get_playlists()
    except RuntimeError as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)

    if not playlists:
        click.echo("No playlists found in your Spotify library.")
        return

    click.echo(f"Spotify Playlists ({len(playlists)}):")
    click.echo("-" * 60)
    for pl in playlists:
        click.echo(f"  {pl.id}")
        click.echo(f"  {pl.name} ({pl.track_count} tracks)")
        if pl.url:
            click.echo(f"  {pl.url}")
        click.echo()


@spotify.command("playlist")
@click.argument("playlist_id")
@click.pass_context
def sp_playlist(ctx: click.Context, playlist_id: str) -> None:
    """View tracks in a Spotify playlist."""
    ctx_obj = ctx.ensure_object(TransmusContext)
    try:
        playlist = ctx_obj.spotify.get_playlist(playlist_id)
    except RuntimeError as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        sys.exit(1)

    click.echo(f"Playlist: {playlist.name}")
    click.echo(f"Tracks: {playlist.track_count}")
    if playlist.description:
        click.echo(f"Description: {playlist.description}")
    click.echo("-" * 60)

    for i, track in enumerate(playlist.tracks, 1):
        click.echo(f"  {i:3d}. {track}")


# ── Transfer Commands ──────────────────────────────────────────────────────


@main.group()
def transfer() -> None:
    """Transfer playlists between music services."""


@transfer.command(name="yt-to-spotify")
@click.argument("playlist_id")
@click.option("--name", "-n", help="New name for the Spotify playlist")
@click.option("--public/--private", default=True, help="Playlist visibility")
@click.pass_context
def transfer_yt_to_spotify(
    ctx: click.Context,
    playlist_id: str,
    name: str | None,
    public: bool,
) -> None:
    """Transfer a YouTube Music playlist to Spotify.

    PLAYLIST_ID is the YouTube Music playlist ID (from 'transmus yt playlists').
    """
    click.echo("Starting transfer: YouTube Music → Spotify")
    click.echo("=" * 50)

    def progress(msg: str, pct: int | None) -> None:
        if pct is not None:
            click.echo(f"[{pct:3d}%] {msg}")
        else:
            click.echo(f"       {msg}")

    try:
        result = transfer_youtube_to_spotify(
            playlist_id=playlist_id,
            new_name=name,
            public=public,
            progress_callback=progress,
        )
    except RuntimeError as e:
        click.secho(f"\nError: {e}", fg="red", bold=True)
        sys.exit(1)

    click.echo()
    click.secho("✓ Transfer Complete!", fg="green", bold=True)
    click.echo(result.summary())


@transfer.command(name="spotify-to-yt")
@click.argument("playlist_id")
@click.option("--name", "-n", help="New name for the YouTube Music playlist")
@click.option("--public/--private", default=True, help="Playlist visibility")
@click.pass_context
def transfer_spotify_to_yt(
    ctx: click.Context,
    playlist_id: str,
    name: str | None,
    public: bool,
) -> None:
    """Transfer a Spotify playlist to YouTube Music.

    PLAYLIST_ID is the Spotify playlist ID (from 'transmus spotify playlists').
    """
    click.echo("Starting transfer: Spotify → YouTube Music")
    click.echo("=" * 50)

    def progress(msg: str, pct: int | None) -> None:
        if pct is not None:
            click.echo(f"[{pct:3d}%] {msg}")
        else:
            click.echo(f"       {msg}")

    try:
        result = transfer_spotify_to_youtube(
            playlist_id=playlist_id,
            new_name=name,
            public=public,
            progress_callback=progress,
        )
    except RuntimeError as e:
        click.secho(f"\nError: {e}", fg="red", bold=True)
        sys.exit(1)

    click.echo()
    click.secho("✓ Transfer Complete!", fg="green", bold=True)
    click.echo(result.summary())


if __name__ == "__main__":
    main()