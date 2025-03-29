"""Download service for video grabber bot."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp
from aiogram import Bot
from loguru import logger

from bot.config import TEMP_DIR
from bot.utils.logging import notify_admin
from aiogram.types import FSInputFile


class DownloadError(Exception):
    """Exception raised for errors during download process."""

    pass


async def download_youtube_video(
    bot: Bot, chat_id: int, url: str, temp_dir: Optional[Path] = None
) -> None:
    """
    Download YouTube video and send it to the user.

    Args:
        bot: Telegram bot instance
        chat_id: ID of the chat to send the video to
        url: URL of the YouTube video
        temp_dir: Directory to store temporary files, defaults to TEMP_DIR

    Raises:
        DownloadError: If downloading or sending fails
    """
    if temp_dir is None:
        temp_dir = TEMP_DIR

    temp_download_dir = tempfile.mkdtemp(dir=temp_dir)
    temp_download_path = Path(temp_download_dir)

    try:
        logger.info(f"Starting download: {url} for chat_id: {chat_id}")

        # Send message indicating download has started
        status_message = await bot.send_message(
            chat_id, f"⏳ <b>Download started</b>\n\nProcessing your request for {url}"
        )

        # Options for yt-dlp
        ydl_opts = {
            "format": "best",  # Best quality format
            "outtmpl": str(temp_download_path / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Extracting info: {url}")
            info = ydl.extract_info(url, download=False)

            logger.debug(f"Starting download with options: {ydl_opts}")
            ydl.download([url])

            # Get downloaded file path - should be only one file in the temp dir
            downloaded_files = list(temp_download_path.glob("*"))
            if not downloaded_files:
                raise DownloadError("Download completed but no files found")

            file_path = downloaded_files[0]
            file_size = file_path.stat().st_size

            logger.info(f"Download completed: {file_path} ({file_size} bytes)")

            # Update status message
            await bot.edit_message_text(
                f"✅ <b>Download completed</b>\n\nNow sending file: {file_path.name}",
                chat_id=chat_id,
                message_id=status_message.message_id,
            )

            # Send file as document (supports files up to 2GB)

            await bot.send_document(
                chat_id,
                document=FSInputFile(file_path),
                caption=f"📥 <b>{info.get('title', 'Video')}</b>\n\nDownloaded from YouTube",
            )

            # Update status message
            await bot.edit_message_text(
                "✅ <b>Download completed</b>\n\nFile sent successfully!",
                chat_id=chat_id,
                message_id=status_message.message_id,
            )

            logger.info(f"File sent successfully to chat_id: {chat_id}")

    except Exception as e:
        error_message = f"Error downloading video: {str(e)}"
        logger.error(error_message, exc_info=True)

        # Notify user of the error
        await bot.send_message(chat_id, f"❌ <b>Download failed</b>\n\n{error_message}")

        # Notify admin
        await notify_admin(bot, f"Download failed: {url}\nError: {str(e)}")

        raise DownloadError(error_message) from e

    finally:
        # Clean up temporary files
        try:
            if os.path.exists(temp_download_dir):
                shutil.rmtree(temp_download_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_download_dir}")
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
    return any(
        domain in url.lower()
        for domain in [
            "youtube.com",
            "youtu.be",
            "m.youtube.com",
            "youtube-nocookie.com",
        ]
    )
