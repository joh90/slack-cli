"""Pytest fixtures for slackasme tests."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Provide a mocked Slack WebClient."""
    with patch("slackasme.client.WebClient") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_token(tmp_path):
    """Set up a temporary token file."""
    config_dir = tmp_path / ".config" / "slackasme"
    config_dir.mkdir(parents=True)
    token_file = config_dir / "token"
    token_file.write_text("xoxp-test-token-12345")

    with patch("slackasme.config.CONFIG_DIR", config_dir):
        with patch("slackasme.config.TOKEN_FILE", token_file):
            yield token_file


@pytest.fixture(autouse=True)
def reset_client_fixture():
    """Reset the global client before and after each test."""
    import slackasme.client
    slackasme.client._client = None
    yield
    slackasme.client._client = None
