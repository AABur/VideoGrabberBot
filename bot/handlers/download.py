# bot/handlers/download.py (изменения)
"""Download handler for processing video links."""

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from loguru import logger

from bot.services.downloader import (
    DownloadError,
    download_youtube_video,
    is_youtube_url,
)
from bot.services.formats import get_format_by_id, get_format_options
from bot.services.storage import store_url, get_url, store_format, clear_url
from bot.telegram_api.client import get_bot
from bot.utils.db import is_user_authorized
from bot.services.queue import download_queue, DownloadTask

# Create router for download handlers
download_router = Router()


@download_router.message(F.text.startswith(("http://", "https://")))
async def process_url(message: Message) -> None:
    """
    Process URL message and show format options.

    Args:
        message: The message containing the URL
    """
    user_id = message.from_user.id
    url = message.text.strip()

    # Check if user is authorized
    if not await is_user_authorized(user_id):
        await message.answer(
            "⛔ <b>Access Denied</b>\n\n"
            "You don't have permission to use this bot.\n"
            "Please contact the administrator for access."
        )
        return

    logger.info(f"Received URL from user {user_id}: {url}")

    # Check if URL is from YouTube
    if is_youtube_url(url):
        # Store URL and get ID
        url_id = store_url(url)

        # Get available format options
        format_options = get_format_options()

        # Create inline keyboard with format options
        keyboard = []
        row = []

        for i, (format_id, label) in enumerate(format_options):
            # Create a new row after every 2 buttons
            if i % 2 == 0 and row:
                keyboard.append(row)
                row = []

            # Use shorter callback data
            button = InlineKeyboardButton(
                text=label, callback_data=f"fmt:{format_id}:{url_id}"
            )
            row.append(button)

        # Add the last row if it's not empty
        if row:
            keyboard.append(row)

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(
            "🎬 <b>Choose Download Format</b>\n\n"
            "Select the format you want to download:",
            reply_markup=markup,
        )
        logger.info(f"Sent format selection keyboard to user {user_id}")

    else:
        await message.answer(
            "⚠️ <b>Unsupported URL</b>\n\nCurrently only YouTube links are supported."
        )


@download_router.callback_query(F.data.startswith("fmt:"))
async def process_format_selection(callback: CallbackQuery) -> None:
    """
    Process format selection callback.

    Args:
        callback: Callback query containing format and URL ID
    """
    # Логирование полученных данных
    logger.debug(f"Received callback data: {callback.data}")

    # Parse callback data
    parts = callback.data.split(":")
    logger.debug(f"Parsed parts: {parts}")

    if len(parts) < 3:
        logger.error(
            f"Invalid format selection: parts length is {len(parts)}, expected at least 3"
        )
        await callback.answer("Invalid format selection")
        return

    # Первая часть - fmt, последняя - url_id, всё между - format_id
    cmd = parts[0]
    url_id = parts[-1]
    format_id = ":".join(parts[1:-1])  # Собираем format_id обратно

    user_id = callback.from_user.id
    logger.debug(f"Parsed values: cmd={cmd}, format_id={format_id}, url_id={url_id}")

    # Get URL from storage
    url = get_url(url_id)
    if not url:
        logger.error(f"URL not found for ID: {url_id}")
        await callback.answer("URL not found or expired")
        return

    # Get format details
    format_data = get_format_by_id(format_id)
    if not format_data:
        logger.error(f"Format not found: {format_id}")
        await callback.answer("Selected format not found")
        return

    logger.info(
        f"User {user_id} selected format: {format_data['label']} for URL: {url}"
    )

    # Store format selection
    store_format(url_id, format_id)

    # Get the bot instance
    bot = get_bot()

    # Acknowledge the callback
    await callback.answer(
        f"Processing your request in {format_data['label']} format..."
    )

    # Check if queue is processing and user is already in queue
    is_processing = download_queue.is_processing
    is_user_in_queue = download_queue.is_user_in_queue(callback.message.chat.id)

    # Prepare status message
    status_text = f"🔄 <b>Download {'' if not is_processing else 'queued'}</b>\n\n"
    status_text += f"Format: <b>{format_data['label']}</b>\n"
    status_text += f"URL: {url}\n\n"

    if is_processing:
        status_text += "Your download has been added to the queue. "
        if is_user_in_queue:
            status_text += "You already have downloads in the queue."
        else:
            status_text += "You will be notified when processing begins."
    else:
        status_text += "Starting download now..."

    # Edit the original message to show the selection
    status_message = await callback.message.edit_text(status_text)

    # Create and add the download task to the queue
    task = DownloadTask(
        chat_id=callback.message.chat.id,
        url=url,
        format_string=format_data["format"],
        status_message_id=status_message.message_id,
        additional_data={"bot": bot, "url_id": url_id},
    )

    queue_position = await download_queue.add_task(task)

    if queue_position > 1:
        # If not first in queue, update the message with position
        await bot.edit_message_text(
            f"{status_text}\n\nQueue position: {queue_position}",
            chat_id=callback.message.chat.id,
            message_id=status_message.message_id,
        )

    # Note: We don't clear the URL here since it will be done by the queue processor
