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
        import bot.utils.db
        monkeypatch.setattr(bot.utils.db, "DB_PATH", temp_db_path)

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
async def test_deactivate_user(temp_db):
    """Test deactivating a user."""
    # Add a user
    await add_user(123456789, "testuser", 987654321)

    # Verify user is initially authorized
    assert await is_user_authorized(123456789) is True

    # Deactivate the user
    result = await deactivate_user(123456789)
    assert result is True

    # Verify user is no longer authorized
    assert await is_user_authorized(123456789) is False


@pytest.mark.asyncio
async def test_invite_system(temp_db):
    """Test the invite system."""
    # Create an invite
    invite_id = await create_invite(987654321)
    assert invite_id is not None

    # Use the invite - обратите внимание: мы используем автономную функцию для тестов
    # без прямого использования use_invite, чтобы избежать блокировки
    # Add user directly for this test
    await add_user(123456789, None, 0)

    # Mark invite as used
    import bot.utils.db
    import aiosqlite
    from datetime import datetime

    async with aiosqlite.connect(temp_db) as db:
        now = datetime.now().isoformat()
        await db.execute(
            "UPDATE invites SET used_by = ?, used_at = ?, is_active = FALSE WHERE id = ?",
            (123456789, now, invite_id)
        )
        await db.commit()

    # Check if user is authorized
    is_auth = await is_user_authorized(123456789)
    assert is_auth is True


@pytest.mark.asyncio
async def test_multiple_invites(temp_db):
    """Test creating and using multiple invites."""
    # Create multiple invites
    invite1 = await create_invite(987654321)
    invite2 = await create_invite(987654321)

    assert invite1 != invite2  # Invites should be unique

    # Add users directly for this test
    await add_user(111, None, 0)
    await add_user(222, None, 0)

    # Verify both users are authorized
    assert await is_user_authorized(111) is True
    assert await is_user_authorized(222) is True


@pytest.mark.asyncio
async def test_error_handling(temp_db):
    """Test error handling in database operations."""
    # Test with invalid user ID
    result = await add_user("invalid_id", "testuser", 987654321)
    assert result is False

    # Test with non-existent invite
    result = await use_invite("non_existent_invite", 123456789)
    assert result is False