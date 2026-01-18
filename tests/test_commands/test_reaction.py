"""Tests for reaction commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from slack_sdk.errors import SlackApiError

from slackasme.cli import cli


class TestReactionAdd:
    def test_add_reaction_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True}

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.reactions_add.return_value = mock_response

                result = runner.invoke(
                    cli, ["reaction", "add", "general", "1234567890.123456", "eyes"]
                )

                assert result.exit_code == 0
                assert ":eyes:" in result.output

    def test_add_reaction_already_reacted(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.get.return_value = "already_reacted"

        error = SlackApiError("already_reacted", mock_response)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.reactions_add.side_effect = error

                result = runner.invoke(
                    cli, ["reaction", "add", "general", "1234567890.123456", "eyes"]
                )

                assert result.exit_code == 0
                assert "Already reacted" in result.output


class TestReactionRemove:
    def test_remove_reaction_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True}

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.reactions_remove.return_value = mock_response

                result = runner.invoke(
                    cli, ["reaction", "remove", "general", "1234567890.123456", "eyes"]
                )

                assert result.exit_code == 0
                assert "Removed" in result.output

    def test_remove_reaction_not_found(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.get.return_value = "no_reaction"

        error = SlackApiError("no_reaction", mock_response)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.reactions_remove.side_effect = error

                result = runner.invoke(
                    cli, ["reaction", "remove", "general", "1234567890.123456", "eyes"]
                )

                assert result.exit_code == 0
                assert "No :eyes: reaction" in result.output
