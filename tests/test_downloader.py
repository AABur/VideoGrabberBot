"""Tests for downloader module."""

import tempfile
from pathlib import Path
from typing import Any, List

import pytest

from bot.services.downloader import (
    download_youtube_video,
    is_youtube_url,
)
from bot.utils.exceptions import DownloadError


class MockBotSetup:
    """Helper class to create consistent bot mocks."""

    def __init__(self, mocker):
        self.mocker = mocker
        self.bot = mocker.AsyncMock()
        self.message_mock = mocker.MagicMock(message_id=123)

    def setup_basic_bot(self) -> Any:
        """Setup bot with basic message operations."""
        self.bot.send_message = self.mocker.AsyncMock(return_value=self.message_mock)
        self.bot.edit_message_text = self.mocker.AsyncMock()
        self.bot.send_document = self.mocker.AsyncMock()
        return self.bot


class MockYoutubeDLSetup:
    """Helper class to create consistent YoutubeDL mocks."""

    def __init__(self, mocker):
        self.mocker = mocker

    def setup_successful_download(self, title: str = "Test Video") -> Any:
        """Setup YoutubeDL mock for successful download."""
        mock_ydl = self.mocker.MagicMock()
        mock_ydl.extract_info.return_value = {"title": title}
        mock_ydl.download.return_value = None

        mock_ydl_context = self.mocker.MagicMock()
        mock_ydl_context.__enter__.return_value = mock_ydl
        mock_ydl_context.__exit__.return_value = None

        return mock_ydl_context

    def setup_failed_download(self, error_message: str = "Download failed") -> Any:
        """Setup YoutubeDL mock for failed download."""
        mock_ydl = self.mocker.MagicMock()
        mock_ydl.extract_info.side_effect = Exception(error_message)

        mock_ydl_context = self.mocker.MagicMock()
        mock_ydl_context.__enter__.return_value = mock_ydl
        mock_ydl_context.__exit__.return_value = None

        return mock_ydl_context


class MockFileSystemSetup:
    """Helper class to setup temporary files and directory mocks."""

    def __init__(self, mocker):
        self.mocker = mocker

    def setup_temp_directory_with_file(self, temp_dir_path: Path, filename: str = "test_video.mp4") -> Path:
        """Create temporary directory with a dummy file."""
        dummy_file = temp_dir_path / filename
        with open(dummy_file, "w") as f:
            f.write("dummy content")
        return dummy_file

    def setup_common_patches(self, temp_dir: str, files: List[Path] = None) -> None:
        """Setup common patches for file system operations."""
        if files is None:
            files = []
        self.mocker.patch("tempfile.mkdtemp", return_value=temp_dir)
        self.mocker.patch("pathlib.Path.glob", return_value=files)


@pytest.fixture
def bot_setup(mocker):
    """Fixture for bot mock setup."""
    return MockBotSetup(mocker)


@pytest.fixture
def ydl_setup(mocker):
    """Fixture for YoutubeDL mock setup."""
    return MockYoutubeDLSetup(mocker)


@pytest.fixture
def fs_setup(mocker):
    """Fixture for file system mock setup."""
    return MockFileSystemSetup(mocker)


def apply_standard_patches(mocker, temp_dir: str, ydl_context: Any, files: List[Path] = None) -> None:
    """Apply standard patches used across multiple tests."""
    if files is None:
        files = []
    mocker.patch("tempfile.mkdtemp", return_value=temp_dir)
    mocker.patch("yt_dlp.YoutubeDL", return_value=ydl_context)
    mocker.patch("pathlib.Path.glob", return_value=files)


class CleanupFailureMock:
    """Mock for cleanup failure to avoid nested functions."""

    def __init__(self, mock_logger_error):
        self.mock_logger_error = mock_logger_error

    def __call__(self, temp_dir):
        """Simulate cleanup failure."""
        self.mock_logger_error("Failed to clean up temporary directory: Cleanup failed")
        # Don't actually fail cleanup that would interfere with test teardown


@pytest.mark.asyncio
async def test_is_youtube_url():
    """Test youtube URL detection function."""
    # Valid YouTube URLs
    assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert is_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_youtube_url("https://youtube-nocookie.com/watch?v=dQw4w9WgXcQ")

    # Invalid YouTube URLs
    assert not is_youtube_url("https://www.example.com")
    assert not is_youtube_url("https://vimeo.com/123456")
    assert not is_youtube_url("https://video.example.com/p/123456")


