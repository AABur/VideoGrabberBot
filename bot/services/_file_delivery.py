# bot/services/_file_delivery.py
"""File delivery service for sending downloaded files via Telegram."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from aiogram import Bot
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types import FSInputFile
from loguru import logger

from bot.services._download_core import MB_SIZE, TELEGRAM_UPLOAD_LIMIT


@dataclass
class _StatusMessageRef:
    """Lightweight reference to an existing Telegram message."""

    message_id: int


class _StatusMessage(Protocol):
    """Protocol for objects with message_id attribute."""

    message_id: int


async def _create_or_update_status_message(
    bot: Bot, chat_id: int, url: str, status_message_id: Optional[int]
) -> _StatusMessage:
    """Create or update status message for download."""
    status_text = f"⏳ <b>Download started</b>\n\nProcessing your request for {url}"

    if status_message_id:
        await bot.edit_message_text(status_text, chat_id=chat_id, message_id=status_message_id)
        return _StatusMessageRef(message_id=status_message_id)

    return await bot.send_message(chat_id, status_text)


async def _send_downloaded_file(
    bot: Bot, chat_id: int, file_path: Path, video_info: Dict[str, Any], status_message: _StatusMessage
) -> None:
    """Send downloaded file to user with size validation."""
    # Check file size
    file_size = file_path.stat().st_size
    file_size_mb = file_size / MB_SIZE

    # Update status message with file info
    await bot.edit_message_text(
        f"✅ <b>Download completed</b>\n\nFile: {file_path.name}\nSize: {file_size_mb:.1f} MB\n\nNow sending file...",
        chat_id=chat_id,
        message_id=status_message.message_id,
    )

    # Check if file exceeds Telegram limits
    if file_size > TELEGRAM_UPLOAD_LIMIT:
        logger.warning(f"File size {file_size_mb:.1f} MB exceeds Telegram limit of 50 MB")
        await bot.edit_message_text(
            f"❌ <b>File Too Large</b>\n\n"
            f"File size: {file_size_mb:.1f} MB\n"
            f"Telegram limit: 50 MB\n\n"
            f"Please try a lower quality format (SD or HD) for shorter videos.",
            chat_id=chat_id,
            message_id=status_message.message_id,
        )
        return

    try:
        # Send file as document
        video_title = video_info.get("title", "Video")
        await bot.send_document(
            chat_id,
            document=FSInputFile(file_path),
            caption=f"📥 <b>{video_title}</b>\n\nDownloaded from YouTube",
            request_timeout=300,  # 5 minutes for large files
        )

        # Update status message on success
        await bot.edit_message_text(
            "✅ <b>Download completed</b>\n\nFile sent successfully!",
            chat_id=chat_id,
            message_id=status_message.message_id,
        )

        logger.info(f"File sent successfully to chat_id: {chat_id}, size: {file_size_mb:.1f} MB")

    except TelegramEntityTooLarge:
        # Handle Telegram file size limit exceeded
        await bot.edit_message_text(
            f"❌ <b>Upload Failed</b>\n\n"
            f"File size: {file_size_mb:.1f} MB\n"
            f"Telegram rejected the upload due to size limits.\n\n"
            f"Please try a lower quality format (SD or HD).",
            chat_id=chat_id,
            message_id=status_message.message_id,
        )
        logger.error(f"TelegramEntityTooLarge: {file_size_mb:.1f} MB file rejected for chat {chat_id}")

    except Exception as e:
        # Handle other upload errors
        error_msg = str(e)
        if "Request Entity Too Large" in error_msg or "Entity Too Large" in error_msg:
            await bot.edit_message_text(
                f"❌ <b>Upload Failed</b>\n\n"
                f"File size: {file_size_mb:.1f} MB\n"
                f"Telegram rejected the upload due to size limits.\n\n"
                f"Please try a lower quality format.",
                chat_id=chat_id,
                message_id=status_message.message_id,
            )
            logger.error(f"Upload rejected due to size: {file_size_mb:.1f} MB for chat {chat_id}")
        else:
            # Re-raise other errors to be handled by main error handler
            raise
