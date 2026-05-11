"""Tests for configuration management."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from transmus import config


class TestConfig:
    """Tests for configuration management."""

    def test_default_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return defaults when no config file exists."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", Path("/tmp/nonexistent/.transmus"))
            cfg = config.load_config()
            assert cfg["default_playlist_visibility"] == "public"
            assert cfg["version"] == "0.1.0"

    def test_save_and_load_config(self, temp_config_dir: Path) -> None:
        """Should save and load config correctly."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", temp_config_dir)
            config.save_config({"spotify_client_id": "test-id"})
            cfg = config.load_config()
            assert cfg["spotify_client_id"] == "test-id"
            assert cfg["default_playlist_visibility"] == "public"

    def test_get_set_config(self, temp_config_dir: Path) -> None:
        """Should get and set individual config values."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", temp_config_dir)
            config.set_config("test_key", "test_value")
            assert config.get_config("test_key") == "test_value"
            assert config.get_config("nonexistent", "default") == "default"

    def test_youtube_headers(self, temp_config_dir: Path) -> None:
        """Should save and load YouTube headers."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", temp_config_dir)
            headers = {"Cookie": "test", "Authorization": "test"}
            config.save_youtube_headers(headers)
            loaded = config.load_youtube_headers()
            assert loaded == headers

    def test_clear_youtube_headers(self, temp_config_dir: Path) -> None:
        """Should clear YouTube headers."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", temp_config_dir)
            config.save_youtube_headers({"Cookie": "test"})
            assert config.is_youtube_authenticated()
            config.clear_youtube_headers()
            assert not config.is_youtube_authenticated()

    def test_auth_status(self, temp_config_dir: Path) -> None:
        """Should correctly report auth status."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(config, "CONFIG_DIR", temp_config_dir)
            assert not config.is_youtube_authenticated()
            assert not config.is_spotify_authenticated()

            config.save_youtube_headers({
                "Cookie": "test",
                "X-Goog-AuthUser": "0",
                "X-Goog-Visitor-Id": "test",
                "Authorization": "test",
            })
            assert config.is_youtube_authenticated()