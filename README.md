# Transmus 🎵

**Transfer music playlists between YouTube Music and Spotify — free, open-source, CLI-based.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Transmus is a Python CLI tool that lets you transfer your playlists between YouTube Music and Spotify (and vice versa). No servers, no subscriptions, no data collection — it runs entirely on your machine.

---

## Features

- **Bidirectional transfer** — YouTube Music → Spotify and Spotify → YouTube Music
- **Liked Songs support** — Transfer your Liked Songs / Liked Music between platforms
- **Smart track matching** — Uses fuzzy matching (rapidfuzz) to find the best match even when titles differ
- **No server costs** — Runs locally on your machine, completely free
- **Privacy-first** — No data collection, no telemetry, everything stays on your computer
- **Progress reporting** — See real-time progress during transfers

## Prerequisites

- **Python 3.10 or higher**
- **A Spotify Developer App** (free, created at [developer.spotify.com](https://developer.spotify.com/dashboard))
- **YouTube Music browser cookies** (exported via browser extension)

## Installation

```bash
# Clone the repository
git clone https://github.com/raj-mohan/transmus.git
cd transmus

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # On Linux/Mac
# venv\Scripts\activate     # On Windows

# Install
pip install -e .
```

## Quick Start

### 1. Set up YouTube Music

```bash
transmus auth youtube
```

This will guide you through exporting your YouTube Music browser cookies. You'll need a browser extension like [Cookie-Editor](https://cookie-editor.com/) or [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid) to export your YouTube Music session headers.

### 2. Set up Spotify

```bash
transmus auth spotify
```

You'll need to:
1. Create a free app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Add `http://localhost:8888/callback` as a Redirect URI
3. Enter your Client ID and Client Secret when prompted

Alternatively, set environment variables:
```bash
export SPOTIFY_CLIENT_ID="your-client-id"
export SPOTIFY_CLIENT_SECRET="your-client-secret"
```

### 3. Check authentication status

```bash
transmus status
```

### 4. List your playlists

```bash
# List YouTube Music playlists
transmus yt playlists

# List Spotify playlists
transmus spotify playlists
```

### 5. View your Liked Songs

```bash
# View YouTube Music Liked Songs
transmus yt liked

# View Spotify Liked Songs
transmus spotify liked
```

### 6. Transfer a playlist

```bash
# YouTube Music → Spotify
transmus transfer yt-to-spotify PLAYLIST_ID

# Spotify → YouTube Music
transmus transfer spotify-to-yt PLAYLIST_ID
```

### 7. Transfer your Liked Songs

```bash
# YouTube Music Liked Songs → Spotify
transmus transfer yt-liked-to-spotify

# Spotify Liked Songs → YouTube Music
transmus transfer spotify-liked-to-yt
```

## Command Reference

| Command | Description |
|---------|-------------|
| `transmus auth youtube` | Set up YouTube Music authentication |
| `transmus auth spotify` | Set up Spotify authentication |
| `transmus status` | Check authentication status |
| `transmus yt playlists` | List YouTube Music playlists |
| `transmus yt playlist <id>` | View tracks in a YT Music playlist |
| `transmus yt liked` | View your YouTube Music Liked Songs |
| `transmus spotify playlists` | List Spotify playlists |
| `transmus spotify playlist <id>` | View tracks in a Spotify playlist |
| `transmus spotify liked` | View your Spotify Liked Songs |
| `transmus transfer yt-to-spotify <id>` | Transfer YT Music → Spotify |
| `transmus transfer spotify-to-yt <id>` | Transfer Spotify → YT Music |
| `transmus transfer yt-liked-to-spotify` | Transfer YT Liked Songs → Spotify |
| `transmus transfer spotify-liked-to-yt` | Transfer Spotify Liked Songs → YT |

### Options

- `--name, -n` — Custom name for the destination playlist
- `--public / --private` — Set playlist visibility (default: public)

## How It Works

1. **Authentication**: YouTube Music uses browser cookies (no official API), Spotify uses OAuth
2. **Playlist Reading**: Fetches all tracks from the source playlist
3. **Track Matching**: For each track, searches the destination platform and scores matches using fuzzy string matching (title 60% + artist 40%)
4. **Playlist Creation**: Creates a new playlist on the destination and adds all matched tracks
5. **Reporting**: Shows which tracks were transferred and which couldn't be found

## Configuration

Configuration is stored in `~/.transmus/`:
- `config.json` — General settings
- `youtube_headers.json` — YouTube Music auth headers (sensitive)
- `spotify_cache/` — Spotify OAuth token cache

## Troubleshooting

### "YouTube Music not authenticated"
Run `transmus auth youtube` and ensure your browser cookies are valid (not expired).

### "Spotify not configured"
Run `transmus auth spotify` or set `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` environment variables.

### Many tracks not matched
The fuzzy matcher uses a 75% similarity threshold. Some tracks with very different titles or artists may not match. You can adjust the threshold in `transmus/matcher.py` (`MATCH_THRESHOLD`).

## Tech Stack

- **Python 3.10+** — Core language
- **click** — CLI framework
- **ytmusicapi** — YouTube Music API (unofficial)
- **spotipy** — Spotify Web API wrapper
- **rapidfuzz** — Fuzzy string matching

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.