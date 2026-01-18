"""Tests for validators module."""

import os
import tempfile

import click
import pytest

from slack_cli.validators import (
    validate_channel,
    validate_emoji,
    validate_file_path,
    validate_limit,
    validate_search_query,
    validate_text,
    validate_timestamp,
)


class TestValidateChannel:
    def test_valid_channel_name(self):
        assert validate_channel(None, None, "general") == "general"

    def test_valid_channel_with_hash(self):
        assert validate_channel(None, None, "#general") == "#general"

    def test_valid_channel_id(self):
        assert validate_channel(None, None, "C12345678") == "C12345678"

    def test_valid_dm_user(self):
        assert validate_channel(None, None, "@username") == "@username"

    def test_empty_channel(self):
        with pytest.raises(click.BadParameter, match="cannot be empty"):
            validate_channel(None, None, "")

    def test_channel_too_long(self):
        with pytest.raises(click.BadParameter, match="too long"):
            validate_channel(None, None, "a" * 101)

    def test_invalid_characters(self):
        with pytest.raises(click.BadParameter, match="Invalid channel format"):
            validate_channel(None, None, "chan<>nel")


class TestValidateText:
    def test_valid_text(self):
        assert validate_text(None, None, "Hello world") == "Hello world"

    def test_empty_text(self):
        with pytest.raises(click.BadParameter, match="cannot be empty"):
            validate_text(None, None, "")

    def test_text_too_long(self):
        with pytest.raises(click.BadParameter, match="too long"):
            validate_text(None, None, "a" * 40001)


class TestValidateTimestamp:
    def test_valid_timestamp(self):
        assert validate_timestamp(None, None, "1234567890.123456") == "1234567890.123456"

    def test_empty_timestamp(self):
        assert validate_timestamp(None, None, None) is None
        assert validate_timestamp(None, None, "") == ""

    def test_invalid_timestamp(self):
        with pytest.raises(click.BadParameter, match="Invalid timestamp format"):
            validate_timestamp(None, None, "12345")

    def test_invalid_timestamp_no_dot(self):
        with pytest.raises(click.BadParameter, match="Invalid timestamp format"):
            validate_timestamp(None, None, "1234567890123456")


class TestValidateEmoji:
    def test_valid_emoji(self):
        assert validate_emoji(None, None, "eyes") == "eyes"
        assert validate_emoji(None, None, "white_check_mark") == "white_check_mark"
        assert validate_emoji(None, None, "+1") == "+1"

    def test_empty_emoji(self):
        with pytest.raises(click.BadParameter, match="cannot be empty"):
            validate_emoji(None, None, "")

    def test_invalid_emoji(self):
        with pytest.raises(click.BadParameter, match="Invalid emoji format"):
            validate_emoji(None, None, ":eyes:")


class TestValidateFilePath:
    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            result = validate_file_path(None, None, path)
            assert os.path.isabs(result)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(click.BadParameter, match="not found"):
            validate_file_path(None, None, "/nonexistent/file.txt")

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name

        try:
            with pytest.raises(click.BadParameter, match="empty"):
                validate_file_path(None, None, path)
        finally:
            os.unlink(path)

    def test_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises(click.BadParameter, match="directory"):
                validate_file_path(None, None, d)


class TestValidateLimit:
    def test_valid_limit(self):
        assert validate_limit(None, None, 100) == 100

    def test_limit_too_low(self):
        with pytest.raises(click.BadParameter, match="at least 1"):
            validate_limit(None, None, 0)

    def test_limit_too_high(self):
        with pytest.raises(click.BadParameter, match="too high"):
            validate_limit(None, None, 1001)


class TestValidateSearchQuery:
    def test_valid_query(self):
        assert validate_search_query(None, None, "test query") == "test query"

    def test_empty_query(self):
        with pytest.raises(click.BadParameter, match="cannot be empty"):
            validate_search_query(None, None, "")

    def test_query_too_long(self):
        with pytest.raises(click.BadParameter, match="too long"):
            validate_search_query(None, None, "a" * 1001)