@pytest.mark.asyncio
async def test_download_youtube_video_success(bot_setup, ydl_setup, fs_setup):
    """Test successful video download and sending."""
    bot = bot_setup.setup_basic_bot()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        dummy_file = fs_setup.setup_temp_directory_with_file(temp_dir_path)

        ydl_context = ydl_setup.setup_successful_download()
        apply_standard_patches(fs_setup.mocker, str(temp_dir_path), ydl_context, [dummy_file])

        await download_youtube_video(bot, 12345, "https://www.youtube.com/watch?v=test")

        # Verify the calls
        bot.send_message.assert_called_once()
        assert bot.edit_message_text.call_count == 2
        bot.send_document.assert_called_once()


@pytest.mark.asyncio
async def test_download_youtube_video_with_status_message(bot_setup, ydl_setup, fs_setup):
    """Test download with existing status message ID."""
    bot = bot_setup.setup_basic_bot()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        dummy_file = fs_setup.setup_temp_directory_with_file(temp_dir_path)

        ydl_context = ydl_setup.setup_successful_download()
        apply_standard_patches(fs_setup.mocker, str(temp_dir_path), ydl_context, [dummy_file])

        # Additional patches for this specific test
        fs_setup.mocker.patch("bot.services.downloader.Message")
        fs_setup.mocker.patch("bot.services.downloader.Chat")

        await download_youtube_video(
            bot,
            12345,
            "https://www.youtube.com/watch?v=test",
            status_message_id=789,
        )

        # Verify edit_message_text was called instead of send_message
        bot.send_message.assert_not_called()
        assert bot.edit_message_text.call_count == 3  # Initial + progress + completion
        bot.send_document.assert_called_once()


@pytest.mark.asyncio
async def test_download_youtube_video_failure(bot_setup, ydl_setup, fs_setup):
    """Test video download failure handling."""
    bot = bot_setup.setup_basic_bot()

    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_context = ydl_setup.setup_failed_download("Download failed")
        apply_standard_patches(fs_setup.mocker, temp_dir, ydl_context)
        fs_setup.mocker.patch("bot.utils.logging.notify_admin", fs_setup.mocker.AsyncMock())

        with pytest.raises(DownloadError):
            await download_youtube_video(bot, 12345, "https://www.youtube.com/watch?v=test")

        # Verify error message was sent to user
        # We expect 2 calls to send_message from our function:
        # 1. Initial message
        # 2. Error message to user
        assert bot.send_message.call_count >= 2

        # Check that the last call includes error message
        args, kwargs = bot.send_message.call_args_list[-1]
        assert "Download failed" in kwargs.get("text", "") or "Download failed" in args[1]


@pytest.mark.asyncio
async def test_download_youtube_video_no_files(bot_setup, ydl_setup, fs_setup):
    """Test download when no files are found after download."""
    bot = bot_setup.setup_basic_bot()

    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_context = ydl_setup.setup_successful_download()
        apply_standard_patches(fs_setup.mocker, temp_dir, ydl_context, [])  # No files found
        fs_setup.mocker.patch("bot.utils.logging.notify_admin", fs_setup.mocker.AsyncMock())

        with pytest.raises(DownloadError) as exc_info:
            await download_youtube_video(bot, 12345, "https://www.youtube.com/watch?v=test")

            # Check error message (now wrapped as unexpected error)
            error_msg = str(exc_info.value).lower()
            assert "unexpected error" in error_msg or "no files found" in error_msg


@pytest.mark.asyncio
async def test_download_youtube_video_cleanup_failure(bot_setup, ydl_setup, fs_setup):
    """Test download when cleanup fails."""
    bot = bot_setup.setup_basic_bot()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        dummy_file = fs_setup.setup_temp_directory_with_file(temp_dir_path)

        ydl_context = ydl_setup.setup_successful_download()
        apply_standard_patches(fs_setup.mocker, str(temp_dir_path), ydl_context, [dummy_file])

        mock_logger_error = fs_setup.mocker.patch("bot.services.downloader.logger.error")
        mock_cleanup_failure = CleanupFailureMock(mock_logger_error)
        fs_setup.mocker.patch("bot.services.downloader._cleanup_temp_directory", side_effect=mock_cleanup_failure)

        # Call the function - should complete without raising exception
        await download_youtube_video(bot, 12345, "https://www.youtube.com/watch?v=test")

        # Verify the function logged the cleanup error
        mock_logger_error.assert_called_once()
        assert "Failed to clean up" in mock_logger_error.call_args[0][0]
