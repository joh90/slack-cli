"""Tests for channel commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slackasme.cli import cli


class TestChannelList:
    def test_list_channels_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "channels": [
                {"id": "C123", "name": "general", "num_members": 50, "purpose": {"value": "Chat"}},
                {"id": "C456", "name": "random", "num_members": 30, "purpose": {"value": "Random"}},
            ],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.conversations_list.return_value = mock_response

                result = runner.invoke(cli, ["channel", "list"])

                assert result.exit_code == 0

    def test_list_private_channels(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "channels": [],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.conversations_list.return_value = mock_response

                result = runner.invoke(cli, ["channel", "list", "--type", "private"])

                assert result.exit_code == 0
                mock_client.return_value.conversations_list.assert_called_once()
                call_kwargs = mock_client.return_value.conversations_list.call_args[1]
                assert call_kwargs["types"] == "private_channel"


class TestChannelInfo:
    def test_channel_info_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "channel": {
                "id": "C123",
                "name": "general",
                "num_members": 50,
                "purpose": {"value": "General chat"},
                "topic": {"value": "Company-wide discussions"},
                "created": 1234567890,
            },
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.conversations_info.return_value = mock_response

                result = runner.invoke(cli, ["channel", "info", "general"])

                assert result.exit_code == 0
                assert "C123" in result.output
                assert "general" in result.output
