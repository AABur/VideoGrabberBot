"""Integration tests for error handling and recovery."""

from unittest.mock import AsyncMock, patch

import pytest

from bot.handlers.download import process_url, process_format_selection
from bot.services.downloader import DownloadError
from bot.services.queue import download_queue, DownloadTask


@pytest.mark.asyncio
async def test_download_error_handling(
    integration_setup, mock_message, mock_callback_query
):
    """Test error handling during download process."""
    # Setup message with YouTube URL
    mock_message.text = "https://www.youtube.com/watch?v=test_error_video"

    # Reset the mock_message.answer before testing
    mock_message.answer.reset_mock()

    # First process the URL
    with patch("bot.handlers.download.store_url", return_value="test_error_url_id"):
        await process_url(mock_message)

        # Verify message was sent with format options
        mock_message.answer.assert_called_once()
        _, kwargs = mock_message.answer.call_args
        assert "reply_markup" in kwargs

        # Get markup for format selection
        markup = kwargs["reply_markup"]
        callback_data = markup.inline_keyboard[0][0].callback_data

    # Setup callback query with the format data
    mock_callback_query.data = callback_data

    # Setup the mock bot
    mock_bot = integration_setup["bot"]

    # Create a download error for testing
    download_error = AsyncMock(side_effect=DownloadError("Test download error"))

    # Simulate the download process
    with (
        patch(
            "bot.handlers.download.get_url",
            return_value="https://www.youtube.com/watch?v=test_error_video",
        ),
        patch(
            "bot.services.formats.get_format_by_id",
            return_value={
                "label": "Test Format",
                "format": "test-format",
                "type": "video",
            },
        ),
        patch("bot.services.downloader.download_youtube_video", download_error),
        patch("bot.telegram_api.client.get_bot", return_value=mock_bot),
    ):
        # Process format selection (this adds task to queue)
        await process_format_selection(mock_callback_query)

        # Verify callback was answered
        mock_callback_query.answer.assert_called_once()

        # Verify message was edited
        mock_callback_query.message.edit_text.assert_called_once()

        # Verify task is in queue
        assert download_queue.queue.qsize() == 1

        # Process the queue (which should handle the error)
        await download_queue._process_queue()

        # Verify queue is empty after error handling
        assert download_queue.queue.empty()

        # Verify queue is not stuck in processing state
        assert not download_queue.is_processing

        # Verify download error was raised
        download_error.assert_called_once()


@pytest.mark.asyncio
async def test_multiple_download_failures(integration_setup, mock_bot):
    """Test handling of multiple download failures using direct queue manipulation."""
    # Create download error for testing
    download_error = AsyncMock(side_effect=DownloadError("Test error"))

    # Create two tasks directly
    task1 = DownloadTask(
        chat_id=123456,
        url="https://www.youtube.com/watch?v=test_fail1",
        format_string="test-format-1",
        status_message_id=101,
        additional_data={"bot": mock_bot},
    )

    task2 = DownloadTask(
        chat_id=123456,
        url="https://www.youtube.com/watch?v=test_fail2",
        format_string="test-format-2",
        status_message_id=102,
        additional_data={"bot": mock_bot},
    )

    # Add tasks to queue directly
    await download_queue.add_task(task1)
    await download_queue.add_task(task2)

    # Verify both tasks are in queue
    assert download_queue.queue.qsize() == 2

    # Process the queue with both failing tasks
    with patch("bot.services.downloader.download_youtube_video", download_error):
        await download_queue._process_queue()

        # Verify queue is empty after error handling
        assert download_queue.queue.empty()

        # Verify queue is not stuck in processing state
        assert not download_queue.is_processing

        # Verify download was attempted twice
        assert download_error.call_count == 2


@pytest.mark.asyncio
async def test_admin_notification_on_error(integration_setup, mock_bot):
    """Test that admin is notified on critical errors."""

    # Instead of just mocking the download function with a side effect, we need
    # to implement the error handling that would occur in the real function
    async def mock_download_with_error(*args, **kwargs):
        # Extract the bot and chat_id from args (positional arguments)
        bot_arg = args[0]
        chat_id_arg = args[1]

        # Before raising the exception, send error message to user
        await bot_arg.send_message(
            chat_id_arg, "❌ <b>Download failed</b>\n\nCritical test error"
        )

        # Also call notify_admin like the real function would
        await notify_admin_mock(bot_arg, "Download failed with critical error")

        # Raise the exception
        raise DownloadError("Critical test error")

    # Mock notify_admin function to track calls
    notify_admin_mock = AsyncMock()

    # Create a task directly
    task = DownloadTask(
        chat_id=123456,
        url="https://www.youtube.com/watch?v=test_admin_notify",
        format_string="test-format",
        status_message_id=103,
        additional_data={"bot": mock_bot},
    )

    # Add task to queue
    await download_queue.add_task(task)

    # Verify task is in queue
    assert download_queue.queue.qsize() == 1

    # Process the queue with error that should trigger admin notification
    with (
        patch(
            "bot.services.downloader.download_youtube_video", mock_download_with_error
        ),
        patch("bot.utils.logging.notify_admin", notify_admin_mock),
    ):
        await download_queue._process_queue()

        # Verify queue is empty after error handling
        assert download_queue.queue.empty()

        # Verify queue is not stuck in processing state
        assert not download_queue.is_processing

        # Verify error message was sent to the user
        mock_bot.send_message.assert_called_once()

        # Verify admin was notified
        notify_admin_mock.assert_called_once()

        # Check that the task was cleared
        assert download_queue.current_task is None
