"""Input validation for CLI arguments."""

import os
import re

import click

# Limits
MAX_MESSAGE_LENGTH = 40000  # Slack limit
MAX_SEARCH_QUERY_LENGTH = 1000
MAX_LIMIT = 1000
DEFAULT_LIMIT = 100
MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB


def validate_channel(ctx, param, value):
    """Validate channel format."""
    if not value:
        raise click.BadParameter("Channel cannot be empty")

    # Allow: C123, #general, general, @username, D123, G123
    if not re.match(r"^[@#]?[a-zA-Z0-9._-]+$", value):
        raise click.BadParameter(f"Invalid channel format: {value}")

    if len(value) > 100:
        raise click.BadParameter("Channel name too long")

    return value


def validate_text(ctx, param, value):
    """Validate message text."""
    if not value:
        raise click.BadParameter("Message cannot be empty")

    if len(value) > MAX_MESSAGE_LENGTH:
        raise click.BadParameter(f"Message too long (max {MAX_MESSAGE_LENGTH} chars)")

    return value


def validate_timestamp(ctx, param, value):
    """Validate Slack timestamp format."""
    if not value:
        return value

    # Format: 1234567890.123456
    if not re.match(r"^\d+\.\d+$", value):
        raise click.BadParameter(
            f"Invalid timestamp format: {value} (expected: 1234567890.123456)"
        )

    return value


def validate_emoji(ctx, param, value):
    """Validate emoji name."""
    if not value:
        raise click.BadParameter("Emoji cannot be empty")

    # Allow: eyes, white_check_mark, +1, etc.
    if not re.match(r"^[a-zA-Z0-9_+-]+$", value):
        raise click.BadParameter(f"Invalid emoji format: {value}")

    return value


def validate_file_path(ctx, param, value):
    """Validate file path for upload."""
    # Resolve to absolute path first
    abs_path = os.path.abspath(value)

    if not os.path.exists(abs_path):
        raise click.BadParameter(f"File not found: {value}")

    if os.path.isdir(abs_path):
        raise click.BadParameter(f"Path is a directory: {value}")

    size = os.path.getsize(abs_path)
    if size > MAX_FILE_SIZE:
        raise click.BadParameter(
            f"File too large: {size // 1024 // 1024}MB (max {MAX_FILE_SIZE // 1024 // 1024}MB)"
        )

    if size == 0:
        raise click.BadParameter("File is empty")

    return abs_path


def validate_limit(ctx, param, value):
    """Validate limit parameter."""
    if value < 1:
        raise click.BadParameter("Limit must be at least 1")

    if value > MAX_LIMIT:
        raise click.BadParameter(f"Limit too high (max {MAX_LIMIT})")

    return value


def validate_search_query(ctx, param, value):
    """Validate search query."""
    if not value:
        raise click.BadParameter("Search query cannot be empty")

    if len(value) > MAX_SEARCH_QUERY_LENGTH:
        raise click.BadParameter(f"Search query too long (max {MAX_SEARCH_QUERY_LENGTH} chars)")

    return value
