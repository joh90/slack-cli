"""Reaction commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import output_json
from slackasme.logging import logger
from slackasme.validators import validate_channel, validate_emoji, validate_timestamp


@click.group()
def reaction():
    """Add and remove reactions."""
    pass


@reaction.command()
@click.argument("channel", callback=validate_channel)
@click.argument("timestamp", callback=validate_timestamp)
@click.argument("emoji", callback=validate_emoji)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def add(channel, timestamp, emoji, as_json):
    """Add a reaction to a message.

    Examples:
        slack reaction add general 1234567890.123456 eyes
        slack reaction add general 1234567890.123456 white_check_mark
        slack reaction add general 1234567890.123456 +1
    """
    client = get_client()
    logger.info(f"Adding :{emoji}: to {channel}/{timestamp}")

    try:
        response = client.reactions_add(channel=channel, timestamp=timestamp, name=emoji)

        if as_json:
            output_json(response.data)
        else:
            click.echo(f"Added :{emoji}:")

    except SlackApiError as e:
        if e.response.get("error") == "already_reacted":
            click.echo(f"Already reacted with :{emoji}:")
        else:
            handle_api_error(e)


@reaction.command()
@click.argument("channel", callback=validate_channel)
@click.argument("timestamp", callback=validate_timestamp)
@click.argument("emoji", callback=validate_emoji)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def remove(channel, timestamp, emoji, as_json):
    """Remove a reaction from a message.

    Examples:
        slack reaction remove general 1234567890.123456 eyes
    """
    client = get_client()
    logger.info(f"Removing :{emoji}: from {channel}/{timestamp}")

    try:
        response = client.reactions_remove(channel=channel, timestamp=timestamp, name=emoji)

        if as_json:
            output_json(response.data)
        else:
            click.echo(f"Removed :{emoji}:")

    except SlackApiError as e:
        if e.response.get("error") == "no_reaction":
            click.echo(f"No :{emoji}: reaction to remove")
        else:
            handle_api_error(e)
