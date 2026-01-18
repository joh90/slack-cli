"""Tests for file commands."""

import tempfile
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from slack_cli.cli import cli


class TestFileUpload:
    def test_upload_file_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "file": {"id": "F123", "name": "test.txt"},
        }
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            filepath = f.name

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.return_value = mock_response

                result = runner.invoke(cli, ["file", "upload", "general", filepath])

                assert result.exit_code == 0
                assert "Uploaded" in result.output
                assert "F123" in result.output

    def test_upload_file_with_message(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "file": {"id": "F123", "name": "test.txt"},
        }
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            filepath = f.name

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.return_value = mock_response

                result = runner.invoke(
                    cli, ["file", "upload", "general", filepath, "-m", "Here's the file"]
                )

                assert result.exit_code == 0
                mock_client.return_value.files_upload_v2.assert_called_once()
                call_kwargs = mock_client.return_value.files_upload_v2.call_args[1]
                assert call_kwargs["initial_comment"] == "Here's the file"


class TestFileList:
    def test_list_files_success(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "files": [
                {"id": "F123", "name": "file1.txt", "filetype": "text", "size": 1024},
                {"id": "F456", "name": "file2.png", "filetype": "png", "size": 2048000},
            ],
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.files_list.return_value = mock_response

                result = runner.invoke(cli, ["file", "list", "general"])

                assert result.exit_code == 0

    def test_list_files_json(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {
            "ok": True,
            "files": [{"id": "F123", "name": "file1.txt"}],
        }

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.files_list.return_value = mock_response

                result = runner.invoke(cli, ["file", "list", "general", "--json"])

                assert result.exit_code == 0
                assert '"ok": true' in result.output

    def test_list_files_empty(self):
        runner = CliRunner()

        mock_response = MagicMock()
        mock_response.data = {"ok": True, "files": []}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]

        with patch("slack_cli.client.load_token", return_value="xoxp-test-token"):
            with patch("slack_cli.client.WebClient") as mock_client:
                mock_client.return_value.files_list.return_value = mock_response

                result = runner.invoke(cli, ["file", "list", "general"])

                assert result.exit_code == 0
                assert "No files found" in result.output
