"""Tests for missing command handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User

from bot.handlers.commands import command_help, command_cancel


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
        "bot.handlers.commands.is_user_authorized", AsyncMock(return_value=True)
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
        "bot.handlers.commands.is_user_authorized", AsyncMock(return_value=False)
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
    mock_queue.clear_user_tasks.return_value = 2  # 2 downloads cancelled

    # Mock dependencies
    with (
        patch("bot.handlers.commands.is_user_authorized", AsyncMock(return_value=True)),
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
        patch("bot.handlers.commands.is_user_authorized", AsyncMock(return_value=True)),
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
        "bot.handlers.commands.is_user_authorized", AsyncMock(return_value=False)
    ):
        await command_cancel(mock_message)

        # Check that answer was called once with access restricted message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Restricted" in args