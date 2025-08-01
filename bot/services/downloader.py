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

from bot.config import TEMP_DIR
from bot.utils.logging import notify_admin


class DownloadError(Exception):
    """Exception raised for errors during download process."""


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
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.debug(f"Extracting info: {url}")
        video_info = ydl.extract_info(url, download=False)

        logger.debug(f"Starting download with options: {ydl_opts}")
        ydl.download([url])

        # Get downloaded file path
        downloaded_files = list(temp_download_path.glob("*"))
        if not downloaded_files:
            raise DownloadError("Download completed but no files found")

        file_path = downloaded_files[0]
        file_size = file_path.stat().st_size
        logger.info(f"Download completed: {file_path} ({file_size} bytes)")

        return file_path, video_info


async def _download_video_file(url: str, ydl_opts: dict, temp_download_path: Path) -> tuple[Path, dict]:
    """Download video and return file path and video info (async wrapper)."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as executor:
        return await loop.run_in_executor(executor, _sync_download_video_file, url, ydl_opts, temp_download_path)


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
    """Handle download error by notifying user and admin."""
    error_message = f"Error downloading video: {str(error)}"
    logger.error(error_message, exc_info=True)

    # Notify user of the error
    await bot.send_message(chat_id, f"❌ <b>Download failed</b>\n\n{error_message}")

    # Notify admin
    await notify_admin(bot, f"Download failed: {url}\nError: {str(error)}")


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
