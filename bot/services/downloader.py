# bot/services/downloader.py
"""Download service for video grabber bot."""

import asyncio
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types import Chat, Message  # re-exported for backward compatibility
from loguru import logger

from bot.config import config
from bot.services._download_core import (
    MB_SIZE,
    TELEGRAM_UPLOAD_LIMIT,
    _create_ydl_options,
    _sync_download_video_file,
)
from bot.services._file_delivery import (
    _create_or_update_status_message,
    _send_downloaded_file,
)
from bot.utils.exceptions import (
    DownloadError,
    NetworkError,
    UnsupportedFormatError,
    VideoNotFoundError,
    VideoTooLargeError,
)
from bot.utils.logging import notify_admin

__all__ = [
    "MB_SIZE",
    "TELEGRAM_UPLOAD_LIMIT",
    "Chat",
    "Message",
    "NetworkError",
    "UnsupportedFormatError",
    "VideoNotFoundError",
    "VideoTooLargeError",
    "_create_or_update_status_message",
    "_create_ydl_options",
    "_download_video_file",
    "_send_downloaded_file",
    "_sync_download_video_file",
    "_validate_file_size",
    "download_youtube_video",
    "is_youtube_url",
]


def _validate_file_size(file_size: int, url: str, file_path: Optional[Path] = None) -> None:
    """Validate file size and raise error if too large.

    Args:
        file_size: Size of file in bytes
        url: URL for context in error message
        file_path: Optional file path to delete if oversized

    Raises:
        VideoTooLargeError: If file size exceeds limit
    """
    if file_size > config.MAX_FILE_SIZE:
        if file_path:
            file_path.unlink()  # Delete oversized file

        actual_mb = file_size // MB_SIZE
        limit_mb = config.MAX_FILE_SIZE // MB_SIZE
        raise VideoTooLargeError(
            f"File size ({actual_mb} MB) exceeds limit ({limit_mb} MB)",
            context={"url": url, "file_size": file_size, "limit": config.MAX_FILE_SIZE},
        )


async def _download_video_file(
    url: str, ydl_opts: Dict[str, Any], temp_download_path: Path
) -> tuple[Path, Dict[str, Any]]:
    """Download video and return file path and video info (async wrapper)."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as executor:
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(executor, _sync_download_video_file, url, ydl_opts, temp_download_path),
                timeout=config.DOWNLOAD_TIMEOUT,
            )
        except asyncio.TimeoutError as e:
            raise NetworkError(
                f"Download timed out after {config.DOWNLOAD_TIMEOUT} seconds",
                context={"url": url, "timeout": config.DOWNLOAD_TIMEOUT},
            ) from e


async def _execute_download_process(
    bot: Bot, chat_id: int, url: str, format_string: str, temp_download_path: Path, status_message_id: Optional[int]
) -> None:
    """Execute the main download process."""
    status_message = await _create_or_update_status_message(bot, chat_id, url, status_message_id)
    ydl_opts = _create_ydl_options(format_string, temp_download_path)
    file_path, video_info = await _download_video_file(url, ydl_opts, temp_download_path)
    await _send_downloaded_file(bot, chat_id, file_path, video_info, status_message)


async def _handle_download_error(bot: Bot, chat_id: int, url: str, error: Exception) -> None:
    """Handle download error by notifying user and admin with specific messages."""
    # Log with context
    context = getattr(error, "context", {})
    logger.error(f"Download failed: {str(error)}", exc_info=True, extra={"url": url, "chat_id": chat_id, **context})

    # Generate user-friendly message based on error type
    if isinstance(error, VideoNotFoundError):
        user_message = (
            "❌ <b>Video Not Found</b>\n\n"
            "The video you requested is not available. This could be due to:\n"
            "• Video was deleted or made private\n"
            "• Invalid or expired link\n"
            "• Geographic restrictions"
        )
    elif isinstance(error, VideoTooLargeError):
        user_message = (
            f"❌ <b>File Too Large</b>\n\n{str(error)}\n\nPlease try a lower quality format or shorter video."
        )
    elif isinstance(error, UnsupportedFormatError):
        user_message = (
            "❌ <b>Unsupported Format</b>\n\n"
            "This video format is not supported. Please try:\n"
            "• A different video URL\n"
            "• A different quality setting"
        )
    elif isinstance(error, NetworkError):
        user_message = (
            "❌ <b>Network Error</b>\n\n"
            "Failed to download video due to network issues.\n"
            "Please try again in a few minutes."
        )
    elif isinstance(error, TelegramEntityTooLarge):
        user_message = (
            "❌ <b>File Too Large for Upload</b>\n\n"
            "The file was downloaded successfully but is too large to send via Telegram.\n"
            "Please try a lower quality format (SD or HD)."
        )
    else:
        user_message = "❌ <b>Download Failed</b>\n\nAn unexpected error occurred. Please try again or contact support."

    # Notify user with specific message
    await bot.send_message(chat_id, user_message)

    # Notify admin with technical details
    admin_message = f"Download failed: {url}\nError type: {type(error).__name__}\nError: {str(error)}\nUser: {chat_id}"
    if context:
        admin_message += f"\nContext: {context}"

    await notify_admin(bot, admin_message)


async def download_youtube_video(
    bot: Bot,
    chat_id: int,
    url: str,
    format_string: str = "best",
    temp_dir: Optional[Path] = None,
    status_message_id: Optional[int] = None,
) -> None:
    """
    Download YouTube video and send it to the user.

    Args:
        bot: Telegram bot instance
        chat_id: ID of the chat to send the video to
        url: URL of the YouTube video
        format_string: yt-dlp format string
        temp_dir: Directory to store temporary files, defaults to config.TEMP_DIR
        status_message_id: ID of the status message to update

    Raises:
        DownloadError: If downloading or sending fails
    """
    if temp_dir is None:
        temp_dir = config.TEMP_DIR

    temp_download_dir = tempfile.mkdtemp(dir=temp_dir)
    temp_download_path = Path(temp_download_dir)

    logger.info(f"Starting download: {url} with format: {format_string} for chat_id: {chat_id}")

    try:
        await _execute_download_process(bot, chat_id, url, format_string, temp_download_path, status_message_id)
    except Exception as e:
        await _handle_download_error(bot, chat_id, url, e)
        raise DownloadError(f"Error downloading video: {str(e)}") from e

    finally:
        _cleanup_temp_directory(temp_download_dir)


def _cleanup_temp_directory(temp_dir: str) -> None:
    """Clean up temporary directory safely."""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Failed to clean up temporary directory: {str(e)}")


def is_youtube_url(url: str) -> bool:
    """
    Check if the URL is a YouTube URL.

    Args:
        url: URL to check

    Returns:
        True if URL is from YouTube, False otherwise
    """
    youtube_domains = (
        "youtube.com",
        "youtu.be",
        "m.youtube.com",
        "youtube-nocookie.com",
    )
    url_lower = url.lower()
    return any(domain in url_lower for domain in youtube_domains)
