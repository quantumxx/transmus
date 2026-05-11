"""Track matching engine for Transmus.

Uses rapidfuzz to find the best matching track on the destination platform
by comparing title and artist similarity.
"""

from __future__ import annotations

import re
from typing import Optional

from rapidfuzz import fuzz

from transmus.models import Track

# Minimum similarity score (0-100) to consider a match valid
MATCH_THRESHOLD = 75

# Title weight vs artist weight in composite score
TITLE_WEIGHT = 0.6
ARTIST_WEIGHT = 0.4


def normalize(text: str) -> str:
    """Normalize text for fuzzy matching.

    - Lowercase
    - Strip whitespace
    - Collapse multiple spaces
    - Remove common parenthetical suffixes (remaster, live, etc.)
    - Remove "feat.", "ft.", "featuring" and following text
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    # Remove parenthetical qualifiers like (Remastered), (Live), etc.
    text = re.sub(
        r"\(.*?(remaster|live|deluxe|edit|version|mix|mono|stereo|anniversary|expanded).*?\)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove "feat." / "ft." / "featuring" and what follows
    text = re.sub(
        r"\s+(feat\.|ft\.|featuring)\s+.*$", "", text, flags=re.IGNORECASE
    )

    return text.strip()


def compute_score(source: Track, candidate: Track) -> float:
    """Compute a composite similarity score between source and candidate tracks.

    Uses token_sort_ratio which is robust to word reordering.

    Args:
        source: The source track.
        candidate: A candidate match track.

    Returns:
        A score from 0 to 100.
    """
    title_score = fuzz.token_sort_ratio(
        normalize(source.title), normalize(candidate.title)
    )
    artist_score = fuzz.token_sort_ratio(
        normalize(source.artist), normalize(candidate.artist)
    )

    return (title_score * TITLE_WEIGHT) + (artist_score * ARTIST_WEIGHT)


def find_best_match(
    source: Track, candidates: list[Track]
) -> Optional[tuple[Track, float]]:
    """Find the best matching track from a list of candidates.

    Args:
        source: The source track to match.
        candidates: List of candidate tracks from the destination platform.

    Returns:
        Tuple of (best_match_track, score) if a match above threshold is found,
        or None if no candidate meets the threshold.
    """
    if not candidates:
        return None

    best_score = 0.0
    best_match: Optional[Track] = None

    for candidate in candidates:
        score = compute_score(source, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_match and best_score >= MATCH_THRESHOLD:
        return (best_match, best_score)

    return None


def match_tracks(
    source_tracks: list[Track],
    search_fn,
    progress_callback=None,
) -> tuple[list[tuple[Track, Track]], list[Track]]:
    """Match a list of source tracks against a destination platform.

    Args:
        source_tracks: List of tracks to match.
        search_fn: Async function that takes (title, artist) and returns
                   a list of candidate Track objects.
        progress_callback: Optional callback(track, matched, score) for progress.

    Returns:
        Tuple of:
        - List of (source_track, matched_track) for successful matches
        - List of source_tracks that could not be matched
    """
    matched: list[tuple[Track, Track]] = []
    unmatched: list[Track] = []

    for i, track in enumerate(source_tracks):
        candidates = search_fn(track.title, track.artist)
        if not candidates:
            unmatched.append(track)
            if progress_callback:
                progress_callback(track, False, 0.0)
            continue

        result = find_best_match(track, candidates)
        if result:
            best_match, score = result
            matched.append((track, best_match))
            if progress_callback:
                progress_callback(track, True, score)
        else:
            unmatched.append(track)
            if progress_callback:
                progress_callback(track, False, 0.0)

    return matched, unmatched