"""User commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import format_users, output_json
from slackasme.logging import logger
from slackasme.utils.resolution import paginate_until, resolve_user
from slackasme.validators import DEFAULT_LIMIT, validate_limit


@click.group()
def user():
    """List and view users."""
    pass


@user.command("list")
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max users")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_users(limit, as_json):
    """List workspace users.

    Examples:
        slack user list
        slack user list --limit 50
        slack user list --limit 500  # Paginates automatically
    """
    client = get_client()
    logger.info(f"Fetching up to {limit} users")

    try:
        members = paginate_until(client.users_list, "members", limit=limit)

        if as_json:
            output_json({"members": members})
        else:
            format_users(members)

    except SlackApiError as e:
        handle_api_error(e)


@user.command()
@click.argument("identifier")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def info(identifier, as_json):
    """Get user info.

    IDENTIFIER can be @username, email@domain.com, or U12345678.

    Examples:
        slack user info @username
        slack user info user@company.com
        slack user info U12345678
    """
    client = get_client()
    logger.info(f"Fetching info for {identifier}")

    try:
        user_data = resolve_user(client, identifier)

        if not user_data:
            click.echo(f"User not found: {identifier}", err=True)
            return

        if as_json:
            output_json(user_data)
        else:
            click.echo(f"ID: {user_data['id']}")
            click.echo(f"Username: @{user_data.get('name', '-')}")
            click.echo(f"Name: {user_data.get('real_name', '-')}")
            click.echo(f"Email: {user_data.get('profile', {}).get('email', '-')}")
            click.echo(f"Title: {user_data.get('profile', {}).get('title', '-')}")
            click.echo(f"Status: {user_data.get('profile', {}).get('status_text', '-')}")
            click.echo(f"Timezone: {user_data.get('tz', '-')}")

    except SlackApiError as e:
        handle_api_error(e)
