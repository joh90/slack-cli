"""Tests for client module."""

from slack_cli.client import mask_token


class TestMaskToken:
    def test_mask_user_token(self):
        text = "Error: invalid_auth xoxp-1234-5678-abcd-efgh"
        result = mask_token(text)
        assert "xoxp-1234" not in result
        assert "xox*-****" in result

    def test_mask_bot_token(self):
        text = "Token: xoxb-9876-5432-wxyz"
        result = mask_token(text)
        assert "xoxb-9876" not in result
        assert "xox*-****" in result

    def test_mask_multiple_tokens(self):
        text = "Tokens: xoxp-111 and xoxb-222"
        result = mask_token(text)
        assert "xoxp-111" not in result
        assert "xoxb-222" not in result

    def test_no_token(self):
        text = "No token here"
        result = mask_token(text)
        assert result == "No token here"
