"""Tests for the logging module."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from loguru import logger

from bot.utils.logging import notify_admin, setup_logger


def test_setup_logger(monkeypatch):
    """Test logger setup."""
    # Mock logger functions
    logger_remove_called = False
    logger_add_calls = []
    logger_info_called = False

    def mock_remove():
        nonlocal logger_remove_called
        logger_remove_called = True

    def mock_add(sink, **kwargs):
        logger_add_calls.append((sink, kwargs))

    def mock_info(message):
        nonlocal logger_info_called
        logger_info_called = True

    # Apply mocks
    monkeypatch.setattr(logger, "remove", mock_remove)
    monkeypatch.setattr(logger, "add", mock_add)
    monkeypatch.setattr(logger, "info", mock_info)

    # Call the setup function
    temp_log_file = Path("test_log.log")
    setup_logger(temp_log_file)

    # Verify that logger was configured correctly
    assert logger_remove_called

    # Check that add was called for both stdout and file
    assert len(logger_add_calls) == 2

    # Check that info was called (initialization message)
    assert logger_info_called


def test_setup_logger_default_path(monkeypatch):
    """Test logger setup with default log path."""
    # Mock logger functions
    logger_remove_called = False
    logger_add_calls = []
    logger_info_called = False

    def mock_remove():
        nonlocal logger_remove_called
        logger_remove_called = True

    def mock_add(sink, **kwargs):
        logger_add_calls.append((sink, kwargs))

    def mock_info(message):
        nonlocal logger_info_called
        logger_info_called = True

    # Mock Path
    mock_data_dir = Path("/mock/data/dir")

    # Apply mocks
    monkeypatch.setattr(logger, "remove", mock_remove)
    monkeypatch.setattr(logger, "add", mock_add)
    monkeypatch.setattr(logger, "info", mock_info)
    monkeypatch.setattr("bot.utils.logging.DATA_DIR", mock_data_dir)

    # Call the setup function with default path
    setup_logger()

    # Verify that logger was configured correctly
    assert logger_remove_called

    # Check that add was called for both stdout and file
    assert len(logger_add_calls) == 2

    # Check that default path was used
    file_sink = logger_add_calls[1][0]
    assert str(mock_data_dir / "bot.log") == str(file_sink)


@pytest.mark.asyncio
async def test_notify_admin_success(monkeypatch):
    """Test that admin notifications are sent successfully."""
    # Create mock bot
    send_message_called = False
    send_message_args = None

    class MockBot:
        async def send_message(self, chat_id, text):
            nonlocal send_message_called, send_message_args
            send_message_called = True
            send_message_args = (chat_id, text)

    mock_bot = MockBot()

    # Mock logger.log function
    log_called = False

    def mock_log(level, message, **kwargs):
        nonlocal log_called
        log_called = True

    monkeypatch.setattr(logger, "log", mock_log)

    # Test message
    test_message = "Test notification"

    # Call the function
    await notify_admin(mock_bot, test_message, level="INFO")

    # Verify that send_message was called
    assert send_message_called

    # Check arguments
    assert "Test notification" in send_message_args[1]
    assert log_called


@pytest.mark.asyncio
async def test_notify_admin_error_level(monkeypatch):
    """Test that error-level notifications use logger.error."""
    # Create mock bot
    mock_bot = AsyncMock()

    # Mock logger.error
    error_called = False
    error_message = None

    def mock_error(message, **kwargs):
        nonlocal error_called, error_message
        error_called = True
        error_message = message

    # Apply mock
    monkeypatch.setattr(logger, "error", mock_error)
    monkeypatch.setattr(logger, "log", MagicMock())

    # Call the function with ERROR level
    await notify_admin(mock_bot, "Error message", level="ERROR")

    # Verify logger.error was called
    assert error_called
    assert "Error message" in error_message


@pytest.mark.asyncio
async def test_notify_admin_error(monkeypatch):
    """Test handling of errors during admin notification."""

    # Create mock bot that raises an exception
    class MockBot:
        async def send_message(self, chat_id, text):
            raise Exception("Test error")

    mock_bot = MockBot()

    # Mock logger.error
    error_message = None

    def mock_error(message):
        nonlocal error_message
        error_message = message

    monkeypatch.setattr(logger, "error", mock_error)

    # Call the function
    await notify_admin(mock_bot, "Test message")

    # Verify that error was logged
    assert error_message is not None
    assert "Failed to notify admin" in error_message


@pytest.mark.asyncio
async def test_notify_admin_with_kwargs(monkeypatch):
    """Test that additional kwargs are included in the notification."""
    # Create mock bot
    send_message_text = None

    class MockBot:
        async def send_message(self, chat_id, text):
            nonlocal send_message_text
            send_message_text = text

    mock_bot = MockBot()

    # Mock logger functions
    monkeypatch.setattr(logger, "log", lambda *args, **kwargs: None)

    # Call with additional data
    await notify_admin(
        mock_bot,
        "Test with data",
        level="WARNING",
        user_id=12345,
        action="test_action",
    )

    # Check message content includes the additional data
    assert "Test with data" in send_message_text
    assert "user_id: 12345" in send_message_text
    assert "action: test_action" in send_message_text
