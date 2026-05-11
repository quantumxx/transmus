# Changelog

## [0.2.0] - 2026-05-11

### Changed
- Simplified YouTube Music authentication: users now paste their Cookie directly from browser DevTools instead of installing extensions and creating JSON files
- Removed dead "Get cookies.txt" extension references and links
- Fixed ytmusicapi documentation links
- Added automatic SAPISID hash computation from Cookie value (no manual Authorization header needed)

### Added
- Cookie paste method as the primary authentication flow
- JSON file method retained as a fallback for advanced users

## [0.1.0] - 2026-05-11

### Added
- Initial release of Transmus
- YouTube Music authentication (cookie-based via ytmusicapi)
- Spotify authentication (OAuth via spotipy)
- List playlists from YouTube Music and Spotify
- View tracks in any playlist
- Transfer playlists from YouTube Music → Spotify
- Transfer playlists from Spotify → YouTube Music
- Fuzzy track matching with rapidfuzz (title + artist similarity scoring)
- Progress reporting during transfers
- MIT License