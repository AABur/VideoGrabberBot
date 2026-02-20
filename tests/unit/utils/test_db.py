"""Tests for the database module."""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from bot.utils.db import (
    add_user,
    create_invite,
    deactivate_user,
    get_all_users,
    init_db,
    is_user_authorized,
    use_invite,
)


@pytest_asyncio.fixture
async def temp_db(monkeypatch):
    """Create a temporary database for testing."""
    # Create temp directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = Path(temp_dir) / "test_bot.db"
        # Patch DB_PATH in the db module
        from bot.utils import db as db_module

        monkeypatch.setattr(db_module, "DB_PATH", temp_db_path)

        # Initialize database
        await init_db()

        yield temp_db_path


@pytest.mark.asyncio
async def test_add_user(temp_db):
    """Test adding users to the database."""
    # Add a new user
    result1 = await add_user(123456789, "testuser", 987654321)
    assert result1 is True

    # Try to add the same user again
    result2 = await add_user(123456789, "testuser_updated", 987654321)
    assert result2 is False

    # Check if user is authorized
    is_auth = await is_user_authorized(123456789)
    assert is_auth is True


@pytest.mark.asyncio
async def test_add_user_exception(temp_db, mocker):
    """Test handling exception when adding a user."""
    # Mock aiosqlite.connect to raise an exception
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    success = await add_user(123456789, "testuser", 987654321)
    assert success is False


@pytest.mark.asyncio
async def test_get_all_users(temp_db):
    """Test retrieving all users."""
    # Add multiple users
    await add_user(111, "user1", 999)
    await add_user(222, "user2", 999)
    await add_user(333, "user3", 999)

    # Get all users
    users = await get_all_users()

    # Verify user count
    assert len(users) >= 3

    # Verify user data
    user_ids = [user["id"] for user in users]
    assert 111 in user_ids
    assert 222 in user_ids
    assert 333 in user_ids


@pytest.mark.asyncio
async def test_get_all_users_exception(temp_db, mocker):
    """Test exception handling when retrieving users."""
    # Mock aiosqlite.connect to raise an exception
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    users = await get_all_users()
    assert users == []


@pytest.mark.asyncio
async def test_deactivate_user(temp_db):
    """Test deactivating a user."""
    # Add a user
    await add_user(123456789, "testuser", 987654321)

    # Verify user is initially authorized
    assert await is_user_authorized(123456789) is True

    # Deactivate the user
    success = await deactivate_user(123456789)
    assert success is True

    # Verify user is no longer authorized
    assert await is_user_authorized(123456789) is False


@pytest.mark.asyncio
async def test_deactivate_user_exception(temp_db, mocker):
    """Test exception handling when deactivating a user."""
    # Mock aiosqlite.connect to raise an exception
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    success = await deactivate_user(123456789)
    assert success is False


@pytest.mark.asyncio
async def test_is_user_authorized_exception(temp_db, mocker):
    """Test exception handling when checking if a user is authorized."""
    # Mock aiosqlite.connect to raise an exception
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    is_auth = await is_user_authorized(123456789)
    assert is_auth is False


@pytest.mark.asyncio
async def test_invite_create_and_exceptions(mocker):
    """Test creating invites and exception handling."""
    # Normal case with mock
    mock_connect = mocker.patch("aiosqlite.connect")
    mocker.patch("uuid.uuid4", return_value="test-uuid")

    # Configure mock connection and cursor
    mock_cursor = mocker.AsyncMock()
    mock_conn = mocker.AsyncMock()
    mock_conn.execute = mocker.AsyncMock(return_value=mock_cursor)
    mock_conn.__aenter__.return_value = mock_conn
    mock_connect.return_value = mock_conn

    # Create invite
    invite_id = await create_invite(987654321)
    assert invite_id == "test-uuid"

    # Verify db calls
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

    # Reset mock for exception case
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    invite_id = await create_invite(987654321)
    assert invite_id is None


@pytest.mark.asyncio
async def test_use_invite_and_exceptions(mocker):
    """Test using invites and exception handling."""
    # Case 1: invite exists, user is new (4 execute calls)
    mock_connect = mocker.patch("aiosqlite.connect")

    invite_cursor = mocker.AsyncMock()
    invite_cursor.fetchone.return_value = ["test-invite-id"]  # Invite exists

    user_cursor = mocker.AsyncMock()
    user_cursor.fetchone.return_value = None  # User doesn't exist yet

    mock_conn = mocker.AsyncMock()
    mock_conn.execute = mocker.AsyncMock(
        side_effect=[
            invite_cursor,       # SELECT FROM invites
            mocker.AsyncMock(),  # UPDATE invites SET used_by ...
            user_cursor,         # SELECT FROM users
            mocker.AsyncMock(),  # INSERT INTO users
        ]
    )
    mock_conn.__aenter__.return_value = mock_conn
    mock_connect.return_value = mock_conn

    success = await use_invite("test-invite-id", 123456789)
    assert success is True
    assert mock_conn.execute.call_count == 4
    mock_conn.commit.assert_called_once()

    # Case 2: invite doesn't exist (1 execute call, early return)
    no_invite_cursor = mocker.AsyncMock()
    no_invite_cursor.fetchone.return_value = None

    mock_conn2 = mocker.AsyncMock()
    mock_conn2.execute = mocker.AsyncMock(return_value=no_invite_cursor)
    mock_conn2.__aenter__.return_value = mock_conn2
    mock_connect.return_value = mock_conn2

    success = await use_invite("invalid-invite", 123456789)
    assert success is False
    assert mock_conn2.execute.call_count == 1
    mock_conn2.commit.assert_not_called()

    # Exception case
    mocker.patch("aiosqlite.connect", side_effect=Exception("Database error"))
    success = await use_invite("test-invite-id", 123456789)
    assert success is False


@pytest.mark.asyncio
async def test_error_handling(temp_db):
    """Test error handling in database operations."""
    # Test with invalid user ID
    success = await add_user("invalid_id", "testuser", 987654321)
    assert success is False

    # Test with non-existent invite
    success = await use_invite("non_existent_invite", 123456789)
    assert success is False
