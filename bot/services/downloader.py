# bot/services/downloader.py
"""Download service for video grabber bot."""

import asyncio
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import yt_dlp
from aiogram import Bot
from aiogram.types import Chat, FSInputFile, Message
from loguru import logger

from bot.config import DOWNLOAD_TIMEOUT, MAX_FILE_SIZE, TEMP_DIR
from bot.utils.exceptions import (
    DownloadError,
    NetworkError,
    UnsupportedFormatError,
    VideoNotFoundError,
    VideoTooLargeError,
)
from bot.utils.logging import notify_admin


async def _create_or_update_status_message(
    bot: Bot, chat_id: int, url: str, status_message_id: Optional[int]
) -> Message:
    """Create or update status message for download."""
    status_text = f"⏳ <b>Download started</b>\n\nProcessing your request for {url}"

    if status_message_id:
        await bot.edit_message_text(status_text, chat_id=chat_id, message_id=status_message_id)
        return Message(message_id=status_message_id, chat=Chat(id=chat_id), bot=bot)

    return await bot.send_message(chat_id, status_text)


def _create_ydl_options(format_string: str, temp_download_path: Path) -> dict:
    """Create yt-dlp options dictionary."""
    return {
        "format": format_string,
        "outtmpl": str(temp_download_path / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }


def _sync_download_video_file(url: str, ydl_opts: dict, temp_download_path: Path) -> tuple[Path, dict]:
    """Synchronous download function to be run in thread pool."""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Extracting info: {url}")
            
            try:
                video_info = ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e).lower()
                if "not available" in error_msg or "video not found" in error_msg:
                    raise VideoNotFoundError(
                        "Video not found or unavailable",
                        context={"url": url, "original_error": str(e)}
                    ) from e
                if "unsupported url" in error_msg or "unsupported format" in error_msg:
                    raise UnsupportedFormatError(
                        "Video format not supported",
                        context={"url": url, "original_error": str(e)}
                    ) from e
                raise NetworkError(
                    "Network error during video info extraction",
                    context={"url": url, "original_error": str(e)}
                ) from e
            
            # Check expected file size if available
            if video_info and video_info.get("filesize"):
                expected_size = video_info["filesize"]
                if expected_size > MAX_FILE_SIZE:
                    raise VideoTooLargeError(
                        f"Video file size ({expected_size // (1024*1024)} MB) exceeds limit ({MAX_FILE_SIZE // (1024*1024)} MB)",
                        context={"url": url, "file_size": expected_size, "limit": MAX_FILE_SIZE}
                    )
            
            logger.debug(f"Starting download with options: {ydl_opts}")
            
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                raise NetworkError(
                    "Network error during video download",
                    context={"url": url, "original_error": str(e)}
                ) from e

            # Get downloaded file path
            downloaded_files = list(temp_download_path.glob("*"))
            if not downloaded_files:
                raise DownloadError(
                    "Download completed but no files found",
                    context={"url": url, "temp_path": str(temp_download_path)}
                )

            file_path = downloaded_files[0]
            file_size = file_path.stat().st_size
            
            # Check actual file size
            if file_size > MAX_FILE_SIZE:
                file_path.unlink()  # Delete oversized file
                raise VideoTooLargeError(
                    f"Downloaded file size ({file_size // (1024*1024)} MB) exceeds limit ({MAX_FILE_SIZE // (1024*1024)} MB)",
                    context={"url": url, "file_size": file_size, "limit": MAX_FILE_SIZE}
                )
            
            logger.info(f"Download completed: {file_path} ({file_size} bytes)")
            return file_path, video_info
            
    except Exception as e:
        if isinstance(e, (VideoNotFoundError, UnsupportedFormatError, NetworkError, VideoTooLargeError)):
            raise
        raise DownloadError(
            "Unexpected error during download",
            context={"url": url, "original_error": str(e)}
        ) from e


async def _download_video_file(url: str, ydl_opts: dict, temp_download_path: Path) -> tuple[Path, dict]:
    """Download video and return file path and video info (async wrapper)."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as executor:
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(executor, _sync_download_video_file, url, ydl_opts, temp_download_path),
                timeout=DOWNLOAD_TIMEOUT
            )
        except asyncio.TimeoutError as e:
            raise NetworkError(
                f"Download timed out after {DOWNLOAD_TIMEOUT} seconds",
                context={"url": url, "timeout": DOWNLOAD_TIMEOUT}
            ) from e


async def _send_downloaded_file(
    bot: Bot, chat_id: int, file_path: Path, video_info: dict, status_message: Message
) -> None:
    """Send downloaded file to user."""
    # Update status message
    await bot.edit_message_text(
        f"✅ <b>Download completed</b>\n\nNow sending file: {file_path.name}",
        chat_id=chat_id,
        message_id=status_message.message_id,
    )

    # Send file as document
    video_title = video_info.get("title", "Video")
    await bot.send_document(
        chat_id,
        document=FSInputFile(file_path),
        caption=f"📥 <b>{video_title}</b>\n\nDownloaded from YouTube",
    )

    # Update status message
    await bot.edit_message_text(
        "✅ <b>Download completed</b>\n\nFile sent successfully!",
        chat_id=chat_id,
        message_id=status_message.message_id,
    )

    logger.info(f"File sent successfully to chat_id: {chat_id}")


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
    context = getattr(error, 'context', {})
    logger.error(
        f"Download failed: {str(error)}",
        exc_info=True,
        extra={"url": url, "chat_id": chat_id, **context}
    )

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
            "❌ <b>File Too Large</b>\n\n"
            f"{str(error)}\n\n"
            "Please try a lower quality format or shorter video."
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
    else:
        user_message = (
            "❌ <b>Download Failed</b>\n\n"
            "An unexpected error occurred. Please try again or contact support."
        )

    # Notify user with specific message
    await bot.send_message(chat_id, user_message)

    # Notify admin with technical details
    admin_message = (
        f"Download failed: {url}\n"
        f"Error type: {type(error).__name__}\n"
        f"Error: {str(error)}\n"
        f"User: {chat_id}"
    )
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
        temp_dir: Directory to store temporary files, defaults to TEMP_DIR
        status_message_id: ID of the status message to update

    Raises:
        DownloadError: If downloading or sending fails
    """
    if temp_dir is None:
        temp_dir = TEMP_DIR

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
