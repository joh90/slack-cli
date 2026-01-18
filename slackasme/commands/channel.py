"""Channel commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import format_channels, output_json
from slackasme.logging import logger
from slackasme.utils.resolution import paginate_until
from slackasme.validators import DEFAULT_LIMIT, validate_channel, validate_limit


@click.group()
def channel():
    """List and view channels."""
    pass


@channel.command("list")
@click.option(
    "--type",
    "channel_type",
    type=click.Choice(["public", "private", "mpim", "im"]),
    default="public",
    help="Channel type to list",
)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max channels")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_channels(channel_type, limit, as_json):
    """List channels.

    Examples:
        slack channel list
        slack channel list --type private
        slack channel list --limit 500  # Paginates automatically
    """
    client = get_client()
    logger.info(f"Fetching up to {limit} {channel_type} channels")

    # Map type to API types parameter
    type_map = {
        "public": "public_channel",
        "private": "private_channel",
        "mpim": "mpim",
        "im": "im",
    }

    try:
        channels = paginate_until(
            client.conversations_list,
            "channels",
            limit=limit,
            types=type_map[channel_type],
        )

        if as_json:
            output_json({"channels": channels})
        else:
            format_channels(channels)

    except SlackApiError as e:
        handle_api_error(e)


@channel.command()
@click.argument("channel", callback=validate_channel)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def info(channel, as_json):
    """Get channel info.

    Examples:
        slack channel info general
        slack channel info C12345678
    """
    client = get_client()
    logger.info(f"Fetching info for {channel}")

    try:
        response = client.conversations_info(channel=channel)

        if as_json:
            output_json(response.data)
        else:
            ch = response["channel"]
            click.echo(f"ID: {ch['id']}")
            click.echo(f"Name: #{ch.get('name', 'DM')}")
            click.echo(f"Members: {ch.get('num_members', '-')}")
            click.echo(f"Purpose: {ch.get('purpose', {}).get('value', '-')}")
            click.echo(f"Topic: {ch.get('topic', {}).get('value', '-')}")
            click.echo(f"Created: {ch.get('created', '-')}")

    except SlackApiError as e:
        handle_api_error(e)
