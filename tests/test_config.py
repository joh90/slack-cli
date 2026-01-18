"""Tests for config module."""

import os
import stat
from unittest.mock import patch

from slackasme.config import delete_token, get_config_dir, load_token, save_token


class TestGetConfigDir:
    def test_creates_directory(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            result = get_config_dir()

            assert result == config_dir
            assert config_dir.exists()
            # Check permissions (700 = owner rwx only)
            assert stat.S_IMODE(config_dir.stat().st_mode) == 0o700


class TestSaveToken:
    def test_saves_token_with_permissions(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        token_file = config_dir / "token"

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            with patch("slackasme.config.TOKEN_FILE", token_file):
                save_token("xoxp-test-token-12345")

                assert token_file.exists()
                assert token_file.read_text() == "xoxp-test-token-12345"
                # Check permissions (600 = owner rw only)
                assert stat.S_IMODE(token_file.stat().st_mode) == 0o600


class TestLoadToken:
    def test_loads_from_env_var(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        token_file = config_dir / "token"

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            with patch("slackasme.config.TOKEN_FILE", token_file):
                with patch.dict(os.environ, {"SLACK_USER_TOKEN": "xoxp-env-token"}):
                    result = load_token()
                    assert result == "xoxp-env-token"

    def test_loads_from_file(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token"
        token_file.write_text("xoxp-file-token")

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            with patch("slackasme.config.TOKEN_FILE", token_file):
                with patch.dict(os.environ, {}, clear=True):
                    # Remove SLACK_USER_TOKEN if present
                    os.environ.pop("SLACK_USER_TOKEN", None)
                    result = load_token()
                    assert result == "xoxp-file-token"

    def test_returns_none_if_no_token(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        token_file = config_dir / "token"

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            with patch("slackasme.config.TOKEN_FILE", token_file):
                with patch.dict(os.environ, {}, clear=True):
                    os.environ.pop("SLACK_USER_TOKEN", None)
                    result = load_token()
                    assert result is None

    def test_env_var_takes_priority(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token"
        token_file.write_text("xoxp-file-token")

        with patch("slackasme.config.CONFIG_DIR", config_dir):
            with patch("slackasme.config.TOKEN_FILE", token_file):
                with patch.dict(os.environ, {"SLACK_USER_TOKEN": "xoxp-env-token"}):
                    result = load_token()
                    assert result == "xoxp-env-token"


class TestDeleteToken:
    def test_deletes_existing_token(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token"
        token_file.write_text("xoxp-test-token")

        with patch("slackasme.config.TOKEN_FILE", token_file):
            delete_token()

            assert not token_file.exists()

    def test_handles_missing_file(self, tmp_path):
        config_dir = tmp_path / ".config" / "slackasme"
        token_file = config_dir / "token"

        with patch("slackasme.config.TOKEN_FILE", token_file):
            # Should not raise
            delete_token()
