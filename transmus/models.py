"""Data models for Transmus."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Track:
    """Represents a single music track."""

    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    source_id: Optional[str] = None
    source_uri: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"

    @property
    def normalized_title(self) -> str:
        """Return a normalized version of the title for matching."""
        return _normalize(self.title)

    @property
    def normalized_artist(self) -> str:
        """Return a normalized version of the artist for matching."""
        return _normalize(self.artist)


@dataclass
class Playlist:
    """Represents a music playlist."""

    id: str
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    track_count: int = 0
    url: Optional[str] = None
    tracks: list[Track] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.track_count} tracks)"


@dataclass
class TransferResult:
    """Result of a playlist transfer operation."""

    source_playlist: Playlist
    destination_name: str
    matched_tracks: list[Track] = field(default_factory=list)
    unmatched_tracks: list[Track] = field(default_factory=list)
    destination_url: Optional[str] = None

    @property
    def total(self) -> int:
        return len(self.matched_tracks) + len(self.unmatched_tracks)

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (len(self.matched_tracks) / self.total) * 100

    def summary(self) -> str:
        """Return a human-readable summary of the transfer."""
        lines = [
            f"Transfer complete: {self.destination_name}",
            f"  ✓ {len(self.matched_tracks)}/{self.total} tracks transferred",
            f"  Success rate: {self.success_rate:.0f}%",
        ]
        if self.destination_url:
            lines.append(f"  URL: {self.destination_url}")
        if self.unmatched_tracks:
            lines.append("")
            lines.append("  Unmatched tracks:")
            for track in self.unmatched_tracks:
                lines.append(f"    ✗ {track}")
        return "\n".join(lines)


def _normalize(text: str) -> str:
    """Normalize text for fuzzy matching.

    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse multiple spaces
    """
    import re

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text