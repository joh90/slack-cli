"""Search commands."""

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import format_search_results, format_users, output_json
from slackasme.logging import logger
from slackasme.validators import DEFAULT_LIMIT, validate_limit, validate_search_query


@click.group()
def search():
    """Search messages and users."""
    pass


@search.command()
@click.argument("query", callback=validate_search_query)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def messages(query, limit, as_json):
    """Search messages.

    Supports Slack search modifiers like:
    - from:@username
    - in:#channel
    - before:2024-01-01
    - after:2024-01-01

    Examples:
        slack search messages "deployment issue"
        slack search messages "from:@johnson in:#general"
    """
    client = get_client()
    logger.info(f"Searching: {query}")

    try:
        response = client.search_messages(query=query, count=limit)

        if as_json:
            output_json(response.data)
        else:
            matches = response.get("messages", {}).get("matches", [])
            format_search_results(matches)
            total = response.get("messages", {}).get("total", 0)
            click.echo(f"\nTotal matches: {total}")

    except SlackApiError as e:
        handle_api_error(e)


@search.command()
@click.argument("query", callback=validate_search_query)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def users(query, limit, as_json):
    """Search users by name.

    Examples:
        slack search users "johnson"
        slack search users "engineering"
    """
    client = get_client()
    logger.info(f"Searching users: {query}")

    try:
        # Slack doesn't have a direct user search API, so we list and filter
        response = client.users_list(limit=1000)

        query_lower = query.lower()
        matches = [
            u
            for u in response["members"]
            if not u.get("deleted")
            and not u.get("is_bot")
            and (
                query_lower in u.get("name", "").lower()
                or query_lower in u.get("real_name", "").lower()
                or query_lower in u.get("profile", {}).get("title", "").lower()
            )
        ][:limit]

        if as_json:
            output_json({"members": matches})
        else:
            format_users(matches)
            click.echo(f"\nFound: {len(matches)} users")

    except SlackApiError as e:
        handle_api_error(e)
