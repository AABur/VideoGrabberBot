"""Tests for download handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message, User, CallbackQuery

from bot.handlers.download import process_url, process_format_selection


@pytest.mark.asyncio
async def test_process_url_authorized_youtube():
    """Test processing of a YouTube URL from an authorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://www.youtube.com/watch?v=test"

    # Setup mocks
    with (
        patch("bot.handlers.download.is_user_authorized", AsyncMock(return_value=True)),
        patch("bot.handlers.download.is_youtube_url", return_value=True),
        patch("bot.handlers.download.store_url", return_value="test_url_id"),
        patch(
            "bot.handlers.download.get_format_options",
            return_value=[
                ("SD", "SD (480p)"),
                ("HD", "HD (720p)"),
                ("FHD", "Full HD (1080p)"),
                ("ORIGINAL", "Original"),
            ],
        ),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_url(mock_message)

        # Verify message was answered
        mock_message.answer.assert_called_once()

        # Get the args and kwargs
        args, kwargs = mock_message.answer.call_args

        # Verify the message contains format selection
        assert "Choose Download Format" in args[0]
        # Verify we have a reply_markup with the keyboard
        assert "reply_markup" in kwargs


@pytest.mark.asyncio
async def test_process_url_authorized_non_youtube():
    """Test processing of a non-YouTube URL from an authorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 123456

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://example.com/video"

    # Setup mocks
    with (
        patch("bot.handlers.download.is_user_authorized", AsyncMock(return_value=True)),
        patch("bot.handlers.download.is_youtube_url", return_value=False),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_url(mock_message)

        # Verify message was answered
        mock_message.answer.assert_called_once()

        # Verify the message contains unsupported URL info
        args = mock_message.answer.call_args[0][0]
        assert "Unsupported URL" in args
        assert "valid YouTube link" in args


@pytest.mark.asyncio
async def test_process_url_unauthorized():
    """Test processing of a URL from an unauthorized user."""
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 999999

    # Mock message with answer as AsyncMock
    mock_message = MagicMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.from_user = mock_user
    mock_message.text = "https://www.youtube.com/watch?v=test"

    # Setup mocks
    with (
        patch(
            "bot.handlers.download.is_user_authorized", AsyncMock(return_value=False)
        ),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_url(mock_message)

        # Verify message was answered
        mock_message.answer.assert_called_once()

        # Verify the message contains access denied info
        args = mock_message.answer.call_args[0][0]
        assert "Access Denied" in args


@pytest.mark.asyncio
async def test_process_format_selection_success():
    """Test successful format selection processing."""
    # Mock callback query
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt:HD:url123"
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = MagicMock(id=123456)

    # Mock message to edit
    mock_message = MagicMock()
    mock_message.edit_text = AsyncMock()
    mock_message.chat.id = 123456
    mock_callback.message = mock_message

    # Mock status message response
    mock_status_message = MagicMock()
    mock_message.edit_text.return_value = mock_status_message

    # Mock format data
    mock_format_data = {
        "label": "HD (720p)",
        "format": "best[height<=720]",
    }

    # Mock bot instance
    mock_bot = MagicMock(spec=Bot)
    mock_bot.edit_message_text = AsyncMock()

    # Mock queue task
    mock_download_queue = MagicMock()
    mock_download_queue.is_processing = False
    mock_download_queue.is_user_in_queue.return_value = False
    mock_download_queue.add_task = AsyncMock(return_value=1)  # Position 1 in queue

    # Mock dependencies
    with (
        patch("bot.handlers.download.get_format_by_id", return_value=mock_format_data),
        patch(
            "bot.handlers.download.get_url",
            return_value="https://www.youtube.com/watch?v=test",
        ),
        patch("bot.handlers.download.store_format"),
        patch("bot.handlers.download.get_bot", return_value=mock_bot),
        patch("bot.handlers.download.download_queue", mock_download_queue),
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_format_selection(mock_callback)

        # Verify callback was answered
        mock_callback.answer.assert_called_once()

        # Verify message was edited
        mock_message.edit_text.assert_called_once()

        # Verify task was added to queue
        mock_download_queue.add_task.assert_called_once()

        # Verify bot.edit_message_text was NOT called (since position = 1)
        mock_bot.edit_message_text.assert_not_called()


@pytest.mark.asyncio
async def test_process_format_selection_queued():
    """Test format selection with position > 1 in queue."""
    # Mock callback query
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt:HD:url123"
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = MagicMock(id=123456)

    # Mock message to edit
    mock_message = MagicMock()
    mock_message.edit_text = AsyncMock()
    mock_message.chat.id = 123456
    mock_callback.message = mock_message

    # Mock status message response
    mock_status_message = MagicMock()
    mock_message.edit_text.return_value = mock_status_message

    # Mock format data
    mock_format_data = {
        "label": "HD (720p)",
        "format": "best[height<=720]",
    }

    # Mock bot instance
    mock_bot = MagicMock(spec=Bot)
    mock_bot.edit_message_text = AsyncMock()

    # Mock queue task
    mock_download_queue = MagicMock()
    mock_download_queue.is_processing = False
    mock_download_queue.is_user_in_queue.return_value = False
    mock_download_queue.add_task = AsyncMock(return_value=2)  # Position 2 in queue

    # Mock dependencies
    with (
        patch("bot.handlers.download.get_format_by_id", return_value=mock_format_data),
        patch(
            "bot.handlers.download.get_url",
            return_value="https://www.youtube.com/watch?v=test",
        ),
        patch("bot.handlers.download.store_format"),
        patch("bot.handlers.download.get_bot", return_value=mock_bot),
        patch("bot.handlers.download.download_queue", mock_download_queue),
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_format_selection(mock_callback)

        # Verify callback was answered
        mock_callback.answer.assert_called_once()

        # Verify message was edited
        mock_message.edit_text.assert_called_once()

        # Verify task was added to queue
        mock_download_queue.add_task.assert_called_once()

        # Verify bot.edit_message_text was called to update queue position
        mock_bot.edit_message_text.assert_called_once()
        # Check the queue position in the message
        args, kwargs = mock_bot.edit_message_text.call_args
        assert "Queue position: 2" in args[0]


@pytest.mark.asyncio
async def test_process_format_selection_already_processing():
    """Test format selection when queue is already processing."""
    # Mock callback query
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt:HD:url123"
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = MagicMock(id=123456)

    # Mock message to edit
    mock_message = MagicMock()
    mock_message.edit_text = AsyncMock()
    mock_message.chat.id = 123456
    mock_callback.message = mock_message

    # Mock status message response
    mock_status_message = MagicMock()
    mock_message.edit_text.return_value = mock_status_message

    # Mock format data
    mock_format_data = {
        "label": "HD (720p)",
        "format": "best[height<=720]",
    }

    # Mock bot instance
    mock_bot = MagicMock(spec=Bot)
    mock_bot.edit_message_text = AsyncMock()

    # Mock queue task
    mock_download_queue = MagicMock()
    mock_download_queue.is_processing = True  # Queue is processing
    mock_download_queue.is_user_in_queue.return_value = True  # User already has tasks
    mock_download_queue.add_task = AsyncMock(return_value=3)  # Position 3 in queue

    # Mock dependencies
    with (
        patch("bot.handlers.download.get_format_by_id", return_value=mock_format_data),
        patch(
            "bot.handlers.download.get_url",
            return_value="https://www.youtube.com/watch?v=test",
        ),
        patch("bot.handlers.download.store_format"),
        patch("bot.handlers.download.get_bot", return_value=mock_bot),
        patch("bot.handlers.download.download_queue", mock_download_queue),
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.info"),
    ):
        await process_format_selection(mock_callback)

        # The edited text should include queue notification
        args, kwargs = mock_message.edit_text.call_args
        assert "Download queued" in args[0]
        assert "You already have downloads in the queue" in args[0]


@pytest.mark.asyncio
async def test_process_format_selection_invalid_callback_data():
    """Test format selection with invalid callback data."""
    # Mock from_user
    mock_from_user = MagicMock()
    mock_from_user.id = 123456

    # Mock callback query with invalid format (missing parts)
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt"  # Missing format and URL ID
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = mock_from_user  # Add the missing attribute

    # Setup mocks for logger
    logger_error_mock = MagicMock()

    with (
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.error", logger_error_mock),
    ):
        await process_format_selection(mock_callback)

        # Verify logger.error was called
        logger_error_mock.assert_called_once()

        # Verify callback was answered with error
        mock_callback.answer.assert_called_once_with("Invalid format selection")


@pytest.mark.asyncio
async def test_process_format_selection_url_not_found():
    """Test format selection when URL is not found."""
    # Mock from_user
    mock_from_user = MagicMock()
    mock_from_user.id = 123456

    # Mock callback query
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt:HD:url123"
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = mock_from_user  # Add the missing attribute

    # Setup mocks
    with (
        patch("bot.handlers.download.get_url", return_value=None),
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.error"),
    ):
        await process_format_selection(mock_callback)

        # Verify callback was answered with error
        mock_callback.answer.assert_called_once_with("URL not found or expired")


@pytest.mark.asyncio
async def test_process_format_selection_format_not_found():
    """Test format selection when format is not found."""
    # Mock from_user
    mock_from_user = MagicMock()
    mock_from_user.id = 123456

    # Mock callback query
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "fmt:INVALID:url123"
    mock_callback.answer = AsyncMock()
    mock_callback.from_user = mock_from_user  # Add the missing attribute

    # Setup mocks
    with (
        patch(
            "bot.handlers.download.get_url",
            return_value="https://www.youtube.com/watch?v=test",
        ),
        patch("bot.handlers.download.get_format_by_id", return_value=None),
        patch("bot.handlers.download.logger.debug"),
        patch("bot.handlers.download.logger.error"),
    ):
        await process_format_selection(mock_callback)

        # Verify callback was answered with error
        mock_callback.answer.assert_called_once_with("Selected format not found")
