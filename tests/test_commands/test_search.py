"""Tests for search commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slack_cli.cli import cli


class TestSearchMessages:
    def test_search_messages_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "messages": {
                "total": 2,
                "matches": [
                    {
                        "ts": "1234567890.123456",
                        "user": "U123",
                        "text": "Found message 1",
                        "channel": {"name": "general"},
                    },
                    {
                        "ts": "1234567890.123457",
                        "user": "U456",
                        "text": "Found message 2",
                        "channel": {"name": "random"},
                    },
                ],
            },
        }
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.search_messages.return_value = mock_response

                result = runner.invoke(cli, ["search", "messages", "test query"])

                assert result.exit_code == 0
                assert "Total matches: 2" in result.output

    def test_search_messages_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "messages": {"total": 1, "matches": []},
        }

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.search_messages.return_value = mock_response

                result = runner.invoke(cli, ["search", "messages", "test", "--json"])

                assert result.exit_code == 0
                assert '"ok": true' in result.output

    def test_search_messages_no_results(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "messages": {"total": 0, "matches": []},
        }
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.search_messages.return_value = mock_response

                result = runner.invoke(cli, ["search", "messages", "nonexistent"])

                assert result.exit_code == 0
                assert "No results found" in result.output


class TestSearchUsers:
    def test_search_users_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "members": [
                {
                    "id": "U123",
                    "name": "johndoe",
                    "real_name": "John Doe",
                    "deleted": False,
                    "is_bot": False,
                    "profile": {"title": "Engineer", "status_text": ""},
                },
                {
                    "id": "U456",
                    "name": "johnsmith",
                    "real_name": "John Smith",
                    "deleted": False,
                    "is_bot": False,
                    "profile": {"title": "Designer", "status_text": ""},
                },
            ],
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_response

                result = runner.invoke(cli, ["search", "users", "john"])

                assert result.exit_code == 0
                assert "Found: 2 users" in result.output

    def test_search_users_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "members": [
                {"id": "U123", "name": "johndoe", "deleted": False, "is_bot": False},
            ],
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_response

                result = runner.invoke(cli, ["search", "users", "john", "--json"])

                assert result.exit_code == 0
                assert '"members"' in result.output

    def test_search_users_no_results(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True, "members": []}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_response

                result = runner.invoke(cli, ["search", "users", "nonexistent"])

                assert result.exit_code == 0
                assert "No users found" in result.output or "Found: 0 users" in result.output
