"""Tests for auth commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slackasme.cli import cli


class TestAuthTest:
    def test_auth_test_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "user": "testuser",
            "user_id": "U12345",
            "team": "TestTeam",
            "team_id": "T12345",
            "url": "https://testteam.slack.com/",
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.auth_test.return_value = mock_response

                result = runner.invoke(cli, ["auth", "test"])

                assert result.exit_code == 0
                assert "testuser" in result.output
                assert "TestTeam" in result.output

    def test_auth_test_json_output(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "user": "testuser",
            "user_id": "U12345",
            "team": "TestTeam",
            "team_id": "T12345",
            "url": "https://testteam.slack.com/",
        }

        with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
            with patch("slackasme.client.WebClient") as mock_client:
                mock_client.return_value.auth_test.return_value = mock_response

                result = runner.invoke(cli, ["auth", "test", "--json"])

                assert result.exit_code == 0
                assert '"user": "testuser"' in result.output


class TestAuthLogout:
    def test_logout_with_token(self):
        runner = CliRunner()

        with patch("slackasme.commands.auth.load_token", return_value="xoxp-token"):
            with patch("slackasme.commands.auth.delete_token") as mock_delete:
                result = runner.invoke(cli, ["auth", "logout"])

                assert result.exit_code == 0
                assert "removed" in result.output
                mock_delete.assert_called_once()

    def test_logout_no_token(self):
        runner = CliRunner()

        with patch("slackasme.commands.auth.load_token", return_value=None):
            result = runner.invoke(cli, ["auth", "logout"])

            assert result.exit_code == 0
            assert "No token configured" in result.output
