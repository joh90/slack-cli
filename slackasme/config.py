"""Configuration management with secure token storage."""

import os
import stat
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "slackasme"
TOKEN_FILE = CONFIG_DIR / "token"


def get_config_dir() -> Path:
    """Get or create config directory with secure permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)  # 700 - owner only
    return CONFIG_DIR


def save_token(token: str) -> None:
    """Save token to secure file."""
    get_config_dir()
    TOKEN_FILE.write_text(token)
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600 - owner only


def load_token() -> str | None:
    """Load token from env var or config file."""
    # 1. Check env var first (for CI, wrappers)
    if token := os.environ.get("SLACK_USER_TOKEN"):
        return token

    # 2. Check config file
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()

    return None


def delete_token() -> None:
    """Delete stored token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
