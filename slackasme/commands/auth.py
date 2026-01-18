"""Auth commands."""

import click
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error, mask_token
from slackasme.config import delete_token, load_token, save_token
from slackasme.formatters import output_json
from slackasme.logging import logger


@click.group()
def auth():
    """Manage authentication."""
    pass


@auth.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def test(as_json):
    """Test authentication and show user info.

    Examples:
        slack auth test
    """
    client = get_client()
    logger.info("Testing authentication")

    try:
        response = client.auth_test()

        if as_json:
            output_json(response.data)
        else:
            click.echo(f"Authenticated as: {response['user']} ({response['user_id']})")
            click.echo(f"Workspace: {response['team']} ({response['team_id']})")
            click.echo(f"URL: {response['url']}")

    except SlackApiError as e:
        handle_api_error(e)


@auth.command()
def configure():
    """Configure Slack token interactively.

    The token will be stored securely in ~/.config/slackasme/token
    with 600 permissions (owner read/write only).

    Examples:
        slack auth configure
    """
    click.echo("Slack CLI Configuration")
    click.echo("-" * 40)
    click.echo()
    click.echo("To get your token:")
    click.echo("1. Go to https://api.slack.com/apps")
    click.echo("2. Select your app (or create one)")
    click.echo("3. Go to OAuth & Permissions")
    click.echo("4. Copy the 'User OAuth Token' (starts with xoxp-)")
    click.echo()

    token = click.prompt("Enter your Slack User OAuth Token", hide_input=True)

    if not token.startswith("xoxp-"):
        click.echo("Warning: Token should start with 'xoxp-' for user tokens", err=True)
        if not click.confirm("Continue anyway?"):
            return

    # Validate token
    click.echo("Validating token...")
    client = WebClient(token=token)

    try:
        response = client.auth_test()
        click.echo(f"Authenticated as: {response['user']} @ {response['team']}")
    except SlackApiError as e:
        click.echo(f"Invalid token: {mask_token(str(e))}", err=True)
        return

    # Save token
    save_token(token)
    click.echo()
    click.echo("Token saved to ~/.config/slackasme/token")
    click.echo("You can now use: slack message send general 'Hello!'")


@auth.command()
def logout():
    """Remove stored token.

    Examples:
        slack auth logout
    """
    if load_token():
        delete_token()
        click.echo("Token removed")
    else:
        click.echo("No token configured")
