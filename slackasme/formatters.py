"""Output formatters."""

import json
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

console = Console()


def output_json(data: dict) -> None:
    """Output data as formatted JSON."""
    click.echo(json.dumps(data, indent=2, default=str))


def format_messages(messages: list) -> None:
    """Format messages as a table."""
    if not messages:
        click.echo("No messages found")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Time", style="dim", width=12)
    table.add_column("User", width=15)
    table.add_column("Message")
    table.add_column("TS", style="dim", width=18)

    for msg in reversed(messages):  # Oldest first
        ts = datetime.fromtimestamp(float(msg["ts"]))
        time_str = ts.strftime("%H:%M:%S")
        user = msg.get("user", msg.get("username", "bot"))
        text = msg.get("text", "")[:100]  # Truncate long messages

        table.add_row(time_str, user, text, msg["ts"])

    console.print(table)


def format_channels(channels: list) -> None:
    """Format channels as a table."""
    if not channels:
        click.echo("No channels found")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Members", justify="right")
    table.add_column("Purpose")

    for chan in channels:
        table.add_row(
            chan["id"],
            f"#{chan['name']}",
            str(chan.get("num_members", "-")),
            chan.get("purpose", {}).get("value", "")[:50],
        )

    console.print(table)


def format_users(users: list) -> None:
    """Format users as a table."""
    if not users:
        click.echo("No users found")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Username")
    table.add_column("Name")
    table.add_column("Status")

    for user in users:
        if user.get("deleted") or user.get("is_bot"):
            continue
        table.add_row(
            user["id"],
            f"@{user.get('name', '')}",
            user.get("real_name", ""),
            user.get("profile", {}).get("status_text", "")[:30],
        )

    console.print(table)


def format_files(files: list) -> None:
    """Format files as a table."""
    if not files:
        click.echo("No files found")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Size", justify="right")

    for f in files:
        size = f.get("size", 0)
        if size > 1024 * 1024:
            size_str = f"{size // 1024 // 1024}MB"
        elif size > 1024:
            size_str = f"{size // 1024}KB"
        else:
            size_str = f"{size}B"

        table.add_row(
            f["id"],
            f.get("name", "")[:40],
            f.get("filetype", "-"),
            size_str,
        )

    console.print(table)


def format_search_results(matches: list) -> None:
    """Format search results as a table."""
    if not matches:
        click.echo("No results found")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Channel", width=15)
    table.add_column("User", width=12)
    table.add_column("Message")
    table.add_column("TS", style="dim", width=18)

    for match in matches:
        channel_name = match.get("channel", {}).get("name", "-")
        user = match.get("user", "-")
        text = match.get("text", "")[:80]
        ts = match.get("ts", "-")

        table.add_row(f"#{channel_name}", user, text, ts)

    console.print(table)
