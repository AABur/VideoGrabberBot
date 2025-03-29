"""Tests for command handlers."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User

from bot.handlers.commands import command_start, command_help, command_invite, command_adduser
from bot.config import ADMIN_USER_ID


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
    with patch("bot.handlers.commands.is_user_authorized", AsyncMock(return_value=True)):
        await command_start(mock_message)

        # Check that answer was called once with welcome message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Welcome to VideoGrabberBot" in args


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
    with patch("bot.handlers.commands.is_user_authorized", AsyncMock(return_value=False)):
        await command_start(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_invite_command():
    """Test /invite command."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock bot
    mock_bot = MagicMock()
    mock_bot.get_me = AsyncMock()
    mock_bot.get_me.return_value = MagicMock(username="test_bot")

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.bot = mock_bot

    # Mock is_user_authorized to return True
    with patch("bot.handlers.commands.is_user_authorized", AsyncMock(return_value=True)):
        # Mock create_invite to return a code
        with patch("bot.handlers.commands.create_invite", AsyncMock(return_value="test_invite_code")):
            await command_invite(mock_message)

            # Check that answer was called with invite link
            mock_message.answer.assert_called_once()
            args = mock_message.answer.call_args[0][0]
            assert "Invite Link Generated" in args
            assert "https://t.me/test_bot?start=test_invite_code" in args


@pytest.mark.asyncio
async def test_adduser_command_admin():
    """Test /adduser command with admin user."""
    # Mock admin user
    mock_user = MagicMock(spec=User)
    mock_user.id = ADMIN_USER_ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser 123456"

    # Mock add_user to return True (user added successfully)
    with patch("bot.handlers.commands.add_user", AsyncMock(return_value=True)):
        await command_adduser(mock_message)

        # Check that answer was called with success message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "User Added" in args


@pytest.mark.asyncio
async def test_adduser_command_non_admin():
    """Test /adduser command with non-admin user."""
    # Mock non-admin user
    mock_user = MagicMock(spec=User)
    mock_user.id = ADMIN_USER_ID + 1  # Different from admin ID

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user

    await command_adduser(mock_message)

    # Check that answer was called with admin only message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Admin Only" in args