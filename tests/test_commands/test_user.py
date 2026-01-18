"""Tests for user commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slackasme.cli import cli


class TestUserList:
    def test_list_users_success(self):
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
                    "profile": {"status_text": "Working"},
                },
                {
                    "id": "U456",
                    "name": "janedoe",
                    "real_name": "Jane Doe",
                    "deleted": False,
                    "is_bot": False,
                    "profile": {"status_text": ""},
                },
            ],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_response

                result = runner.invoke(cli, ["user", "list"])

                assert result.exit_code == 0

    def test_list_users_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "members": [
                {"id": "U123", "name": "johndoe", "deleted": False, "is_bot": False},
            ],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_response

                result = runner.invoke(cli, ["user", "list", "--json"])

                assert result.exit_code == 0
                assert '"members"' in result.output


class TestUserInfo:
    def test_user_info_by_id(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "user": {
                "id": "U12345678",
                "name": "johndoe",
                "real_name": "John Doe",
                "tz": "America/New_York",
                "profile": {
                    "email": "john@example.com",
                    "title": "Engineer",
                    "status_text": "Working",
                },
            },
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_info.return_value = mock_response

                result = runner.invoke(cli, ["user", "info", "U12345678"])

                assert result.exit_code == 0
                assert "U12345678" in result.output
                assert "johndoe" in result.output

    def test_user_info_by_name(self):
        runner = CliRunner()

        mock_list_response = MagicMock()
        mock_list_response.data = {
            "ok": True,
            "members": [
                {
                    "id": "U123",
                    "name": "johndoe",
                    "real_name": "John Doe",
                    "tz": "America/New_York",
                    "profile": {"email": "john@example.com", "title": "", "status_text": ""},
                },
            ],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_list_response

                result = runner.invoke(cli, ["user", "info", "@johndoe"])

                assert result.exit_code == 0
                assert "U123" in result.output

    def test_user_info_not_found(self):
        runner = CliRunner()

        mock_list_response = MagicMock()
        mock_list_response.data = {
            "ok": True,
            "members": [],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_list_response

                result = runner.invoke(cli, ["user", "info", "nonexistent"])

                assert "not found" in result.output

    def test_user_info_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "user": {
                "id": "U12345678",
                "name": "johndoe",
                "real_name": "John Doe",
                "profile": {},
            },
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_info.return_value = mock_response

                result = runner.invoke(cli, ["user", "info", "U12345678", "--json"])

                assert result.exit_code == 0
                assert '"id": "U12345678"' in result.output
