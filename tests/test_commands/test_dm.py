"""Tests for dm commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slackasme.cli import cli


class TestDmOpen:
    def test_open_dm_single_user_by_id(self):
        runner = CliRunner()

        mock_info_response = MagicMock()
        mock_info_response.data = {"user": {"id": "U12345678", "name": "johndoe"}}
        mock_info_response.__getitem__ = lambda self, key: mock_info_response.data[key]

        mock_dm_response = MagicMock()
        mock_dm_response.data = {
            "ok": True,
            "channel": {"id": "D12345678", "is_im": True, "is_mpim": False},
        }
        mock_dm_response.__getitem__ = lambda self, key: mock_dm_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_info.return_value = mock_info_response
                mock_client.return_value.conversations_open.return_value = mock_dm_response

                result = runner.invoke(cli, ["dm", "open", "U12345678"])

                assert result.exit_code == 0
                assert "D12345678" in result.output
                assert "Direct Message" in result.output

    def test_open_dm_single_user_by_name(self):
        runner = CliRunner()

        mock_users_response = MagicMock()
        mock_users_response.data = {
            "ok": True,
            "members": [{"id": "U12345678", "name": "johndoe"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_users_response.__getitem__ = lambda self, key: mock_users_response.data[key]
        mock_users_response.get = lambda key, default=None: mock_users_response.data.get(key, default)

        mock_dm_response = MagicMock()
        mock_dm_response.data = {
            "ok": True,
            "channel": {"id": "D12345678", "is_im": True, "is_mpim": False},
        }
        mock_dm_response.__getitem__ = lambda self, key: mock_dm_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_users_response
                mock_client.return_value.conversations_open.return_value = mock_dm_response

                result = runner.invoke(cli, ["dm", "open", "@johndoe"])

                assert result.exit_code == 0
                assert "D12345678" in result.output

    def test_open_dm_user_not_found(self):
        runner = CliRunner()

        mock_users_response = MagicMock()
        mock_users_response.data = {
            "ok": True,
            "members": [],
            "response_metadata": {"next_cursor": ""},
        }
        mock_users_response.__getitem__ = lambda self, key: mock_users_response.data[key]
        mock_users_response.get = lambda key, default=None: mock_users_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_users_response

                result = runner.invoke(cli, ["dm", "open", "@nonexistent"])

                assert "not found" in result.output

    def test_open_group_dm(self):
        runner = CliRunner()

        mock_users_response = MagicMock()
        mock_users_response.data = {
            "ok": True,
            "members": [
                {"id": "U12345678", "name": "user1"},
                {"id": "U87654321", "name": "user2"},
            ],
            "response_metadata": {"next_cursor": ""},
        }
        mock_users_response.__getitem__ = lambda self, key: mock_users_response.data[key]
        mock_users_response.get = lambda key, default=None: mock_users_response.data.get(key, default)

        mock_dm_response = MagicMock()
        mock_dm_response.data = {
            "ok": True,
            "channel": {"id": "G12345678", "is_im": False, "is_mpim": True},
        }
        mock_dm_response.__getitem__ = lambda self, key: mock_dm_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_users_response
                mock_client.return_value.conversations_open.return_value = mock_dm_response

                result = runner.invoke(cli, ["dm", "open", "@user1", "@user2"])

                assert result.exit_code == 0
                assert "G12345678" in result.output
                assert "Group DM" in result.output

    def test_open_group_dm_user_not_found(self):
        runner = CliRunner()

        mock_users_response = MagicMock()
        mock_users_response.data = {
            "ok": True,
            "members": [{"id": "U12345678", "name": "user1"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_users_response.__getitem__ = lambda self, key: mock_users_response.data[key]
        mock_users_response.get = lambda key, default=None: mock_users_response.data.get(key, default)

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_list.return_value = mock_users_response

                result = runner.invoke(cli, ["dm", "open", "@user1", "@nonexistent"])

                assert "not found" in result.output

    def test_open_dm_json(self):
        runner = CliRunner()

        mock_info_response = MagicMock()
        mock_info_response.data = {"user": {"id": "U12345678", "name": "johndoe"}}
        mock_info_response.__getitem__ = lambda self, key: mock_info_response.data[key]

        mock_dm_response = MagicMock()
        mock_dm_response.data = {
            "ok": True,
            "channel": {"id": "D12345678", "is_im": True},
        }

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.users_info.return_value = mock_info_response
                mock_client.return_value.conversations_open.return_value = mock_dm_response

                result = runner.invoke(cli, ["dm", "open", "U12345678", "--json"])

                assert result.exit_code == 0
                assert '"ok": true' in result.output
