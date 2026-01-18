"""File commands."""

import os

import click
from slack_sdk.errors import SlackApiError

from slackasme.client import get_client, handle_api_error
from slackasme.formatters import format_files, output_json
from slackasme.logging import logger
from slackasme.validators import DEFAULT_LIMIT, validate_channel, validate_file_path, validate_limit


@click.group()
def file():
    """Upload and list files."""
    pass


@file.command()
@click.argument("channel", callback=validate_channel)
@click.argument("filepath", callback=validate_file_path)
@click.option("--message", "-m", help="Message to include with file")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def upload(channel, filepath, message, as_json):
    """Upload a file to a channel.

    Examples:
        slack file upload general /path/to/file.png
        slack file upload general /path/to/file.png --message "Screenshot"
    """
    client = get_client()
    filename = os.path.basename(filepath)
    logger.info(f"Uploading {filename} to {channel}")

    try:
        response = client.files_upload_v2(
            channel=channel,
            file=filepath,
            filename=filename,
            initial_comment=message,
        )

        if as_json:
            output_json(response.data)
        else:
            file_info = response.get("file", {})
            click.echo(f"Uploaded: {file_info.get('name', filename)}")
            click.echo(f"File ID: {file_info.get('id', '-')}")

    except SlackApiError as e:
        handle_api_error(e)


@file.command("list")
@click.argument("channel", callback=validate_channel)
@click.option("--limit", "-n", default=DEFAULT_LIMIT, callback=validate_limit, help="Max files")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_files(channel, limit, as_json):
    """List files in a channel.

    Examples:
        slack file list general
        slack file list general --limit 20
    """
    client = get_client()
    logger.info(f"Fetching files from {channel}")

    try:
        response = client.files_list(channel=channel, count=limit)

        if as_json:
            output_json(response.data)
        else:
            format_files(response["files"])

    except SlackApiError as e:
        handle_api_error(e)
