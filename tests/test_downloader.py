"""Tests for downloader module."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.services.downloader import (
    DownloadError,
    download_youtube_video,
    is_youtube_url,
)


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
async def test_download_youtube_video_success():
    """Test successful video download and sending."""
    # Create mocks
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=123))
    bot.edit_message_text = AsyncMock()
    bot.send_document = AsyncMock()

    # Create a temporary file to simulate download
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Mock YoutubeDL
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {"title": "Test Video"}
        mock_ydl.download.return_value = None

        # Create a dummy file to simulate downloaded content
        dummy_file = temp_dir_path / "test_video.mp4"
        with open(dummy_file, "w") as f:
            f.write("dummy content")

        # Mock the YoutubeDL context manager
        mock_ydl_context = MagicMock()
        mock_ydl_context.__enter__.return_value = mock_ydl
        mock_ydl_context.__exit__.return_value = None

        # Mock tempfile.mkdtemp to return our controlled temporary directory
        with (
            patch("tempfile.mkdtemp", return_value=str(temp_dir_path)),
            patch("yt_dlp.YoutubeDL", return_value=mock_ydl_context),
            patch("pathlib.Path.glob", return_value=[dummy_file]),
        ):
            # Call the function
            await download_youtube_video(
                bot, 12345, "https://www.youtube.com/watch?v=test"
            )

            # Verify the calls
            bot.send_message.assert_called_once()
            assert bot.edit_message_text.call_count == 2
            bot.send_document.assert_called_once()


@pytest.mark.asyncio
async def test_download_youtube_video_failure():
    """Test video download failure handling."""
    # Create mocks
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=123))

    # Mock YoutubeDL to raise an exception
    mock_ydl = MagicMock()
    mock_ydl.extract_info.side_effect = Exception("Download failed")

    # Mock the YoutubeDL context manager
    mock_ydl_context = MagicMock()
    mock_ydl_context.__enter__.return_value = mock_ydl
    mock_ydl_context.__exit__.return_value = None

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock tempfile.mkdtemp
        with (
            patch("tempfile.mkdtemp", return_value=temp_dir),
            patch("yt_dlp.YoutubeDL", return_value=mock_ydl_context),
            patch("bot.utils.logging.notify_admin", AsyncMock()),
        ):
            # Call the function and verify it raises the expected exception
            with pytest.raises(DownloadError):
                await download_youtube_video(
                    bot, 12345, "https://www.youtube.com/watch?v=test"
                )

            # Verify error message was sent to user
            # We expect 2 calls to send_message from our function:
            # 1. Initial message
            # 2. Error message to user
            assert bot.send_message.call_count >= 2

            # Check that the last call includes error message
            args, kwargs = bot.send_message.call_args_list[-1]
            assert (
                "Download failed" in kwargs.get("text", "")
                or "Download failed" in args[1]
            )
