"""Slack client wrapper with rate limiting and error handling."""

import re
import sys

import click
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

from slackasme.config import load_token

_client = None


def mask_token(text: str) -> str:
    """Mask any xoxp-/xoxb- tokens in text."""
    return re.sub(r"xox[bp]-[a-zA-Z0-9-]+", "xox*-****", str(text))


def get_client() -> WebClient:
    """Get or create Slack client with retry handling."""
    global _client

    if _client is None:
        token = load_token()

        if not token:
            click.echo("Error: No Slack token configured.", err=True)
            click.echo("Run: slack auth configure", err=True)
            sys.exit(1)

        _client = WebClient(token=token)
        # Add rate limit retry handler
        _client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=3))

    return _client


def reset_client() -> None:
    """Reset client (for testing)."""
    global _client
    _client = None


def handle_api_error(e: SlackApiError) -> None:
    """Handle Slack API errors with masked output."""
    error_msg = mask_token(str(e))

    if e.response.get("error") in ["invalid_auth", "token_revoked", "account_inactive"]:
        click.echo(f"Authentication error: {error_msg}", err=True)
        click.echo("Run: slack auth configure", err=True)
        sys.exit(1)

    click.echo(f"Slack API error: {error_msg}", err=True)
    sys.exit(1)
