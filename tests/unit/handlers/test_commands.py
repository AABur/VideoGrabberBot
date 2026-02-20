"""Tests for command handlers."""

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
async def test_help_command_authorized(mocker):
    """Test /help command with authorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return True
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )

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
async def test_help_command_unauthorized(mocker):
    """Test /help command with unauthorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=False),
    )

    await command_help(mock_message)

    # Check that answer was called once with access restricted message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_cancel_command_with_active_downloads(mocker):
    """Test /cancel command when user has active downloads."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.chat = mocker.MagicMock(id=123456)

    # Setup download queue mock
    mock_queue = mocker.MagicMock()
    mock_queue.is_user_in_queue.return_value = True
    mock_queue.clear_user_tasks = mocker.AsyncMock(return_value=2)  # 2 downloads cancelled

    # Mock dependencies
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )
    mocker.patch("bot.services.queue.download_queue", mock_queue)

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
async def test_cancel_command_no_downloads(mocker):
    """Test /cancel command when user has no active downloads."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.chat = mocker.MagicMock(id=123456)

    # Setup download queue mock
    mock_queue = mocker.MagicMock()
    mock_queue.is_user_in_queue.return_value = False  # No downloads

    # Mock dependencies
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )
    mocker.patch("bot.services.queue.download_queue", mock_queue)

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
async def test_cancel_command_unauthorized(mocker):
    """Test /cancel command with unauthorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=False),
    )

    await command_cancel(mock_message)

    # Check that answer was called once with access restricted message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_start_command_authorized(mocker):
    """Test /start command with authorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456
    mock_user.username = "test_user"

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/start"

    # Mock is_user_authorized to return True
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())

    await command_start(mock_message)

    # Check that answer was called once with welcome message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Welcome to VideoGrabberBot" in args
    assert "How to use" in args
    assert "Send me a YouTube link" in args


@pytest.mark.asyncio
async def test_start_command_unauthorized(mocker):
    """Test /start command with unauthorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999
    mock_user.username = "unauthorized_user"

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/start"

    # Mock is_user_authorized to return False
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=False),
    )
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())

    await command_start(mock_message)

    # Check that answer was called once with access restricted message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Access Restricted" in args


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invite_valid,expected_fragment",
    [
        (True, "Welcome"),
        (False, "Invalid Invite"),
    ],
)
async def test_start_command_with_invite_code(mocker, invite_valid, expected_fragment):
    """Test /start command with invite code — valid and invalid cases."""
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999
    mock_user.username = "new_user"

    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/start INVITE123"

    mocker.patch("bot.handlers.commands.use_invite", mocker.AsyncMock(return_value=invite_valid))
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())
    mocker.patch("bot.handlers.commands.logger.warning", mocker.MagicMock())

    await command_start(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert expected_fragment in args


@pytest.mark.asyncio
async def test_invite_command_success(mocker):
    """Test /invite command with successful invite creation."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456

    # Mock bot
    mock_bot_info = mocker.MagicMock()
    mock_bot_info.username = "test_bot"
    mock_bot = mocker.MagicMock(spec=Bot)
    mock_bot.get_me = mocker.AsyncMock(return_value=mock_bot_info)

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.bot = mock_bot

    # Mock dependencies
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )
    mocker.patch(
        "bot.handlers.commands.create_invite",
        mocker.AsyncMock(return_value="test_invite_code"),
    )
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())

    await command_invite(mock_message)

    # Check that answer was called once with invite link
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Invite Link Generated" in args
    assert "https://t.me/test_bot?start=test_invite_code" in args


@pytest.mark.asyncio
async def test_invite_command_failure(mocker):
    """Test /invite command with failed invite creation."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock dependencies
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=True),
    )
    mocker.patch("bot.handlers.commands.create_invite", mocker.AsyncMock(return_value=None))
    mocker.patch("bot.handlers.commands.logger.error", mocker.MagicMock())

    await command_invite(mock_message)

    # Check that answer was called once with error message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Error" in args
    assert "Could not generate invite link" in args


@pytest.mark.asyncio
async def test_invite_command_unauthorized(mocker):
    """Test /invite command with unauthorized user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock is_user_authorized to return False
    mocker.patch(
        "bot.handlers.commands.is_user_authorized",
        mocker.AsyncMock(return_value=False),
    )

    await command_invite(mock_message)

    # Check that answer was called once with access restricted message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Access Restricted" in args


@pytest.mark.asyncio
async def test_adduser_command_non_admin(mocker):
    """Test /adduser command with non-admin user."""
    # Mock user
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 999999  # Not the admin ID

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user

    # Mock admin ID
    mocker.patch(
        "bot.handlers.commands.ADMIN_USER_ID",
        123456,  # Different from mock_user.id
    )
    mocker.patch("bot.handlers.commands.logger.warning", mocker.MagicMock())

    await command_adduser(mock_message)

    # Check that answer was called once with admin only message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Admin Only" in args


@pytest.mark.asyncio
async def test_adduser_command_missing_args(mocker):
    """Test /adduser command without arguments."""
    # Mock user (admin)
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser"  # No args

    # Mock admin ID
    mocker.patch("bot.handlers.commands.ADMIN_USER_ID", 123456)

    await command_adduser(mock_message)

    # Check that answer was called once with usage error message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "Usage Error" in args
    assert "Please provide a username or user ID" in args


@pytest.mark.asyncio
async def test_adduser_command_with_userid_success(mocker):
    """Test /adduser command with user ID (success case)."""
    # Mock user (admin)
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser 789012"  # User ID as arg

    # Mock dependencies
    mocker.patch("bot.handlers.commands.ADMIN_USER_ID", 123456)
    mocker.patch("bot.handlers.commands.add_user", mocker.AsyncMock(return_value=True))
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())

    await command_adduser(mock_message)

    # Check that answer was called once with success message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "User Added" in args
    assert "789012" in args


@pytest.mark.asyncio
async def test_adduser_command_with_userid_already_exists(mocker):
    """Test /adduser command with user ID that already exists."""
    # Mock user (admin)
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser 789012"  # User ID as arg

    # Mock dependencies
    mocker.patch("bot.handlers.commands.ADMIN_USER_ID", 123456)
    mocker.patch("bot.handlers.commands.add_user", mocker.AsyncMock(return_value=False))

    await command_adduser(mock_message)

    # Check that answer was called once with already exists message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "User Already Exists" in args
    assert "789012" in args


@pytest.mark.asyncio
async def test_adduser_command_with_username(mocker):
    """Test /adduser command with username instead of user ID."""
    # Mock user (admin)
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 123456  # Admin ID

    # Mock message with answer as AsyncMock
    mock_message = mocker.MagicMock(spec=Message)
    mock_message.answer = mocker.AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "/adduser @test_user"  # Username as arg

    # Mock dependencies
    mocker.patch("bot.handlers.commands.ADMIN_USER_ID", 123456)
    mocker.patch("bot.handlers.commands.logger.info", mocker.MagicMock())

    await command_adduser(mock_message)

    # Check that answer was called once with username limitation message
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0][0]
    assert "User Cannot Be Added Directly by Username" in args
    assert "@test_user" in args
