"""Tests for the track matching engine."""

from __future__ import annotations

from transmus.matcher import (
    MATCH_THRESHOLD,
    compute_score,
    find_best_match,
    match_tracks,
    normalize,
)
from transmus.models import Track


class TestNormalize:
    """Tests for text normalization."""

    def test_lowercase(self) -> None:
        assert normalize("Bohemian Rhapsody") == "bohemian rhapsody"

    def test_strip_whitespace(self) -> None:
        assert normalize("  Hello World  ") == "hello world"

    def test_collapse_spaces(self) -> None:
        assert normalize("Hello   World") == "hello world"

    def test_remove_remastered(self) -> None:
        assert normalize("Song (Remastered)") == "song"

    def test_remove_live(self) -> None:
        assert normalize("Song (Live at Wembley)") == "song"

    def test_remove_feat(self) -> None:
        assert normalize("Song feat. Some Artist") == "song"

    def test_remove_ft(self) -> None:
        assert normalize("Song ft. Some Artist") == "song"

    def test_remove_featuring(self) -> None:
        assert normalize("Song featuring Some Artist") == "song"

    def test_remove_deluxe(self) -> None:
        assert normalize("Song (Deluxe Edition)") == "song"

    def test_complex_normalization(self) -> None:
        result = normalize("  Hello (Remastered) feat. World  ")
        assert result == "hello"


class TestComputeScore:
    """Tests for track similarity scoring."""

    def test_exact_match(self) -> None:
        source = Track(title="Bohemian Rhapsody", artist="Queen")
        candidate = Track(title="Bohemian Rhapsody", artist="Queen")
        score = compute_score(source, candidate)
        assert score >= 95  # Should be very close to 100

    def test_partial_match(self) -> None:
        source = Track(title="Bohemian Rhapsody", artist="Queen")
        candidate = Track(title="Bohemian Rhapsody (Remastered 2011)", artist="Queen")
        score = compute_score(source, candidate)
        assert score >= MATCH_THRESHOLD  # Should still match

    def test_different_tracks(self) -> None:
        source = Track(title="Bohemian Rhapsody", artist="Queen")
        candidate = Track(title="Shape of You", artist="Ed Sheeran")
        score = compute_score(source, candidate)
        assert score < MATCH_THRESHOLD  # Should not match

    def test_same_title_different_artist(self) -> None:
        source = Track(title="Hurt", artist="Johnny Cash")
        candidate = Track(title="Hurt", artist="Nine Inch Nails")
        score = compute_score(source, candidate)
        # Same title but different artist - should be borderline
        assert score < 90

    def test_feat_variation(self) -> None:
        source = Track(title="Love Me Like You Do", artist="Ellie Goulding")
        candidate = Track(title="Love Me Like You Do", artist="Ellie Goulding")
        score = compute_score(source, candidate)
        assert score >= 95


class TestFindBestMatch:
    """Tests for finding the best match from candidates."""

    def test_exact_match_found(self) -> None:
        source = Track(title="Bohemian Rhapsody", artist="Queen")
        candidates = [
            Track(title="Some Other Song", artist="Other Artist"),
            Track(title="Bohemian Rhapsody", artist="Queen"),
            Track(title="Another Track", artist="Someone Else"),
        ]
        result = find_best_match(source, candidates)
        assert result is not None
        best, score = result
        assert best.title == "Bohemian Rhapsody"
        assert best.artist == "Queen"
        assert score >= MATCH_THRESHOLD

    def test_no_match(self) -> None:
        source = Track(title="Obscure Track", artist="Unknown Artist")
        candidates = [
            Track(title="Completely Different", artist="Other Artist"),
            Track(title="Nothing Alike", artist="Someone Else"),
        ]
        result = find_best_match(source, candidates)
        assert result is None

    def test_empty_candidates(self) -> None:
        source = Track(title="Test", artist="Test")
        result = find_best_match(source, [])
        assert result is None

    def test_best_match_selected(self) -> None:
        source = Track(title="Bohemian Rhapsody", artist="Queen")
        candidates = [
            Track(title="Bohemian Rhapsody", artist="Queen"),  # Exact
            Track(title="Bohemian Rhapsody (Remastered)", artist="Queen"),  # Close
            Track(title="Rhapsody", artist="Queen"),  # Partial
        ]
        result = find_best_match(source, candidates)
        assert result is not None
        best, _ = result
        # The exact match should be selected
        assert best.title == "Bohemian Rhapsody"


class TestMatchTracks:
    """Tests for bulk track matching."""

    def test_all_matched(self) -> None:
        source_tracks = [
            Track(title="Song A", artist="Artist A"),
            Track(title="Song B", artist="Artist B"),
        ]

        def search_fn(title: str, artist: str) -> list[Track]:
            return [Track(title=title, artist=artist)]

        matched, unmatched = match_tracks(source_tracks, search_fn)
        assert len(matched) == 2
        assert len(unmatched) == 0

    def test_some_unmatched(self) -> None:
        source_tracks = [
            Track(title="Song A", artist="Artist A"),
            Track(title="Obscure Song", artist="Unknown"),
        ]

        def search_fn(title: str, artist: str) -> list[Track]:
            if "Obscure" in title:
                return []
            return [Track(title=title, artist=artist)]

        matched, unmatched = match_tracks(source_tracks, search_fn)
        assert len(matched) == 1
        assert len(unmatched) == 1
        assert unmatched[0].title == "Obscure Song"

    def test_empty_source(self) -> None:
        matched, unmatched = match_tracks([], lambda t, a: [])
        assert len(matched) == 0
        assert len(unmatched) == 0

    def test_progress_callback(self) -> None:
        source_tracks = [
            Track(title="Song A", artist="Artist A"),
            Track(title="Song B", artist="Artist B"),
        ]
        calls: list[bool] = []

        def search_fn(title: str, artist: str) -> list[Track]:
            return [Track(title=title, artist=artist)]

        def progress(track, matched, score):
            calls.append(matched)

        matched, unmatched = match_tracks(source_tracks, search_fn, progress)
        assert len(calls) == 2
        assert all(calls)  # Both should be matched