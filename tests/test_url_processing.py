"""Tests for URL processing in download handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import InlineKeyboardMarkup, Message, User

from bot.handlers.download import process_url
from bot.services.storage import clear_url


@pytest.mark.asyncio
async def test_process_url_youtube_authorized():
    """Test processing a YouTube URL from an authorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Set up mocks for dependencies
    with (
        patch("bot.handlers.download.is_user_authorized", AsyncMock(return_value=True)),
        patch("bot.handlers.download.is_youtube_url", return_value=True),
        patch("bot.handlers.download.store_url", return_value="test_url_id"),
        patch(
            "bot.handlers.download.get_format_options",
            return_value=[
                ("video:HD", "HD Video (720p)"),
                ("video:FHD", "Full HD Video (1080p)"),
                ("audio:mp3", "MP3 Audio (320kbps)"),
            ],
        ),
    ):
        await process_url(mock_message)

        # Verify answer was called with format selection
        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        
        # Check message content
        assert "Choose Download Format" in args[0]
        
        # Check keyboard markup
        assert "reply_markup" in kwargs
        markup = kwargs["reply_markup"]
        assert isinstance(markup, InlineKeyboardMarkup)
        
        # Check buttons
        keyboard = markup.inline_keyboard
        assert len(keyboard) > 0  # At least one row
        
        # Check callback data format
        first_button = keyboard[0][0]
        assert first_button.callback_data.startswith("fmt:")
        assert "test_url_id" in first_button.callback_data


@pytest.mark.asyncio
async def test_process_url_non_youtube():
    """Test processing a non-YouTube URL."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://example.com/some/video"

    # Set up mocks for dependencies
    with (
        patch("bot.handlers.download.is_user_authorized", AsyncMock(return_value=True)),
        patch("bot.handlers.download.is_youtube_url", return_value=False),
    ):
        await process_url(mock_message)

        # Verify answer was called with unsupported URL message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Unsupported URL" in args
        assert "valid YouTube link" in args


@pytest.mark.asyncio
async def test_process_url_unauthorized():
    """Test URL processing from an unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Mock is_user_authorized to return False
    with patch(
        "bot.handlers.download.is_user_authorized", AsyncMock(return_value=False)
    ):
        await process_url(mock_message)

        # Check that answer was called once with access denied message
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Access Denied" in args


@pytest.mark.asyncio
async def test_url_storage_cleanup():
    """Test URL cleanup after processing."""
    # Test the URL cleanup function
    with patch("bot.services.storage.URL_STORAGE", {"test_id": ("test_url", None)}):
        # Verify URL exists before cleanup
        from bot.services.storage import URL_STORAGE, get_url
        
        assert get_url("test_id") == "test_url"
        
        # Call cleanup function
        clear_url("test_id")
        
        # Verify URL was removed
        assert "test_id" not in URL_STORAGE
        assert get_url("test_id") is None