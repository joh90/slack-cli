"""DM commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import output_json
from slackasme.logging import logger
from slackasme.utils.resolution import resolve_user, resolve_users


@click.group()
def dm():
    """Direct message operations."""
    pass


@dm.command()
@click.argument("users", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def open(users, as_json):
    """Open a DM or group DM with user(s).

    For a single user, opens/returns the DM channel.
    For multiple users, opens/returns a group DM (mpim).

    USERS can be @username, email@domain.com, or U12345678.

    Examples:
        slack dm open @username
        slack dm open user@company.com
        slack dm open U12345678
        slack dm open @user1 @user2 @user3
    """
    client = get_client()
    logger.info(f"Opening DM with {users}")

    try:
        if len(users) == 1:
            # Single user - resolve and open DM
            user = resolve_user(client, users[0])
            if not user:
                click.echo(f"User not found: {users[0]}", err=True)
                return

            response = client.conversations_open(users=user["id"])
        else:
            # Multiple users - resolve all and open group DM (mpim)
            resolved, not_found = resolve_users(client, list(users))

            if not_found:
                click.echo(f"Users not found: {', '.join(not_found)}", err=True)
                return

            user_ids = [u["id"] for u in resolved]
            response = client.conversations_open(users=",".join(user_ids))

        if as_json:
            output_json(response.data)
        else:
            channel = response["channel"]
            click.echo(f"Channel ID: {channel['id']}")
            if channel.get("is_im"):
                click.echo("Type: Direct Message")
            elif channel.get("is_mpim"):
                click.echo("Type: Group DM")

    except SlackApiError as e:
        handle_api_error(e)
