#!/usr/bin/env python3
"""Slack CLI - Send messages as yourself."""

import click

from slackasme import __version__
from slackasme.commands import auth, channel, dm, file, message, reaction, search, user
from slackasme.logging import setup_logging


@click.group()
@click.version_option(version=__version__, prog_name="slack")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--debug", is_flag=True, help="Debug output")
@click.pass_context
def cli(ctx, verbose, debug):
    """Slack CLI - Interact with Slack as yourself."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    setup_logging(verbose=verbose, debug=debug)


# Register command groups
cli.add_command(message.message)
cli.add_command(channel.channel)
cli.add_command(user.user)
cli.add_command(dm.dm)
cli.add_command(reaction.reaction)
cli.add_command(file.file)
cli.add_command(search.search)
cli.add_command(auth.auth)


if __name__ == "__main__":
    cli()
