"""Tests for command handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message, User

from bot.handlers.commands import (
    command_adduser,
    command_cancel,
    command_help,
    command_invite,
    command_start,
)


@pytest.mark.asyncio
async def test_help_command_authorized():
    """Test /help command with authorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return True
    with patch(
        "bot.handlers.commands.is_user_authorized",
        AsyncMock(return_value=True),
    ):
        await command_help(mock_message)

        # Check that answer was called once with help message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "VideoGrabberBot Help" in args
        assert "Available commands" in args
        assert "/help" in args
        assert "/start" in args
        assert "/invite" in args
        assert "/cancel" in args


@pytest.mark.asyncio
async def test_help_command_unauthorized():
    """Test /help command with unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    with patch(
        "bot.handlers.commands.is_user_authorized",
        AsyncMock(return_value=False),
    ):
        await command_help(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_cancel_command_with_active_downloads():
    """Test /cancel command when user has active downloads."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.chat = MagicMock(id=123456)

    # Setup download queue mock
    mock_queue = MagicMock()
    mock_queue.is_user_in_queue.return_value = True
    mock_queue.clear_user_tasks = AsyncMock(return_value=2)  # 2 downloads cancelled

    # Mock dependencies
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=True),
        ),
        patch("bot.services.queue.download_queue", mock_queue),
    ):
        await command_cancel(mock_message)

        # Verify user queue check
        mock_queue.is_user_in_queue.assert_called_once_with(123456)

        # Verify user tasks cleared
        mock_queue.clear_user_tasks.assert_called_once_with(123456)

        # Check response message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Downloads Cancelled" in args
        assert "2 downloads" in args


@pytest.mark.asyncio
async def test_cancel_command_no_downloads():
    """Test /cancel command when user has no active downloads."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.chat = MagicMock(id=123456)

    # Setup download queue mock
    mock_queue = MagicMock()
    mock_queue.is_user_in_queue.return_value = False  # No downloads

    # Mock dependencies
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=True),
        ),
        patch("bot.services.queue.download_queue", mock_queue),
    ):
        await command_cancel(mock_message)

        # Verify user queue check
        mock_queue.is_user_in_queue.assert_called_once_with(123456)

        # Verify clear_user_tasks was not called
        mock_queue.clear_user_tasks.assert_not_called()

        # Check response message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "No Active Downloads" in args


@pytest.mark.asyncio
async def test_cancel_command_unauthorized():
    """Test /cancel command with unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    with patch(
        "bot.handlers.commands.is_user_authorized",
        AsyncMock(return_value=False),
    ):
        await command_cancel(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_start_command_authorized():
    """Test /start command with authorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456
    mock_user.username = "test_user"

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return True
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=True),
        ),
        patch("bot.handlers.commands.logger.info", MagicMock()),
    ):
        await command_start(mock_message)

        # Check that answer was called once with welcome message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Welcome to VideoGrabberBot" in args
        assert "How to use" in args
        assert "Send me a YouTube link" in args


@pytest.mark.asyncio
async def test_start_command_unauthorized():
    """Test /start command with unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999
    mock_user.username = "unauthorized_user"

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=False),
        ),
        patch("bot.handlers.commands.logger.info", MagicMock()),
    ):
        await command_start(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_invite_command_success():
    """Test /invite command with successful invite creation."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock bot
    mock_bot_info = MagicMock()
    mock_bot_info.username = "test_bot"
    mock_bot = MagicMock(spec=Bot)
    mock_bot.get_me = AsyncMock(return_value=mock_bot_info)

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.bot = mock_bot

    # Mock dependencies
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=True),
        ),
        patch(
            "bot.handlers.commands.create_invite",
            AsyncMock(return_value="test_invite_code"),
        ),
        patch("bot.handlers.commands.logger.info", MagicMock()),
    ):
        await command_invite(mock_message)

        # Check that answer was called once with invite link
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Invite Link Generated" in args
        assert "https://t.me/test_bot?start=test_invite_code" in args


@pytest.mark.asyncio
async def test_invite_command_failure():
    """Test /invite command with failed invite creation."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock dependencies
    with (
        patch(
            "bot.handlers.commands.is_user_authorized",
            AsyncMock(return_value=True),
        ),
        patch("bot.handlers.commands.create_invite", AsyncMock(return_value=None)),
        patch("bot.handlers.commands.logger.error", MagicMock()),
    ):
        await command_invite(mock_message)

        # Check that answer was called once with error message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Error" in args
        assert "Could not generate invite link" in args


@pytest.mark.asyncio
async def test_invite_command_unauthorized():
    """Test /invite command with unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    with patch(
        "bot.handlers.commands.is_user_authorized",
        AsyncMock(return_value=False),
    ):
        await command_invite(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_adduser_command_non_admin():
    """Test /adduser command with non-admin user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999  # Not the admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    # Mock admin ID
    with (
        patch(
            "bot.handlers.commands.ADMIN_USER_ID",
            123456,  # Different from mock_user.id
        ),
        patch("bot.handlers.commands.logger.warning", MagicMock()),
    ):
        await command_adduser(mock_message)

        # Check that answer was called once with admin only message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Admin Only" in args


@pytest.mark.asyncio
async def test_adduser_command_missing_args():
    """Test /adduser command without arguments."""
    # Mock user (admin)
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser"  # No args

    # Mock admin ID
    with patch("bot.handlers.commands.ADMIN_USER_ID", 123456):
        await command_adduser(mock_message)

        # Check that answer was called once with usage error message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Usage Error" in args
        assert "Please provide a username or user ID" in args


@pytest.mark.asyncio
async def test_adduser_command_with_userid_success():
    """Test /adduser command with user ID (success case)."""
    # Mock user (admin)
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser 789012"  # User ID as arg

    # Mock dependencies
    with (
        patch("bot.handlers.commands.ADMIN_USER_ID", 123456),
        patch("bot.handlers.commands.add_user", AsyncMock(return_value=True)),
        patch("bot.handlers.commands.logger.info", MagicMock()),
    ):
        await command_adduser(mock_message)

        # Check that answer was called once with success message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "User Added" in args
        assert "789012" in args


@pytest.mark.asyncio
async def test_adduser_command_with_userid_already_exists():
    """Test /adduser command with user ID that already exists."""
    # Mock user (admin)
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser 789012"  # User ID as arg

    # Mock dependencies
    with (
        patch("bot.handlers.commands.ADMIN_USER_ID", 123456),
        patch("bot.handlers.commands.add_user", AsyncMock(return_value=False)),
    ):
        await command_adduser(mock_message)

        # Check that answer was called once with already exists message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "User Already Exists" in args
        assert "789012" in args


@pytest.mark.asyncio
async def test_adduser_command_with_username():
    """Test /adduser command with username instead of user ID."""
    # Mock user (admin)
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser @test_user"  # Username as arg

    # Mock dependencies
    with (
        patch("bot.handlers.commands.ADMIN_USER_ID", 123456),
        patch("bot.handlers.commands.logger.info", MagicMock()),
    ):
        await command_adduser(mock_message)

        # Check that answer was called once with username limitation message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "User Cannot Be Added Directly by Username" in args
        assert "@test_user" in args
