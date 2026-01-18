"""Logging setup for CLI."""

import logging
import sys

logger = logging.getLogger("slackasme")


def setup_logging(verbose: bool = False, debug: bool = False):
    """Configure logging based on flags."""
    if debug:
        level = logging.DEBUG
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    elif verbose:
        level = logging.INFO
        fmt = "%(levelname)s: %(message)s"
    else:
        level = logging.WARNING
        fmt = "%(message)s"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))

    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)

    # Also configure slack_sdk logger in debug mode
    if debug:
        slack_logger = logging.getLogger("slack_sdk")
        slack_logger.setLevel(logging.DEBUG)
        slack_logger.handlers.clear()
        slack_logger.addHandler(handler)
