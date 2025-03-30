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
    # Добавляем логирование полученных данных
    logger.debug(f"Received callback data: {callback.data}")

    # Parse callback data (первые две части + последняя)
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

    # Acknowledge the callback
    await callback.answer(f"Starting download in {format_data['label']} format...")

    # Edit the original message to show the selection
    await callback.message.edit_text(
        f"🔄 <b>Download started</b>\n\n"
        f"Format: <b>{format_data['label']}</b>\n"
        f"URL: {url}\n\n"
        "Please wait while your file is being downloaded..."
    )

    try:
        # Get the bot instance
        bot = get_bot()

        # Download with selected format
        await download_youtube_video(
            bot, callback.message.chat.id, url, format_string=format_data["format"]
        )

        # Clear URL from storage after successful download
        clear_url(url_id)

    except DownloadError as e:
        logger.error(f"Download failed: {str(e)}")
        # Clear URL from storage after failed download
        clear_url(url_id)
    """
    Process format selection callback.

    Args:
        callback: Callback query containing format and URL ID
    """
    # Добавляем логирование полученных данных
    logger.debug(f"Received callback data: {callback.data}")

    # Parse callback data
    parts = callback.data.split(":")
    logger.debug(f"Parsed parts: {parts}")

    if len(parts) != 3:
        logger.error(
            f"Invalid format selection: parts length is {len(parts)}, expected 3"
        )
        await callback.answer("Invalid format selection")
        return

    _, format_id, url_id = parts
    user_id = callback.from_user.id

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

    # Acknowledge the callback
    await callback.answer(f"Starting download in {format_data['label']} format...")

    # Edit the original message to show the selection
    await callback.message.edit_text(
        f"🔄 <b>Download started</b>\n\n"
        f"Format: <b>{format_data['label']}</b>\n"
        f"URL: {url}\n\n"
        "Please wait while your file is being downloaded..."
    )

    try:
        # Get the bot instance
        bot = get_bot()

        # Download with selected format
        await download_youtube_video(
            bot, callback.message.chat.id, url, format_string=format_data["format"]
        )

        # Clear URL from storage after successful download
        clear_url(url_id)

    except DownloadError as e:
        logger.error(f"Download failed: {str(e)}")
        # Clear URL from storage after failed download
        clear_url(url_id)
