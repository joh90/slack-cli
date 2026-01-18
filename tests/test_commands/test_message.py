"""Tests for message commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slackasme.cli import cli


class TestMessageSend:
    def test_send_message_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True, "ts": "1234567890.123456"}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.chat_postMessage.return_value = mock_response

                result = runner.invoke(cli, ["message", "send", "general", "Hello!"])

                assert result.exit_code == 0
                assert "1234567890.123456" in result.output

    def test_send_message_with_thread(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True, "ts": "1234567890.654321"}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.chat_postMessage.return_value = mock_response

                result = runner.invoke(
                    cli,
                    ["message", "send", "general", "Reply", "--thread", "1234567890.123456"],
                )

                assert result.exit_code == 0
                mock_client.return_value.chat_postMessage.assert_called_once_with(
                    channel="general",
                    text="Reply",
                    thread_ts="1234567890.123456",
                )


class TestMessageList:
    def test_list_messages_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "messages": [
                {"ts": "1234567890.123456", "user": "U123", "text": "Hello"},
                {"ts": "1234567890.123457", "user": "U456", "text": "World"},
            ],
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.conversations_history.return_value = mock_response

                result = runner.invoke(cli, ["message", "list", "general"])

                assert result.exit_code == 0

    def test_list_messages_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "messages": [
                {"ts": "1234567890.123456", "user": "U123", "text": "Hello"},
            ],
        }

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.conversations_history.return_value = mock_response

                result = runner.invoke(cli, ["message", "list", "general", "--json"])

                assert result.exit_code == 0
                assert '"ok": true' in result.output


class TestMessageDelete:
    def test_delete_message_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.chat_delete.return_value = mock_response

                result = runner.invoke(
                    cli, ["message", "delete", "general", "1234567890.123456"]
                )

                assert result.exit_code == 0
                assert "deleted" in result.output
