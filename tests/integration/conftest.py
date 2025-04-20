"""Configuration and fixtures for integration tests."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Chat, Message, User

from bot.config import ADMIN_USER_ID
from bot.handlers.commands import router as commands_router
from bot.handlers.download import download_router
from bot.services.queue import download_queue


@pytest_asyncio.fixture
async def temp_db(monkeypatch):
    """Create a temporary database for testing."""
    # Create temp directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = Path(temp_dir) / "test_bot.db"
        temp_dir_path = Path(temp_dir)

        # Patch DB_PATH and TEMP_DIR in the config module
        import bot.config
        import bot.utils.db

        monkeypatch.setattr(bot.utils.db, "DB_PATH", temp_db_path)
        monkeypatch.setattr(bot.config, "DB_PATH", temp_db_path)
        monkeypatch.setattr(bot.config, "TEMP_DIR", temp_dir_path)
        monkeypatch.setattr(bot.config, "DATA_DIR", temp_dir_path)

        # Initialize database
        from bot.utils.db import init_db

        await init_db()

        yield temp_db_path


@pytest_asyncio.fixture
async def mock_bot():
    """Create a mocked bot instance."""
    # Create a properly mocked bot instance
    bot = MagicMock(spec=Bot)
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=100))
    bot.edit_message_text = AsyncMock()
    bot.send_document = AsyncMock()

    # Make get_me return a proper object with username
    bot_info = MagicMock()
    bot_info.username = "test_bot"
    bot.get_me = AsyncMock(return_value=bot_info)

    # Patch the get_bot function to return our mock
    with patch("bot.telegram_api.client.get_bot", return_value=bot):
        yield bot


@pytest_asyncio.fixture
async def mock_dispatcher():
    """Create a mocked dispatcher instance."""
    dp = MagicMock(spec=Dispatcher)
    dp.include_router = MagicMock()
    dp.start_polling = AsyncMock()

    # Add our routers
    dp.include_router(commands_router)
    dp.include_router(download_router)

    return dp


@pytest_asyncio.fixture
async def authorized_user():
    """Create an authorized user for testing."""
    from bot.utils.db import add_user

    user_id = 123456789
    username = "test_user"

    await add_user(user_id, username, ADMIN_USER_ID)

    # Create a mock user object
    user = MagicMock(spec=User)
    user.id = user_id
    user.username = username

    return user


@pytest_asyncio.fixture
async def unauthorized_user():
    """Create an unauthorized user for testing."""
    user = MagicMock(spec=User)
    user.id = 999999999
    user.username = "unauthorized_user"

    return user


@pytest_asyncio.fixture
async def mock_message(authorized_user, mock_bot):
    """Create a mock message for testing."""
    message = MagicMock(spec=Message)
    message.from_user = authorized_user
    message.chat = MagicMock(spec=Chat, id=authorized_user.id)
    message.answer = AsyncMock(return_value=MagicMock(message_id=101))
    message.message_id = 101
    message.bot = mock_bot

    return message


@pytest_asyncio.fixture
async def mock_callback_query(authorized_user, mock_message):
    """Create a mock callback query for testing."""
    callback = MagicMock(spec=CallbackQuery)
    callback.from_user = authorized_user

    # Create a message that can be properly awaited
    message = MagicMock(spec=Message)
    message.from_user = authorized_user
    message.chat = MagicMock(spec=Chat, id=authorized_user.id)
    message.message_id = 101
    message.bot = mock_message.bot

    # Make edit_text async and set a return value
    message.edit_text = AsyncMock(return_value=MagicMock(message_id=102))

    # Set the message
    callback.message = message
    callback.answer = AsyncMock()

    return callback


@pytest_asyncio.fixture
async def reset_queue():
    """Reset the download queue between tests."""
    # Clear the queue before test
    download_queue.queue = asyncio.Queue()
    download_queue.is_processing = False
    download_queue.current_task = None

    yield

    # Clear the queue after test
    download_queue.queue = asyncio.Queue()
    download_queue.is_processing = False
    download_queue.current_task = None


@pytest_asyncio.fixture
async def integration_setup(temp_db, mock_bot, authorized_user, reset_queue):
    """Setup for integration tests with all components initialized."""
    # To prevent actual downloads, we'll mock the needed functions

    # Mock the key components used by the download workflow
    with (
        patch("bot.services.downloader.download_youtube_video", AsyncMock()),
        patch("bot.handlers.download.is_youtube_url", return_value=True),
        patch(
            "bot.services.formats.get_available_formats",
            return_value={
                "video:SD": {
                    "label": "SD (480p)",
                    "format": "best[height<=480]",
                    "type": "video",
                },
                "video:HD": {
                    "label": "HD (720p)",
                    "format": "best[height<=720]",
                    "type": "video",
                },
            },
        ),
    ):
        yield {"bot": mock_bot, "user": authorized_user, "db_path": temp_db}
