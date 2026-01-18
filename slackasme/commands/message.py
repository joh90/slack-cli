"""Message commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import format_messages, output_json
from slackasme.logging import logger
from slackasme.validators import (
    DEFAULT_LIMIT,
    validate_channel,
    validate_limit,
    validate_text,
    validate_timestamp,
)


@click.group()
def message():
    """Send and read messages."""
    pass


@message.command()
@click.argument("channel", callback=validate_channel)
@click.argument("text", callback=validate_text)
@click.option("--thread", "-t", callback=validate_timestamp, help="Thread timestamp to reply to")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def send(channel, text, thread, as_json):
    """Send a message to a channel or user.

    Examples:
        slack message send general "Hello team!"
        slack message send @username "Direct message"
        slack message send general "Reply" --thread 1234567890.123456
    """
    client = get_client()
    logger.info(f"Sending message to {channel}")

    try:
        response = client.chat_postMessage(channel=channel, text=text, thread_ts=thread)

        if as_json:
            output_json(response.data)
        else:
            click.echo(f"Message sent: {response['ts']}")

    except SlackApiError as e:
        handle_api_error(e)


@message.command("list")
@click.argument("channel", callback=validate_channel)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max messages")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_messages(channel, limit, as_json):
    """List recent messages in a channel.

    Examples:
        slack message list general
        slack message list general --limit 20
    """
    client = get_client()
    logger.info(f"Fetching {limit} messages from {channel}")

    try:
        response = client.conversations_history(channel=channel, limit=limit)

        if as_json:
            output_json(response.data)
        else:
            format_messages(response["messages"])

    except SlackApiError as e:
        handle_api_error(e)


@message.command()
@click.argument("channel", callback=validate_channel)
@click.argument("thread_ts", callback=validate_timestamp)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max replies")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def thread(channel, thread_ts, limit, as_json):
    """Get replies in a thread.

    Examples:
        slack message thread general 1234567890.123456
    """
    client = get_client()
    logger.info(f"Fetching thread {thread_ts} from {channel}")

    try:
        response = client.conversations_replies(channel=channel, ts=thread_ts, limit=limit)

        if as_json:
            output_json(response.data)
        else:
            format_messages(response["messages"])

    except SlackApiError as e:
        handle_api_error(e)


@message.command()
@click.argument("channel", callback=validate_channel)
@click.argument("text", callback=validate_text)
@click.argument("post_at", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def schedule(channel, text, post_at, as_json):
    """Schedule a message for later.

    POST_AT is a Unix timestamp (seconds since epoch).

    Examples:
        slack message schedule general "Reminder!" 1704067200
    """
    client = get_client()
    logger.info(f"Scheduling message to {channel} at {post_at}")

    try:
        response = client.chat_scheduleMessage(channel=channel, text=text, post_at=post_at)

        if as_json:
            output_json(response.data)
        else:
            click.echo(f"Scheduled: {response['scheduled_message_id']}")

    except SlackApiError as e:
        handle_api_error(e)


@message.command()
@click.argument("channel", callback=validate_channel)
@click.argument("timestamp", callback=validate_timestamp)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def delete(channel, timestamp, as_json):
    """Delete a message you sent.

    Examples:
        slack message delete general 1234567890.123456
    """
    client = get_client()
    logger.info(f"Deleting message {timestamp} from {channel}")

    try:
        response = client.chat_delete(channel=channel, ts=timestamp)

        if as_json:
            output_json(response.data)
        else:
            click.echo("Message deleted")

    except SlackApiError as e:
        handle_api_error(e)
