# Tests

This directory contains tests for slackasme using pytest with mocked Slack API responses.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=slackasme

# Run specific test file
uv run pytest tests/test_validators.py

# Run specific test class
uv run pytest tests/test_commands/test_message.py::TestMessageSend

# Verbose output
uv run pytest -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_client.py           # Client module tests
├── test_config.py           # Config module tests
├── test_validators.py       # Input validation tests
└── test_commands/
    ├── test_auth.py         # auth test/configure/logout
    ├── test_channel.py      # channel list/info
    ├── test_dm.py           # dm open
    ├── test_file.py         # file upload/list
    ├── test_message.py      # message send/list/thread/delete
    ├── test_reaction.py     # reaction add/remove
    ├── test_search.py       # search messages/users
    └── test_user.py         # user list/info
```

## Mocking Pattern

All command tests follow the same pattern:

```python
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from slackasme.cli import cli

def test_example():
    runner = CliRunner()

    # 1. Create mock response matching Slack API structure
    mock_response = MagicMock()
    mock_response.data = {"ok": True, "ts": "1234567890.123456"}
    mock_response.__getitem__ = lambda self, key: mock_response.data[key]

    # 2. Patch token loading and WebClient
    with patch("slackasme.client.load_token", return_value="xoxp-test-token"):
        with patch("slackasme.client.WebClient") as mock_client:
            # 3. Set up the mock API method response
            mock_client.return_value.chat_postMessage.return_value = mock_response

            # 4. Invoke CLI command
            result = runner.invoke(cli, ["message", "send", "general", "Hello!"])

            # 5. Assert results
            assert result.exit_code == 0
            assert "1234567890.123456" in result.output
```

### Key Points

| Concept | Implementation |
|---------|----------------|
| Mock token | `patch("slackasme.client.load_token", return_value="xoxp-...")` |
| Mock Slack SDK | `patch("slackasme.client.WebClient")` |
| Set API response | `mock_client.return_value.<method>.return_value = response` |
| Simulate error | `mock_client.return_value.<method>.side_effect = SlackApiError(...)` |
| Dict access | `mock_response.__getitem__ = lambda self, key: data[key]` |

**Important:** Patch where it's **used** (`slackasme.client.load_token`), not where it's **defined** (`slackasme.config.load_token`).

## Mock Response Examples

Mock responses mirror Slack API structure. Reference: https://api.slack.com/methods

### auth.test
```python
# https://api.slack.com/methods/auth.test
mock_response.data = {
    "ok": True,
    "user": "testuser",
    "user_id": "U12345",
    "team": "TestTeam",
    "team_id": "T12345",
    "url": "https://testteam.slack.com/",
}
```

### chat.postMessage
```python
# https://api.slack.com/methods/chat.postMessage
mock_response.data = {
    "ok": True,
    "ts": "1234567890.123456",
    "channel": "C123",
}
```

### conversations.history
```python
# https://api.slack.com/methods/conversations.history
mock_response.data = {
    "ok": True,
    "messages": [
        {"ts": "1234567890.123456", "user": "U123", "text": "Hello"},
        {"ts": "1234567890.123457", "user": "U456", "text": "World"},
    ],
}
```

### conversations.list
```python
# https://api.slack.com/methods/conversations.list
mock_response.data = {
    "ok": True,
    "channels": [
        {"id": "C123", "name": "general", "num_members": 50, "purpose": {"value": "Chat"}},
    ],
}
```

### conversations.info
```python
# https://api.slack.com/methods/conversations.info
mock_response.data = {
    "ok": True,
    "channel": {
        "id": "C123",
        "name": "general",
        "num_members": 50,
        "purpose": {"value": "General chat"},
        "topic": {"value": "Company discussions"},
        "created": 1234567890,
    },
}
```

### users.list
```python
# https://api.slack.com/methods/users.list
mock_response.data = {
    "ok": True,
    "members": [
        {
            "id": "U123",
            "name": "johndoe",
            "real_name": "John Doe",
            "deleted": False,
            "is_bot": False,
            "profile": {
                "email": "john@example.com",
                "title": "Engineer",
                "status_text": "Working",
            },
        },
    ],
}
```

### users.info
```python
# https://api.slack.com/methods/users.info
mock_response.data = {
    "ok": True,
    "user": {
        "id": "U123",
        "name": "johndoe",
        "real_name": "John Doe",
        "tz": "America/New_York",
        "profile": {
            "email": "john@example.com",
            "title": "Engineer",
            "status_text": "Working",
        },
    },
}
```

### conversations.open (DM)
```python
# https://api.slack.com/methods/conversations.open
mock_response.data = {
    "ok": True,
    "channel": {
        "id": "D123",
        "is_im": True,
        "is_mpim": False,
    },
}
```

### conversations.open (Group DM)
```python
mock_response.data = {
    "ok": True,
    "channel": {
        "id": "G123",
        "is_im": False,
        "is_mpim": True,
    },
}
```

### files.upload_v2
```python
# https://api.slack.com/methods/files.upload
mock_response.data = {
    "ok": True,
    "file": {
        "id": "F123",
        "name": "file.txt",
    },
}
```

### files.list
```python
# https://api.slack.com/methods/files.list
mock_response.data = {
    "ok": True,
    "files": [
        {"id": "F123", "name": "file.txt", "filetype": "text", "size": 1024},
    ],
}
```

### search.messages
```python
# https://api.slack.com/methods/search.messages
mock_response.data = {
    "ok": True,
    "messages": {
        "total": 2,
        "matches": [
            {
                "ts": "1234567890.123456",
                "user": "U123",
                "text": "Found message",
                "channel": {"name": "general"},
            },
        ],
    },
}
```

### reactions.add / reactions.remove
```python
# https://api.slack.com/methods/reactions.add
mock_response.data = {"ok": True}
```

## Error Simulation

To test error handling, use `side_effect`:

```python
from slack_sdk.errors import SlackApiError

# Create error response
mock_error_response = MagicMock()
mock_error_response.get.return_value = "already_reacted"

# Create exception
error = SlackApiError("already_reacted", mock_error_response)

# Make API call raise the exception
mock_client.return_value.reactions_add.side_effect = error
```

Common error codes:
- `invalid_auth` - Invalid token
- `channel_not_found` - Channel doesn't exist
- `already_reacted` - Already added this reaction
- `no_reaction` - No reaction to remove
- `cant_delete_message` - Can't delete this message

## Config Tests

Config tests mock file paths using pytest's `tmp_path` fixture:

```python
def test_saves_token(self, tmp_path):
    config_dir = tmp_path / ".config" / "slackasme"
    token_file = config_dir / "token"

    with patch("slackasme.config.CONFIG_DIR", config_dir):
        with patch("slackasme.config.TOKEN_FILE", token_file):
            save_token("xoxp-test-token")

            assert token_file.read_text() == "xoxp-test-token"
```

## Fixtures (conftest.py)

```python
@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()

@pytest.fixture(autouse=True)
def reset_client_fixture():
    """Reset the global client before/after each test."""
    import slackasme.client
    slackasme.client._client = None
    yield
    slackasme.client._client = None
```

The `reset_client_fixture` is `autouse=True` so it runs for every test automatically, ensuring the global client singleton doesn't leak between tests.
