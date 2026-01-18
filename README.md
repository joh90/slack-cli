# slackasme

[![Tests](https://github.com/joh90/slackasme/actions/workflows/test.yml/badge.svg)](https://github.com/joh90/slackasme/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)](tests/)

A command-line interface for Slack that sends messages **as yourself** (not a bot).

Built with the official [Slack Python SDK](https://github.com/slackapi/python-slack-sdk).

## Features

- **Post messages** to channels, DMs, and group DMs
- **Read messages** from any conversation you have access to
- **Reply to threads**
- **Schedule messages** for later
- **Delete your messages**
- **Add/remove reactions**
- **Upload files**
- **Search messages**
- **JSON output** for scripting

## Installation

### Homebrew (macOS/Linux)

```bash
brew tap joh90/tap
brew install slackasme
```

### Binary Download

```bash
# macOS (Apple Silicon)
curl -Lo slack https://github.com/joh90/slackasme/releases/latest/download/slack-darwin-arm64
chmod +x slack && mv slack /usr/local/bin/

# macOS (Intel)
curl -Lo slack https://github.com/joh90/slackasme/releases/latest/download/slack-darwin-amd64
chmod +x slack && mv slack /usr/local/bin/

# Linux (x64)
curl -Lo slack https://github.com/joh90/slackasme/releases/latest/download/slack-linux-amd64
chmod +x slack && mv slack /usr/local/bin/
```

### From Source (Development)

```bash
git clone https://github.com/joh90/slackasme.git
cd slackasme
uv sync
uv run slack --help
```

## Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name it (e.g., "My CLI") and select your workspace

### 2. Add User Token Scopes

Go to **OAuth & Permissions** → **User Token Scopes** and add:

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send/update/delete/schedule messages |
| `channels:history` | Read public channels |
| `channels:read` | List public channels |
| `groups:history` | Read private channels |
| `groups:read` | List private channels |
| `im:history` | Read DMs |
| `im:read` | List DMs |
| `im:write` | Start DMs |
| `mpim:history` | Read group DMs |
| `mpim:read` | List group DMs |
| `mpim:write` | Start group DMs |
| `users:read` | List users |
| `reactions:write` | Add reactions |
| `reactions:read` | View reactions |
| `files:write` | Upload files |
| `files:read` | List files |
| `search:read` | Search messages |

### 3. Install and Get Token

1. Click **Install to Workspace**
2. Copy the **User OAuth Token** (starts with `xoxp-`)

### 4. Configure the CLI

**Option A: Interactive setup (recommended)**

```bash
slack auth configure
```

This stores your token securely at `~/.config/slackasme/token` with `600` permissions.

**Option B: Environment variable**

```bash
export SLACK_USER_TOKEN="xoxp-your-token-here"
```

**Option C: Wrapper script**

```bash
#!/bin/bash
export SLACK_USER_TOKEN="xoxp-your-token-here"
exec slack "$@"
```

### 5. Test Authentication

```bash
slack auth test
```

## Usage

### Messages

```bash
# Send message to channel
slack message send general "Hello team!"
slack message send "#general" "Hello team!"

# Send DM to user
slack message send @username "Hey!"

# Reply in thread
slack message send general "Reply here" --thread 1234567890.123456

# List recent messages
slack message list general
slack message list general --limit 20

# Get thread replies
slack message thread general 1234567890.123456

# Schedule message (Unix timestamp)
slack message schedule general "Reminder!" 1704067200

# Delete message
slack message delete general 1234567890.123456
```

### Channels

```bash
# List channels
slack channel list
slack channel list --type private

# Get channel info
slack channel info general
slack channel info C12345678
```

### Users

```bash
# List users
slack user list

# Get user info (by ID, username, or email)
slack user info U12345678
slack user info @username
slack user info user@example.com
```

### Direct Messages

```bash
# Open DM with user
slack dm open @username
slack dm open U12345678

# Open group DM
slack dm open @user1 @user2 @user3
```

### Reactions

```bash
# Add reaction
slack reaction add general 1234567890.123456 eyes

# Remove reaction
slack reaction remove general 1234567890.123456 eyes
```

### Files

```bash
# Upload file
slack file upload general /path/to/file.png
slack file upload general /path/to/file.png --message "Screenshot"

# List files
slack file list general
```

### Search

```bash
# Search messages
slack search messages "deployment issue"
slack search messages "from:@johnson in:#general"

# Search users
slack search users "johnson"
```

### Auth

```bash
# Test authentication
slack auth test

# Configure token interactively
slack auth configure

# Remove stored token
slack auth logout
```

### Global Options

```bash
# JSON output (for scripting)
slack message list general --json

# Verbose output
slack message send general "Hi" --verbose

# Debug output (includes SDK logs)
slack message list general --debug

# Help
slack --help
slack message --help

# Version
slack --version
```

## Development

### Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Quick Start

```bash
# Clone repository
git clone https://github.com/joh90/slackasme.git
cd slackasme

# Install dependencies with uv
uv sync

# Run CLI
uv run slack --help

# Or install in editable mode
uv pip install -e .
slack --help
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=slackasme

# Run with coverage report
uv run pytest --cov=slackasme --cov-report=html

# Run specific test file
uv run pytest tests/test_validators.py

# Run specific test class
uv run pytest tests/test_commands/test_message.py::TestMessageSend

# Verbose output
uv run pytest -v
```

See [tests/README.md](tests/README.md) for testing conventions and mock patterns.

### Linting

```bash
# Check for issues
uv run ruff check slackasme/

# Auto-fix issues
uv run ruff check slackasme/ --fix

# Format code
uv run ruff format slackasme/
```

### Build Binary

```bash
# Install PyInstaller
uv pip install pyinstaller

# Build single binary
uv run pyinstaller --onefile \
  --name slack \
  --hidden-import slack_sdk \
  --hidden-import click \
  --hidden-import rich \
  slackasme/__main__.py

# Test binary
./dist/slack --version
```

### Releasing

See [RELEASE.md](RELEASE.md) for the release process and automation.

## Project Structure

```
slackasme/
├── slackasme/
│   ├── __init__.py          # Version
│   ├── __main__.py           # Entry point
│   ├── cli.py                # Main CLI (Click)
│   ├── client.py             # Slack API wrapper
│   ├── config.py             # Token storage
│   ├── formatters.py         # Output formatting
│   ├── validators.py         # Input validation
│   ├── logging.py            # Logging setup
│   ├── commands/
│   │   ├── message.py        # message send/list/thread/schedule/delete
│   │   ├── channel.py        # channel list/info
│   │   ├── user.py           # user list/info
│   │   ├── dm.py             # dm open
│   │   ├── reaction.py       # reaction add/remove
│   │   ├── file.py           # file upload/list
│   │   ├── search.py         # search messages/users
│   │   └── auth.py           # auth test/configure/logout
│   └── utils/
│       └── resolution.py     # User/channel resolution
├── tests/
│   ├── README.md             # Testing guide
│   ├── conftest.py           # Pytest fixtures
│   └── test_commands/        # Command tests
├── pyproject.toml
├── Makefile
├── CLAUDE.md                 # Claude Code instructions
├── CHANGELOG.md              # Version history
└── README.md
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- Built with [Slack Python SDK](https://github.com/slackapi/python-slack-sdk)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Pretty output with [Rich](https://github.com/Textualize/rich)
