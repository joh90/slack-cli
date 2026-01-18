"""Tests for resolution utilities with pagination."""

from unittest.mock import MagicMock, patch, call

import pytest

from slackasme.utils.resolution import paginate_until, resolve_user, resolve_users


class TestPaginateUntil:
    """Test paginate_until utility."""

    def test_single_page_no_cursor(self):
        """Test with single page (no next_cursor)."""
        mock_response = MagicMock()
        mock_response.data = {
            "members": [{"id": "U1"}, {"id": "U2"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        mock_method = MagicMock(return_value=mock_response)

        result = paginate_until(mock_method, "members", limit=10)

        assert len(result) == 2
        assert result[0]["id"] == "U1"
        mock_method.assert_called_once()

    def test_multiple_pages_with_cursor(self):
        """Test pagination across multiple pages."""
        # First page - has next_cursor
        mock_response1 = MagicMock()
        mock_response1.data = {
            "members": [{"id": "U1"}, {"id": "U2"}],
            "response_metadata": {"next_cursor": "cursor_page_2"},
        }
        mock_response1.__getitem__ = lambda self, key: mock_response1.data[key]
        mock_response1.get = lambda key, default=None: mock_response1.data.get(key, default)

        # Second page - no next_cursor (last page)
        mock_response2 = MagicMock()
        mock_response2.data = {
            "members": [{"id": "U3"}, {"id": "U4"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response2.__getitem__ = lambda self, key: mock_response2.data[key]
        mock_response2.get = lambda key, default=None: mock_response2.data.get(key, default)

        mock_method = MagicMock(side_effect=[mock_response1, mock_response2])

        result = paginate_until(mock_method, "members", limit=10)

        assert len(result) == 4
        assert [r["id"] for r in result] == ["U1", "U2", "U3", "U4"]
        assert mock_method.call_count == 2
        # Verify cursor was passed on second call
        mock_method.assert_any_call(cursor=None, limit=200)
        mock_method.assert_any_call(cursor="cursor_page_2", limit=200)

    def test_limit_stops_pagination(self):
        """Test that limit stops pagination before exhausting pages."""
        # First page
        mock_response1 = MagicMock()
        mock_response1.data = {
            "members": [{"id": "U1"}, {"id": "U2"}, {"id": "U3"}],
            "response_metadata": {"next_cursor": "cursor_page_2"},
        }
        mock_response1.__getitem__ = lambda self, key: mock_response1.data[key]
        mock_response1.get = lambda key, default=None: mock_response1.data.get(key, default)

        mock_method = MagicMock(return_value=mock_response1)

        # Request only 2 items
        result = paginate_until(mock_method, "members", limit=2)

        assert len(result) == 2
        assert [r["id"] for r in result] == ["U1", "U2"]
        # Should NOT make second call since limit was reached
        mock_method.assert_called_once()

    def test_find_func_early_exit(self):
        """Test early exit when find_func matches."""
        mock_response = MagicMock()
        mock_response.data = {
            "members": [{"id": "U1", "name": "alice"}, {"id": "U2", "name": "bob"}],
            "response_metadata": {"next_cursor": "cursor_page_2"},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        mock_method = MagicMock(return_value=mock_response)

        # Find "bob" - should return immediately without fetching more pages
        result = paginate_until(
            mock_method, "members", find_func=lambda u: u.get("name") == "bob"
        )

        assert result["id"] == "U2"
        assert result["name"] == "bob"
        mock_method.assert_called_once()

    def test_find_func_across_pages(self):
        """Test find_func that matches on second page."""
        # First page - no match
        mock_response1 = MagicMock()
        mock_response1.data = {
            "members": [{"id": "U1", "name": "alice"}],
            "response_metadata": {"next_cursor": "cursor_page_2"},
        }
        mock_response1.__getitem__ = lambda self, key: mock_response1.data[key]
        mock_response1.get = lambda key, default=None: mock_response1.data.get(key, default)

        # Second page - has match
        mock_response2 = MagicMock()
        mock_response2.data = {
            "members": [{"id": "U2", "name": "bob"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response2.__getitem__ = lambda self, key: mock_response2.data[key]
        mock_response2.get = lambda key, default=None: mock_response2.data.get(key, default)

        mock_method = MagicMock(side_effect=[mock_response1, mock_response2])

        result = paginate_until(
            mock_method, "members", find_func=lambda u: u.get("name") == "bob"
        )

        assert result["name"] == "bob"
        assert mock_method.call_count == 2

    def test_find_func_not_found(self):
        """Test find_func returns None when not found."""
        mock_response = MagicMock()
        mock_response.data = {
            "members": [{"id": "U1", "name": "alice"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_response.get = lambda key, default=None: mock_response.data.get(key, default)

        mock_method = MagicMock(return_value=mock_response)

        result = paginate_until(
            mock_method, "members", find_func=lambda u: u.get("name") == "nonexistent"
        )

        assert result is None


class TestResolveUser:
    """Test resolve_user smart resolution."""

    def test_resolve_by_user_id(self):
        """Test resolution by valid user ID (9-11 chars)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = {"user": {"id": "U12345678", "name": "johndoe"}}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_client.users_info.return_value = mock_response

        result = resolve_user(mock_client, "U12345678")

        assert result["id"] == "U12345678"
        mock_client.users_info.assert_called_once_with(user="U12345678")
        # Should NOT call users_list or lookupByEmail
        mock_client.users_list.assert_not_called()
        mock_client.users_lookupByEmail.assert_not_called()

    def test_short_user_id_falls_back_to_username(self):
        """Test that short IDs like 'U123' are treated as usernames."""
        mock_client = MagicMock()
        mock_list_response = MagicMock()
        mock_list_response.data = {
            "members": [{"id": "UREAL12345", "name": "U123"}],  # Username happens to be U123
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)
        mock_client.users_list.return_value = mock_list_response

        result = resolve_user(mock_client, "U123")

        # Should fall back to username search, not users.info
        mock_client.users_info.assert_not_called()
        mock_client.users_list.assert_called()
        assert result["name"] == "U123"

    def test_resolve_by_email(self):
        """Test resolution by valid email."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = {"user": {"id": "U12345678", "name": "johndoe"}}
        mock_response.__getitem__ = lambda self, key: mock_response.data[key]
        mock_client.users_lookupByEmail.return_value = mock_response

        result = resolve_user(mock_client, "john@example.com")

        assert result["id"] == "U12345678"
        mock_client.users_lookupByEmail.assert_called_once_with(email="john@example.com")
        # Should NOT call users_info or users_list
        mock_client.users_info.assert_not_called()
        mock_client.users_list.assert_not_called()

    def test_invalid_email_falls_back_to_username(self):
        """Test that invalid emails like 'foo@bar.' fall back to username search."""
        mock_client = MagicMock()
        mock_list_response = MagicMock()
        mock_list_response.data = {
            "members": [],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)
        mock_client.users_list.return_value = mock_list_response

        # These should NOT be detected as emails
        for invalid in ["foo@bar.", "@.x", "noat.com", "spaces @test.com"]:
            mock_client.reset_mock()
            resolve_user(mock_client, invalid)
            mock_client.users_lookupByEmail.assert_not_called()
            mock_client.users_list.assert_called()

    def test_resolve_by_username_fallback(self):
        """Test resolution by username (paginated fallback)."""
        mock_client = MagicMock()
        mock_list_response = MagicMock()
        mock_list_response.data = {
            "members": [{"id": "U123", "name": "johndoe"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)
        mock_client.users_list.return_value = mock_list_response

        result = resolve_user(mock_client, "johndoe")

        assert result["id"] == "U123"
        mock_client.users_list.assert_called()
        # Should NOT call users_info or lookupByEmail
        mock_client.users_info.assert_not_called()
        mock_client.users_lookupByEmail.assert_not_called()

    def test_resolve_strips_at_prefix(self):
        """Test that @ prefix is stripped from username."""
        mock_client = MagicMock()
        mock_list_response = MagicMock()
        mock_list_response.data = {
            "members": [{"id": "U123", "name": "johndoe"}],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)
        mock_client.users_list.return_value = mock_list_response

        result = resolve_user(mock_client, "@johndoe")

        assert result["id"] == "U123"


class TestResolveUsers:
    """Test resolve_users for multiple users."""

    def test_resolve_multiple_users(self):
        """Test resolving multiple users."""
        mock_client = MagicMock()

        # User 1 - by ID (valid length)
        mock_info_response = MagicMock()
        mock_info_response.data = {"user": {"id": "U12345678", "name": "user1"}}
        mock_info_response.__getitem__ = lambda self, key: mock_info_response.data[key]
        mock_client.users_info.return_value = mock_info_response

        # User 2 - by email
        mock_email_response = MagicMock()
        mock_email_response.data = {"user": {"id": "U87654321", "name": "user2"}}
        mock_email_response.__getitem__ = lambda self, key: mock_email_response.data[key]
        mock_client.users_lookupByEmail.return_value = mock_email_response

        resolved, not_found = resolve_users(mock_client, ["U12345678", "user2@example.com"])

        assert len(resolved) == 2
        assert len(not_found) == 0
        assert resolved[0]["id"] == "U12345678"
        assert resolved[1]["id"] == "U87654321"

    def test_resolve_users_with_not_found(self):
        """Test resolving users where some are not found."""
        mock_client = MagicMock()

        # User 1 - found (valid ID length)
        mock_info_response = MagicMock()
        mock_info_response.data = {"user": {"id": "U12345678", "name": "user1"}}
        mock_info_response.__getitem__ = lambda self, key: mock_info_response.data[key]
        mock_client.users_info.return_value = mock_info_response

        # User 2 - not found (username search)
        mock_list_response = MagicMock()
        mock_list_response.data = {
            "members": [],
            "response_metadata": {"next_cursor": ""},
        }
        mock_list_response.__getitem__ = lambda self, key: mock_list_response.data[key]
        mock_list_response.get = lambda key, default=None: mock_list_response.data.get(key, default)
        mock_client.users_list.return_value = mock_list_response

        resolved, not_found = resolve_users(mock_client, ["U12345678", "nonexistent"])

        assert len(resolved) == 1
        assert len(not_found) == 1
        assert resolved[0]["id"] == "U12345678"
        assert not_found[0] == "nonexistent"
