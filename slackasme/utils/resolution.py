"""User and channel resolution utilities.

Provides smart resolution for user/channel identifiers:
- User ID (U123) -> users.info (fast)
- Email (user@domain.com) -> users.lookupByEmail (fast)
- Username (@name) -> users.list with pagination (fallback)
"""

import re

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slackasme.logging import logger

# Slack ID patterns (typically 9-11 chars, but can vary)
USER_ID_PATTERN = re.compile(r"^U[A-Z0-9]{8,12}$")
# Basic email pattern - not RFC compliant but good enough for detection
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def paginate_until(client_method, result_key, *, limit=None, find_func=None, **kwargs):
    """
    Paginate API calls until limit reached or item found.

    Args:
        client_method: Slack API method to call (e.g., client.users_list)
        result_key: Key in response containing results (e.g., "members")
        limit: Stop after collecting N items (for list commands)
        find_func: Stop when find_func(item) returns True (for lookups)
        **kwargs: Additional arguments to pass to the API method

    Returns:
        - If find_func: The found item, or None if not found
        - If limit: List of items up to limit
        - Otherwise: All items
    """
    results = []
    cursor = None

    while True:
        response = client_method(cursor=cursor, limit=200, **kwargs)

        for item in response[result_key]:
            if find_func:
                if find_func(item):
                    return item  # Early exit - found it!
            else:
                results.append(item)
                if limit and len(results) >= limit:
                    return results[:limit]

        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return None if find_func else results


def resolve_user(client: WebClient, identifier: str) -> dict | None:
    """
    Resolve a user identifier to a user object.

    Resolution order (fastest first):
    1. User ID (U123) -> users.info
    2. Email (user@domain.com) -> users.lookupByEmail
    3. Username (@name or name) -> users.list with paginated search

    Args:
        client: Slack WebClient instance
        identifier: User ID, email, or username

    Returns:
        User dict if found, None otherwise
    """
    identifier = identifier.strip()

    # Strip @ prefix if present
    if identifier.startswith("@"):
        identifier = identifier[1:]

    # 1. User ID - direct lookup (fastest)
    # Slack user IDs: U + 8-12 alphanumeric chars (uppercase)
    if USER_ID_PATTERN.match(identifier.upper()):
        logger.debug(f"Resolving user by ID: {identifier}")
        try:
            response = client.users_info(user=identifier)
            return response["user"]
        except SlackApiError as e:
            if e.response.get("error") == "user_not_found":
                return None
            raise

    # 2. Email - direct lookup (fast)
    if EMAIL_PATTERN.match(identifier):
        logger.debug(f"Resolving user by email: {identifier}")
        try:
            response = client.users_lookupByEmail(email=identifier)
            return response["user"]
        except SlackApiError as e:
            if e.response.get("error") == "users_not_found":
                return None
            raise

    # 3. Username - paginated search (fallback)
    logger.debug(f"Resolving user by name (paginated): {identifier}")
    return paginate_until(
        client.users_list,
        "members",
        find_func=lambda u: u.get("name") == identifier,
    )


def resolve_users(client: WebClient, identifiers: list[str]) -> tuple[list[dict], list[str]]:
    """
    Resolve multiple user identifiers.

    Args:
        client: Slack WebClient instance
        identifiers: List of user IDs, emails, or usernames

    Returns:
        Tuple of (resolved_users, not_found_identifiers)
    """
    resolved = []
    not_found = []

    for identifier in identifiers:
        user = resolve_user(client, identifier)
        if user:
            resolved.append(user)
        else:
            not_found.append(identifier)

    return resolved, not_found
